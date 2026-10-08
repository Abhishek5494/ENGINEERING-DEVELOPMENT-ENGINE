"""Tests for PEM system/hardware detection (T-0101).

Covers: real detection on this host, JSON serializability, UNKNOWN
handling for failing detectors, and the no-empty-string rule.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import pytest

from src.pem import detect as detect_mod
from src.pem.detect import SYSTEM_KEYS, detect_system

VALID_EVIDENCE = {"OBSERVED", "UNKNOWN"}


def _walk_values(node: Any):
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_values(item)
    else:
        yield node


@pytest.fixture(scope="module")
def system_record() -> dict[str, Any]:
    return detect_system()


def test_required_keys_exact(system_record: dict[str, Any]) -> None:
    assert tuple(system_record.keys()) == SYSTEM_KEYS


def test_fields_have_value_and_valid_evidence(system_record: dict[str, Any]) -> None:
    for key, field in system_record.items():
        assert set(field.keys()) == {"value", "evidence"}, key
        assert field["evidence"] in VALID_EVIDENCE, key
        if field["evidence"] == "UNKNOWN":
            assert field["value"] == "UNKNOWN", key
        else:
            assert field["value"] != "UNKNOWN", key


def test_runs_on_this_host_and_detects_basics(system_record: dict[str, Any]) -> None:
    assert system_record["os_name"]["evidence"] == "OBSERVED"
    assert system_record["os_name"]["value"] in {"Windows", "Linux", "Darwin"}
    assert system_record["architecture"]["evidence"] == "OBSERVED"
    assert system_record["ram_bytes"]["evidence"] == "OBSERVED"
    assert isinstance(system_record["ram_bytes"]["value"], int)
    assert system_record["ram_bytes"]["value"] > 0
    if sys.platform == "win32":
        assert system_record["os_version"]["evidence"] == "OBSERVED"
        assert system_record["os_version"]["value"] != "UNKNOWN"


def test_json_serializable(system_record: dict[str, Any]) -> None:
    encoded = json.dumps(system_record)
    assert json.loads(encoded) == system_record


def test_no_empty_string_values(system_record: dict[str, Any]) -> None:
    for value in _walk_values(system_record):
        assert value != "", "empty string is not an acceptable value (use UNKNOWN)"


def test_no_empty_list_values(system_record: dict[str, Any]) -> None:
    for key, field in system_record.items():
        if field["evidence"] == "OBSERVED" and key in {"storage", "gpu"}:
            assert isinstance(field["value"], list) and len(field["value"]) > 0, key


def test_detector_failure_maps_to_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom() -> Any:
        raise RuntimeError("detector exploded")

    monkeypatch.setattr(detect_mod, "_detect_gpu", boom)
    monkeypatch.setattr(detect_mod, "_detect_ram_bytes", lambda: None)
    record = detect_mod.detect_system()
    assert record["gpu"] == {"value": "UNKNOWN", "evidence": "UNKNOWN"}
    assert record["ram_bytes"] == {"value": "UNKNOWN", "evidence": "UNKNOWN"}


def test_empty_collection_maps_to_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(detect_mod, "_detect_gpu", lambda: [])
    monkeypatch.setattr(detect_mod, "_detect_storage", lambda: [])
    record = detect_mod.detect_system()
    assert record["gpu"]["value"] == "UNKNOWN"
    assert record["storage"]["value"] == "UNKNOWN"


def test_detect_system_never_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom() -> Any:
        raise KeyboardInterrupt  # only SystemExit/BaseException subclasses slip through

    monkeypatch.setattr(detect_mod, "_detect_os_name", boom)
    with pytest.raises(KeyboardInterrupt):
        # document the exception policy: ordinary Exception is swallowed,
        # BaseException (e.g. Ctrl-C) propagates — detection must stay interruptible
        detect_mod.detect_system()
