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
