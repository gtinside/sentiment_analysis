from sentiment_analysis.datasource.twitter_fetch import TwitterStreamProcessor
from sentiment_analysis.common.environment.set_env import get_sqs_conn, get_twitter_keys, get_redis_conn
from multiprocessing import Pool
import logging
from logging.config import fileConfig
fileConfig('../common/logging/logging_config.ini')

logger = logging.getLogger(__name__)


class Environment:
    def __init__(self):
        sqs_conn = get_sqs_conn()
        twitter_keys = get_twitter_keys()
        self._stream_processor = TwitterStreamProcessor(consumer_key=twitter_keys[0],
                                                        consumer_key_secret=twitter_keys[1],
                                                        twitter_key=twitter_keys[2],
                                                        twitter_key_secret=twitter_keys[3],
                                                        redis_conn=get_redis_conn(),
                                                        symbols_list="../metadata/symbols.log",
                                                        sqs_client=sqs_conn[0], sqs_queue_url=sqs_conn[1])

    def get_stream_processor(self):
        return self._stream_processor


env = Environment()


def init_process(event_type):
    if event_type == "stream":
        logging.info("Initializing stream")
        env.get_stream_processor().init_streaming()
    else:
        logging.info("Initializing processor")
        env.get_stream_processor().init_processing()


if __name__ == '__main__':
    Pool().map(init_process, ["stream", "processor"])
