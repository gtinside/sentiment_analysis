import os
import boto3
import json
import redis
import logging
from logging.config import fileConfig
fileConfig(os.path.dirname(__file__) + '/../logging/logging_config.ini')

logger = logging.getLogger(__name__)


def get_sqs_conn():
    if os.environ.get('LocalDevelopment') is not None:
        logging.info("Initializing the setup for local development, setting fake properties")
        client = boto3.client('sqs',
                              endpoint_url=_get_local_stack_url(),
                              use_ssl=False,
                              aws_access_key_id='ACCESS_KEY',
                              aws_secret_access_key='SECRET_KEY',
                              region_name='us-east-1')
    else:
        logging.info("Beware this is production !!!")
        client = boto3.client('sqs', region_name='us-east-2')
    queues = client.list_queues()
    if 'QueueUrls' in queues and 'Tweets' in str(queues['QueueUrls']):
        for queue in queues['QueueUrls']:
            if 'Tweets' in queue:
                return client, queue
    logging.info("No queue for handling tweets found, creating one")
    response = client.create_queue(
        QueueName='Tweets'
    )
    return client, response['QueueUrl']


def get_twitter_keys():
    """
    Twitter keys are expected to be stored in S3
    :return: consumer_key, consumer_key_secret, twitter_key, twitter_key_secret
    """
    if os.environ.get('LocalDevelopment') is not None:
        logging.info("Initializing the setup for local development, setting fake properties")
        client = boto3.client('s3',
                              endpoint_url=_get_local_stack_url(),
                              use_ssl=False,
                              aws_access_key_id='ACCESS_KEY',
                              aws_secret_access_key='SECRET_KEY',
                              region_name='us-east-1')
    else:
        client = boto3.client('s3')
    # Read the json file keys.cfg from bucket application-keys
    obj = client.get_object(Bucket='application-keys', Key='keys.cfg')
    j = json.loads(obj['Body'].read().decode('utf-8'))
    return j['consumer_key'], j['consumer_key_secret'], j['twitter_key'], j['twitter_secret']


def get_redis_conn():
    """
    Function is responsible for initializing the connection based on env
    :return: Redis connection details
    """
    if os.environ.get('LocalDevelopment') is not None:
        logging.info("Initializing the setup for local development, setting fake properties")
        if os.environ.get('RedisContainer') is not None:
            return redis.Redis(host=os.environ.get('RedisContainer'), port=6379)
        client = boto3.client('s3',
                              endpoint_url=_get_local_stack_url(),
                              use_ssl=False,
                              aws_access_key_id='ACCESS_KEY',
                              aws_secret_access_key='SECRET_KEY',
                              region_name='us-east-1')
    else:
        logging.info("Initializing the setup for production")
        client = boto3.client('s3')

    # Read the json file keys.cfg from bucket application-keys
    obj = client.get_object(Bucket='application-keys', Key='keys.cfg')
    j = json.loads(obj['Body'].read().decode('utf-8'))

    return redis.Redis(host=j['redis_primary_endpoint'], port=int(j['redis_port']))


def _get_local_stack_url():
    if os.environ.get('LocalStackContainer') is not None:
        return "http://{}:4566".format(os.environ.get('LocalStackContainer'))
    else:
        return "http://{}:4566".format("localhost")
