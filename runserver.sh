#!/usr/bin/env sh

mv /vendor/ /app/vendor/

echo "--------------------------------------------------------" && \
echo "Access ARte from external devices on the same network by accessing:" && \
echo "  - https://<server-device-name>" && \
echo "  - https://<server-device-ip>" && \
echo "--------------------------------------------------------" && \
live-server --https=/usr/local/lib/node_modules/live-server-https --no-browser