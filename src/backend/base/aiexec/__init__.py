"""Aiexec backwards compatibility layer.

This module provides backwards compatibility by forwarding imports from
aiexec.* to wfx.* to maintain compatibility with existing code that
references the old aiexec module structure.
"""

import importlib
import importlib.util
import sys
from types import ModuleType
from typing import Any


class AiexecCompatibilityModule(ModuleType):
    """A module that forwards attribute access to the corresponding wfx module."""

    def __init__(self, name: str, wfx_module_name: str):
        super().__init__(name)
        self._wfx_module_name = wfx_module_name
        self._wfx_module = None

    def _get_wfx_module(self):
        """Lazily import and cache the wfx module."""
        if self._wfx_module is None:
            try:
                self._wfx_module = importlib.import_module(self._wfx_module_name)
            except ImportError as e:
                msg = f"Cannot import {self._wfx_module_name} for backwards compatibility with {self.__name__}"
                raise ImportError(msg) from e
        return self._wfx_module

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to the wfx module with caching."""
        wfx_module = self._get_wfx_module()
        try:
            attr = getattr(wfx_module, name)
        except AttributeError as e:
            msg = f"module '{self.__name__}' has no attribute '{name}'"
            raise AttributeError(msg) from e
        else:
            # Cache the attribute in our __dict__ for faster subsequent access
            setattr(self, name, attr)
            return attr

    def __dir__(self):
        """Return directory of the wfx module."""
        try:
            wfx_module = self._get_wfx_module()
            return dir(wfx_module)
        except ImportError:
            return []


def _setup_compatibility_modules():
    """Set up comprehensive compatibility modules for aiexec.base imports."""
    # First, set up the base attribute on this module (aiexec)
    current_module = sys.modules[__name__]

    # Define all the modules we need to support
    module_mappings = {
        # Core base module
        "aiexec.base": "wfx.base",
        # Inputs module - critical for class identity
        "aiexec.inputs": "wfx.inputs",
        "aiexec.inputs.inputs": "wfx.inputs.inputs",
        # Schema modules - also critical for class identity
        "aiexec.schema": "wfx.schema",
        "aiexec.schema.data": "wfx.schema.data",
        "aiexec.schema.serialize": "wfx.schema.serialize",
        # Template modules
        "aiexec.template": "wfx.template",
        "aiexec.template.field": "wfx.template.field",
        "aiexec.template.field.base": "wfx.template.field.base",
        # Components modules
        "aiexec.components": "wfx.components",
        "aiexec.components.helpers": "wfx.components.helpers",
        "aiexec.components.helpers.calculator_core": "wfx.components.helpers.calculator_core",
        "aiexec.components.helpers.create_list": "wfx.components.helpers.create_list",
        "aiexec.components.helpers.current_date": "wfx.components.helpers.current_date",
        "aiexec.components.helpers.id_generator": "wfx.components.helpers.id_generator",
        "aiexec.components.helpers.memory": "wfx.components.helpers.memory",
        "aiexec.components.helpers.output_parser": "wfx.components.helpers.output_parser",
        "aiexec.components.helpers.store_message": "wfx.components.helpers.store_message",
        # Individual modules that exist in wfx
        "aiexec.base.agents": "wfx.base.agents",
        "aiexec.base.chains": "wfx.base.chains",
        "aiexec.base.data": "wfx.base.data",
        "aiexec.base.data.utils": "wfx.base.data.utils",
        "aiexec.base.document_transformers": "wfx.base.document_transformers",
        "aiexec.base.embeddings": "wfx.base.embeddings",
        "aiexec.base.flow_processing": "wfx.base.flow_processing",
        "aiexec.base.io": "wfx.base.io",
        "aiexec.base.io.chat": "wfx.base.io.chat",
        "aiexec.base.io.text": "wfx.base.io.text",
        "aiexec.base.langchain_utilities": "wfx.base.langchain_utilities",
        "aiexec.base.memory": "wfx.base.memory",
        "aiexec.base.models": "wfx.base.models",
        "aiexec.base.models.google_generative_ai_constants": "wfx.base.models.google_generative_ai_constants",
        "aiexec.base.models.openai_constants": "wfx.base.models.openai_constants",
        "aiexec.base.models.anthropic_constants": "wfx.base.models.anthropic_constants",
        "aiexec.base.models.aiml_constants": "wfx.base.models.aiml_constants",
        "aiexec.base.models.aws_constants": "wfx.base.models.aws_constants",
        "aiexec.base.models.groq_constants": "wfx.base.models.groq_constants",
        "aiexec.base.models.novita_constants": "wfx.base.models.novita_constants",
        "aiexec.base.models.ollama_constants": "wfx.base.models.ollama_constants",
        "aiexec.base.models.sambanova_constants": "wfx.base.models.sambanova_constants",
        "aiexec.base.models.cometapi_constants": "wfx.base.models.cometapi_constants",
        "aiexec.base.prompts": "wfx.base.prompts",
        "aiexec.base.prompts.api_utils": "wfx.base.prompts.api_utils",
        "aiexec.base.prompts.utils": "wfx.base.prompts.utils",
        "aiexec.base.textsplitters": "wfx.base.textsplitters",
        "aiexec.base.tools": "wfx.base.tools",
        "aiexec.base.vectorstores": "wfx.base.vectorstores",
    }

    # Create compatibility modules for each mapping
    for aiexec_name, wfx_name in module_mappings.items():
        if aiexec_name not in sys.modules:
            # Check if the wfx module exists
            try:
                spec = importlib.util.find_spec(wfx_name)
                if spec is not None:
                    # Create compatibility module
                    compat_module = AiexecCompatibilityModule(aiexec_name, wfx_name)
                    sys.modules[aiexec_name] = compat_module

                    # Set up the module hierarchy
                    parts = aiexec_name.split(".")
                    if len(parts) > 1:
                        parent_name = ".".join(parts[:-1])
                        parent_module = sys.modules.get(parent_name)
                        if parent_module is not None:
                            setattr(parent_module, parts[-1], compat_module)

                    # Special handling for top-level modules
                    if aiexec_name == "aiexec.base":
                        current_module.base = compat_module
                    elif aiexec_name == "aiexec.inputs":
                        current_module.inputs = compat_module
                    elif aiexec_name == "aiexec.schema":
                        current_module.schema = compat_module
                    elif aiexec_name == "aiexec.template":
                        current_module.template = compat_module
                    elif aiexec_name == "aiexec.components":
                        current_module.components = compat_module
            except (ImportError, ValueError):
                # Skip modules that don't exist in wfx
                continue

    # Handle modules that exist only in aiexec (like knowledge_bases)
    # These need special handling because they're not in wfx yet
    aiexec_only_modules = {
        "aiexec.base.data.kb_utils": "aiexec.base.data.kb_utils",
        "aiexec.base.knowledge_bases": "aiexec.base.knowledge_bases",
        "aiexec.components.knowledge_bases": "aiexec.components.knowledge_bases",
    }

    for aiexec_name in aiexec_only_modules:
        if aiexec_name not in sys.modules:
            try:
                # Try to find the actual physical module file
                from pathlib import Path

                base_dir = Path(__file__).parent

                if aiexec_name == "aiexec.base.data.kb_utils":
                    kb_utils_file = base_dir / "base" / "data" / "kb_utils.py"
                    if kb_utils_file.exists():
                        spec = importlib.util.spec_from_file_location(aiexec_name, kb_utils_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[aiexec_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("aiexec.base.data")
                            if parent_module is not None:
                                parent_module.kb_utils = module

                elif aiexec_name == "aiexec.base.knowledge_bases":
                    kb_dir = base_dir / "base" / "knowledge_bases"
                    kb_init_file = kb_dir / "__init__.py"
                    if kb_init_file.exists():
                        spec = importlib.util.spec_from_file_location(aiexec_name, kb_init_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[aiexec_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("aiexec.base")
                            if parent_module is not None:
                                parent_module.knowledge_bases = module

                elif aiexec_name == "aiexec.components.knowledge_bases":
                    components_kb_dir = base_dir / "components" / "knowledge_bases"
                    components_kb_init_file = components_kb_dir / "__init__.py"
                    if components_kb_init_file.exists():
                        spec = importlib.util.spec_from_file_location(aiexec_name, components_kb_init_file)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[aiexec_name] = module
                            spec.loader.exec_module(module)

                            # Also add to parent module
                            parent_module = sys.modules.get("aiexec.components")
                            if parent_module is not None:
                                parent_module.knowledge_bases = module
            except (ImportError, AttributeError):
                # If direct file loading fails, skip silently
                continue


# Set up all the compatibility modules
_setup_compatibility_modules()
