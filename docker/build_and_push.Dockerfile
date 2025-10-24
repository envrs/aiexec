# syntax=docker/dockerfile:1
# BuildKit syntax enabled for cache mounts

################################
# BUILDER-BASE
################################
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# -------------------
# ENVIRONMENT SETTINGS
# -------------------
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV RUSTFLAGS='--cfg reqwest_unstable'
ENV TMPDIR=/tmp
ENV UV_CACHE_DIR=/tmp/uv_cache
ENV NPM_CONFIG_CACHE=/tmp/npm_cache

# -------------------
# SYSTEM DEPENDENCIES
# -------------------
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
        build-essential \
        git \
        npm \
        gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# -------------------
# COPY LOCK FILES & METADATA
# -------------------
COPY ./uv.lock ./pyproject.toml ./README.md /app/
COPY ./src/backend/base/uv.lock ./src/backend/base/pyproject.toml ./src/backend/base/README.md /app/src/backend/base/
COPY ./src/wfx/pyproject.toml ./src/wfx/README.md /app/src/wfx/

# -------------------
# INSTALL PYTHON DEPENDENCIES
# -------------------
RUN --mount=type=cache,target=/tmp/uv_cache \
    uv sync --frozen --no-install-project --no-editable --extra postgresql

# -------------------
# COPY SOURCE CODE
# -------------------
COPY ./src /app/src

# -------------------
# FRONTEND BUILD
# -------------------
COPY src/frontend /tmp/src/frontend
WORKDIR /tmp/src/frontend

RUN --mount=type=cache,target=/tmp/npm_cache \
    npm ci \
    && ESBUILD_BINARY_PATH="" NODE_OPTIONS="--max-old-space-size=12288" JOBS=1 npm run build \
    && cp -r build /app/src/backend/aiexec/frontend \
    && rm -rf /tmp/src/frontend /tmp/npm_cache

# -------------------
# FINAL UV SYNC
# -------------------
WORKDIR /app
RUN --mount=type=cache,target=/tmp/uv_cache \
    uv sync --frozen --no-editable --extra postgresql \
    && rm -rf /tmp/uv_cache

################################
# RUNTIME
################################
FROM python:3.12.3-slim AS runtime

# -------------------
# ENVIRONMENT SETTINGS
# -------------------
ENV TMPDIR=/tmp
ENV UV_CACHE_DIR=/tmp/uv_cache
ENV NPM_CONFIG_CACHE=/tmp/npm_cache

# -------------------
# SYSTEM DEPENDENCIES
# -------------------
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y curl git libpq5 gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -u 1000 -g 0 --no-create-home --home-dir /app/data user

# -------------------
# COPY VIRTUAL ENV
# -------------------
COPY --from=builder --chown=1000 /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# -------------------
# USER & WORKDIR
# -------------------
USER user
WORKDIR /app

# -------------------
# APP CONFIGURATION
# -------------------
ENV AIEXEC_HOST=0.0.0.0
ENV AIEXEC_PORT=7860

LABEL org.opencontainers.image.title=aiexec
LABEL org.opencontainers.image.authors=['Aiexec']
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.url=https://github.com/khulnasoft/aiexec
LABEL org.opencontainers.image.source=https://github.com/khulnasoft/aiexec

CMD ["aiexec", "run"]
