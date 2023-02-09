FROM python:3.10-slim-bullseye

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gettext \
    docutils-common \
    curl \
    wget


COPY ./pyproject.toml /pyproject.toml
COPY ./poetry.lock /poetry.lock



ENV PATH="$PATH:/root/.local/bin" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    TINI_VERSION=v0.19.0 \
    # poetry:
    POETRY_VERSION=1.3.1

# Installing `poetry` package manager:
# https://github.com/python-poetry/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && poetry --version

RUN poetry install

RUN dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && wget "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" -O /usr/local/bin/tini \
  && chmod +x /usr/local/bin/tini && tini --version

RUN mkdir -p /src
WORKDIR /src
COPY ./src/ /src/
COPY ./docs/ /src/docs/
COPY ./locale/ /src/locale/
COPY ./tasks.py /src/tasks.py
COPY ./run.sh /src/run.sh
COPY ./etc/ /src/etc/

RUN pip install --upgrade pip

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf


ENTRYPOINT ["tini", "--"]