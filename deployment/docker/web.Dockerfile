# Base image
FROM python:3.7 AS base

ENV PYTHONUNBUFFERED 1

# Install apt-utils
RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils

# Install postgresql
RUN pip install psycopg2 && \
    apt-get update && \
    apt-get install -y postgresql-client

# Install numpy
RUN apt-get -y update && \
    apt-get -y install libav-tools imagemagick libopencv-dev python-opencv

# Set the locales
RUN apt-get install -y locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8
ENV LC_ALL C.UTF-8

# Install more dependencies
RUN apt-get install -y tidy pandoc
RUN pip install imageio numpy scipy matplotlib pandas sympy nose decorator \
    tqdm pillow pytest scikit-image sklearn imageio-ffmpeg

# Add soft link so that ffmpeg can executed (like usual) from command line
RUN ln -sf /root/.imageio/ffmpeg/ffmpeg.linux64 /usr/bin/ffmpeg

# Modify ImageMagick policy file so that Textclips work correctly.
RUN cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml

# Install requirements
ADD requirements/master.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy code
COPY . /code
WORKDIR /code