"""Unit tests for the wfx.helpers.flow module."""

import pytest

from wfx.utils.aiexec_utils import has_aiexec_memory

# Globals

_WFX_HELPER_MODULE_FLOW = "wfx.helpers.flow"

# Helper Functions


def is_helper_module(module, module_name):
    return module.__module__ == module_name


# Test Scenarios


class TestDynamicImport:
    """Test dynamic imports of the wfx implementation."""

    def test_aiexec_available(self):
        """Test whether the aiexec implementation is available."""
        # Aiexec implementation should not be available
        if has_aiexec_memory():
            pytest.fail("Aiexec implementation is available")

    def test_helpers_import_build_schema_from_inputs(self):
        """Test the wfx.helpers.build_schema_from_inputs import."""
        try:
            from wfx.helpers import build_schema_from_inputs
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import wfx.helpers.build_schema_from_inputs: {e}")

        # Helper module should be the wfx implementation
        assert is_helper_module(build_schema_from_inputs, _WFX_HELPER_MODULE_FLOW)

    def test_helpers_import_get_arg_names(self):
        """Test the wfx.helpers.get_arg_names import."""
        try:
            from wfx.helpers import get_arg_names
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import wfx.helpers.get_arg_names: {e}")

        # Helper module should be the wfx implementation
        assert is_helper_module(get_arg_names, _WFX_HELPER_MODULE_FLOW)

    def test_helpers_import_get_flow_inputs(self):
        """Test the wfx.helpers.get_flow_inputs import."""
        try:
            from wfx.helpers import get_flow_inputs
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import wfx.helpers.get_flow_inputs: {e}")

        # Helper module should be the wfx implementation
        assert is_helper_module(get_flow_inputs, _WFX_HELPER_MODULE_FLOW)

    def test_helpers_import_list_flows(self):
        """Test the wfx.helpers.list_flows import."""
        try:
            from wfx.helpers import list_flows
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import wfx.helpers.list_flows: {e}")

        # Helper module should be the wfx implementation
        assert is_helper_module(list_flows, _WFX_HELPER_MODULE_FLOW)

    def test_helpers_import_load_flow(self):
        """Test the wfx.helpers.load_flow import."""
        try:
            from wfx.helpers import load_flow
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import wfx.helpers.load_flow: {e}")

        # Helper module should be the wfx implementation
        assert is_helper_module(load_flow, _WFX_HELPER_MODULE_FLOW)

    def test_helpers_import_run_flow(self):
        """Test the wfx.helpers.run_flow import."""
        try:
            from wfx.helpers import run_flow
        except (ImportError, ModuleNotFoundError) as e:
            pytest.fail(f"Failed to dynamically import wfx.helpers.run_flow: {e}")

        # Helper module should be the wfx implementation
        assert is_helper_module(run_flow, _WFX_HELPER_MODULE_FLOW)
