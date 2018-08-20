FROM node:8.11-alpine

WORKDIR /app

RUN npm i npm@latest -g
RUN npm install -g live-server live-server-https

COPY /src /app/
CMD ["live-server", "--https=/usr/local/lib/node_modules/live-server-https", "--no-browser"]