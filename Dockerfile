FROM python:2.7.13

ENV PYTHONUNBUFFERED 1
ENV ENV docker

RUN mkdir /opt/referee

ADD requirements.txt /opt/referee/
RUN pip install -r /opt/referee/requirements.txt

ADD . /opt/referee/
WORKDIR /opt/referee