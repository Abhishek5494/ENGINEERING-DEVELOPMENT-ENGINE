"""Tool manifest loader and validator (T-0201, MASTER.md section 24).

Loads ``config/tool-manifest.json`` and validates it against the same
rules expressed in ``config/tool-manifest.schema.json``. Implemented with
the standard library only (json); the JSON Schema file exists for
external tooling, while this module enforces the equivalent rules with
clear, typed errors.

The manifest describes tools and HOW to detect them. It must never assert
whether a tool is installed — that is runtime data produced by PEM
(T-0102) into environment.json.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST_PATH = Path(__file__).resolve().parents[2] / "config" / "tool-manifest.json"
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "config" / "tool-manifest.schema.json"

SUPPORTED_PLATFORMS = frozenset({"windows", "linux", "macos"})
REQUIRED_VALUES = frozenset({"required", "optional"})
DETECTION_METHODS = frozenset({"command", "python_module", "path", "none"})
CAPABILITIES = frozenset(
    {
        "LLM inference",
        "CAD",
        "PCB design",
        "circuit simulation",
        "robotics simulation",
        "3D rendering",
        "numerical optimization",
        "web acquisition",
    }
)
# Runtime capability states (MASTER section 22). Not stored in the
# manifest; exposed here so every subsystem uses the same vocabulary.
CAPABILITY_STATES = ("READY", "LIMITED", "UNAVAILABLE", "UNKNOWN")

# Fields every tool entry must carry (MASTER section 24 + stable id).
REQUIRED_TOOL_FIELDS = (
    "id",
    "tool",
    "purpose",
    "required",
    "supported_platforms",
    "min_version",
    "preferred_version",
    "detection_method",
    "executable",
    "dependencies",
    "installation_method",
    "install_command",
    "health_check",
    "capability",
)
OPTIONAL_TOOL_FIELDS = ("notes",)
ALLOWED_TOOL_FIELDS = frozenset(REQUIRED_TOOL_FIELDS) | frozenset(OPTIONAL_TOOL_FIELDS)

# Keys that would amount to asserting installation state — forbidden.
FORBIDDEN_STATE_KEYS = frozenset({"installed", "version", "status", "state", "path"})

_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class ManifestError(Exception):
    """Raised when the manifest is missing, unparseable, or invalid."""


def _err(where: str, message: str) -> ManifestError:
    return ManifestError(f"tool manifest: {where}: {message}")


def _check_optional_str(value: Any, where: str, field: str) -> None:
    if value is not None and not isinstance(value, str):
        raise _err(where, f"field '{field}' must be a string or null, got {type(value).__name__}")


def _check_str_list(value: Any, where: str, field: str) -> None:
    if not isinstance(value, list):
        raise _err(where, f"field '{field}' must be a list, got {type(value).__name__}")
    for item in value:
        if not isinstance(item, str):
            raise _err(where, f"field '{field}' must contain only strings")
    if len(set(value)) != len(value):
        raise _err(where, f"field '{field}' must not contain duplicates")


def _validate_tool(entry: Any, index: int, seen_ids: set[str]) -> None:
    where = f"tools[{index}]"
    if not isinstance(entry, dict):
        raise _err(where, f"tool entry must be an object, got {type(entry).__name__}")

    tool_id = entry.get("id")
    if isinstance(tool_id, str):
        where = f"tools[{index}] ({tool_id})"

    missing = [field for field in REQUIRED_TOOL_FIELDS if field not in entry]
    if missing:
        raise _err(where, f"missing required field(s): {', '.join(missing)}")

    forbidden = [key for key in entry if key in FORBIDDEN_STATE_KEYS]
    if forbidden:
        raise _err(
            where,
            f"field(s) {', '.join(sorted(forbidden))} assert installation state; "
            "the manifest may only describe how to detect, never the result",
        )

    unknown = [key for key in entry if key not in ALLOWED_TOOL_FIELDS]
    if unknown:
        raise _err(where, f"unknown field(s): {', '.join(sorted(unknown))}")

    if not isinstance(tool_id, str) or not _ID_PATTERN.match(tool_id):
        raise _err(where, f"id must be a lowercase kebab-case string, got {tool_id!r}")
    if tool_id in seen_ids:
        raise _err(where, f"duplicate tool id '{tool_id}'")
    seen_ids.add(tool_id)

    for field in ("tool", "purpose"):
        value = entry[field]
        if not isinstance(value, str) or not value.strip():
            raise _err(where, f"field '{field}' must be a non-empty string")

    if entry["required"] not in REQUIRED_VALUES:
        raise _err(
            where,
            f"field 'required' must be one of {sorted(REQUIRED_VALUES)}, "
            f"got {entry['required']!r}",
        )

    platforms = entry["supported_platforms"]
    _check_str_list(platforms, where, "supported_platforms")
    if not platforms:
        raise _err(where, "field 'supported_platforms' must not be empty")
    for platform in platforms:
        if platform not in SUPPORTED_PLATFORMS:
            raise _err(
                where,
                f"unsupported platform {platform!r}; "
                f"allowed: {', '.join(sorted(SUPPORTED_PLATFORMS))}",
            )

    _check_optional_str(entry["min_version"], where, "min_version")
    _check_optional_str(entry["preferred_version"], where, "preferred_version")

    if entry["detection_method"] not in DETECTION_METHODS:
        raise _err(
            where,
            f"field 'detection_method' must be one of {sorted(DETECTION_METHODS)}, "
            f"got {entry['detection_method']!r}",
        )
    _check_optional_str(entry["executable"], where, "executable")
    if entry["detection_method"] in {"command", "python_module"} and not entry["executable"]:
        raise _err(where, f"detection_method '{entry['detection_method']}' requires an executable")

    _check_str_list(entry["dependencies"], where, "dependencies")
    _check_optional_str(entry["installation_method"], where, "installation_method")
    _check_optional_str(entry["install_command"], where, "install_command")
    _check_optional_str(entry["health_check"], where, "health_check")

    _check_str_list(entry["capability"], where, "capability")
    for capability in entry["capability"]:
        if capability not in CAPABILITIES:
            raise _err(
                where,
                f"unknown capability {capability!r}; allowed: "
                f"{', '.join(sorted(CAPABILITIES))}",
            )

    if "notes" in entry:
        _check_optional_str(entry["notes"], where, "notes")


def validate_capability_state(state: Any) -> str:
    """Validate a runtime capability state (MASTER section 22)."""
    if state not in CAPABILITY_STATES:
        raise ManifestError(
            f"tool manifest: invalid capability state {state!r}; "
            f"allowed: {', '.join(CAPABILITY_STATES)}"
        )
    return state


def validate_manifest(data: Any) -> dict[str, Any]:
    """Validate an already-parsed manifest document. Returns it on success."""
    if not isinstance(data, dict):
        raise _err("<document>", f"manifest must be an object, got {type(data).__name__}")

    for field in ("schema_version", "tools"):
        if field not in data:
            raise _err("<document>", f"missing required field '{field}'")
    unknown = [key for key in data if key not in {"schema_version", "tools"}]
    if unknown:
        raise _err("<document>", f"unknown field(s): {', '.join(sorted(unknown))}")

    if not isinstance(data["schema_version"], str):
        raise _err("<document>", "field 'schema_version' must be a string")
    tools = data["tools"]
    if not isinstance(tools, list) or not tools:
        raise _err("<document>", "field 'tools' must be a non-empty list")

    seen_ids: set[str] = set()
    for index, entry in enumerate(tools):
        _validate_tool(entry, index, seen_ids)

    for entry in tools:
        for dependency in entry["dependencies"]:
            if dependency not in seen_ids:
                raise _err(
                    f"tools ({entry['id']})",
                    f"dependency '{dependency}' does not match any tool id in the manifest",
                )

    return data


def load_manifest(path: str | Path | None = None) -> dict[str, Any]:
    """Load and validate the tool manifest.

    Raises:
        ManifestError: file missing, invalid JSON, or schema violation.
    """
    manifest_path = Path(path) if path is not None else DEFAULT_MANIFEST_PATH
    if not manifest_path.is_file():
        raise _err(str(manifest_path), "manifest file not found")
    try:
        raw = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _err(str(manifest_path), f"cannot read manifest: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise _err(str(manifest_path), f"invalid JSON: {exc}") from exc
    return validate_manifest(data)


def tool_ids(manifest: dict[str, Any] | None = None) -> list[str]:
    """Return the ordered list of tool ids from the manifest."""
    data = manifest if manifest is not None else load_manifest()
    return [entry["id"] for entry in data["tools"]]


if __name__ == "__main__":
    loaded = load_manifest()
    print(f"tool manifest OK: {len(loaded['tools'])} tools: {', '.join(tool_ids(loaded))}")
