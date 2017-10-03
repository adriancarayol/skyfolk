FROM python:3.6

WORKDIR /app

ADD . /app 

ENV DJANGO_SETTINGS_MODULE=skyfolk.settings.develop

RUN pip install -r requirements/develop.txt

RUN adduser --disabled-password --gecos '' admin


