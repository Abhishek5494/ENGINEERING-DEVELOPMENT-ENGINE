"""Upstream-source registry loader and validator (MASTER §2, §3, §49).

Loads ``config/upstream-sources.json`` and validates it against the same
rules expressed in ``config/upstream-sources.schema.json``. Implemented with
the standard library only (json); the JSON Schema file exists for external
tooling, while this module enforces the equivalent rules with clear, typed
errors.

The registry is a canonical, reference-only list of the upstream repositories
for every project-owned integration and specialist tool. It records WHERE an
upstream lives and HOW FAR it has been verified. It must never assert:

* installation state (runtime data, produced by PEM into environment.json);
* a version or commit that has not been verified;
* a license that has not been verified.

``null`` means UNKNOWN. Do not guess. Tool detection/installation metadata
remains in ``config/tool-manifest.json``; ids here match the corresponding
tool-manifest ids where one exists.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from src.core.config import UPSTREAM_SOURCES_PATH, UPSTREAM_SOURCES_SCHEMA_PATH

DEFAULT_REGISTRY_PATH = UPSTREAM_SOURCES_PATH
DEFAULT_SCHEMA_PATH = UPSTREAM_SOURCES_SCHEMA_PATH

SOURCE_TYPES = frozenset({"core-integration", "specialist-tool", "version-control"})
VERIFICATION_STATUSES = frozenset({"VERIFIED", "UNVERIFIED", "UNKNOWN"})
INTEGRATION_STATUSES = frozenset(
    {"COMPLETE", "PARTIAL", "PLANNED", "BLOCKED", "NOT_INTEGRATED", "UNKNOWN"}
)

REQUIRED_SOURCE_FIELDS = (
    "id",
    "name",
    "purpose",
    "repository_url",
    "documentation_url",
    "source_type",
    "license_status",
    "version_status",
    "integration_status",
)
OPTIONAL_SOURCE_FIELDS = ("version", "commit", "license", "notes")
ALLOWED_SOURCE_FIELDS = frozenset(REQUIRED_SOURCE_FIELDS) | frozenset(OPTIONAL_SOURCE_FIELDS)

_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class UpstreamRegistryError(Exception):
    """Raised when the registry is missing, unparseable, or invalid."""


def _err(where: str, message: str) -> UpstreamRegistryError:
    return UpstreamRegistryError(f"upstream registry: {where}: {message}")


def _check_optional_str(value: Any, where: str, field: str) -> None:
    if value is not None and not isinstance(value, str):
        raise _err(where, f"field '{field}' must be a string or null, got {type(value).__name__}")


def _check_https_url(value: Any, where: str, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise _err(where, f"field '{field}' must be a non-empty https URL string")
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.netloc:
        raise _err(where, f"field '{field}' must be a valid https URL, got {value!r}")


def _validate_source(entry: Any, index: int, seen_ids: set[str]) -> None:
    where = f"sources[{index}]"
    if not isinstance(entry, dict):
        raise _err(where, f"source entry must be an object, got {type(entry).__name__}")

    source_id = entry.get("id")
    if isinstance(source_id, str):
        where = f"sources[{index}] ({source_id})"

    missing = [field for field in REQUIRED_SOURCE_FIELDS if field not in entry]
    if missing:
        raise _err(where, f"missing required field(s): {', '.join(missing)}")

    unknown = [key for key in entry if key not in ALLOWED_SOURCE_FIELDS]
    if unknown:
        raise _err(where, f"unknown field(s): {', '.join(sorted(unknown))}")

    if not isinstance(source_id, str) or not _ID_PATTERN.match(source_id):
        raise _err(where, f"id must be a lowercase kebab-case string, got {source_id!r}")
    if source_id in seen_ids:
        raise _err(where, f"duplicate source id '{source_id}'")
    seen_ids.add(source_id)

    for field in ("name", "purpose"):
        value = entry[field]
        if not isinstance(value, str) or not value.strip():
            raise _err(where, f"field '{field}' must be a non-empty string")

    _check_https_url(entry["repository_url"], where, "repository_url")

    doc_url = entry["documentation_url"]
    if doc_url is not None:
        _check_https_url(doc_url, where, "documentation_url")

    if entry["source_type"] not in SOURCE_TYPES:
        raise _err(
            where,
            f"field 'source_type' must be one of {sorted(SOURCE_TYPES)}, "
            f"got {entry['source_type']!r}",
        )

    for field in ("license_status", "version_status"):
        if entry[field] not in VERIFICATION_STATUSES:
            raise _err(
                where,
                f"field '{field}' must be one of {sorted(VERIFICATION_STATUSES)}, "
                f"got {entry[field]!r}",
            )

    if entry["integration_status"] not in INTEGRATION_STATUSES:
        raise _err(
            where,
            f"field 'integration_status' must be one of {sorted(INTEGRATION_STATUSES)}, "
            f"got {entry['integration_status']!r}",
        )

    for field in OPTIONAL_SOURCE_FIELDS:
        if field in entry:
            _check_optional_str(entry[field], where, field)

    # Honesty: UNKNOWN forbids a claimed value; a claim must not be empty.
    license_status = entry["license_status"]
    license_value = entry.get("license")
    if license_status == "UNKNOWN" and license_value is not None:
        raise _err(where, "license must be null when license_status is UNKNOWN")
    if license_status == "VERIFIED" and not (isinstance(license_value, str) and license_value.strip()):
        raise _err(where, "license_status VERIFIED requires a non-empty 'license' value")

    version_status = entry["version_status"]
    version_value = entry.get("version")
    commit_value = entry.get("commit")
    if version_status == "UNKNOWN" and (version_value is not None or commit_value is not None):
        raise _err(where, "version/commit must be null when version_status is UNKNOWN")
    if version_status == "VERIFIED" and not (
        (isinstance(version_value, str) and version_value.strip())
        or (isinstance(commit_value, str) and commit_value.strip())
    ):
        raise _err(where, "version_status VERIFIED requires a non-empty 'version' or 'commit'")


def validate_registry(data: Any) -> dict[str, Any]:
    """Validate an already-parsed registry document. Returns it on success."""
    if not isinstance(data, dict):
        raise _err("<document>", f"registry must be an object, got {type(data).__name__}")

    for field in ("schema_version", "sources"):
        if field not in data:
            raise _err("<document>", f"missing required field '{field}'")
    unknown = [key for key in data if key not in {"schema_version", "sources"}]
    if unknown:
        raise _err("<document>", f"unknown field(s): {', '.join(sorted(unknown))}")

    if not isinstance(data["schema_version"], str):
        raise _err("<document>", "field 'schema_version' must be a string")

    sources = data["sources"]
    if not isinstance(sources, list) or not sources:
        raise _err("<document>", "field 'sources' must be a non-empty list")

    seen_ids: set[str] = set()
    for index, entry in enumerate(sources):
        _validate_source(entry, index, seen_ids)

    return data


def load_upstream_sources(path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate the upstream-source registry.

    Raises:
        UpstreamRegistryError: file missing, invalid JSON, or schema violation.
    """
    registry_path = Path(path) if path is not None else DEFAULT_REGISTRY_PATH
    if not registry_path.is_file():
        raise _err(str(registry_path), "registry file not found")
    try:
        raw = registry_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _err(str(registry_path), f"cannot read registry: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise _err(str(registry_path), f"invalid JSON: {exc}") from exc
    return validate_registry(data)


def source_ids(registry: dict[str, Any] | None = None) -> list[str]:
    """Return the ordered list of source ids from the registry."""
    data = registry if registry is not None else load_upstream_sources()
    return [entry["id"] for entry in data["sources"]]


def get_source(source_id: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the registry entry for ``source_id``.

    Raises:
        UpstreamRegistryError: no entry with that id.
    """
    data = registry if registry is not None else load_upstream_sources()
    for entry in data["sources"]:
        if entry["id"] == source_id:
            return entry
    raise _err("<lookup>", f"no source with id {source_id!r}")


if __name__ == "__main__":
    loaded = load_upstream_sources()
    print(
        f"upstream registry OK: {len(loaded['sources'])} sources: "
        f"{', '.join(source_ids(loaded))}"
    )
