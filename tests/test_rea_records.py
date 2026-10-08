"""Tests for REA investigation records + §19/§20 rules (T-0701)."""

from __future__ import annotations

import pytest

from src.core.evidence import EvidenceLabel
from src.rea.records import (
    AuthorizationError,
    EvidenceEntry,
    EvidenceRuleError,
    Finding,
    Investigation,
    build_investigation,
)


def test_investigation_requires_authorization() -> None:
    with pytest.raises(AuthorizationError):
        Investigation(name="demo", target="app.exe", authorized=False, authorization_basis="x")
    with pytest.raises(AuthorizationError):
        Investigation(name="demo", target="app.exe", authorized=True, authorization_basis="  ")


def test_investigation_requires_valid_slug_and_target() -> None:
    with pytest.raises(ValueError):
        Investigation(name="Demo App", target="app.exe", authorized=True, authorization_basis="ok")
    with pytest.raises(ValueError):
        Investigation(name="demo", target="", authorized=True, authorization_basis="ok")


def test_build_investigation_is_authorized() -> None:
    inv = build_investigation("demo", "app.exe", "written approval 2026-10-08")
    assert inv.authorized is True
    assert inv.name == "demo"


def test_finding_rejects_recovered_source_claim() -> None:
    with pytest.raises(EvidenceRuleError):
        Finding("this is the original source", source_recovered=True)


def test_reconstruction_cannot_be_observed() -> None:
    with pytest.raises(EvidenceRuleError):
        Finding("control loop behaves like X", label=EvidenceLabel.OBSERVED, reconstructed=True)
    ok = Finding("control loop behaves like X", label=EvidenceLabel.INFERRED, reconstructed=True)
    assert ok.reconstructed is True
    assert ok.label is EvidenceLabel.INFERRED


def test_finding_and_evidence_validate_label() -> None:
    with pytest.raises(EvidenceRuleError):
        Finding("x", label="INSTALLED")  # type: ignore[arg-type]
    with pytest.raises(EvidenceRuleError):
        EvidenceEntry("x", label="INSTALLED")  # type: ignore[arg-type]


def test_evidence_entry_roundtrip_and_source() -> None:
    entry = EvidenceEntry("serial port emits 9600 baud", EvidenceLabel.MEASURED, source="logic analyzer")
    assert entry.to_dict() == {
        "statement": "serial port emits 9600 baud",
        "label": "MEASURED",
        "source": "logic analyzer",
    }
    plain = EvidenceEntry("observed text")
    assert "source" not in plain.to_dict()


def test_investigation_to_dict() -> None:
    inv = build_investigation(
        "demo",
        "app.exe",
        "approval",
        scope="understand motor control",
        findings=(Finding("loop is PI", EvidenceLabel.INFERRED),),
        evidence=(EvidenceEntry("log line 12", EvidenceLabel.OBSERVED),),
        unknowns=("exact gains",),
        limitations=("no hardware",),
        behavior_notes=("ramps on start",),
        implementation_notes=("use PID",),
    )
    data = inv.to_dict()
    assert data["name"] == "demo"
    assert data["findings"][0]["statement"] == "loop is PI"
    assert data["evidence"][0]["label"] == "OBSERVED"
    assert data["unknowns"] == ["exact gains"]
    assert data["implementation_notes"] == ["use PID"]