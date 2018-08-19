# Base image
FROM python:3.6 AS base

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils

# Install postgresql
RUN pip install psycopg2
RUN apt-get update
RUN apt-get install -y postgresql-client

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
RUN pip install imageio numpy scipy matplotlib pandas sympy nose decorator tqdm pillow pytest

# Install scikit-image after the other deps, it doesn't cause errors this way.
RUN pip install scikit-image sklearn

# Install ffmpeg from imageio.
RUN python -c "import imageio; imageio.plugins.ffmpeg.download()"

# Add soft link so that ffmpeg can executed (like usual) from command line
RUN ln -sf /root/.imageio/ffmpeg/ffmpeg.linux64 /usr/bin/ffmpeg

# Create webapp folders and giving some permissions
RUN mkdir -p /var/www/skyfolk.net/run/static/static
RUN mkdir -p /var/www/skyfolk.net/run/static/media
RUN chmod -R g+w /var/www
RUN chmod -R 777 /var/www
RUN chmod -R 770 /root/

# Modify ImageMagick policy file so that Textclips work correctly.
RUN cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml

VOLUME /root

# Install some demands
ADD requirements/master.txt /tmp/requirements.txt
RUN pip install -r requirements/master.txt

# Reuse base image
FROM base

# Copy code
RUN mkdir /code
WORKDIR /code
COPY . /code