
FROM python:3.13.0-slim-bookworm as base-image

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gettext \
      docutils-common \
      curl \
      wget

      
ENV PATH="$PATH:/root/.local/bin" \
    TINI_VERSION=v0.19.0 \
    # poetry:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_VERSION=1.8.4
      

# Installing `poetry` package manager:
# https://github.com/python-poetry/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && wget "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" -O /usr/local/bin/tini \
  && chmod +x /usr/local/bin/tini && tini --version


RUN mkdir -p /jandig/src /jandig/locale /jandig/docs /jandig/static /jandig/build

WORKDIR /jandig

COPY ./pyproject.toml /jandig/pyproject.toml
COPY ./poetry.lock /jandig/poetry.lock

COPY ./src/ /jandig/src/
COPY ./docs/ /jandig/docs/
COPY ./locale/ /jandig/locale/
COPY ./tasks.py /jandig/tasks.py
COPY ./run.sh /jandig/run.sh
COPY ./etc/ /jandig/etc/


RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf


ENTRYPOINT ["tini", "--"]