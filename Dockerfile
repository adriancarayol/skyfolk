# update and install ffmpeg
FROM ubuntu


RUN apt-get update
RUN apt-get dist-upgrade -y

RUN DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-software-properties
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install software-properties-common
RUN DEBIAN_FRONTEND=noninteractive apt-add-repository -y ppa:jonathonf/ffmpeg-3
RUN apt-get update
RUN apt-get install -y ffmpeg

RUN echo 'alias ffmpeg="/usr/bin/ffmpeg"' >> ~/.bashrc

FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=skyfolk.settings.pre


RUN mkdir /code
WORKDIR /code

ADD requirements/develop.txt /code/

RUN pip install -r develop.txt

ADD . /code/

RUN adduser --disabled-password --gecos "" skyfolk
RUN adduser skyfolk sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
