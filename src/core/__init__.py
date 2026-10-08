"""core package — shared services used by all subsystems.

Exposes the tool-manifest loader (T-0201), the shared configuration /
canonical-path module (T-0202), and the evidence/claim primitives
(T-0302). Project-state utilities arrive in T-0301.
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
from src.core.evidence import (
    EVIDENCE_LABELS,
    Claim,
    EvidenceError,
    EvidenceLabel,
    compare,
    is_stronger,
    parse_label,
    rank,
    strongest,
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
    "EVIDENCE_LABELS",
    "EvidenceLabel",
    "EvidenceError",
    "Claim",
    "parse_label",
    "rank",
    "is_stronger",
    "compare",
    "strongest",
]