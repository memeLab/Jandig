#!/usr/bin/env sh

mv /vendor/ /app/vendor/

echo "--------------------------------------------------------" && \
echo "Access ARte from external devices on the same network by accessing:" && \
echo "  - https://<server-device-name>" && \
echo "  - https://<server-device-ip>" && \
echo "--------------------------------------------------------" && \

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py runsslserver 0.0.0.0:443