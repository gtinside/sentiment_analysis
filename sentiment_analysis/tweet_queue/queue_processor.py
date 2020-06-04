import logging
from logging.config import fileConfig
import os
fileConfig(os.path.dirname(__file__) + '/../common/logging/logging_config.ini')

logger = logging.getLogger(__name__)


class QueueProcessor:
    def __init__(self, client=None, queue_url=None):
        self._sqs = client
        self._queue_url = queue_url

    def queue_message(self, tweet, tag):
        try:
            response = self._sqs.send_message(QueueUrl=self._queue_url, MessageAttributes={
                'name': {
                    'StringValue': tag[0],
                    'DataType': 'String'
                },
                'symbol': {
                    'StringValue': tag[1],
                    'DataType': 'String'
                }
            }, MessageBody=tweet)
            logging.info(response['MessageId'])
        except Exception as e:
            logging.exception("Error queueing to SQS due to {}".format(e), exc_info=True)

    def read_message(self):
        try:
            response = self._sqs.receive_message(QueueUrl=self._queue_url, MaxNumberOfMessages=1,
                                                 MessageAttributeNames=['All'])
            return response['Messages'][0]
        except Exception as e:
            logging.exception("Error reading message from SQS, probably the queue is empty or {}".format(e), exc_info=True)
            return None

    def delete_message(self, message):
        receipt_handle = message['ReceiptHandle']
        self._sqs.delete_message(
            QueueUrl=self._queue_url,
            ReceiptHandle=receipt_handle
        )
