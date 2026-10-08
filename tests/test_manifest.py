"""Tests for the tool manifest schema, content and loader (T-0201)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from src.core import manifest as manifest_mod
from src.core.manifest import (
    CAPABILITY_STATES,
    DEFAULT_MANIFEST_PATH,
    DEFAULT_SCHEMA_PATH,
    REQUIRED_TOOL_FIELDS,
    ManifestError,
    load_manifest,
    tool_ids,
    validate_capability_state,
)

EXPECTED_TOOL_IDS = [
    "git",
    "python",
    "jupyter",
    "taiga-s1",
    "freecad",
    "kicad",
    "ngspice",
    "gazebo",
    "blender",
    "rea",
    "scrapling",
]


@pytest.fixture()
def real_manifest() -> dict[str, Any]:
    return load_manifest()


@pytest.fixture()
def tmp_manifest(tmp_path: Path, real_manifest: dict[str, Any]):
    """Write a (mutated) manifest to a temp file and return its path."""

    def write(data: dict[str, Any]) -> Path:
        path = tmp_path / "tool-manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    return write


def test_real_manifest_loads(real_manifest: dict[str, Any]) -> None:
    assert tool_ids(real_manifest) == EXPECTED_TOOL_IDS


def test_all_eleven_required_tools_present(real_manifest: dict[str, Any]) -> None:
    assert len(real_manifest["tools"]) == 11


def test_schema_and_loader_agree_on_required_fields() -> None:
    schema = json.loads(DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_required = set(schema["definitions"]["tool"]["required"])
    assert schema_required == set(REQUIRED_TOOL_FIELDS)


def test_schema_and_loader_agree_on_enums() -> None:
    schema = json.loads(DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8"))
    props = schema["definitions"]["tool"]["properties"]
    assert set(props["required"]["enum"]) == manifest_mod.REQUIRED_VALUES
    assert set(props["detection_method"]["enum"]) == manifest_mod.DETECTION_METHODS
    assert set(props["supported_platforms"]["items"]["enum"]) == manifest_mod.SUPPORTED_PLATFORMS
    assert set(props["capability"]["items"]["enum"]) == manifest_mod.CAPABILITIES


def test_entries_never_assert_installation_state(real_manifest: dict[str, Any]) -> None:
    for entry in real_manifest["tools"]:
        for key in entry:
            assert key not in manifest_mod.FORBIDDEN_STATE_KEYS, (
                f"{entry['id']}: key '{key}' would assert installation state"
            )


def test_versions_are_string_or_null_only(real_manifest: dict[str, Any]) -> None:
    for entry in real_manifest["tools"]:
        for field in ("min_version", "preferred_version"):
            value = entry[field]
            assert value is None or isinstance(value, str), f"{entry['id']}.{field}"


def test_every_entry_has_purpose_and_justification(real_manifest: dict[str, Any]) -> None:
    for entry in real_manifest["tools"]:
        assert entry["tool"].strip()
        assert entry["purpose"].strip()
        if entry["min_version"] is not None or entry["preferred_version"] is not None:
            assert entry.get("notes"), f"{entry['id']}: version choices must be justified"


def test_loader_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ManifestError, match="not found"):
        load_manifest(tmp_path / "absent.json")


def test_loader_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ManifestError, match="invalid JSON"):
        load_manifest(path)


def test_rejects_missing_field(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    del data["tools"][0]["purpose"]
    with pytest.raises(ManifestError, match="missing required field.*purpose"):
        load_manifest(tmp_manifest(data))


def test_rejects_bad_type(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    data["tools"][0]["min_version"] = 123
    with pytest.raises(ManifestError, match="min_version.*string or null"):
        load_manifest(tmp_manifest(data))


def test_rejects_unsupported_required_value(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    data["tools"][0]["required"] = "maybe"
    with pytest.raises(ManifestError, match="field 'required' must be one of"):
        load_manifest(tmp_manifest(data))


def test_rejects_unsupported_platform(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    data["tools"][0]["supported_platforms"] = ["beos"]
    with pytest.raises(ManifestError, match="unsupported platform 'beos'"):
        load_manifest(tmp_manifest(data))


def test_rejects_invalid_capability(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    data["tools"][0]["capability"] = ["time travel"]
    with pytest.raises(ManifestError, match="unknown capability 'time travel'"):
        load_manifest(tmp_manifest(data))


def test_rejects_duplicate_ids(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    data["tools"].append(copy.deepcopy(data["tools"][0]))
    with pytest.raises(ManifestError, match="duplicate tool id 'git'"):
        load_manifest(tmp_manifest(data))


def test_rejects_dangling_dependency(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    data["tools"][0]["dependencies"] = ["nonexistent-tool"]
    with pytest.raises(ManifestError, match="dependency 'nonexistent-tool' does not match"):
        load_manifest(tmp_manifest(data))


def test_rejects_unknown_field(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    data["tools"][0]["install_state"] = "present"
    with pytest.raises(ManifestError, match="unknown field.*install_state"):
        load_manifest(tmp_manifest(data))


def test_rejects_asserted_installation_state(tmp_manifest, real_manifest) -> None:
    data = copy.deepcopy(real_manifest)
    data["tools"][0]["installed"] = True
    with pytest.raises(ManifestError, match="assert installation state"):
        load_manifest(tmp_manifest(data))


def test_rejects_non_object_document(tmp_manifest) -> None:
    with pytest.raises(ManifestError, match="must be an object"):
        load_manifest(tmp_manifest(["not", "a", "manifest"]))


def test_capability_state_vocabulary_is_exact() -> None:
    assert set(CAPABILITY_STATES) == {"READY", "LIMITED", "UNAVAILABLE", "UNKNOWN"}
    assert validate_capability_state("READY") == "READY"
    assert validate_capability_state("UNKNOWN") == "UNKNOWN"
    for bad in ("ready", "BROKEN", "", None, 3):
        with pytest.raises(ManifestError, match="invalid capability state"):
            validate_capability_state(bad)


def test_default_manifest_path_exists() -> None:
    assert DEFAULT_MANIFEST_PATH.is_file()
    assert DEFAULT_SCHEMA_PATH.is_file()
