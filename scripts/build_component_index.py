#!/usr/bin/env python3
"""Component Index Builder for WFX.

This script scans all WFX components and creates a static index file that allows
for instant component loading without dynamic imports during runtime.

The index contains:
- Component metadata (name, module, file path)
- Component categories for selective loading
- Component dependencies and requirements

Usage:
    python scripts/build_component_index.py
"""

import json
import sys
from pathlib import Path
from typing import Any


# Simple logger implementation
class SimpleLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")

    def debug(self, msg):
        print(f"[DEBUG] {msg}")

    def warning(self, msg):
        print(f"[WARNING] {msg}")

    def error(self, msg):
        print(f"[ERROR] {msg}")


logger = SimpleLogger()


class ComponentIndexBuilder:
    """Builder for creating static component index."""

    def __init__(self, components_path: Path):
        """Initialize the component index builder.

        Args:
            components_path: Path to the components directory
        """
        self.components_path = Path(components_path)
        if not self.components_path.exists():
            msg = f"Components path does not exist: {self.components_path}"
            raise ValueError(msg)

        self.index: dict[str, Any] = {
            "metadata": {
                "version": "1.0",
                "generated_at": None,
                "total_components": 0,
                "total_modules": 0,
            },
            "components": {},
            "modules": {},
            "categories": {},
        }

    def scan_components(self) -> None:
        """Scan all component directories and build the index."""
        logger.info("Scanning components in: %s", self.components_path)

        # Get all component module directories
        module_dirs = [
            d
            for d in self.components_path.iterdir()
            if d.is_dir() and not d.name.startswith("__") and not d.name.startswith(".")
        ]

        logger.info("Found %s component modules", len(module_dirs))

        for module_dir in sorted(module_dirs):
            module_name = module_dir.name
            logger.debug("Scanning module: %s", module_name)

            # Check if the module has an __init__.py file
            init_file = module_dir / "__init__.py"
            if not init_file.exists():
                logger.debug("Skipping %s: no __init__.py file", module_name)
                continue

            # Try to import the module to get its _dynamic_imports
            try:
                # Read the __init__.py file to extract _dynamic_imports
                init_content = init_file.read_text(encoding="utf-8")

                # Parse _dynamic_imports from the file
                dynamic_imports = self._extract_dynamic_imports(init_content)
                if not dynamic_imports:
                    logger.debug("No dynamic imports found in %s", module_name)
                    continue

                # Process each component in the module
                for component_name, file_path in dynamic_imports.items():
                    if component_name != "__module__":  # Skip module-level imports
                        self._add_component_to_index(module_name, component_name, file_path)

                # Add module info to index
                self._add_module_to_index(module_name, dynamic_imports)

            except Exception as e:  # Broad exception catch needed for various module import failures  # noqa: BLE001
                logger.warning("Error scanning module %s: %s", module_name, e)
                continue

        # Update metadata
        self.index["metadata"]["total_components"] = len(self.index["components"])
        self.index["metadata"]["total_modules"] = len(self.index["modules"])
        self.index["metadata"]["generated_at"] = str(Path.cwd())

    def _extract_dynamic_imports(self, content: str) -> dict[str, str]:
        """Extract _dynamic_imports dictionary from module init file content.

        Args:
            content: The content of the __init__.py file

        Returns:
            Dictionary mapping component names to file paths
        """
        dynamic_imports = {}

        # Find the _dynamic_imports assignment
        lines = content.split("\n")
        in_dynamic_imports = False
        brace_count = 0
        dict_lines = []

        for line in lines:
            stripped = line.strip()

            # Check for start of _dynamic_imports
            if stripped.startswith("_dynamic_imports = {"):
                in_dynamic_imports = True
                brace_count = 1
                dict_lines.append(stripped)
            elif in_dynamic_imports:
                dict_lines.append(stripped)

                # Count braces to track nesting
                brace_count += stripped.count("{")
                brace_count -= stripped.count("}")

                # Check if we've reached the end
                if brace_count <= 0:
                    in_dynamic_imports = False
                    break

        if not dict_lines:
            return {}

        # Join all the lines and parse the dictionary
        dict_content = "\n".join(dict_lines)

        try:
            # Simple parsing - extract key-value pairs
            import re

            # Find all quoted key-value pairs
            matches = re.findall(r'"([^"]+)":\s*"([^"]*)"', dict_content)
            dynamic_imports.update(dict(matches))

            # Also handle "__module__" entries
            if '"__module__"' in dict_content:
                dynamic_imports["__module__"] = "__module__"

        except Exception as e:  # Broad exception catch needed for various parsing failures  # noqa: BLE001
            logger.warning("Error parsing dynamic imports: %s", e)

        return dynamic_imports

    def _add_component_to_index(self, module_name: str, component_name: str, file_path: str) -> None:
        """Add a component to the index.

        Args:
            module_name: Name of the component module
            component_name: Name of the component
            file_path: Path to the component file
        """
        component_key = f"{module_name}.{component_name}"

        # Extract component info from the file if possible
        component_file = self.components_path / module_name / f"{file_path}.py"
        component_info = self._extract_component_info(component_file, component_name)

        self.index["components"][component_key] = {
            "module": module_name,
            "name": component_name,
            "file_path": file_path,
            "full_path": str(component_file),
            "category": self._get_category_from_module(module_name),
            "info": component_info,
        }

        # Add to categories
        category = self._get_category_from_module(module_name)
        if category not in self.index["categories"]:
            self.index["categories"][category] = []
        self.index["categories"][category].append(component_key)

    def _add_module_to_index(self, module_name: str, dynamic_imports: dict[str, str]) -> None:
        """Add a module to the index.

        Args:
            module_name: Name of the module
            dynamic_imports: Dynamic imports for this module
        """
        self.index["modules"][module_name] = {
            "name": module_name,
            "category": self._get_category_from_module(module_name),
            "dynamic_imports": dynamic_imports,
            "component_count": sum(1 for k in dynamic_imports if k != "__module__"),
        }

    def _get_category_from_module(self, module_name: str) -> str:
        """Get the category for a module name.

        Args:
            module_name: Name of the module

        Returns:
            Category name for the module
        """
        # Map module names to categories
        category_map = {
            # AI/ML Models
            "anthropic": "models",
            "openai": "models",
            "mistral": "models",
            "vertexai": "models",
            "cohere": "models",
            "huggingface": "models",
            "nvidia": "models",
            "ollama": "models",
            "groq": "models",
            "perplexity": "models",
            "deepseek": "models",
            "xai": "models",
            "novita": "models",
            "sambanova": "models",
            "aiml": "models",
            # Vector Stores
            "faiss": "vectorstores",
            "pinecone": "vectorstores",
            "weaviate": "vectorstores",
            "qdrant": "vectorstores",
            "chroma": "vectorstores",
            "pgvector": "vectorstores",
            "milvus": "vectorstores",
            "vectara": "vectorstores",
            "supabase": "vectorstores",
            "upstash": "vectorstores",
            "redis": "vectorstores",
            # Data Sources
            "notion": "datasources",
            "confluence": "datasources",
            "wikipedia": "datasources",
            "arxiv": "datasources",
            "youtube": "datasources",
            "github": "datasources",
            # Search
            "duckduckgo": "search",
            "bing": "search",
            "google": "search",
            "serpapi": "search",
            "tavily": "search",
            "exa": "search",
            "searchapi": "search",
            # Tools & Utilities
            "tools": "tools",
            "helpers": "tools",
            "processing": "tools",
            "chains": "tools",
            "logic": "tools",
            "crewai": "tools",
            # Document Processing
            "documentloaders": "document_processing",
            "textsplitters": "document_processing",
            "unstructured": "document_processing",
            "docling": "document_processing",
            # Embeddings
            "embeddings": "embeddings",
            # Cloud & Platform
            "aws": "cloud",
            "amazon": "cloud",
            "gcp": "cloud",
            "azure": "cloud",
            # Custom & Other
            "custom_component": "custom",
            "composio": "integration",
            "homeassistant": "iot",
        }

        return category_map.get(module_name.lower(), "other")

    def _extract_component_info(self, component_file: Path, component_name: str) -> dict[str, Any]:
        """Extract information about a component from its file.

        Args:
            component_file: Path to the component file
            component_name: Name of the component class

        Returns:
            Dictionary with component information
        """
        info = {
            "description": "",
            "inputs": [],
            "outputs": [],
            "dependencies": [],
            "tags": [],
        }

        if not component_file.exists():
            return info

        try:
            content = component_file.read_text(encoding="utf-8")

            # Extract class docstring
            lines = content.split("\n")
            in_class = False
            in_docstring = False
            docstring_lines = []

            for line in lines:
                stripped = line.strip()

                # Look for class definition
                if stripped.startswith(f"class {component_name}"):
                    in_class = True
                    # Check if there's a docstring on the next line
                    continue

                if in_class and not in_docstring and stripped.startswith(('"""', "'''")):
                    in_docstring = True
                    if not (stripped.endswith(('"""', "'''"))):
                        continue
                    # Single line docstring
                    docstring = stripped.strip("\"'")
                    info["description"] = docstring
                    break

                if in_docstring:
                    if stripped.endswith(('"""', "'''")):
                        # End of docstring
                        docstring = "\n".join(docstring_lines).strip()
                        info["description"] = docstring
                        break
                    docstring_lines.append(line)

            # Extract dependencies from imports
            import_lines = [line for line in lines if line.strip().startswith(("import ", "from "))]
            for line in import_lines:
                # Simple extraction of package names
                if "import " in line:
                    parts = line.split("import")[1].split()
                    if parts:
                        pkg = parts[0].split(".")[0]
                        if pkg not in ["typing", "os", "sys", "json", "pathlib"] and pkg not in info["dependencies"]:
                            info["dependencies"].append(pkg)
                elif "from " in line:
                    parts = line.split("from")[1].split("import")
                    if parts:
                        pkg = parts[0].strip().split(".")[0]
                        if pkg not in ["typing", "os", "sys", "json", "pathlib"] and pkg not in info["dependencies"]:
                            info["dependencies"].append(pkg)

        except Exception as e:  # Broad exception catch needed for various file reading failures  # noqa: BLE001
            logger.warning("Error extracting component info from %s: %s", component_file, e)

        return info

    def save_index(self, output_path: Path) -> None:
        """Save the component index to a JSON file.

        Args:
            output_path: Path where to save the index file
        """
        logger.info("Saving component index to: %s", output_path)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, sort_keys=True)

        logger.info("Component index saved with %s components", len(self.index["components"]))

    def validate_index(self) -> bool:
        """Validate the generated index.

        Returns:
            True if index is valid, False otherwise
        """
        required_keys = ["metadata", "components", "modules", "categories"]
        for key in required_keys:
            if key not in self.index:
                logger.error("Missing required key: %s", key)
                return False

        # Check that all components reference valid modules
        for component_key, component_info in self.index["components"].items():
            module_name = component_info["module"]
            if module_name not in self.index["modules"]:
                logger.error("Component %s references unknown module: %s", component_key, module_name)
                return False

        logger.info("Component index validation passed")
        return True


def main():
    """Main entry point for the component index builder."""
    # Find the components directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Look for components directory in src/wfx/src/wfx/components
    components_path = project_root / "src" / "wfx" / "src" / "wfx" / "components"

    if not components_path.exists():
        logger.error("Components directory not found: %s", components_path)
        logger.info("Make sure you're running this script from the project root")
        sys.exit(1)

    # Create output directory for the index
    output_dir = project_root / "src" / "wfx" / "src" / "wfx" / "_assets"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "component_index.json"

    # Build the index
    builder = ComponentIndexBuilder(components_path)
    builder.scan_components()

    if not builder.validate_index():
        logger.error("Index validation failed")
        sys.exit(1)

    builder.save_index(output_path)
    logger.info("Component index build completed successfully!")


if __name__ == "__main__":
    main()
