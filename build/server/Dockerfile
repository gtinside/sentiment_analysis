# --- Python server for S&P 500 sentiment analysis --
FROM python:3.8.3-buster
WORKDIR /app
COPY . /app
RUN ls -la /app/*
# install app dependencies
RUN apt-get install gcc
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader stopwords
WORKDIR /app/sentiment_analysis/server
ENV PYTHONPATH "${PYTONPATH}:/app"
CMD [ "python", "main.py" ]