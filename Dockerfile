# update and install ffmpeg
FROM ubuntu

RUN apt-get -y update && apt-get install -y wget nano git build-essential yasm pkg-config

# Compile and install ffmpeg from source
RUN mkdir /root/.imageio
RUN git clone https://github.com/FFmpeg/FFmpeg /root/.imageio/ffmpeg && \
        cd /root/.imageio/ffmpeg && \
        ./configure --enable-nonfree --disable-shared --extra-cflags=-I/usr/local/include && \
        make -j8 && make install -j8

ENV FFMPEG_BINARY = /root/.imageio/ffmpeg

FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=skyfolk.settings.pre


RUN mkdir /code
WORKDIR /code

ADD requirements/develop.txt /code/

RUN pip install -r develop.txt
RUN pip install git+https://github.com/adriancarayol/asgi_rabbitmq.git

ADD . /code/

RUN adduser --disabled-password --gecos '' skyfolk 
