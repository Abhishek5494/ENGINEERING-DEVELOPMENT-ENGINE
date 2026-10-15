"""Tests for the storage preflight utility and workspace config (T-1800)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core import storage
from src.core.storage import (
    DEFAULT_MIN_FREE_BYTES,
    DiskUsage,
    InsufficientStorageError,
    StorageCheck,
    StorageError,
    check_storage,
    development_root,
    disk_usage,
    drive_of,
    format_bytes,
    free_bytes,
    load_storage_config,
    location,
    preflight,
    require_storage,
)

GIB = 1024**3

EXPECTED_LOCATIONS = {
    "project",
    "environments",
    "pip_cache",
    "npm_cache",
    "huggingface_home",
    "temp",
    "builds",
    "test_artifacts",
    "logs",
    "models",
    "datasets",
    "packages",
    "downloads",
    "backups",
}

EXPECTED_OPERATIONS = {
    "dependency_install",
    "model_download",
    "build",
    "dataset_extraction",
    "large_test_run",
    "container_image",
    "vm_create",
}


def test_storage_config_exists_and_is_wellformed() -> None:
    data = load_storage_config()
    assert data["schema_version"] == "1.0"
    assert data["development_root"]
    assert set(data["locations"]) == EXPECTED_LOCATIONS
    assert set(data["operations"]) == EXPECTED_OPERATIONS
    for spec in data["operations"].values():
        assert spec["min_free_bytes"] > 0
        assert spec.get("required_bytes", 0) >= 0
        assert spec["description"].strip()


def test_operations_do_not_use_one_universal_threshold() -> None:
    ops = load_storage_config()["operations"]
    thresholds = {spec["min_free_bytes"] for spec in ops.values()}
    assert len(thresholds) > 1, "operations must not share a single threshold"
    assert ops["vm_create"]["min_free_bytes"] > ops["large_test_run"]["min_free_bytes"]


def test_location_resolves_under_development_root() -> None:
    data = load_storage_config()
    root = development_root(data)
    assert location("pip_cache", data) == root / "caches" / "pip"
    assert location("huggingface_home", data) == root / "models" / "huggingface"


def test_unknown_location_raises() -> None:
    with pytest.raises(StorageError, match="unknown storage location"):
        location("no-such-location")


def test_development_root_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(storage.DEVELOPMENT_ROOT_ENV, str(tmp_path))
    assert development_root() == tmp_path


def test_load_storage_config_missing_file_returns_defaults(tmp_path: Path) -> None:
    data = load_storage_config(tmp_path / "absent.json")
    assert data["development_root"]
    assert data["min_free_bytes_default"] == DEFAULT_MIN_FREE_BYTES


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0 B"),
        (512, "512 B"),
        (1024, "1.00 KiB"),
        (GIB, "1.00 GiB"),
        (2 * GIB + 512 * 1024**2, "2.50 GiB"),
    ],
)
def test_format_bytes(value: int, expected: str) -> None:
    assert format_bytes(value) == expected


def test_disk_usage_and_drive_of(tmp_path: Path) -> None:
    usage = disk_usage(tmp_path)
    assert isinstance(usage, DiskUsage)
    assert usage.total_bytes > 0
    assert 0 <= usage.free_bytes <= usage.total_bytes
    assert drive_of(tmp_path)


def test_disk_usage_non_existing_path_walks_to_ancestor(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b" / "c"
    usage = disk_usage(deep)
    assert usage.free_bytes == free_bytes(tmp_path)


def test_check_storage_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 10 * GIB)
    check = check_storage("demo", min_free_bytes=2 * GIB)
    assert check.ok
    assert check.shortfall_bytes == 0
    assert "OK" in check.message


def test_check_storage_blocked_reports_drive_and_shortfall(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 1 * GIB)
    check = check_storage("demo", min_free_bytes=3 * GIB)
    assert not check.ok
    assert check.shortfall_bytes == 2 * GIB
    assert "BLOCKED" in check.message
    assert check.drive in check.message
    assert check.needed_bytes == 3 * GIB


def test_check_storage_counts_required_and_margin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 5 * GIB)
    check = check_storage(
        "demo", min_free_bytes=1 * GIB, required_bytes=3 * GIB, margin_bytes=2 * GIB
    )
    assert not check.ok
    assert check.needed_bytes == 6 * GIB
    assert check.shortfall_bytes == 1 * GIB


def test_check_storage_rejects_negative_amounts() -> None:
    with pytest.raises(StorageError, match="non-negative"):
        check_storage("demo", required_bytes=-1)


def test_storage_check_to_dict_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 8 * GIB)
    check = check_storage("demo", min_free_bytes=1 * GIB)
    as_dict = check.to_dict()
    assert as_dict["ok"] is True
    assert json.loads(json.dumps(as_dict)) == as_dict


def test_preflight_uses_operation_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 3 * GIB)
    assert preflight("large_test_run").ok is True
    assert preflight("vm_create").ok is False


def test_preflight_unknown_operation_raises() -> None:
    with pytest.raises(StorageError, match="unknown operation"):
        preflight("teleport")


def test_require_storage_raises_with_check(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 1 * GIB)
    with pytest.raises(InsufficientStorageError) as excinfo:
        require_storage("vm_create")
    assert isinstance(excinfo.value.check, StorageCheck)
    assert excinfo.value.check.ok is False


def test_require_storage_returns_check_when_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 100 * GIB)
    check = require_storage("vm_create")
    assert check.ok


def test_cli_preflight_ok(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 100 * GIB)
    code = storage.main(["preflight", "large_test_run", "--path", str(tmp_path)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True


def test_cli_preflight_blocked(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(storage, "free_bytes", lambda _p: 1 * GIB)
    code = storage.main(["preflight", "vm_create", "--path", str(tmp_path)])
    assert code == 3
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is False
