# --- Python server for S&P 500 sentiment analysis --
FROM python:3.8.3-slim
WORKDIR /app
COPY . /app
RUN ls -la /app/*
# install app dependencies
RUN pip install redis flask boto3
ENV PYTHONPATH "${PYTONPATH}:/app"
WORKDIR /app/sentiment_analysis/web
EXPOSE 5001
CMD [ "python", "web_main.py" ]