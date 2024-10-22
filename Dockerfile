FROM python:3.8.15-alpine

RUN apk update && apk add python3-dev gcc libc-dev

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install gunicorn
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt

ADD ./core /app/core
ADD ./docker /app/docker

RUN chmod +x /app/docker/core/server-entrypoint.sh
RUN chmod +x /app/docker/core/worker-entrypoint.sh