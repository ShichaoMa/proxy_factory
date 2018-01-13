FROM ubuntu

MAINTAINER Shichao Ma

COPY Shanghai /etc/localtime

COPY timezone /etc

RUN apt-get clean && apt-get update

RUN apt-get install -y locales

RUN locale-gen en_US.UTF-8

RUN update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8

RUN apt-get install -y --no-install-recommends gcc make wget

RUN apt-get install -y --no-install-recommends tesseract-ocr

RUN apt-get install -y --no-install-recommends python3-dev

RUN wget https://bootstrap.pypa.io/get-pip.py --no-check-certificate

RUN python3 get-pip.py

RUN pip install proxy-factory==0.2.7

RUN mkdir /app

COPY custom_proxies_site.py /app/custom_proxies_site.py

COPY https_check.py /app/https_check.py

WORKDIR /app

