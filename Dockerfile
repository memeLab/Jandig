FROM rodrigocam/nodejs-python3-alpine

WORKDIR /app

RUN npm i npm@latest -g
RUN npm install -g live-server live-server-https

COPY /src /app/

ENTRYPOINT ["sh", "./entrypoint.sh"]