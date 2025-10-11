"""Test to ensure all aiexec modules that re-export wfx modules work correctly.

This test validates that every aiexec module that re-exports from wfx
can successfully import and access all expected symbols, maintaining
backward compatibility and proper API exposure.

Based on analysis, there are 24 aiexec modules that re-export from wfx:

Base Modules (11):
- aiexec.base (wildcard from wfx.base)
- aiexec.base.agents (from wfx.base.agents)
- aiexec.base.data (from wfx.base.data)
- aiexec.base.embeddings (from wfx.base.embeddings)
- aiexec.base.io (from wfx.base.io)
- aiexec.base.memory (from wfx.base.memory)
- aiexec.base.models (from wfx.base.models)
- aiexec.base.prompts (from wfx.base.prompts)
- aiexec.base.textsplitters (from wfx.base.textsplitters)
- aiexec.base.tools (from wfx.base.tools)
- aiexec.base.vectorstores (from wfx.base.vectorstores)

Core System Modules (13):
- aiexec.custom (from wfx.custom)
- aiexec.custom.custom_component (from wfx.custom.custom_component)
- aiexec.field_typing (from wfx.field_typing with __getattr__)
- aiexec.graph (from wfx.graph)
- aiexec.inputs (from wfx.inputs.inputs)
- aiexec.interface (from wfx.interface)
- aiexec.io (from wfx.io + wfx.template)
- aiexec.load (from wfx.load)
- aiexec.logging (from wfx.log.logger)
- aiexec.schema (from wfx.schema)
- aiexec.template (wildcard from wfx.template)
- aiexec.template.field (from wfx.template.field)
"""

import importlib
import inspect
import pkgutil
import re
import time
from pathlib import Path

import pytest


def get_all_reexport_modules():
    """Get all known re-export modules for parametrized testing."""
    # Define the modules here so they can be accessed by parametrize
    direct_reexport_modules = {
        "aiexec.base.agents": "wfx.base.agents",
        "aiexec.base.data": "wfx.base.data",
        "aiexec.base.embeddings": "wfx.base.embeddings",
        "aiexec.base.io": "wfx.base.io",
        "aiexec.base.memory": "wfx.base.memory",
        "aiexec.base.models": "wfx.base.models",
        "aiexec.base.prompts": "wfx.base.prompts",
        "aiexec.base.textsplitters": "wfx.base.textsplitters",
        "aiexec.base.tools": "wfx.base.tools",
        "aiexec.base.vectorstores": "wfx.base.vectorstores",
        "aiexec.custom.custom_component": "wfx.custom.custom_component",
        "aiexec.graph": "wfx.graph",
        "aiexec.inputs": "wfx.inputs.inputs",
        "aiexec.interface": "wfx.interface",
        "aiexec.load": "wfx.load",
        "aiexec.logging": "wfx.log",
        "aiexec.schema": "wfx.schema",
        "aiexec.template.field": "wfx.template.field",
    }

    wildcard_reexport_modules = {
        "aiexec.base": "wfx.base",
        "aiexec.template": "wfx.template",
    }

    complex_reexport_modules = {
        "aiexec.custom": ["wfx.custom", "wfx.custom.custom_component", "wfx.custom.utils"],
        "aiexec.io": ["wfx.io", "wfx.template"],
    }

    dynamic_reexport_modules = {
        "aiexec.field_typing": "wfx.field_typing",
    }

    return list(
        {
            **direct_reexport_modules,
            **wildcard_reexport_modules,
            **complex_reexport_modules,
            **dynamic_reexport_modules,
        }.keys()
    )


class TestLfxReexportModules:
    """Test that all aiexec modules that re-export from wfx work correctly."""

    @classmethod
    def _discover_aiexec_modules(cls) -> list[str]:
        """Dynamically discover all aiexec modules."""
        aiexec_modules = []
        try:
            import aiexec

            for _importer, modname, _ispkg in pkgutil.walk_packages(aiexec.__path__, aiexec.__name__ + "."):
                aiexec_modules.append(modname)
        except ImportError:
            pass
        return aiexec_modules

    @classmethod
    def _detect_reexport_pattern(cls, module_name: str) -> dict[str, str | None]:
        """Detect what kind of re-export pattern a module uses."""
        try:
            module = importlib.import_module(module_name)

            # Check if module has source code that mentions wfx
            source_file = getattr(module, "__file__", None)
            if source_file:
                try:
                    with Path(source_file).open() as f:
                        content = f.read()
                        if "from wfx" in content:
                            # Try to extract the wfx module being imported
                            patterns = [
                                r"from (lfx\.[.\w]+) import",
                                r"from (lfx\.[.\w]+) import \*",
                                r"import (lfx\.[.\w]+)",
                            ]
                            for pattern in patterns:
                                match = re.search(pattern, content)
                                if match:
                                    return {"type": "direct", "source": match.group(1)}

                        if "__getattr__" in content and "wfx" in content:
                            return {"type": "dynamic", "source": None}

                        # If we get here, file exists but no patterns matched
                        return {"type": "none", "source": None}

                except (OSError, UnicodeDecodeError):
                    return {"type": "none", "source": None}
            else:
                return {"type": "none", "source": None}

        except ImportError:
            return {"type": "import_error", "source": None}

    @classmethod
    def _get_expected_symbols(cls, wfx_source: str | None = None) -> list[str]:
        """Get expected symbols that should be available in a module."""
        if not wfx_source:
            return []

        try:
            wfx_module = importlib.import_module(wfx_source)
            if hasattr(wfx_module, "__all__"):
                return list(wfx_module.__all__)
            # Return public attributes (not starting with _)
            return [name for name in dir(wfx_module) if not name.startswith("_")]
        except ImportError:
            return []

    # Define all the modules that re-export from wfx (kept for backward compatibility)
    DIRECT_REEXPORT_MODULES = {
        # Base modules with direct re-exports
        "aiexec.base.agents": "wfx.base.agents",
        "aiexec.base.data": "wfx.base.data",
        "aiexec.base.embeddings": "wfx.base.embeddings",
        "aiexec.base.io": "wfx.base.io",
        "aiexec.base.memory": "wfx.base.memory",
        "aiexec.base.models": "wfx.base.models",
        "aiexec.base.prompts": "wfx.base.prompts",
        "aiexec.base.textsplitters": "wfx.base.textsplitters",
        "aiexec.base.tools": "wfx.base.tools",
        "aiexec.base.vectorstores": "wfx.base.vectorstores",
        # Core system modules with direct re-exports
        "aiexec.custom.custom_component": "wfx.custom.custom_component",
        "aiexec.graph": "wfx.graph",
        "aiexec.inputs": "wfx.inputs.inputs",
        "aiexec.interface": "wfx.interface",
        "aiexec.load": "wfx.load",
        "aiexec.logging": "wfx.log",  # Note: imports from wfx.log.logger
        "aiexec.schema": "wfx.schema",
        "aiexec.template.field": "wfx.template.field",
    }

    # Modules that use wildcard imports from wfx
    WILDCARD_REEXPORT_MODULES = {
        "aiexec.base": "wfx.base",
        "aiexec.template": "wfx.template",
    }

    # Modules with complex/mixed import patterns
    COMPLEX_REEXPORT_MODULES = {
        "aiexec.custom": ["wfx.custom", "wfx.custom.custom_component", "wfx.custom.utils"],
        "aiexec.io": ["wfx.io", "wfx.template"],  # Mixed imports
    }

    # Modules with dynamic __getattr__ patterns
    DYNAMIC_REEXPORT_MODULES = {
        "aiexec.field_typing": "wfx.field_typing",
    }

    def test_direct_reexport_modules_importable(self):
        """Test that all direct re-export modules can be imported."""
        successful_imports = 0

        for aiexec_module, wfx_module in self.DIRECT_REEXPORT_MODULES.items():
            try:
                # Import the aiexec module
                lf_module = importlib.import_module(aiexec_module)
                assert lf_module is not None, f"Aiexec module {aiexec_module} is None"

                # Import the corresponding wfx module to compare

                wfx_mod = importlib.import_module(wfx_module)
                assert wfx_mod is not None, f"WFX module {wfx_module} is None"

                successful_imports += 1

            except Exception as e:
                pytest.fail(f"Failed to import direct re-export module {aiexec_module}: {e!s}")

    def test_wildcard_reexport_modules_importable(self):
        """Test that modules using wildcard imports work correctly."""
        successful_imports = 0

        for aiexec_module, wfx_module in self.WILDCARD_REEXPORT_MODULES.items():
            try:
                # Import the aiexec module
                lf_module = importlib.import_module(aiexec_module)
                assert lf_module is not None, f"Aiexec module {aiexec_module} is None"

                # Wildcard imports should expose most/all attributes from wfx module
                wfx_mod = importlib.import_module(wfx_module)

                # Check that all attributes are available
                if hasattr(wfx_mod, "__all__"):
                    all_attrs = list(wfx_mod.__all__)  # Test all attributes
                    for attr in all_attrs:
                        if hasattr(wfx_mod, attr):
                            assert hasattr(lf_module, attr), f"Attribute {attr} missing from {aiexec_module}"

                successful_imports += 1

            except Exception as e:
                pytest.fail(f"Failed to import wildcard re-export module {aiexec_module}: {e!s}")

    def test_complex_reexport_modules_importable(self):
        """Test that modules with complex/mixed import patterns work correctly."""
        successful_imports = 0

        for aiexec_module in self.COMPLEX_REEXPORT_MODULES:
            try:
                # Import the aiexec module
                lf_module = importlib.import_module(aiexec_module)
                assert lf_module is not None, f"Aiexec module {aiexec_module} is None"

                # Verify it has __all__ attribute for complex modules
                assert hasattr(lf_module, "__all__"), f"Complex module {aiexec_module} missing __all__"
                assert len(lf_module.__all__) > 0, f"Complex module {aiexec_module} has empty __all__"

                # Try to access all items from __all__
                all_items = lf_module.__all__  # Test all items
                for item in all_items:
                    try:
                        attr = getattr(lf_module, item)
                        assert attr is not None, f"Attribute {item} is None in {aiexec_module}"
                    except AttributeError:
                        pytest.fail(f"Complex module {aiexec_module} missing expected attribute {item} from __all__")

                successful_imports += 1

            except Exception as e:
                pytest.fail(f"Failed to import complex re-export module {aiexec_module}: {e!s}")

    def test_dynamic_reexport_modules_importable(self):
        """Test that modules with __getattr__ dynamic loading work correctly."""
        successful_imports = 0

        for aiexec_module in self.DYNAMIC_REEXPORT_MODULES:
            try:
                # Import the aiexec module
                lf_module = importlib.import_module(aiexec_module)
                assert lf_module is not None, f"Aiexec module {aiexec_module} is None"

                # Dynamic modules should have __getattr__ method
                assert hasattr(lf_module, "__getattr__"), f"Dynamic module {aiexec_module} missing __getattr__"

                # Test accessing some known attributes dynamically
                if aiexec_module == "aiexec.field_typing":
                    # Test some known field typing constants
                    test_attrs = ["Data", "Text", "LanguageModel"]
                    for attr in test_attrs:
                        try:
                            value = getattr(lf_module, attr)
                            assert value is not None, f"Dynamic attribute {attr} is None"
                        except AttributeError:
                            pytest.fail(f"Dynamic module {aiexec_module} missing expected attribute {attr}")

                successful_imports += 1

            except Exception as e:
                pytest.fail(f"Failed to import dynamic re-export module {aiexec_module}: {e!s}")

    def test_all_reexport_modules_have_required_structure(self):
        """Test that re-export modules have the expected structure."""
        all_modules = {}
        all_modules.update(self.DIRECT_REEXPORT_MODULES)
        all_modules.update(self.WILDCARD_REEXPORT_MODULES)
        all_modules.update(self.DYNAMIC_REEXPORT_MODULES)

        # Add complex modules
        for lf_mod in self.COMPLEX_REEXPORT_MODULES:
            all_modules[lf_mod] = self.COMPLEX_REEXPORT_MODULES[lf_mod]

        for aiexec_module in all_modules:
            try:
                lf_module = importlib.import_module(aiexec_module)

                # All modules should be importable
                assert lf_module is not None

                # Most should have __name__ attribute
                assert hasattr(lf_module, "__name__")

                # Check for basic module structure
                assert hasattr(lf_module, "__file__") or hasattr(lf_module, "__path__")

            except Exception as e:
                pytest.fail(f"Module structure issue with {aiexec_module}: {e!s}")

    def test_reexport_modules_backward_compatibility(self):
        """Test that common import patterns still work for backward compatibility."""
        # Test some key imports that should always work
        backward_compatible_imports = [
            ("aiexec.schema", "Data"),
            ("aiexec.inputs", "StrInput"),
            ("aiexec.inputs", "IntInput"),
            ("aiexec.custom", "Component"),  # Base component class
            ("aiexec.custom", "CustomComponent"),
            ("aiexec.field_typing", "Text"),  # Dynamic
            ("aiexec.field_typing", "Data"),  # Dynamic
            ("aiexec.load", "load_flow_from_json"),
            ("aiexec.logging", "logger"),
        ]

        for module_name, symbol_name in backward_compatible_imports:
            try:
                module = importlib.import_module(module_name)
                symbol = getattr(module, symbol_name)
                assert symbol is not None

                # For callable objects, ensure they're callable
                if inspect.isclass(symbol) or inspect.isfunction(symbol):
                    assert callable(symbol)

            except Exception as e:
                pytest.fail(f"Backward compatibility issue with {module_name}.{symbol_name}: {e!s}")

    def test_no_circular_imports_in_reexports(self):
        """Test that there are no circular import issues in re-export modules."""
        # Test importing modules in different orders to catch circular imports
        import_orders = [
            ["aiexec.schema", "aiexec.inputs", "aiexec.base"],
            ["aiexec.base", "aiexec.schema", "aiexec.inputs"],
            ["aiexec.inputs", "aiexec.base", "aiexec.schema"],
            ["aiexec.custom", "aiexec.field_typing", "aiexec.template"],
            ["aiexec.template", "aiexec.custom", "aiexec.field_typing"],
            ["aiexec.field_typing", "aiexec.template", "aiexec.custom"],
        ]

        for order in import_orders:
            try:
                for module_name in order:
                    importlib.import_module(module_name)
                    # Try to access something from each module to trigger full loading
                    module = importlib.import_module(module_name)
                    if hasattr(module, "__all__") and module.__all__:
                        # Try to access first item in __all__
                        first_item = module.__all__[0]
                        try:
                            getattr(module, first_item)
                        except AttributeError:
                            pytest.fail(f"Module {module_name} missing expected attribute {first_item} from __all__")

            except Exception as e:
                pytest.fail(f"Circular import issue with order {order}: {e!s}")

    def test_reexport_modules_performance(self):
        """Test that re-export modules import efficiently."""
        # Test that basic imports are fast
        performance_critical_modules = [
            "aiexec.schema",
            "aiexec.inputs",
            "aiexec.field_typing",
            "aiexec.load",
            "aiexec.logging",
        ]

        slow_imports = []

        for module_name in performance_critical_modules:
            start_time = time.time()
            try:
                importlib.import_module(module_name)
                import_time = time.time() - start_time

                # Re-export modules should import quickly (< 1 second)
                if import_time > 1.0:
                    slow_imports.append(f"{module_name}: {import_time:.3f}s")

            except ImportError:
                # Import failures are tested elsewhere
                pass

        # Don't fail the test, just record slow imports for information

    def test_coverage_completeness(self):
        """Test that we're testing all known re-export modules."""
        # This test ensures we don't miss any re-export modules
        all_tested_modules = set()
        all_tested_modules.update(self.DIRECT_REEXPORT_MODULES.keys())
        all_tested_modules.update(self.WILDCARD_REEXPORT_MODULES.keys())
        all_tested_modules.update(self.COMPLEX_REEXPORT_MODULES.keys())
        all_tested_modules.update(self.DYNAMIC_REEXPORT_MODULES.keys())

        # Should be testing all 24 identified modules based on our analysis
        actual_count = len(all_tested_modules)

        # Ensure we have a reasonable number of modules
        assert actual_count >= 20, f"Too few modules being tested: {actual_count}"
        assert actual_count <= 30, f"Too many modules being tested: {actual_count}"

    # Dynamic test methods using the discovery functions
    def test_dynamic_module_discovery(self):
        """Test that we can dynamically discover aiexec modules."""
        modules = self._discover_aiexec_modules()
        assert len(modules) > 0, "Should discover at least some aiexec modules"

        # Check that known modules are found
        expected_modules = ["aiexec.schema", "aiexec.inputs", "aiexec.custom"]
        found_modules = [mod for mod in expected_modules if mod in modules]
        assert len(found_modules) > 0, f"Expected to find some of {expected_modules}, but found: {found_modules}"

    @pytest.mark.parametrize("module_name", get_all_reexport_modules())
    def test_parametrized_module_import_and_pattern_detection(self, module_name: str):
        """Parametrized test that checks module import and pattern detection."""
        # Test that module can be imported
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"Module {module_name} should not be None"
        except ImportError:
            pytest.fail(f"Could not import {module_name}")

        # Test pattern detection
        pattern_info = self._detect_reexport_pattern(module_name)
        assert isinstance(pattern_info, dict), "Pattern detection should return a dict"
        assert "type" in pattern_info, "Pattern info should have 'type' key"
        assert pattern_info["type"] in ["direct", "dynamic", "none", "import_error"], (
            f"Unknown pattern type: {pattern_info['type']}"
        )

    def test_generate_backward_compatibility_imports(self):
        """Test generating backward compatibility imports dynamically."""
        # Test with a known module that has wfx imports
        test_cases = [("aiexec.schema", "wfx.schema"), ("aiexec.custom", "wfx.custom")]

        for lf_module, expected_wfx_source in test_cases:
            symbols = self._get_expected_symbols(expected_wfx_source)
            assert len(symbols) > 0, f"Should find some symbols in {expected_wfx_source}"

            # Test that at least some symbols are accessible in the aiexec module
            module = importlib.import_module(lf_module)
            available_symbols = [sym for sym in symbols[:3] if hasattr(module, sym)]  # Test first 3
            assert len(available_symbols) > 0, f"Module {lf_module} should have some symbols from {expected_wfx_source}"
