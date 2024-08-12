# docker build -f Dockerfile -t leondeoliveirapedrosa/todo-api:dev . && docker push leondeoliveirapedrosa/todo-api:dev
FROM ubuntu:latest
LABEL authors="leon"
FROM alpine:3.18
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add --no-cache curl tzdata python3 py3-pip gcc python3-dev postgresql-dev libc-dev file-dev
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir
COPY . /app/
CMD ["gunicorn","--bind=0.0.0.0:8000", "--workers=4", "--threads=4", "--worker-class=gthread", "--worker-tmp-dir=/dev/shm", "--log-level", "info", "todo.wsgi:application"]
