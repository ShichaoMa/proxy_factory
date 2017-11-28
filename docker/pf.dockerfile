FROM ubuntu

MAINTAINER Shichao Ma

RUN apt-get clean && apt-get update

RUN apt-get install -y locales

RUN locale-gen en_US.UTF-8

RUN update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8

COPY Shanghai /etc/localtime

COPY timezone /etc

RUN apt-get install -y --no-install-recommends libc6-dev gcc make

RUN apt-get install -y --no-install-recommends \
      libjpeg8-dev zlib1g-dev \
      libfreetype6-dev liblcms2-dev \
      libwebp-dev tcl8.5-dev \
      tk8.5-dev python-tk

RUN apt-get install -y --no-install-recommends tesseract-ocr

RUN apt-get install -y --no-install-recommends git

RUN apt-get install -y --no-install-recommends ca-certificates

RUN apt-get install -y --no-install-recommends python3 wget

RUN apt-get install -y --no-install-recommends python3-dev

RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python3 get-pip.py

RUN pip install proxy-factory==0.1.8

RUN mkdir /app

COPY custom_proxies_site.py /app/custom_proxies_site.py

COPY https_check.py /app/https_check.py

WORKDIR /app

