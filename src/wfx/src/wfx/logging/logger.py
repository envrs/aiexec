"""Backwards compatibility module for wfx.logging.logger.

This module provides backwards compatibility for code that imports from wfx.logging.logger.
All functionality has been moved to wfx.log.logger.
"""

# Ensure we maintain all the original exports
from wfx.log.logger import (
    InterceptHandler,
    LogConfig,
    configure,
    logger,
    setup_gunicorn_logger,
    setup_uvicorn_logger,
)

__all__ = [
    "InterceptHandler",
    "LogConfig",
    "configure",
    "logger",
    "setup_gunicorn_logger",
    "setup_uvicorn_logger",
]
