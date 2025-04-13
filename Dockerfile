
FROM python:3.13.3-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.6.13 /uv /uvx /bin/

ENV PATH="$PATH:/home/jandig/.local/bin:/jandig/.venv/bin" \
    TINI_VERSION=v0.19.0 \
    UV_CACHE_DIR=/home/jandig/jandig/cache/uv

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gettext \
      docutils-common \
      curl \
      wget


RUN dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && wget "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" -O /usr/local/bin/tini \
  && chmod +x /usr/local/bin/tini && tini --version


RUN mkdir -p /jandig/src /jandig/locale /jandig/docs /jandig/.venv /jandig/static /jandig/build /home/jandig/jandig/cache/uv

WORKDIR /jandig

COPY ./pyproject.toml /jandig/pyproject.toml
COPY ./uv.lock /jandig/uv.lock

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

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

RUN uv sync --frozen --no-dev
ENTRYPOINT ["tini", "--"]

CMD [ "/jandig/run.sh" ]
