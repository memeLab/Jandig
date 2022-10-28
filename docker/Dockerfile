FROM python:3.10-slim-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gettext \
    docutils-common \
    curl

COPY ./pyproject.toml /pyproject.toml
COPY ./poetry.lock /poetry.lock

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="$PATH:/root/.local/bin" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN poetry install

RUN mkdir -p /ARte
WORKDIR /ARte
COPY docs/ /ARte/docs/
COPY ./src/ARte /ARte/src/ARte/
COPY ./locale/ /ARte/locale/
COPY ./tasks.py /ARte/tasks.py
COPY ./run.sh /ARte/run.sh
COPY ./etc/ /ARte/etc/

RUN pip install --upgrade pip

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
