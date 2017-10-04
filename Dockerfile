FROM python:3.6

ADD . /app 

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=skyfolk.settings.pre

RUN pip install -r requirements/develop.txt

RUN adduser --disabled-password --gecos '' skyfolk