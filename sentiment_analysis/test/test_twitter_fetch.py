import unittest
from unittest.mock import MagicMock, patch
import tweepy
import os
from sentiment_analysis.datasource.twitter_fetch import TwitterStreamProcessor, TweetStreamListener


class TwitterOperationTestCases(unittest.TestCase):
    _stream_processor = TwitterStreamProcessor(consumer_key=None,
                                               consumer_key_secret=None,
                                               twitter_key=None,
                                               twitter_key_secret=None,
                                               redis_conn=None,
                                               symbols_list=os.path.dirname(__file__)+"/metadata/test_symbols.log",
                                               sqs_client=None, sqs_queue_url=None, run_forever=False,
                                               use_stop_words=False, use_tokenizer=False)
    _twitter_stream = TweetStreamListener("FakeTag", None)

    def test_get_tags(self):
        tags = self._stream_processor.get_tags()
        self.assertEqual(len(tags) == 2, True, "Tags should not be empty")
        self.assertEqual('Microsoft' in tags[0], True, "S&P 500 index has MSFT as part of it")

    @patch('tweepy.Stream')
    def test_init_streaming(self, mock_class):
        self._stream_processor.init_streaming()
        assert mock_class.stream
        assert mock_class is tweepy.Stream

    def test_analyze_positive_tweets(self):
        fake_sqs = MagicMock()
        fake_redis = MagicMock()
        self._stream_processor._queue_processor = fake_sqs
        self._stream_processor._persist = fake_redis

        fake_msg_attr = {'name': {'StringValue': 'FakeName'}, 'symbol': {'StringValue': 'FakeSymbol'}}
        fake_sqs_msg = {'Body': 'PYTHON IS EXTREMELY GREAT', 'MessageAttributes': fake_msg_attr}
        fake_sqs.read_message.return_value = fake_sqs_msg
        self._stream_processor.analyze_tweets()
        assert fake_redis.increment_counter.called
        fake_redis.increment_counter.assert_any_call('FakeName:FakeSymbol:positive')
        fake_redis.increment_counter.assert_any_call('FakeName:FakeSymbol:total')

    def test_analyze_negative_tweets(self):
        fake_sqs = MagicMock()
        fake_redis = MagicMock()
        self._stream_processor._queue_processor = fake_sqs
        self._stream_processor._persist = fake_redis
        fake_msg_attr = {'name': {'StringValue': 'FakeName'}, 'symbol': {'StringValue': 'FakeSymbol'}}
        fake_sqs_msg = {'Body': 'Today SUX!', 'MessageAttributes': fake_msg_attr}
        fake_sqs.read_message.return_value = fake_sqs_msg
        self._stream_processor.analyze_tweets()
        assert fake_redis.increment_counter.called
        fake_redis.increment_counter.assert_any_call('FakeName:FakeSymbol:negative')
        fake_redis.increment_counter.assert_any_call('FakeName:FakeSymbol:total')

    def test_on_status(self):
        self._twitter_stream._default_timeout = 0
        fake_sqs = MagicMock()
        self._twitter_stream._queue_processor = fake_sqs
        mock_status = MagicMock()
        mock_status.text = 'FakeMessage'
        response = self._twitter_stream.on_status(mock_status)
        fake_sqs.queue_message.assert_any_call('FakeMessage', 'FakeTag')
        self.assertEqual(response, False)

    def test_on_error_exception(self):
        mock_status_code = MagicMock()
        response1 = self._twitter_stream.on_error(mock_status_code)
        response2 = self._twitter_stream.on_exception(mock_status_code)
        self.assertEqual(response1, False)
        self.assertEqual(response2, False)


if __name__ == '__main__':
    unittest.main()
