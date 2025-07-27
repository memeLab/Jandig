FROM debian:bookworm-slim AS base

ENV UV_VERSION=0.6.16 \
    UV_PYTHON_VERSION=3.13.3 \
    TINI_VERSION=v0.19.0 \
    UV_COMPILE_BYTECODE=1 \ 
    # Copy from the cache instead of linking since it's a mounted volume
    UV_LINK_MODE=copy \ 
    UV_PYTHON_INSTALL_DIR=/python \
    UV_PYTHON_PREFERENCE=only-managed

COPY --from=ghcr.io/astral-sh/uv:0.6.16 /uv /uvx /bin/

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ca-certificates \
      gettext \
      docutils-common \
      curl \
      wget \
      git \
      # To render GLB files
      libosmesa6-dev \
  && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && wget "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" -O /usr/local/bin/tini \
  && chmod +x /usr/local/bin/tini && tini --version \ 
  && uv python install $UV_PYTHON_VERSION \
  && apt-get clean \
  && apt-get autoclean

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Place executables in the virtual environment at the front of the path
ENV PATH="/.venv/bin:$PATH"

# Create folders for running Jandig without Gunicorn or MinIO
RUN mkdir -p /jandig/static /jandig/build

WORKDIR /jandig

COPY ./run.sh /jandig/run.sh
COPY ./docs/ /jandig/docs/
COPY ./locale/ /jandig/locale/
COPY ./pyproject.toml /jandig/pyproject.toml
COPY ./uv.lock /jandig/uv.lock
COPY ./src/ /jandig/src/

ENTRYPOINT ["tini", "--"]

CMD [ "/jandig/run.sh" ]


FROM base AS local_dev
ENV PATH="$PATH:/jandig/minio-binaries/"

# Install MinIO client
COPY --from=minio/mc:RELEASE.2025-04-16T18-13-26Z /usr/bin/mc /jandig/minio-binaries/mc

COPY ./collection/ /jandig/collection/
COPY ./etc/create_buckets.sh /jandig/create_buckets.sh

WORKDIR /
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync

RUN uv run playwright install chromium --with-deps

RUN groupadd -g 1000 jandig && useradd -u 1000 -g 1000 -r -m -d /home/jandig jandig
RUN chown -R jandig:jandig /jandig
USER jandig

WORKDIR /jandig

CMD ["/bin/bash", "-c", "/jandig/etc/create_buckets.sh && /jandig/run.sh"]
