FROM python:3.6.5

WORKDIR /app

COPY requirements.txt /

RUN pip install -r /requirements.txt

COPY /ARte /app/

RUN mkdir /vendor
RUN apt-get update && apt-get install unzip
ADD https://github.com/pablodiegoss/ARte-libs/archive/master.zip /master.zip
RUN unzip /master.zip \
 && cd ARte-libs-master \
 && mv * /vendor \
 && echo "Downloaded Libs"

COPY runserver.sh /
CMD ["/runserver.sh"]