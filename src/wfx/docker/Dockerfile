# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

################################
# BUILDER
# Used to build WFX and create our virtual environment
################################

# Use an Alpine-based Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

# Install build dependencies needed for some Python packages on Alpine
RUN apk add --no-cache build-base libaio-dev linux-headers

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# --- Copy only files that affect dependency resolution (best cache) ---
# Workspace root metadata + lockfile
COPY pyproject.toml uv.lock ./

# Member's pyproject so uv knows about 'wfx' (no source yet, better cache)
COPY src/wfx/pyproject.toml /app/src/wfx/pyproject.toml
COPY src/wfx/README.md /app/src/wfx/README.md

# Create the venv and install *only* what wfx needs (no dev)
# We expect some packages to be built from source, so we mount the cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package wfx

# --- Now copy the source (doesn't bust the deps layer) ---
COPY src/wfx/src /app/src/wfx/src

# Install the WFX package into the virtual environment (non-editable)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --package wfx

################################
# RUNTIME
# Setup user, utilities and copy the virtual environment only
################################
FROM python:3.12-alpine AS runtime

# Create a non-root user
# -D: Don't assign a password
# -u: Set user ID
# -G: Add to group (root)
# -h: Set home directory
# -s: Set shell
RUN adduser -D -u 1000 -G root -h /app/data -s /sbin/nologin wfx

# Copy the virtual environment from the builder stage
COPY --from=builder --chown=1000 /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

LABEL org.opencontainers.image.title=wfx
LABEL org.opencontainers.image.authors=['Aiexec']
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.url=https://github.com/khulnasoft/aiexec
LABEL org.opencontainers.image.source=https://github.com/khulnasoft/aiexec
LABEL org.opencontainers.image.description="WFX - Aiexec Executor CLI Tool"

USER wfx
WORKDIR /app/data

# Default command shows WFX help
CMD ["wfx", "--help"]