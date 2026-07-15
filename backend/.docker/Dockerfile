FROM python:3.10-slim-bullseye
LABEL maintainer="Soccer Solver"

RUN apt-get update \
    && apt-get -y install tini \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000