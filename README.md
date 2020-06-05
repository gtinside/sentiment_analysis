### Sentiment Analysis on top 20 S&P 500 stocks
![Server component build & deploy](https://github.com/gtinside/sentiment_analysis/workflows/Server%20component%20build%20&%20deploy/badge.svg?branch=master) ![Web component build & deploy](https://github.com/gtinside/sentiment_analysis/workflows/Web%20component%20build%20&%20deploy/badge.svg?branch=master)

The purpose of this application is to analyze the sentiments for top to 20 S&P 500 stocks (based on market cap). Streaming Twitter APIs are used to capture the corpus for running the sentiment analysis

#### Architecture
<hr/>

A python server is responsible for streaming the tweets based on ticker from Twitter. Tweets are cleansed and queued in SQS. From SQS the tweets are read by a a separate process that score them using [vaderSentiment](https://pypi.org/project/vaderSentiment/)

#### Requirements
<hr/>

1. Docker 
2. [AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
3. Python 3.8
4. nltk punkt and stopwords packages (https://www.nltk.org/)
5. pip python package manager
6. Tested on Mac OSX, Ubuntu 14.X, CentOS 6.X 

#### Getting Started
<hr/>

Before getting started update the *sentiment_analysis/setup/keys.cfg* file with the following:

1. Twitter Consumer Key & Consumer Key Secret
2. Twitter Key and Twitter Secret

**Local Development in an IDE**
```
git clone
# Navigate to sentiment_analysis/setup directory
./setup.sh
# Upload keys.cfg to localstack S3
aws --endpoint-url=http://localhost:4566 s3 mb s3://application-keys
aws --endpoint-url=http://localhost:4566 s3 cp keys.cfg  s3://application-keys/
```
**Containerized  local development/deployment**
```
git clone
# Navigate to sentiment_analysis/setup directory
./setup.sh

# Upload keys.cfg to localstack S3
aws --endpoint-url=http://localhost:4566 s3 mb s3://application-keys
aws --endpoint-url=http://localhost:4566 s3 cp keys.cfg  s3://application-keys/

# Build docker images
docker build -t sentiment_analysis_server -f build/server/Dockerfile .
docker build -t sentiment_analysis_web -f build/web/Dockerfile .

# Run
docker run --network sentimental_network -e LocalDevelopment=1 -e LocalStackContainer=localstack -e RedisContainer=redis sentiment_analysis_server:latest
docker run --network sentimental_network -p 5001:5001  -e LocalDevelopment=1 -e LocalStackContainer=localstack -e RedisContainer=redis sentiment_analysis_web:latest
```
After the steps mentioned above navigate to http://localhost:5001 to analyze the heat map

#### Packaging & Deployment
<hr/>

Refer to the [Workflow](https://github.com/gtinside/sentiment_analysis/tree/master/.github/workflows) for build and deployment details. 
Following workflows are embedded in it:
1. Image build and publish to Github package registry
2. Image build and publish to [Docker public registry](https://hub.docker.com/repository/docker/gtinside/)
3. Refresh of AWS ECS Service. I have hardcoded the ECS Cluster and Deployment Service name for now.

#### Output
<hr/>

The output of this analysis is a Tree Map representing the trend based on sentiments on the received tweets

![Tree Map](/docs/images/sentimentanalysis.png)

![Analysis](/docs/images/details.png)

#### Calculations
<hr/>

> **Size of the rectangle in TreeMap for stock A** = (T<sub>PA</sub> + T<sub>NA</sub>) / T<sub>P</sub> + T<sub>N</sub>
> **Overall Sentiment for stock A** = T<sub>PA</sub>/T<sub>P</sub> - T<sub>NA</sub>/T<sub>N</sub>

> T<sub>PA</sub>: Number of tweets with positive sentiment for stock A
> T<sub>NA</sub>: Number of tweets with negative sentiment for stock A
> T<sub>P</sub>: Total number of positive tweets across all stocks
> T<sub>N</sub>: Total number of negative tweets across all stocks