"""CIE component data model (T-0401, MASTER §12) and motor extension (§13).

Machine-readable component records where every field is optional and an
unset field is the explicit `UNKNOWN` sentinel — never empty-string/zero
padding (MASTER §12: "Do not create fields merely to make the record
look complete. Missing information remains UNKNOWN.").

`to_dict` omits UNKNOWN fields, so serialized records contain only real
facts. Derived values must carry the calculation that produced them
(§13). Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Mapping, Optional

from src.core.evidence import EvidenceLabel, parse_label


class ComponentError(ValueError):
    """Raised for an invalid component record or derived value."""


class _Unknown:
    """Singleton sentinel for an unknown value (distinct from None)."""

    _instance: Optional["_Unknown"] = None

    def __new__(cls) -> "_Unknown":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNKNOWN"

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return self is other

    def __hash__(self) -> int:
        return hash("UNKNOWN")


UNKNOWN = _Unknown()


def is_unknown(value: Any) -> bool:
    """True when ``value`` is the UNKNOWN sentinel."""
    return value is UNKNOWN


def _clean(value: Any) -> Any:
    """Return a JSON-ready copy with UNKNOWN removed; None means 'omit'."""
    if value is UNKNOWN:
        return None
    if isinstance(value, Mapping):
        cleaned = {key: _clean(item) for key, item in value.items()}
        cleaned = {key: item for key, item in cleaned.items() if item is not None}
        return cleaned or None
    if isinstance(value, (list, tuple)):
        items = [_clean(item) for item in value]
        items = [item for item in items if item is not None]
        return items or None
    return value


@dataclass(frozen=True)
class DerivedValue:
    """A value that was calculated, with the method and its evidence class."""

    value: Any
    method: str
    evidence_label: EvidenceLabel = EvidenceLabel.CALCULATED

    def __post_init__(self) -> None:
        if self.value is UNKNOWN or self.value is None:
            raise ComponentError("a derived value must have a real value")
        if not isinstance(self.method, str) or not self.method.strip():
            raise ComponentError("a derived value requires a non-empty method")
        object.__setattr__(self, "evidence_label", parse_label(self.evidence_label))

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": _clean(self.value),
            "method": self.method,
            "evidence": self.evidence_label.value,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "DerivedValue":
        if not isinstance(data, Mapping):
            raise ComponentError("derived value must be a mapping")
        if "value" not in data or "method" not in data:
            raise ComponentError("derived value requires 'value' and 'method'")
        return cls(
            value=data["value"],
            method=data["method"],
            evidence_label=data.get("evidence", EvidenceLabel.CALCULATED.value),
        )


_MOTOR_FIELDS: tuple[str, ...] = (
    "rated_voltage",
    "rated_current",
    "rated_speed_rpm",
    "rated_torque",
    "stall_torque",
    "stall_current",
    "winding_resistance",
    "kv",
    "torque_constant",
    "rotor_inertia",
    "efficiency",
    "thermal_limits",
    "dimensions",
    "gearbox",
    "gear_ratio",
    "shaft",
    "mounting_pattern",
)


@dataclass
class MotorSpec:
    """MASTER §13 motor parameters; any unset field is UNKNOWN."""

    rated_voltage: Any = UNKNOWN
    rated_current: Any = UNKNOWN
    rated_speed_rpm: Any = UNKNOWN
    rated_torque: Any = UNKNOWN
    stall_torque: Any = UNKNOWN
    stall_current: Any = UNKNOWN
    winding_resistance: Any = UNKNOWN
    kv: Any = UNKNOWN
    torque_constant: Any = UNKNOWN
    rotor_inertia: Any = UNKNOWN
    efficiency: Any = UNKNOWN
    thermal_limits: Any = UNKNOWN
    dimensions: Any = UNKNOWN
    gearbox: Any = UNKNOWN
    gear_ratio: Any = UNKNOWN
    shaft: Any = UNKNOWN
    mounting_pattern: Any = UNKNOWN

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for spec_field in fields(self):
            value = getattr(self, spec_field.name)
            if isinstance(value, DerivedValue):
                out[spec_field.name] = value.to_dict()
                continue
            cleaned = _clean(value)
            if cleaned is not None:
                out[spec_field.name] = cleaned
        return out

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MotorSpec":
        if not isinstance(data, Mapping):
            raise ComponentError("motor must be a mapping")
        allowed = set(_MOTOR_FIELDS)
        extra = set(data) - allowed
        if extra:
            raise ComponentError(f"unknown motor field(s): {', '.join(sorted(extra))}")
        kwargs: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, Mapping) and {"value", "method"} <= set(value):
                kwargs[key] = DerivedValue.from_dict(value)
            else:
                kwargs[key] = value
        return cls(**kwargs)


_COMPONENT_SCALARS: tuple[str, ...] = (
    "category",
    "name",
    "manufacturer",
    "model",
    "part_number",
    "sku",
    "retrieval_date",
    "materials",
    "interfaces",
    "dimensions",
    "electrical",
    "mechanical",
    "thermal",
    "environmental",
    "specifications",
)


@dataclass
class Component:
    """MASTER §12 machine-readable component record. Only `id` is required."""

    id: str
    category: Any = UNKNOWN
    name: Any = UNKNOWN
    manufacturer: Any = UNKNOWN
    model: Any = UNKNOWN
    part_number: Any = UNKNOWN
    sku: Any = UNKNOWN
    source_urls: tuple[str, ...] = ()
    retrieval_date: Any = UNKNOWN
    specifications: dict[str, Any] = field(default_factory=dict)
    dimensions: Any = UNKNOWN
    materials: Any = UNKNOWN
    interfaces: Any = UNKNOWN
    electrical: Any = UNKNOWN
    mechanical: Any = UNKNOWN
    thermal: Any = UNKNOWN
    environmental: Any = UNKNOWN
    datasheets: tuple[str, ...] = ()
    motor: Optional[MotorSpec] = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ComponentError("component id must be a non-empty string")
        if self.motor is not None and not isinstance(self.motor, MotorSpec):
            raise ComponentError("motor must be a MotorSpec or None")

    def to_dict(self) -> dict[str, Any]:
        """Serialized record; UNKNOWN fields are omitted (no padding)."""
        out: dict[str, Any] = {"id": self.id}
        for item in fields(self):
            if item.name == "id":
                continue
            value = getattr(self, item.name)
            if item.name == "motor":
                if value is not None:
                    out["motor"] = value.to_dict()
                continue
            if item.name in ("source_urls", "datasheets"):
                if value:
                    out[item.name] = list(value)
                continue
            cleaned = _clean(value)
            if cleaned is not None:
                out[item.name] = cleaned
        return out

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Component":
        if not isinstance(data, Mapping):
            raise ComponentError("component record must be a mapping")
        if "id" not in data:
            raise ComponentError("component record requires an 'id'")
        allowed = {item.name for item in fields(cls)}
        extra = set(data) - allowed
        if extra:
            raise ComponentError(f"unknown component field(s): {', '.join(sorted(extra))}")
        kwargs: dict[str, Any] = {}
        for key, value in data.items():
            if key == "motor":
                kwargs["motor"] = MotorSpec.from_dict(value) if value is not None else None
            elif key in ("source_urls", "datasheets"):
                kwargs[key] = tuple(value)
            elif key in _COMPONENT_SCALARS:
                kwargs[key] = value
            else:  # id
                kwargs[key] = value
        return cls(**kwargs)


__all__ = [
    "UNKNOWN",
    "Component",
    "ComponentError",
    "DerivedValue",
    "MotorSpec",
    "is_unknown",
]