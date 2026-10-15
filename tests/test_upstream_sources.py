"""Tests for the canonical upstream-source registry (T-0203)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest

from src.core.manifest import tool_ids
from src.core.upstream import (
    DEFAULT_REGISTRY_PATH,
    DEFAULT_SCHEMA_PATH,
    INTEGRATION_STATUSES,
    REQUIRED_SOURCE_FIELDS,
    SOURCE_TYPES,
    VERIFICATION_STATUSES,
    UpstreamRegistryError,
    get_source,
    load_upstream_sources,
    source_ids,
)

EXPECTED_SOURCE_IDS = [
    "taiga-s1",
    "scrapling",
    "rea",
    "freecad",
    "kicad",
    "ngspice",
    "python",
    "jupyter",
    "gazebo",
    "blender",
    "git",
]


@pytest.fixture()
def real_registry() -> dict[str, Any]:
    return load_upstream_sources()


@pytest.fixture()
def tmp_registry(tmp_path: Path, real_registry: dict[str, Any]):
    """Write a (mutated) registry to a temp file and return its path."""

    def write(data: dict[str, Any]) -> Path:
        path = tmp_path / "upstream-sources.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    return write


def test_real_registry_loads(real_registry: dict[str, Any]) -> None:
    assert source_ids(real_registry) == EXPECTED_SOURCE_IDS


def test_all_eleven_sources_present(real_registry: dict[str, Any]) -> None:
    assert len(real_registry["sources"]) == 11


def test_schema_and_loader_agree_on_required_fields() -> None:
    schema = json.loads(DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_required = set(schema["definitions"]["source"]["required"])
    assert schema_required == set(REQUIRED_SOURCE_FIELDS)


def test_schema_and_loader_agree_on_enums() -> None:
    schema = json.loads(DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8"))
    props = schema["definitions"]["source"]["properties"]
    assert set(props["source_type"]["enum"]) == SOURCE_TYPES
    assert set(props["license_status"]["enum"]) == VERIFICATION_STATUSES
    assert set(props["version_status"]["enum"]) == VERIFICATION_STATUSES
    assert set(props["integration_status"]["enum"]) == INTEGRATION_STATUSES


def test_every_repository_url_is_https(real_registry: dict[str, Any]) -> None:
    for entry in real_registry["sources"]:
        url = entry["repository_url"]
        parts = urlsplit(url)
        assert parts.scheme == "https" and parts.netloc, f"{entry['id']}: {url!r}"


def test_documentation_url_is_null_or_https(real_registry: dict[str, Any]) -> None:
    for entry in real_registry["sources"]:
        url = entry["documentation_url"]
        if url is not None:
            parts = urlsplit(url)
            assert parts.scheme == "https" and parts.netloc, f"{entry['id']}: {url!r}"


def test_source_ids_are_unique(real_registry: dict[str, Any]) -> None:
    ids = source_ids(real_registry)
    assert len(ids) == len(set(ids))


def test_registry_covers_every_manifest_tool(real_registry: dict[str, Any]) -> None:
    """The registry and the tool manifest describe the same 11 ids."""
    assert set(source_ids(real_registry)) == set(tool_ids())


def test_every_entry_has_name_and_purpose(real_registry: dict[str, Any]) -> None:
    for entry in real_registry["sources"]:
        assert entry["name"].strip()
        assert entry["purpose"].strip()


def test_unknown_statuses_carry_no_claims(real_registry: dict[str, Any]) -> None:
    """UNKNOWN must never be accompanied by an invented license/version/commit."""
    for entry in real_registry["sources"]:
        if entry["license_status"] == "UNKNOWN":
            assert entry.get("license") is None, f"{entry['id']}: license claimed while UNKNOWN"
        if entry["version_status"] == "UNKNOWN":
            assert entry.get("version") is None, f"{entry['id']}: version claimed while UNKNOWN"
            assert entry.get("commit") is None, f"{entry['id']}: commit claimed while UNKNOWN"


def test_get_source_returns_entry(real_registry: dict[str, Any]) -> None:
    assert get_source("taiga-s1", real_registry)["id"] == "taiga-s1"


def test_get_source_unknown_id(real_registry: dict[str, Any]) -> None:
    with pytest.raises(UpstreamRegistryError, match="no source with id"):
        get_source("does-not-exist", real_registry)


def test_loader_missing_file(tmp_path: Path) -> None:
    with pytest.raises(UpstreamRegistryError, match="not found"):
        load_upstream_sources(tmp_path / "absent.json")


def test_loader_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(UpstreamRegistryError, match="invalid JSON"):
        load_upstream_sources(path)


def test_rejects_missing_field(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    del data["sources"][0]["purpose"]
    with pytest.raises(UpstreamRegistryError, match="missing required field.*purpose"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_non_https_repository_url(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    data["sources"][0]["repository_url"] = "http://github.com/x/y"
    with pytest.raises(UpstreamRegistryError, match="repository_url"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_non_https_documentation_url(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    data["sources"][0]["documentation_url"] = "ftp://example.invalid/docs"
    with pytest.raises(UpstreamRegistryError, match="documentation_url"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_duplicate_ids(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    data["sources"].append(copy.deepcopy(data["sources"][0]))
    with pytest.raises(UpstreamRegistryError, match="duplicate source id 'taiga-s1'"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_unknown_field(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    data["sources"][0]["installed"] = True
    with pytest.raises(UpstreamRegistryError, match="unknown field.*installed"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_bad_source_type(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    data["sources"][0]["source_type"] = "magic"
    with pytest.raises(UpstreamRegistryError, match="source_type"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_bad_integration_status(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    data["sources"][0]["integration_status"] = "DONE"
    with pytest.raises(UpstreamRegistryError, match="integration_status"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_unknown_status_with_claimed_license(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    entry = next(e for e in data["sources"] if e["id"] == "scrapling")
    entry["license"] = "MIT"
    with pytest.raises(UpstreamRegistryError, match="license must be null"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_unknown_status_with_claimed_version(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    data["sources"][0]["version"] = "1.2.3"
    with pytest.raises(UpstreamRegistryError, match="version/commit must be null"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_verified_status_without_value(tmp_registry, real_registry) -> None:
    data = copy.deepcopy(real_registry)
    entry = next(e for e in data["sources"] if e["id"] == "scrapling")
    entry["license_status"] = "VERIFIED"
    with pytest.raises(UpstreamRegistryError, match="VERIFIED requires"):
        load_upstream_sources(tmp_registry(data))


def test_rejects_non_object_document(tmp_registry) -> None:
    with pytest.raises(UpstreamRegistryError, match="must be an object"):
        load_upstream_sources(tmp_registry(["not", "a", "registry"]))


def test_default_paths_exist() -> None:
    assert DEFAULT_REGISTRY_PATH.is_file()
    assert DEFAULT_SCHEMA_PATH.is_file()


def test_module_constants_are_exact() -> None:
    assert SOURCE_TYPES == {"core-integration", "specialist-tool", "version-control"}
    assert VERIFICATION_STATUSES == {"VERIFIED", "UNVERIFIED", "UNKNOWN"}
    assert INTEGRATION_STATUSES == {
        "COMPLETE",
        "PARTIAL",
        "PLANNED",
        "BLOCKED",
        "NOT_INTEGRATED",
        "UNKNOWN",
    }
