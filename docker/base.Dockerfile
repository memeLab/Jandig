FROM python:3.10-slim-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gettext \
    docutils-common \
    curl

COPY ./pyproject.toml .
COPY ./poetry.lock .

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
ENV PATH "${PATH}:/root/.poetry/bin"
RUN poetry install
