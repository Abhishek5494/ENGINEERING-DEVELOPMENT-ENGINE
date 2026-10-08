"""Tests for environment report generation (T-0103, MASTER §25)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from src.pem.detect import detect_system
from src.pem.report import (
    JSON_FILENAME,
    LOW_DISK_THRESHOLD_BYTES,
    MARKDOWN_FILENAME,
    REPO_ROOT,
    REPORT_KEYS,
    build_environment,
    render_markdown,
    write_reports,
)
from src.pem.tools import capability_states, detect_tools

SCHEMA_PATH = REPO_ROOT / "config" / "environment-report.schema.json"


def _check(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum")
    declared = schema.get("type")
    if declared is not None:
        allowed = [declared] if isinstance(declared, str) else declared
        checks = {
            "string": lambda v: isinstance(v, str),
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "null": lambda v: v is None,
        }
        if not any(checks[name](instance) for name in allowed):
            errors.append(f"{path}: type {type(instance).__name__} not in {allowed}")
            return errors
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required key {key!r}")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(_check(value, properties[key], f"{path}.{key}"))
            else:
                extra = schema.get("additionalProperties", True)
                if extra is False:
                    errors.append(f"{path}: unexpected key {key!r}")
                elif isinstance(extra, dict):
                    errors.extend(_check(value, extra, f"{path}.{key}"))
    if isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            errors.extend(_check(item, schema["items"], f"{path}[{index}]"))
    if isinstance(instance, str) and len(instance) < schema.get("minLength", 0):
        errors.append(f"{path}: string shorter than minLength")
    return errors


def _field(value: Any) -> dict[str, Any]:
    return {"value": value, "evidence": "OBSERVED"}


@pytest.fixture()
def system() -> dict[str, Any]:
    return {
        "os_name": _field("Windows"),
        "os_version": _field("11 (build 10.0.26200)"),
        "cpu": _field("Test CPU"),
        "architecture": _field("AMD64, 64bit"),
        "ram_bytes": _field(8 * 1024**3),
        "gpu": _field(["Test GPU"]),
        "storage": {
            "value": [
                {"mount": "C:\\", "total_bytes": 100 * 1024**3, "free_bytes": 100},
                {"mount": "D:\\", "total_bytes": 100 * 1024**3, "free_bytes": 50 * 1024**3},
            ],
            "evidence": "OBSERVED",
        },
    }


@pytest.fixture()
def tools() -> list[dict[str, Any]]:
    return [
        {
            "id": "git",
            "state": "DETECTED",
            "version": "2.55.0",
            "executable_path": "C:/git/git.EXE",
            "evidence": "OBSERVED",
            "probe": "git --version",
            "reason": "probe exited 0",
            "health_ok": True,
            "capability": [],
            "min_version": None,
            "required": "required",
        },
        {
            "id": "freecad",
            "state": "NOT_FOUND",
            "version": "UNKNOWN",
            "executable_path": "UNKNOWN",
            "evidence": "OBSERVED",
            "probe": "FreeCADCmd --version",
            "reason": "executable not found on PATH",
            "health_ok": None,
            "capability": ["CAD"],
            "min_version": None,
            "required": "optional",
        },
        {
            "id": "taiga-s1",
            "state": "UNKNOWN",
            "version": "UNKNOWN",
            "executable_path": "UNKNOWN",
            "evidence": "UNKNOWN",
            "probe": None,
            "reason": "not implemented",
            "health_ok": None,
            "capability": ["LLM inference"],
            "min_version": None,
            "required": "optional",
        },
    ]


@pytest.fixture()
def capabilities() -> dict[str, str]:
    return {
        "LLM inference": "UNKNOWN",
        "CAD": "UNAVAILABLE",
        "PCB design": "UNAVAILABLE",
        "circuit simulation": "UNAVAILABLE",
        "robotics simulation": "UNAVAILABLE",
        "3D rendering": "UNAVAILABLE",
        "numerical optimization": "READY",
        "web acquisition": "UNAVAILABLE",
    }


# ---- build_environment ---------------------------------------------------


def test_report_has_required_keys(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    report = build_environment(system, tools, capabilities, generated_at="2026-10-08T00:00:00+00:00")
    assert tuple(report.keys()) == REPORT_KEYS
    json.dumps(report)


def test_deterministic_given_identical_inputs(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    stamp = "2026-10-08T00:00:00+00:00"
    first = build_environment(system, tools, capabilities, generated_at=stamp)
    second = build_environment(system, tools, capabilities, generated_at=stamp)
    assert first == second


def test_missing_and_unknown_classification(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    report = build_environment(system, tools, capabilities, generated_at="t")
    assert report["missing_tools"] == ["freecad"]
    assert report["unknown_tools"] == ["taiga-s1"]
    assert "git" not in report["missing_tools"]
    assert "git" not in report["unknown_tools"]
    assert "freecad" not in report["unknown_tools"]
    assert "taiga-s1" not in report["missing_tools"]


def test_detected_tool_shows_real_version(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    report = build_environment(system, tools, capabilities, generated_at="t")
    git = next(t for t in report["tools"] if t["id"] == "git")
    assert git["state"] == "DETECTED"
    assert git["version"] == "2.55.0"


def test_not_found_tool_never_described_as_installed(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    report = build_environment(system, tools, capabilities, generated_at="t")
    markdown = render_markdown(report)
    for line in markdown.splitlines():
        if "freecad" in line:
            assert "installed" not in line, line
    json_text = json.dumps(report)
    assert "installed" not in json_text


def test_unknown_tool_not_claimed_present_or_missing(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    report = build_environment(system, tools, capabilities, generated_at="t")
    markdown = render_markdown(report)
    assert "taiga-s1" in report["unknown_tools"]
    for line in markdown.splitlines():
        if "taiga-s1" in line and "| taiga-s1" not in line:
            assert "installed" not in line
            assert "NOT_FOUND" not in line


def test_low_disk_warning_names_volume(system: dict[str, Any]) -> None:
    report = build_environment(
        system, [], {"CAD": "UNKNOWN"}, generated_at="t"
    )
    low = [w for w in report["warnings"] if w["code"] == "LOW_DISK_SPACE"]
    assert len(low) == 1
    assert "C:\\" in low[0]["message"]
    assert str(LOW_DISK_THRESHOLD_BYTES) in low[0]["message"]


def test_no_low_disk_warning_for_healthy_volume(system: dict[str, Any]) -> None:
    system["storage"]["value"] = [
        {"mount": "D:\\", "total_bytes": 100 * 1024**3, "free_bytes": 50 * 1024**3}
    ]
    report = build_environment(system, [], {}, generated_at="t")
    assert not [w for w in report["warnings"] if w["code"] == "LOW_DISK_SPACE"]


def test_required_tool_not_detected_warns(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    tools.append(
        {
            "id": "python",
            "state": "NOT_FOUND",
            "version": "UNKNOWN",
            "executable_path": "UNKNOWN",
            "evidence": "OBSERVED",
            "probe": "python --version",
            "reason": "executable not found on PATH",
            "health_ok": None,
            "capability": ["numerical optimization"],
            "min_version": None,
            "required": "required",
        }
    )
    report = build_environment(system, tools, capabilities, generated_at="t")
    required_warnings = [
        w for w in report["warnings"] if w["code"] == "REQUIRED_TOOL_NOT_DETECTED"
    ]
    assert len(required_warnings) == 1
    assert "python" in required_warnings[0]["message"]


def test_unknown_capability_produces_limitation(
    system: dict[str, Any],
    capabilities: dict[str, str],
) -> None:
    report = build_environment(system, [], capabilities, generated_at="t")
    assert any("LLM inference" in item for item in report["limitations"])
    assert any("CAD" in item for item in report["limitations"])  # UNAVAILABLE too


def test_recommendations_are_suggestions(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    report = build_environment(system, tools, capabilities, generated_at="t")
    freecad_recs = [r for r in report["recommendations"] if "freecad" in r]
    assert freecad_recs
    assert "consider installing" in freecad_recs[0]
    assert "CAD" in freecad_recs[0]
    assert any("free disk space" in r for r in report["recommendations"])


# ---- markdown rendering --------------------------------------------------


def test_markdown_has_required_sections(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    report = build_environment(system, tools, capabilities, generated_at="t")
    markdown = render_markdown(report)
    for heading in (
        "# Environment Report",
        "## Platform",
        "## Tools",
        "## Capabilities",
        "## Missing dependencies",
        "## Warnings",
        "## Limitations",
        "## Recommendations",
    ):
        assert heading in markdown, heading
    assert "| git | DETECTED | 2.55.0 | OBSERVED |" in markdown


# ---- write_reports -------------------------------------------------------


def test_write_reports_round_trip(tmp_path: Path, system, tools, capabilities) -> None:
    report = build_environment(system, tools, capabilities, generated_at="t")
    json_path, md_path = write_reports(report, tmp_path)
    assert json_path.name == JSON_FILENAME
    assert md_path.name == MARKDOWN_FILENAME
    reloaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert reloaded == report
    assert md_path.read_text(encoding="utf-8").startswith("# Environment Report")


def test_default_write_target_is_repo_root() -> None:
    assert REPO_ROOT.is_dir()
    assert (REPO_ROOT / ".gitignore").is_file()


def test_gitignore_covers_both_reports() -> None:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "environment.json" in gitignore
    assert "environment-report.md" in gitignore


# ---- schema validation ---------------------------------------------------


def test_schema_file_exists_and_declares_draft07() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert set(schema["required"]) == set(REPORT_KEYS)


def test_synthetic_report_validates_against_schema(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    report = build_environment(system, tools, capabilities, generated_at="t")
    assert _check(report, schema) == []


def test_live_report_validates_against_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    system = detect_system()
    records = detect_tools()
    report = build_environment(system, records, capability_states(records))
    assert _check(report, schema) == []


def test_schema_rejects_fabricated_state() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    report = build_environment({"storage": {}}, [], {}, generated_at="t")
    report["tools"] = [
        {
            "id": "freecad",
            "state": "INSTALLED",
            "version": "1.0",
            "executable_path": "C:/x.exe",
            "evidence": "OBSERVED",
        }
    ]
    assert any("enum" in error for error in _check(report, schema))


# ---- live host -----------------------------------------------------------


def test_live_report_generates_and_warns_about_low_disk_if_present() -> None:
    system = detect_system()
    records = detect_tools()
    report = build_environment(system, records, capability_states(records))
    json.dumps(report)
    assert report["generated_at"]
    low_volumes = [
        v
        for v in system["storage"].get("value", [])
        if v["free_bytes"] < LOW_DISK_THRESHOLD_BYTES
    ]
    low_warnings = [w for w in report["warnings"] if w["code"] == "LOW_DISK_SPACE"]
    if low_volumes:
        assert len(low_warnings) == len(low_volumes)
    assert set(report["missing_tools"]) == {
        r["id"] for r in records if r["state"] == "NOT_FOUND"
    }
