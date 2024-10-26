
FROM python:3.13.0-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gettext \
    docutils-common \
    curl \
    pipx \
    wget

COPY ./pyproject.toml /pyproject.toml
COPY ./poetry.lock /poetry.lock

ENV PATH="$PATH:/root/.local/bin" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    TINI_VERSION=v0.19.0 \
    # poetry:
    POETRY_VERSION=1.8.4

# Installing `poetry` package manager:
# https://github.com/python-poetry/poetry
RUN pip install --upgrade pip
RUN pipx install --python python3 poetry==${POETRY_VERSION}
RUN poetry install


RUN dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && wget "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" -O /usr/local/bin/tini \
  && chmod +x /usr/local/bin/tini && tini --version


RUN mkdir -p /jandig/src /jandig/locale /jandig/docs /jandig/static /jandig/build

WORKDIR /jandig

COPY ./src/ /jandig/src/
COPY ./docs/ /jandig/docs/
COPY ./locale/ /jandig/locale/
COPY ./tasks.py /jandig/tasks.py
COPY ./run.sh /jandig/run.sh
COPY ./etc/ /jandig/etc/


RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf


ENTRYPOINT ["tini", "--"]