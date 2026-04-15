ARG PYTHON_VERSION=3.12
ARG ALPINE_VERSION=3.23
ARG UV_VERSION=0.11.6

FROM ghcr.io/astral-sh/uv:${UV_VERSION}-python${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS uv

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS build

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Grab `uv` from their github images
COPY --from=uv /usr/local/bin/uv /usr/local/bin/uvx /usr/local/bin/

WORKDIR /app

# Cache the dependencies / builds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=./uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=./pyproject.toml \
    uv sync  \
      --no-dev \
      --frozen \
      --no-editable \
      --no-install-project \
      --no-default-groups

# Copy source files into /app/ for creating the packages
COPY README.md ./
COPY src/ src/

# Install the local packages this time (using the cached dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=./uv.lock,target=./uv.lock \
    --mount=type=bind,source=./pyproject.toml,target=./pyproject.toml \
    uv sync \
      --no-dev \
      --frozen \
      --no-editable \
      --no-default-groups


FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION} AS run

RUN apk add --no-cache tini

COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

ENTRYPOINT ["/sbin/tini", "-s", "--"]

CMD ["serve"]