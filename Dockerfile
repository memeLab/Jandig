
FROM python:3.13.0-slim-bookworm

ENV PATH="$PATH:/home/jandig/.local/bin:/jandig/.venv/bin" \
    TINI_VERSION=v0.19.0 \
    # poetry:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_OPTIONS_ALWAYS_COPY=true \
    POETRY_VIRTUALENV_PATH="/jandig/.venv" \
    POETRY_CACHE_DIR='/home/jandig/cache/pypoetry' \
    POETRY_VERSION=1.8.4

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gettext \
      docutils-common \
      curl \
      wget

RUN dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && wget "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" -O /usr/local/bin/tini \
  && chmod +x /usr/local/bin/tini && tini --version


RUN mkdir -p /jandig/src /jandig/locale /jandig/docs /jandig/.venv /jandig/static /jandig/build /home/jandig/cache/pypoetry

WORKDIR /jandig

COPY ./pyproject.toml /jandig/pyproject.toml
COPY ./poetry.lock /jandig/poetry.lock

COPY ./src/ /jandig/src/
COPY ./docs/ /jandig/docs/
COPY ./locale/ /jandig/locale/
COPY ./tasks.py /jandig/tasks.py
COPY ./run.sh /jandig/run.sh
COPY ./etc/ /jandig/etc/


# Create group and user
RUN groupadd -g 1000 jandig && useradd -u 1000 -g 1000 -r -m -d /home/jandig jandig

# Change ownership of the directories to the new user and group
RUN chown -R jandig:jandig /jandig /home/jandig
RUN chmod 2775 /jandig /home/jandig

# Switch to the new user
USER jandig

# Installing `poetry` package manager:
# https://github.com/python-poetry/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

ENTRYPOINT ["tini", "--"]

CMD [ "/jandig/run.sh" ]
