from flask import Flask, render_template
import json
from sentiment_analysis.common.environment.set_env import get_redis_conn
import logging
from logging.config import fileConfig
fileConfig('../common/logging/logging_config.ini')

logger = logging.getLogger(__name__)
app = Flask("Sentiment Analysis")
redis_conn = get_redis_conn()


@app.route("/", methods=['GET'])
def index():
    results = _load_sentiments()
    return render_template("public/index.html", analyzed_map=json.dumps(results[0]), overall_tweets=results[1],
                           total_tweets_per_category=json.dumps(results[2]))


def _load_sentiments():
    heat_map = []
    results = _read_keys_from_redis()
    stock_sentiment_dict = results[0]
    total_positive = results[1]
    total_negative = results[2]
    total_tweets = results[3]
    total_tweets_per_category = {}
    for key in stock_sentiment_dict:
        try:
            value = stock_sentiment_dict[key]
            total_weight = total_positive + total_negative
            if 'positive' not in value:
                value['positive'] = 0
            if 'negative' not in value:
                value['negative'] = 0
            category_weight = round((value['positive'] + value['negative'])*100/total_weight, 2)
            delta = round(((value['positive']/total_positive) - (value['negative']/total_negative))*100, 2)
            logging.info("Total Weight: {}, Category: {}, Category Weight: {}, Delta: {}".format(total_weight, key, category_weight
                                                                                          , delta))
            logging.info("Category:{}, Category pos: {}, Category neg: {}, Total Pos: {}, Total Neg: {}".format(key,
                                                                                                         value['positive'], value['negative'], total_positive, total_negative))
            heat_map.append([key, "S&P500", category_weight, delta])
            total_tweets_per_category[key] = {}
            total_tweets_per_category[key]['total_tweets'] = value['total']
            total_tweets_per_category[key]['total_positive'] = value['positive']
            total_tweets_per_category[key]['total_negative'] = value['negative']
        except Exception as e:
            logging.exception("Error analyzing data for key {}, due to {}".format(key, e), exc_info=True)

    return heat_map, total_tweets, total_tweets_per_category


def _read_keys_from_redis():
    stock_sentiment_dict = {}
    total_positive = 0
    total_negative = 0
    total_tweets = 0
    for key in redis_conn.scan_iter("*"):
        try:
            logging.info("Getting count for category {}".format(key.decode("utf-8")))
            keys = key.decode("utf-8").split(":")
            # Split based on ':',
            # index = 0 will have name
            # index = 1 will have ticker
            # index = 2 will have type of sentiment, positive or negative or total
            if keys[0] not in stock_sentiment_dict:
                stock_sentiment_dict[keys[0]] = {}
                stock_sentiment_dict[keys[0]]['ticker'] = keys[1]
            tweet_count = int(redis_conn.get(key).decode("utf-8"))
            stock_sentiment_dict[keys[0]][keys[2]] = tweet_count
            if keys[2] == 'positive':
                total_positive += tweet_count
            elif keys[2] == 'negative':
                total_negative += tweet_count
            else:
                total_tweets += tweet_count
        except Exception as e:
            logging.exception("Error reading key: {} from redis because of {}:".format(key, e), exc_info=True)
    return stock_sentiment_dict, total_positive, total_negative, total_tweets


app.run(host="0.0.0.0", port=5001)
