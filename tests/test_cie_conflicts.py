"""Tests for CIE fact records + §11 conflict detection (T-0403)."""

from __future__ import annotations

import json
import re
from typing import Any

import pytest

from src.core import config
from src.core.evidence import EvidenceLabel
from src.cie.conflicts import (
    Fact,
    FactError,
    FactStatus,
    FieldRecord,
    build_field_record,
    conflicting_fields,
)
from src.cie.model import UNKNOWN
from src.cie.provenance import Provenance, SourceKind

SCHEMA = config.CONFIG_DIR / "fact-record.schema.json"

MARKETPLACE = Provenance(
    "https://market.example.invalid/motor", "2026-10-08", SourceKind.MARKETPLACE_LISTING
)
DATASHEET = Provenance(
    "https://maker.example.invalid/motor.pdf",
    "2026-10-08",
    SourceKind.MANUFACTURER_DATASHEET,
)


def _check(instance: Any, schema: dict[str, Any], root: dict[str, Any] | None = None, path: str = "$") -> list[str]:
    root = root or schema
    if "$ref" in schema:
        target: Any = root
        for part in schema["$ref"].lstrip("#/").split("/"):
            target = target[part]
        return _check(instance, target, root, path)
    if "anyOf" in schema:
        for sub in schema["anyOf"]:
            if not _check(instance, sub, root, path):
                return []
        return [f"{path}: failed anyOf"]
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
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "null": lambda v: v is None,
        }
        if not any(checks[name](instance) for name in allowed):
            return errors + [f"{path}: bad type {type(instance).__name__}"]
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing {key!r}")
        props = schema.get("properties", {})
        for key, value in instance.items():
            if key in props:
                errors.extend(_check(value, props[key], root, f"{path}.{key}"))
            elif schema.get("additionalProperties", True) is False:
                errors.append(f"{path}: unexpected {key!r}")
    if isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            errors.extend(_check(item, schema["items"], root, f"{path}[{index}]"))
    if isinstance(instance, str) and "pattern" in schema:
        if re.match(schema["pattern"], instance) is None:
            errors.append(f"{path}: pattern mismatch")
    return errors


def _fact(value: Any, provenance: Provenance, label: EvidenceLabel = EvidenceLabel.OBSERVED) -> Fact:
    return Fact(value=value, provenance=provenance, evidence_label=label)


def test_fact_requires_provenance_and_valid_label() -> None:
    with pytest.raises(FactError):
        Fact(value=1, provenance="not-provenance")  # type: ignore[arg-type]
    with pytest.raises(FactError):
        _fact(1, MARKETPLACE, "INSTALLED")  # type: ignore[arg-type]


def test_fact_roundtrip() -> None:
    fact = _fact(8500, DATASHEET, EvidenceLabel.MANUFACTURER_SPECIFIED)
    assert Fact.from_dict(fact.to_dict()) == fact


def test_status_unknown_when_no_real_facts() -> None:
    assert build_field_record("rpm", []).status is FactStatus.UNKNOWN
    only_unknown = build_field_record("rpm", [_fact(UNKNOWN, MARKETPLACE)])
    assert only_unknown.status is FactStatus.UNKNOWN
    assert only_unknown.governing is None


def test_single_and_agreed() -> None:
    single = build_field_record("rpm", [_fact(8500, DATASHEET)])
    assert single.status is FactStatus.SINGLE
    agreed = build_field_record("rated_voltage", [_fact(12, DATASHEET), _fact(12, MARKETPLACE)])
    assert agreed.status is FactStatus.AGREED


def test_conflict_retains_both_and_selects_governing() -> None:
    record = build_field_record(
        "rpm", [_fact(10_000, MARKETPLACE), _fact(8500, DATASHEET)]
    )
    assert record.status is FactStatus.CONFLICT
    assert len(record.facts) == 2
    assert {f.value for f in record.real_facts} == {10000, 8500}
    assert record.governing is not None
    assert record.governing.value == 8500
    assert record.governing.provenance.kind is SourceKind.MANUFACTURER_DATASHEET


def test_marketplace_fact_is_retained_not_overwritten() -> None:
    record = build_field_record("rpm", [_fact(10000, MARKETPLACE), _fact(8500, DATASHEET)])
    assert any(f.value == 10000 for f in record.facts)
    assert any(f.provenance.kind is SourceKind.MARKETPLACE_LISTING for f in record.facts)


def test_unknown_value_facts_do_not_conflict() -> None:
    record = build_field_record(
        "rpm", [_fact(8500, DATASHEET), _fact(UNKNOWN, MARKETPLACE)]
    )
    assert record.status is FactStatus.SINGLE
    assert record.governing.value == 8500


def test_agreement_across_sources() -> None:
    record = build_field_record(
        "kv", [_fact(100, DATASHEET), _fact(100, MARKETPLACE)]
    )
    assert record.status is FactStatus.AGREED


def test_tie_break_by_evidence_strength_then_recency() -> None:
    weak = Fact(
        10,
        Provenance("https://a.example.invalid", "2026-10-01", SourceKind.MARKETPLACE_LISTING),
        EvidenceLabel.OBSERVED,
    )
    recent_same_kind = Fact(
        20,
        Provenance("https://b.example.invalid", "2026-10-08", SourceKind.MARKETPLACE_LISTING),
        EvidenceLabel.OBSERVED,
    )
    stronger = Fact(
        30,
        Provenance("https://c.example.invalid", "2026-09-01", SourceKind.MARKETPLACE_LISTING),
        EvidenceLabel.MEASURED,
    )
    record = build_field_record("x", [weak, recent_same_kind, stronger])
    assert record.governing.value == 30  # MEASURED outranks OBSERVED


def test_conflicting_fields_lists_only_conflicts() -> None:
    single = build_field_record("a", [_fact(1, DATASHEET)])
    conflict = build_field_record("b", [_fact(1, DATASHEET), _fact(2, MARKETPLACE)])
    assert conflicting_fields([single, conflict]) == ["b"]


def test_field_record_roundtrip_and_validation() -> None:
    record = build_field_record(
        "rpm",
        [
            _fact(10000, MARKETPLACE, EvidenceLabel.OBSERVED),
            _fact(8500, DATASHEET, EvidenceLabel.MANUFACTURER_SPECIFIED),
        ],
    )
    restored = FieldRecord.from_dict(record.to_dict())
    assert restored.field == record.field
    assert restored.status is FactStatus.CONFLICT
    assert restored.governing == record.governing
    with pytest.raises(FactError):
        FieldRecord.from_dict({"facts": []})
    with pytest.raises(FactError):
        FieldRecord(field="")


def test_fact_to_dict_unknown_value_is_null() -> None:
    data = _fact(UNKNOWN, MARKETPLACE).to_dict()
    assert data["value"] is None
    assert Fact.from_dict(data).value is UNKNOWN


def test_schema_validates_good_record_and_rejects() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    record = build_field_record(
        "rpm",
        [_fact(10000, MARKETPLACE), _fact(8500, DATASHEET, EvidenceLabel.MANUFACTURER_SPECIFIED)],
    ).to_dict()
    assert _check(record, schema) == []

    bad_status = dict(record, status="MAYBE")
    assert _check(bad_status, schema)
    bad_label = {
        "field": "rpm",
        "status": "SINGLE",
        "facts": [
            {
                "value": 1,
                "evidence_label": "INSTALLED",
                "provenance": MARKETPLACE.to_dict(),
            }
        ],
        "governing": None,
    }
    assert _check(bad_label, schema)
    bad_date = {
        "field": "rpm",
        "status": "SINGLE",
        "facts": [
            {
                "value": 1,
                "evidence_label": "OBSERVED",
                "provenance": {
                    "source_url": "https://x.invalid",
                    "retrieval_date": "2026/10/08",
                    "kind": "MARKETPLACE_LISTING",
                },
            }
        ],
    }
    assert _check(bad_date, schema)
    assert _check({"field": "x", "status": "SINGLE"}, schema)  # missing facts