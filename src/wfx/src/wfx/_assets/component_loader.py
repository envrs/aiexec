"""
Component Index Loader for WFX

This module implements the three-tier loading strategy for WFX components:
1. Production (Built-in Index): Loads from static index file
2. Production (Fallback Cache): Builds cache if index missing
3. Development Mode: Always rebuilds for live code changes

Supports selective module loading for faster development workflows.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from wfx.log.logger import logger


class ComponentIndexLoader:
    """Component index loader with three-tier loading strategy."""

    def __init__(self):
        """Initialize the component index loader."""
        self.index_path: Optional[Path] = None
        self.cache_path: Optional[Path] = None
        self.index_data: Optional[Dict[str, Any]] = None
        self._development_mode = False
        self._selective_modules: Set[str] = set()

        # Set up paths
        self._setup_paths()

        # Check environment variables
        self._check_environment_variables()

    def _setup_paths(self) -> None:
        """Set up paths for index and cache files."""
        try:
            # Find the WFX package root
            wfx_root = Path(__file__).parent.parent.parent
            self.index_path = wfx_root / "_assets" / "component_index.json"

            # Set up cache directory
            if sys.platform == "win32":
                cache_dir = Path.home() / ".cache" / "wfx"
            else:
                cache_dir = Path.home() / ".cache" / "wfx"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_path = cache_dir / "component_index.json"

        except Exception as e:
            logger.warning(f"Error setting up paths: {e}")
            self.index_path = None
            self.cache_path = None

    def _check_environment_variables(self) -> None:
        """Check environment variables for loading configuration."""
        # Check for development mode
        wfx_dev = os.getenv("WFX_DEV", "")
        if wfx_dev:
            self._development_mode = True
            logger.debug("Development mode enabled via WFX_DEV")

            # Parse selective modules if specified
            if wfx_dev not in ["1", "true", "True", "TRUE"]:
                # WFX_DEV contains comma-separated module names
                modules = [m.strip() for m in wfx_dev.split(",") if m.strip()]
                self._selective_modules = set(m.lower() for m in modules)
                logger.debug(f"Selective loading enabled for modules: {', '.join(self._selective_modules)}")

        # Check for custom index path
        custom_index_path = os.getenv("WFX_COMPONENTS_INDEX_PATH")
        if custom_index_path:
            custom_path = Path(custom_index_path)
            if custom_path.exists():
                self.index_path = custom_path
                logger.debug(f"Using custom index path: {custom_path}")
            else:
                logger.warning(f"Custom index path does not exist: {custom_path}")

    def load_index(self) -> Dict[str, Any]:
        """Load component index using three-tier strategy.

        Returns:
            Component index data

        Raises:
            RuntimeError: If no valid index can be loaded
        """
        if self._development_mode:
            return self._load_development_mode()
        else:
            return self._load_production_mode()

    def _load_production_mode(self) -> Dict[str, Any]:
        """Load index in production mode using three-tier strategy."""
        # Tier 1: Try built-in index
        if self._try_load_builtin_index():
            logger.debug("Loaded component index from built-in file")
            return self.index_data

        # Tier 2: Try cached index
        if self._try_load_cached_index():
            logger.debug("Loaded component index from cache")
            return self.index_data

        # Tier 3: Build and cache index
        logger.info("Building component index for first time...")
        if self._build_and_cache_index():
            logger.debug("Built and cached component index")
            return self.index_data

        # Final fallback: raise error
        raise RuntimeError("Failed to load or build component index")

    def _load_development_mode(self) -> Dict[str, Any]:
        """Load index in development mode."""
        if self._selective_modules:
            # Selective loading mode
            logger.info(f"Development mode with selective loading: {', '.join(self._selective_modules)}")
            return self._build_selective_index()
        else:
            # Full rebuild mode
            logger.info("Development mode: rebuilding all components")
            return self._build_full_index()

    def _try_load_builtin_index(self) -> bool:
        """Try to load the built-in index file.

        Returns:
            True if successful, False otherwise
        """
        if not self.index_path or not self.index_path.exists():
            return False

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                self.index_data = json.load(f)
            logger.debug(f"Successfully loaded built-in index from {self.index_path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to load built-in index: {e}")
            return False

    def _try_load_cached_index(self) -> bool:
        """Try to load the cached index file.

        Returns:
            True if successful, False otherwise
        """
        if not self.cache_path or not self.cache_path.exists():
            return False

        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                self.index_data = json.load(f)
            logger.debug(f"Successfully loaded cached index from {self.cache_path}")
            return True
        except Exception as e:
            logger.warning(f"Failed to load cached index: {e}")
            return False

    def _build_and_cache_index(self) -> bool:
        """Build component index and cache it.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from scripts.build_component_index import ComponentIndexBuilder

            if not self.index_path:
                logger.error("No index path configured")
                return False

            # Get components directory
            components_dir = self.index_path.parent.parent / "components"
            if not components_dir.exists():
                logger.error(f"Components directory not found: {components_dir}")
                return False

            # Build the index
            builder = ComponentIndexBuilder(components_dir)
            builder.scan_components()

            if not builder.validate_index():
                logger.error("Built index failed validation")
                return False

            # Cache the index
            if self.cache_path:
                builder.save_index(self.cache_path)
                logger.debug(f"Cached index to {self.cache_path}")

            # Set as current index data
            self.index_data = builder.index
            return True

        except Exception as e:
            logger.error(f"Failed to build component index: {e}")
            return False

    def _build_selective_index(self) -> Dict[str, Any]:
        """Build index with selective module loading.

        Returns:
            Filtered component index
        """
        try:
            # First build the full index
            full_index = self._build_full_index()

            if not self._selective_modules:
                return full_index

            # Filter the index based on selected modules
            filtered_index = {
                "metadata": full_index["metadata"].copy(),
                "components": {},
                "modules": {},
                "categories": {},
            }

            # Update metadata
            filtered_index["metadata"]["selective_modules"] = list(self._selective_modules)
            filtered_index["metadata"]["total_components"] = 0
            filtered_index["metadata"]["total_modules"] = 0

            # Filter modules
            for module_name, module_info in full_index["modules"].items():
                module_category = module_info["category"]
                if module_category in self._selective_modules:
                    filtered_index["modules"][module_name] = module_info
                    filtered_index["metadata"]["total_modules"] += 1

            # Filter components
            for component_key, component_info in full_index["components"].items():
                component_category = component_info["category"]
                if component_category in self._selective_modules:
                    filtered_index["components"][component_key] = component_info
                    filtered_index["metadata"]["total_components"] += 1

                    # Add category if not present
                    if component_category not in filtered_index["categories"]:
                        filtered_index["categories"][component_category] = []
                    filtered_index["categories"][component_category].append(component_key)

            logger.info(f"Filtered index contains {filtered_index['metadata']['total_components']} components from {filtered_index['metadata']['total_modules']} modules")
            return filtered_index

        except Exception as e:
            logger.error(f"Failed to build selective index: {e}")
            # Fallback to full index
            return self._build_full_index()

    def _build_full_index(self) -> Dict[str, Any]:
        """Build full component index for development mode.

        Returns:
            Complete component index
        """
        try:
            # Import here to avoid circular imports
            from scripts.build_component_index import ComponentIndexBuilder

            if not self.index_path:
                logger.error("No index path configured")
                raise RuntimeError("No index path configured")

            # Get components directory
            components_dir = self.index_path.parent.parent / "components"
            if not components_dir.exists():
                logger.error(f"Components directory not found: {components_dir}")
                raise RuntimeError(f"Components directory not found: {components_dir}")

            # Build the index
            builder = ComponentIndexBuilder(components_dir)
            builder.scan_components()

            if not builder.validate_index():
                logger.error("Built index failed validation")
                raise RuntimeError("Built index failed validation")

            return builder.index

        except Exception as e:
            logger.error(f"Failed to build full index: {e}")
            raise

    def get_available_modules(self) -> List[str]:
        """Get list of available component modules.

        Returns:
            List of module names
        """
        if not self.index_data:
            self.load_index()

        if not self.index_data:
            return []

        return list(self.index_data.get("modules", {}).keys())

    def get_available_categories(self) -> List[str]:
        """Get list of available component categories.

        Returns:
            List of category names
        """
        if not self.index_data:
            self.load_index()

        if not self.index_data:
            return []

        return list(self.index_data.get("categories", {}).keys())

    def get_components_in_module(self, module_name: str) -> List[str]:
        """Get list of components in a specific module.

        Args:
            module_name: Name of the module

        Returns:
            List of component names
        """
        if not self.index_data:
            self.load_index()

        if not self.index_data:
            return []

        module_info = self.index_data.get("modules", {}).get(module_name)
        if not module_info:
            return []

        components = []
        for component_key in module_info.get("dynamic_imports", {}):
            if component_key != "__module__":
                components.append(component_key)

        return components

    def get_components_in_category(self, category: str) -> List[str]:
        """Get list of components in a specific category.

        Args:
            category: Name of the category

        Returns:
            List of component keys
        """
        if not self.index_data:
            self.load_index()

        if not self.index_data:
            return []

        return self.index_data.get("categories", {}).get(category, [])

    def is_development_mode(self) -> bool:
        """Check if running in development mode.

        Returns:
            True if in development mode, False otherwise
        """
        return self._development_mode

    def get_selective_modules(self) -> Set[str]:
        """Get the set of selectively loaded modules.

        Returns:
            Set of module names being selectively loaded
        """
        return self._selective_modules.copy()


# Global instance for easy access
_component_loader: Optional[ComponentIndexLoader] = None


def get_component_loader() -> ComponentIndexLoader:
    """Get the global component index loader instance.

    Returns:
        ComponentIndexLoader instance
    """
    global _component_loader
    if _component_loader is None:
        _component_loader = ComponentIndexLoader()
    return _component_loader


def load_component_index() -> Dict[str, Any]:
    """Load the component index using the configured strategy.

    Returns:
        Component index data
    """
    loader = get_component_loader()
    return loader.load_index()


def is_development_mode() -> bool:
    """Check if running in development mode.

    Returns:
        True if in development mode, False otherwise
    """
    loader = get_component_loader()
    return loader.is_development_mode()


def get_available_modules() -> List[str]:
    """Get list of available component modules.

    Returns:
        List of module names
    """
    loader = get_component_loader()
    return loader.get_available_modules()


def get_available_categories() -> List[str]:
    """Get list of available component categories.

    Returns:
        List of category names
    """
    loader = get_component_loader()
    return loader.get_available_categories()
