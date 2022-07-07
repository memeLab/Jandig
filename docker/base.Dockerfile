FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
        gettext \
        docutils-common
COPY ./src/requirements.txt /src/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir toolz
RUN pip install --no-cache-dir -r /src/requirements.txt

RUN rm -rf ~/.cache/pip
