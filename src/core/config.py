"""Shared configuration and canonical repository paths (T-0202, MASTER §49).

Single source of truth for:
- the repository root (derived from this file, never from the CWD);
- canonical subsystem directories;
- the manifest / schema config file locations;
- loading configuration files (JSON always; YAML when a parser is
  available) with default values and clear errors.

Standard library only. Reading a YAML file without PyYAML raises a clear
``ConfigError`` — it never silently returns empty data.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping, Optional

try:  # optional dependency; never required
    import yaml as _yaml  # type: ignore
except Exception:  # pragma: no cover - exercised via branching tests
    _yaml = None


class ConfigError(ValueError):
    """Raised when configuration cannot be located, parsed, or represented."""


# ``src/core/config.py`` -> core -> src -> <repo root>
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

CONFIG_DIR: Path = REPO_ROOT / "config"
CAD_DIR: Path = REPO_ROOT / "cad"
ELECTRONICS_DIR: Path = REPO_ROOT / "electronics"
SIMULATIONS_DIR: Path = REPO_ROOT / "simulations"
MODELS_DIR: Path = REPO_ROOT / "models"
DATA_DIR: Path = REPO_ROOT / "data"
COMPONENTS_DIR: Path = REPO_ROOT / "components"
DOCS_DIR: Path = REPO_ROOT / "docs"
PROJECTS_DIR: Path = REPO_ROOT / "projects"
SCRIPTS_DIR: Path = REPO_ROOT / "scripts"
DECISIONS_DIR: Path = REPO_ROOT / "decisions"
TESTS_DIR: Path = REPO_ROOT / "tests"

MANIFEST_PATH: Path = CONFIG_DIR / "tool-manifest.json"
MANIFEST_SCHEMA_PATH: Path = CONFIG_DIR / "tool-manifest.schema.json"
ENVIRONMENT_REPORT_SCHEMA_PATH: Path = CONFIG_DIR / "environment-report.schema.json"

DIRECTORIES: Mapping[str, Path] = {
    "config": CONFIG_DIR,
    "cad": CAD_DIR,
    "electronics": ELECTRONICS_DIR,
    "simulations": SIMULATIONS_DIR,
    "models": MODELS_DIR,
    "data": DATA_DIR,
    "components": COMPONENTS_DIR,
    "docs": DOCS_DIR,
    "projects": PROJECTS_DIR,
    "scripts": SCRIPTS_DIR,
    "decisions": DECISIONS_DIR,
    "tests": TESTS_DIR,
}

_JSON_SUFFIXES = frozenset({".json"})
_YAML_SUFFIXES = frozenset({".yaml", ".yml"})


def yaml_available() -> bool:
    """True when a YAML parser is importable."""
    return _yaml is not None


def resolve_path(path: str | Path) -> Path:
    """Resolve a path against the repository root when it is relative."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else (REPO_ROOT / candidate)


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` onto a copy of ``base``."""
    merged: dict[str, Any] = copy.deepcopy(dict(base))
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], Mapping)
            and isinstance(value, Mapping)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_json(
    path: Path, *, defaults: Optional[Mapping[str, Any]] = None
) -> dict[str, Any]:
    """Load a JSON file; merge onto ``defaults`` when given.

    Missing file with no defaults, or unreadable/invalid JSON, raises
    ``ConfigError``. A missing file with defaults returns a copy of the
    defaults unchanged.
    """
    resolved = resolve_path(path)
    if not resolved.is_file():
        if defaults is None:
            raise ConfigError(f"config file not found: {resolved}")
        return copy.deepcopy(dict(defaults))
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"cannot read config {resolved}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"config root must be an object: {resolved}")
    if defaults is not None:
        return _deep_merge(defaults, data)
    return data


def load_yaml(path: Path, *, defaults: Optional[Mapping[str, Any]] = None) -> dict[str, Any]:
    """Load a YAML file when a parser is available; otherwise raise."""
    resolved = resolve_path(path)
    if _yaml is None:
        raise ConfigError(
            f"cannot load {resolved}: no YAML parser installed "
            "(install PyYAML or use JSON)"
        )
    if not resolved.is_file():
        if defaults is None:
            raise ConfigError(f"config file not found: {resolved}")
        return copy.deepcopy(dict(defaults))
    try:
        data = _yaml.safe_load(resolved.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"cannot read config {resolved}: {exc}") from exc
    except Exception as exc:  # yaml.YAMLError and subclasses
        raise ConfigError(f"invalid YAML in {resolved}: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"config root must be a mapping: {resolved}")
    if defaults is not None:
        return _deep_merge(defaults, data)
    return data


def load_config(
    name: str,
    *,
    defaults: Optional[Mapping[str, Any]] = None,
    directory: Path = CONFIG_DIR,
) -> dict[str, Any]:
    """Load a config file by name or path.

    Relative names resolve against ``directory`` (default: ``config/``).
    The parser is chosen by extension: ``.json`` always; ``.yaml``/``.yml``
    only when a YAML parser is available.
    """
    candidate = Path(name)
    if not candidate.is_absolute():
        candidate = directory / candidate
    suffix = candidate.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return load_yaml(candidate, defaults=defaults)
    if suffix == ".json":
        return load_json(candidate, defaults=defaults)
    raise ConfigError(
        f"unsupported config extension {suffix!r} for {candidate} "
        "(use .json or .yaml/.yml)"
    )