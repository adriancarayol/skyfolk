FROM python:3.6

ADD . /app 

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=skyfolk.settings.pre

RUN pip install -r requirements/develop.txt
 
RUN adduser --disabled-password --gecos '' skyfolk

RUN chown skyfolk:skyfolk -R /usr/lib/
RUN chown skyfolk:skyfolk -R /usr/local/lib/python3.6
RUN chown skyfolk:skyfolk -R /root/
