FROM python:2.7

RUN apt-get update
RUN apt-get -y install unrar-free

ADD . /application
WORKDIR /application
RUN python setup.py install
