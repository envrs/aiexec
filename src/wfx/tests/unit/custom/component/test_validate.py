from textwrap import dedent

from wfx.custom.validate import create_class


def test_importing_aiexec_module_in_wfx():
    code = dedent("""from aiexec.custom import   Component
class TestComponent(Component):
    def some_method(self):
        pass
    """)
    result = create_class(code, "TestComponent")
    assert result.__name__ == "TestComponent"


def test_importing_aiexec_logging_in_wfx():
    """Test that aiexec.logging can be imported in wfx context without errors."""
    code = dedent("""
from aiexec.logging import logger, configure
from aiexec.custom import Component

class TestLoggingComponent(Component):
    def some_method(self):
        # Test that both logger and configure work
        configure(log_level="INFO")
        logger.info("Test message from component")
        return "success"
    """)
    result = create_class(code, "TestLoggingComponent")
    assert result.__name__ == "TestLoggingComponent"
