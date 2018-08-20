#!/bin/bash
set -e

echo "--------------------------------------------------------"
echo "Access ARte from external devices on the same network by accessing:"
echo "  - https://<server-device-name>"
echo "  - https://<server-device-ip>"
echo "--------------------------------------------------------"


# Start live-server https
live-server --https=/usr/local/lib/node_modules/live-server-https --no-browser

exec "$@"