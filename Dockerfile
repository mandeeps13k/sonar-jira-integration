FROM python:3.8.5-slim-buster
RUN mkdir /app
COPY . /app/
USER root
WORKDIR /app
