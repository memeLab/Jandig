FROM node:8.11-alpine

WORKDIR /app

RUN npm i npm@latest -g
RUN npm install -g live-server live-server-https

COPY /src /app/

RUN mkdir /vendor

ADD https://github.com/pablodiegoss/ARte-libs/archive/master.zip /master.zip
RUN unzip /master.zip \
 && cd ARte-libs-master \
 && mv * /vendor \
 && ls /vendor/ \
 && echo "Downloaded Libs"

COPY runserver.sh /
CMD ["/runserver.sh"]