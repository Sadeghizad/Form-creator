FROM python:3.8.15-alpine

RUN apk update && apk add python3-dev gcc libc-dev

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install gunicorn
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt

ADD ./core /app/core
ADD ./docker /app/docker

ADD ./docker/backend/worker-entrypoint.sh /app/docker/backend/worker-entrypoint.sh  
ADD ./docker/backend/server-entrypoint.sh /app/docker/backend/server-entrypoint.sh  

RUN chmod +x /app/docker/backend/server-entrypoint.sh
RUN chmod +x /app/docker/backend/worker-entrypoint.sh