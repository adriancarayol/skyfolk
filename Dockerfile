FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=skyfolk.settings.pre

RUN mkdir /code
WORKDIR /code

ADD requirements/develop.txt /code/

RUN pip install -r develop.txt

ADD . /code/

# update and install ffmpeg
RUN apt-get update
RUN apt-get dist-upgrade -y

RUN DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python-software-properties
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install software-properties-common
RUN apt-get update

RUN DEBIAN_FRONTEND=noninteractive set -x \
    && add-apt-repository ppa:mc3man/xerus-media \
    && apt-get update \
    && apt-get dist-upgrade \
    && apt-get install -y --no-install-recommends \
        ffmpeg 

RUN adduser --disabled-password --gecos "" skyfolk
RUN adduser skyfolk sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
