### Sentiment Analysis on top 20 S&P 500 stocks
The purpose of this application is to analyze tweets related to top 20 S&P 500 stocks. 
#### Requirements
<hr/>

1. Docker
2. Tested on Mac OSX, Ubuntu 14.X, CentOS 6.X
3. [AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
4. Python 3.8
5. nltk punkt and stopwords packages (https://www.nltk.org/)
5. pip python package manager

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