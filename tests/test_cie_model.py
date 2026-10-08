"""Tests for the CIE component data model and schema (T-0401)."""

from __future__ import annotations

import json
from typing import Any

import pytest

from src.core import config
from src.cie.model import (
    UNKNOWN,
    Component,
    ComponentError,
    DerivedValue,
    MotorSpec,
    is_unknown,
)

SCHEMA_PATH = config.CONFIG_DIR / "component.schema.json"


def _check(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Minimal draft-07 subset validator (no third-party deps)."""
    errors: list[str] = []
    declared = schema.get("type")
    if declared is not None:
        allowed = [declared] if isinstance(declared, str) else declared
        checks = {
            "string": lambda v: isinstance(v, str),
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "null": lambda v: v is None,
        }
        if not any(checks[name](instance) for name in allowed):
            errors.append(f"{path}: {type(instance).__name__} not in {allowed}")
            return errors
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required {key!r}")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(_check(value, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties", True) is False:
                errors.append(f"{path}: unexpected key {key!r}")
    if isinstance(instance, list) and "items" in schema:
        for index, item in enumerate(instance):
            errors.extend(_check(item, schema["items"], f"{path}[{index}]"))
    if isinstance(instance, str) and len(instance) < schema.get("minLength", 0):
        errors.append(f"{path}: shorter than minLength")
    return errors


def test_unknown_is_a_distinct_sentinel() -> None:
    assert is_unknown(UNKNOWN)
    assert UNKNOWN is not None
    assert UNKNOWN != "UNKNOWN"
    assert UNKNOWN != ""
    assert repr(UNKNOWN) == "UNKNOWN"
    assert not UNKNOWN


def test_component_requires_id() -> None:
    with pytest.raises(ComponentError):
        Component(id="")
    with pytest.raises(ComponentError):
        Component(id=123)  # type: ignore[arg-type]


def test_to_dict_omits_unknown_fields() -> None:
    component = Component(id="c1", name="NEMA17")
    data = component.to_dict()
    assert data == {"id": "c1", "name": "NEMA17"}
    assert "manufacturer" not in data
    assert "torque" not in data


def test_component_roundtrip_preserves_values_and_order() -> None:
    component = Component(
        id="c2",
        category="motor",
        name="NEMA17",
        manufacturer="Acme",
        source_urls=("https://b.invalid", "https://a.invalid"),
        specifications={"steps": 200, "holding_torque": "0.4 Nm"},
        electrical={"voltage": 12},
    )
    restored = Component.from_dict(component.to_dict())
    assert restored == component
    assert component.to_dict()["source_urls"] == [
        "https://b.invalid",
        "https://a.invalid",
    ]


def test_nested_specifications_roundtrip() -> None:
    component = Component(id="c2b", specifications={"a": {"b": 1, "c": 2}})
    assert Component.from_dict(component.to_dict()) == component


def test_motor_spec_unknown_and_roundtrip() -> None:
    motor = MotorSpec(rated_voltage=12.0, kv=UNKNOWN)
    assert motor.kv is UNKNOWN
    motor_dict = motor.to_dict()
    assert motor_dict == {"rated_voltage": 12.0}
    assert MotorSpec.from_dict(motor_dict) == motor


def test_motor_derived_value_requires_method() -> None:
    derived = DerivedValue(value=0.5, method="torque = kt * current")
    motor = MotorSpec(stall_torque=derived)
    data = motor.to_dict()
    assert data["stall_torque"]["method"] == "torque = kt * current"
    assert data["stall_torque"]["evidence"] == "CALCULATED"
    assert MotorSpec.from_dict(data) == motor


def test_derived_value_validation() -> None:
    with pytest.raises(ComponentError):
        DerivedValue(value=1, method="")
    with pytest.raises(ComponentError):
        DerivedValue(value=1, method="   ")
    with pytest.raises(ComponentError):
        DerivedValue(value=UNKNOWN, method="x")
    with pytest.raises(Exception):
        DerivedValue(value=1, method="x", evidence_label="INSTALLED")


def test_component_motor_roundtrip() -> None:
    component = Component(id="m1", category="motor", motor=MotorSpec(kv=100))
    assert Component.from_dict(component.to_dict()) == component


def test_from_dict_rejects_unknown_key_and_missing_id() -> None:
    with pytest.raises(ComponentError):
        Component.from_dict({"id": "x", "made_up": 1})
    with pytest.raises(ComponentError):
        Component.from_dict({"name": "no id"})


def test_schema_file_declares_draft07() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["$schema"].endswith("draft-07/schema#")
    assert schema["required"] == ["id"]
    assert schema["additionalProperties"] is False


def test_schema_validates_good_record() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    record = Component(
        id="c9",
        name="Servo",
        source_urls=("https://example.invalid",),
        motor=MotorSpec(rated_voltage=6.0),
    ).to_dict()
    assert _check(record, schema) == []


def test_schema_rejects_wrong_type() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert _check({"id": "x", "name": 5}, schema)
    assert _check({"id": "x", "source_urls": "not-a-list"}, schema)


def test_schema_rejects_fabricated_or_extra_field() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert _check({"id": "c1", "status": "INSTALLED"}, schema)


def test_schema_rejects_empty_id() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert _check({"id": ""}, schema)