# syntax=docker/dockerfile:1
FROM python:3.9-buster
ENV PYTHONUNBUFFERED=1
ENV DB_ENGINE=django.db.backends.postgresql
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
