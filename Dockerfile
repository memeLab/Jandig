FROM node:8.11-alpine

WORKDIR /app

RUN npm i npm@latest -g
RUN npm install -g live-server live-server-https

COPY /src /app/

# ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

CMD echo "--------------------------------------------------------" && \
    echo "Access ARte from external devices on the same network by accessing:" && \
    echo "  - https://<server-device-name>" && \
    echo "  - https://<server-device-ip>" && \
    echo "--------------------------------------------------------" && \
    live-server --https=/usr/local/lib/node_modules/live-server-https --no-browser