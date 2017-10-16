# update and install ffmpeg
FROM ubuntu

RUN apt-get -y update && apt-get install -y python-dev pkg-config libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev python-pip git curl imagemagick python3-scipy python-pil python-numpy 

# Compile and install ffmpeg from source
RUN curl 'https://raw.githubusercontent.com/imageio/imageio-binaries/master/ffmpeg/ffmpeg.linux64' > /usr/bin/ffmpeg.linux64

RUN ln -s /usr/bin/ffmpeg.linux64 /usr/bin/ffmpeg
RUN chmod +x /usr/bin/ffmpeg.linux64

RUN mkdir -p /root/.imageio/ffmpeg
RUN ln -s /usr/bin/ffmpeg.linux64 /root/.imageio/ffmpeg/ffmpeg.linux64
RUN apt-get remove -y python-dev gcc libexpat1-dev libpython-dev libpython2.7 libpython2.7-dev python2.7-dev curl


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
