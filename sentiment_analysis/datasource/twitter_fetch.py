import logging
import time
import schedule
import tweepy
from sentiment_analysis.persistence.persist_analysis import AnalysisPersistence
from sentiment_analysis.processor.process_data import TweetPostProcessor
from sentiment_analysis.tweet_queue.queue_processor import QueueProcessor
from logging.config import fileConfig
fileConfig('../common/logging/logging_config.ini')

logger = logging.getLogger(__name__)


class TwitterStreamProcessor:
    def __init__(self, consumer_key, consumer_key_secret, twitter_key, twitter_key_secret,
                 redis_conn, symbols_list, sqs_client, sqs_queue_url, run_forever=True):
        self._queue_processor = QueueProcessor(sqs_client, sqs_queue_url)
        self._tweet_processor = TweetPostProcessor()
        self._persist = AnalysisPersistence(redis_conn)
        self._consumer_key = consumer_key
        self._consumer_key_secret = consumer_key_secret
        self._twitter_key = twitter_key
        self._twitter_key_secret = twitter_key_secret
        self._symbols_list = symbols_list
        self._run_forever = run_forever

    def get_tags(self):
        tags = []
        logging.info("Reading the properties {} to build the tags".format(self._symbols_list))
        with open(self._symbols_list) as log_file:
            for line in log_file:
                tags.append(line.strip().split(","))
        return tags

    def init_streaming(self):
        # initializing the stream, capture tweets in real time
        while self._run_forever:
            for tag in self.get_tags():
                logging.info("Initiating the stream for {}".format(tag))
                streams = tweepy.Stream(auth=self._authenticate(), listener=TweetStreamListener(tag,
                                                                                                self._queue_processor))
                streams.filter(track=tag, languages=["en"])
                logging.info("Finalizing the stream for {}".format(tag))

    def init_processing(self):
        schedule.every(1).second.do(self.analyze_tweets)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def analyze_tweets(self):
        try:
            message = self._queue_processor.read_message()
            if message is not None:
                logging.info("Received message from queue" + message['Body'])
                score = self._tweet_processor.process_tweets(message['Body'])
                category = message['MessageAttributes']['name']['StringValue'] + ":" + \
                           message['MessageAttributes']['symbol']['StringValue']
                self._persist.increment_counter(category + ":total")
                if score > 0:
                    self._persist.increment_counter(category + ":positive")
                elif score < 0:
                    self._persist.increment_counter(category + ":negative")

                logging.info("Tweet analysed, scored & persisted, lets get rid of it!")
                self._queue_processor.delete_message(message)
        except Exception as e:
            logging.exception("An exception occurred, will retry later {}".format(e), exc_info=True)

    def _authenticate(self):
        auth = tweepy.OAuthHandler(self._consumer_key, self._consumer_key_secret)
        auth.set_access_token(self._twitter_key, self._twitter_key_secret)
        # wait_on_rate_limit flag will cause Tweepy to pause after limit expiry
        return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True).auth


class TweetStreamListener(tweepy.StreamListener):
    def __init__(self, tag, queue_processor, default_timeout=60):
        super(TweetStreamListener, self).__init__()
        self._queue_processor = queue_processor
        self._start_time = time.time()
        self._tag = tag
        self._default_timeout = default_timeout

    def on_status(self, status):
        logging.info("Received tweet on stream for tag:{}".format(self._tag))
        self._queue_processor.queue_message(status.text, self._tag)
        logging.info("Tweet queued successfully for tag: {}".format(self._tag))
        # Let the stream run only for 1 min
        if (time.time() - self._start_time) >= self._default_timeout:
            logging.info("Time's up for stream on {}, cancelling it".format(self._tag))
            return False

    def on_error(self, status_code):
        logging.info("Error establishing stream for tag {}, cancelling it due to {}".format(self._tag, status_code))
        return False

    def on_exception(self, exception):
        logging.info("Exception establishing stream, cancelling it {}".format(exception))
        return False
