"""Tests for manifest-driven tool detection and capability states (T-0102)."""

from __future__ import annotations

import json
import subprocess
from typing import Any

import pytest

from src.core.manifest import CAPABILITIES, load_manifest
from src.pem import tools as tools_mod
from src.pem.tools import capability_states, detect_tools


def _entry(
    tool_id: str,
    *,
    detection_method: str = "command",
    executable: str = "tool",
    health_check: str | None = "tool --version",
    capability: list[str] | None = None,
    min_version: str | None = None,
) -> dict[str, Any]:
    return {
        "id": tool_id,
        "tool": tool_id,
        "purpose": "test entry",
        "required": "optional",
        "supported_platforms": ["windows"],
        "min_version": min_version,
        "preferred_version": None,
        "detection_method": detection_method,
        "executable": executable,
        "dependencies": [],
        "installation_method": None,
        "health_check": health_check,
        "capability": capability or [],
    }


def _completed(rc: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["probe"], returncode=rc, stdout=stdout, stderr=stderr)


def _patch_run(monkeypatch: pytest.MonkeyPatch, fake) -> None:
    monkeypatch.setattr(tools_mod.subprocess, "run", fake)


# ---- per-tool probe behaviour -------------------------------------------


def test_probe_detected_with_version(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(0, stdout="git version 2.55.0.windows.3"))
    record = tools_mod._probe_tool(_entry("git"))
    assert record["state"] == "DETECTED"
    assert record["version"] == "2.55.0"
    assert record["evidence"] == "OBSERVED"
    assert record["health_ok"] is True
    assert record["probe"] == "tool --version"


def test_probe_missing_executable_is_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_missing(*args: Any, **kwargs: Any) -> Any:
        raise FileNotFoundError("no such executable")

    _patch_run(monkeypatch, raise_missing)
    record = tools_mod._probe_tool(_entry("freecad"))
    assert record["state"] == "NOT_FOUND"
    assert record["evidence"] == "OBSERVED"
    assert "not found on PATH" in record["reason"]


def test_probe_timeout_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_timeout(*args: Any, **kwargs: Any) -> Any:
        raise subprocess.TimeoutExpired(cmd="tool", timeout=15)

    _patch_run(monkeypatch, raise_timeout)
    record = tools_mod._probe_tool(_entry("slow-tool"))
    assert record["state"] == "UNKNOWN"
    assert record["evidence"] == "UNKNOWN"
    assert "timed out" in record["reason"]


def test_probe_oserror_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_oserror(*args: Any, **kwargs: Any) -> Any:
        raise PermissionError("denied")

    _patch_run(monkeypatch, raise_oserror)
    record = tools_mod._probe_tool(_entry("tool"))
    assert record["state"] == "UNKNOWN"
    assert record["evidence"] == "UNKNOWN"


def test_probe_nonzero_without_version_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(3, stderr="something odd happened"))
    record = tools_mod._probe_tool(_entry("tool"))
    assert record["state"] == "UNKNOWN"
    assert record["evidence"] == "UNKNOWN"
    assert record["version"] == "UNKNOWN"
    assert "inconclusive" in record["reason"]


def test_probe_nonzero_with_version_marks_health_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(2, stdout="tool v1.2.3 (broken)"))
    record = tools_mod._probe_tool(_entry("tool"))
    assert record["state"] == "DETECTED"
    assert record["version"] == "1.2.3"
    assert record["health_ok"] is False


def test_python_module_absent_is_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_run(
        monkeypatch,
        lambda *a, **k: _completed(
            1, stderr="ModuleNotFoundError: No module named 'scrapling'"
        ),
    )
    record = tools_mod._probe_tool(
        _entry(
            "scrapling",
            detection_method="python_module",
            health_check='python -c "import scrapling; print(scrapling.__version__)"',
        )
    )
    assert record["state"] == "NOT_FOUND"
    assert record["evidence"] == "OBSERVED"


def test_detection_none_is_unknown_without_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    def must_not_run(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("probe must not run for detection_method 'none'")

    _patch_run(monkeypatch, must_not_run)
    record = tools_mod._probe_tool(
        _entry("taiga-s1", detection_method="none", executable=None, health_check=None)
    )
    assert record["state"] == "UNKNOWN"
    assert record["evidence"] == "UNKNOWN"
    assert record["probe"] is None
    assert "not implemented" in record["reason"]


def test_version_extracted_only_from_output(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(0, stdout="no digits here"))
    record = tools_mod._probe_tool(_entry("tool"))
    assert record["state"] == "DETECTED"
    assert record["version"] == "UNKNOWN"


# ---- detect_tools --------------------------------------------------------


def test_detect_tools_covers_whole_manifest_and_is_json_safe() -> None:
    records = detect_tools()
    manifest = load_manifest()
    assert [r["id"] for r in records] == [t["id"] for t in manifest["tools"]]
    json.dumps(records)


def test_detect_tools_accepts_injected_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(0, stdout="tool 9.9.9"))
    records = detect_tools({"tools": [_entry("a"), _entry("b")]})
    assert len(records) == 2
    assert all(r["state"] == "DETECTED" for r in records)


def test_detected_requires_probe_evidence() -> None:
    for record in detect_tools():
        if record["state"] == "DETECTED":
            assert record["evidence"] == "OBSERVED"
            assert record["probe"] is not None
        if record["state"] == "UNKNOWN":
            assert record["evidence"] == "UNKNOWN"


def test_real_host_finds_git_and_python() -> None:
    records = {r["id"]: r for r in detect_tools()}
    assert records["git"]["state"] == "DETECTED", records["git"]
    assert records["git"]["version"] != "UNKNOWN"
    assert records["python"]["state"] == "DETECTED", records["python"]
    assert records["python"]["version"] != "UNKNOWN"


# ---- capability aggregation ---------------------------------------------


def _record(
    tool_id: str,
    state: str,
    *,
    capabilities: list[str],
    health_ok: bool | None = True,
    version: str = "3.0.0",
    min_version: str | None = None,
) -> dict[str, Any]:
    return {
        "id": tool_id,
        "state": state,
        "version": version,
        "executable_path": "/usr/bin/tool",
        "evidence": "OBSERVED" if state != "UNKNOWN" else "UNKNOWN",
        "probe": "tool --version",
        "reason": "test",
        "health_ok": health_ok,
        "capability": capabilities,
        "min_version": min_version,
    }


def test_capability_rules_ready() -> None:
    states = capability_states([_record("a", "DETECTED", capabilities=["CAD"])])
    assert states["CAD"] == "READY"


def test_capability_rules_limited_on_failed_health() -> None:
    states = capability_states(
        [_record("a", "DETECTED", capabilities=["CAD"], health_ok=False)]
    )
    assert states["CAD"] == "LIMITED"


def test_capability_rules_limited_on_version_below_minimum() -> None:
    states = capability_states(
        [
            _record(
                "a",
                "DETECTED",
                capabilities=["CAD"],
                version="1.0",
                min_version="2.0",
            )
        ]
    )
    assert states["CAD"] == "LIMITED"


def test_capability_rules_unknown_on_inconclusive_probe() -> None:
    states = capability_states([_record("a", "UNKNOWN", capabilities=["CAD"])])
    assert states["CAD"] == "UNKNOWN"


def test_capability_rules_unavailable_when_all_absent() -> None:
    states = capability_states(
        [
            _record("a", "NOT_FOUND", capabilities=["CAD"]),
            _record("b", "NOT_FOUND", capabilities=["CAD"]),
        ]
    )
    assert states["CAD"] == "UNAVAILABLE"


def test_capability_rules_ready_beats_unknown_sibling() -> None:
    states = capability_states(
        [
            _record("a", "DETECTED", capabilities=["CAD"]),
            _record("b", "UNKNOWN", capabilities=["CAD"]),
        ]
    )
    assert states["CAD"] == "READY"


def test_capability_rules_limited_beats_unknown_sibling() -> None:
    states = capability_states(
        [
            _record("a", "DETECTED", capabilities=["CAD"], health_ok=False),
            _record("b", "UNKNOWN", capabilities=["CAD"]),
        ]
    )
    assert states["CAD"] == "LIMITED"


def test_capability_rules_unknown_when_no_providers() -> None:
    states = capability_states([_record("a", "DETECTED", capabilities=[])])
    assert set(states.keys()) == set(CAPABILITIES)
    assert all(state in {"READY", "LIMITED", "UNAVAILABLE", "UNKNOWN"} for state in states.values())
    assert states["CAD"] == "UNKNOWN"


def test_capability_states_on_real_manifest_are_valid() -> None:
    states = capability_states(detect_tools())
    assert set(states.keys()) == set(CAPABILITIES)
    for state in states.values():
        tools_mod.validate_capability_state(state)
