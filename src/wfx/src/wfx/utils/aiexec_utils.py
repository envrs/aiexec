"""Aiexec environment utility functions."""

import importlib.util

from wfx.log.logger import logger


class _AiexecModule:
    # Static variable
    # Tri-state:
    # - None: Aiexec check not performed yet
    # - True: Aiexec is available
    # - False: Aiexec is not available
    _available = None

    @classmethod
    def is_available(cls):
        return cls._available

    @classmethod
    def set_available(cls, value):
        cls._available = value


def has_aiexec_memory():
    """Check if aiexec.memory (with database support) and MessageTable are available."""
    # TODO: REVISIT: Optimize this implementation later
    # - Consider refactoring to use lazy loading or a more robust service discovery mechanism
    #   that can handle runtime availability changes.

    # Use cached check from previous invocation (if applicable)

    is_aiexec_available = _AiexecModule.is_available()

    if is_aiexec_available is not None:
        return is_aiexec_available

    # First check (lazy load and cache check)

    module_spec = None

    try:
        module_spec = importlib.util.find_spec("aiexec")
    except ImportError:
        pass
    except (TypeError, ValueError) as e:
        logger.error(f"Error encountered checking for aiexec.memory: {e}")

    is_aiexec_available = module_spec is not None
    _AiexecModule.set_available(is_aiexec_available)

    return is_aiexec_available
