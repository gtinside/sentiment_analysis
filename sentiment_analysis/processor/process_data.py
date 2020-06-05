from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from string import punctuation
import logging
from logging.config import fileConfig
import os
fileConfig(os.path.dirname(__file__) + '/../common/logging/logging_config.ini')

logger = logging.getLogger(__name__)


class TweetPostProcessor:
    def __init__(self, use_stop_words=True, use_tokenizer=True):
        self._stopwords = stopwords.words('english') if use_stop_words else [] + list(punctuation) + ['AT_USER', 'URL']
        self._sentiment_analyzer = SentimentIntensityAnalyzer()
        self._use_tokenizer = use_tokenizer

    def process_tweets(self, tweet):
        """
        This method does the following to tweet text
        1. Lowercase the characters
        2. Remove the URLs
        3. Remove usernames
        4. Remote the # in hashtags
        5. Remove repeated characters (not words!)
        6. Remove stop words
        :param tweet: The tweet text
        :return: Processed tweet
        """
        try:
            tweet = tweet.lower()
            tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
            tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
            tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
            tweet = word_tokenize(tweet) if self._use_tokenizer else tweet
            return self.analyze_data(''.join([word for word in tweet if word not in self._stopwords]))
        except Exception as e:
            logging.exception("Error scoring tweet {}".format(e), exc_info=True)
            return 0

    def analyze_data(self, data):
        """
        Function to analyze the tweet data. Using the VADER sentiment analysis
        library, more details here -> https://github.com/cjhutto/vaderSentiment
        Analysis of score:
        [-1 to 0): negative,
        [0]: neutral
        (0 to +1]: positive

        Looking for compound should get us the sentiment on the data point
        """
        analysis_score = self._sentiment_analyzer.polarity_scores(data)
        compound_score = analysis_score['compound']
        if compound_score >= 0.05:
            return 1
        elif -0.05 < compound_score < 0.05:
            return 0
        else:
            return -1
