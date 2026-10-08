"""Tests for REA investigation storage + templates (T-0701)."""

from __future__ import annotations

import pytest

from src.core.evidence import EvidenceLabel
from src.rea.records import EvidenceEntry, Finding, build_investigation
from src.rea.storage import (
    TEMPLATE_FILES,
    InvestigationExistsError,
    render_template,
    write_investigation,
)


def _investigation():
    return build_investigation(
        "motor-controller",
        "controls/firmware.bin",
        "written authorization 2026-10-08",
        scope="Understand the PI control loop.",
        findings=(Finding("loop is PI", EvidenceLabel.INFERRED),),
        evidence=(EvidenceEntry("ramp observed", EvidenceLabel.OBSERVED),),
        unknowns=("exact gains",),
    )


def test_seven_template_files() -> None:
    assert TEMPLATE_FILES == (
        "scope.md",
        "evidence.md",
        "findings.md",
        "behavior.md",
        "unknowns.md",
        "limitations.md",
        "implementation-notes.md",
    )


def test_render_rejects_unknown_template() -> None:
    with pytest.raises(ValueError):
        render_template("secrets.md", _investigation())


def test_render_scope_and_findings() -> None:
    inv = _investigation()
    scope = render_template("scope.md", inv)
    assert "# Scope" in scope
    assert "motor-controller" in scope
    assert "Understand the PI control loop." in scope
    findings = render_template("findings.md", inv)
    assert "loop is PI" in findings
    assert "`INFERRED`" in findings
    evidence = render_template("evidence.md", inv)
    assert "ramp observed" in evidence


def test_render_empty_sections_are_explicit() -> None:
    inv = _investigation()
    assert "exact gains" in render_template("unknowns.md", inv)
    assert "_None recorded._" in render_template("behavior.md", inv)


def test_write_investigation_creates_seven_files(tmp_path) -> None:
    base = write_investigation(tmp_path, _investigation())
    assert base == tmp_path / "motor-controller"
    names = sorted(p.name for p in base.iterdir())
    assert names == sorted(TEMPLATE_FILES)
    assert "written authorization 2026-10-08" in (base / "scope.md").read_text(encoding="utf-8")


def test_write_refuses_overwrite_without_flag(tmp_path) -> None:
    write_investigation(tmp_path, _investigation())
    with pytest.raises(InvestigationExistsError):
        write_investigation(tmp_path, _investigation())
    write_investigation(tmp_path, _investigation(), overwrite=True)  # ok


def test_write_into_empty_existing_dir_is_allowed(tmp_path) -> None:
    (tmp_path / "motor-controller").mkdir()
    base = write_investigation(tmp_path, _investigation())
    assert (base / "findings.md").exists()