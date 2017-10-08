FROM python:3.6

ENV PYTHONUNBUFFERED 0
ENV DJANGO_SETTINGS_MODULE=skyfolk.settings.pre

RUN mkdir /code
WORKDIR /code

ADD requirements/develop.txt /code/

RUN pip install -r develop.txt

ADD . /code/

RUN adduser --disabled-password --gecos "" skyfolk
RUN adduser skyfolk sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
