FROM python:3.8-slim-buster

RUN apt-get update && \
    apt-get -y install gcc librdkafka-dev

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "app.py"]