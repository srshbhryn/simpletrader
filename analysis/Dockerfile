FROM python:3.10-slim 

WORKDIR /app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

RUN apt -y install netcat

RUN mkdir -p /var/log/simpletrader/

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

RUN pip install -r requirements.txt
RUN chmod +x ./entrypoint.*.sh
