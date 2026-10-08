"""core package — shared services used by all subsystems.

Exposes the tool-manifest loader (T-0201) and the shared configuration /
canonical-path module (T-0202). Project-state utilities arrive in T-0301.
"""

from src.core.config import (
    CAD_DIR,
    COMPONENTS_DIR,
    CONFIG_DIR,
    DATA_DIR,
    DECISIONS_DIR,
    DOCS_DIR,
    ELECTRONICS_DIR,
    MODELS_DIR,
    PROJECTS_DIR,
    REPO_ROOT,
    SCRIPTS_DIR,
    SIMULATIONS_DIR,
    TESTS_DIR,
    ConfigError,
    load_config,
    load_json,
    load_yaml,
    resolve_path,
    yaml_available,
)

__all__ = [
    "REPO_ROOT",
    "CONFIG_DIR",
    "CAD_DIR",
    "ELECTRONICS_DIR",
    "SIMULATIONS_DIR",
    "MODELS_DIR",
    "DATA_DIR",
    "COMPONENTS_DIR",
    "DOCS_DIR",
    "PROJECTS_DIR",
    "SCRIPTS_DIR",
    "DECISIONS_DIR",
    "TESTS_DIR",
    "ConfigError",
    "load_config",
    "load_json",
    "load_yaml",
    "resolve_path",
    "yaml_available",
]