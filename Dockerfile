
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

  # Place executables in the environment at the front of the path
ENV PATH="/jandig/.venv/bin:$PATH"
RUN mkdir -p /jandig/src /jandig/locale /jandig/docs /jandig/static /jandig/build
# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
WORKDIR /jandig

COPY ./src/ /jandig/src/
COPY ./docs/ /jandig/docs/
COPY ./locale/ /jandig/locale/
COPY ./run.sh /jandig/run.sh
COPY ./etc/ /jandig/etc/
COPY ./pyproject.toml /jandig/pyproject.toml
COPY ./uv.lock /jandig/uv.lock

ENTRYPOINT ["tini", "--"]

CMD [ "/jandig/run.sh" ]

FROM base AS local_dev

COPY ./collection/ /jandig/collection/

RUN echo $UV_PROJECT_ENVIRONMENT
RUN uv sync --frozen
RUN playwright install chromium --with-deps