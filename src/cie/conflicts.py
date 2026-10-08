"""Fact records with conflict detection (T-0403, MASTER §11).

A field may be asserted by several sources. This module keeps every fact
and marks the field `CONFLICT` when the sources disagree — nothing is
silently overwritten. A `governing` fact is *selected* by source
authority (then §6 evidence strength, then retrieval date) while the
others are retained for inspection.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field as dataclass_field
from datetime import date
from enum import Enum
from typing import Any, Iterable

from src.core.evidence import EvidenceLabel, parse_label, rank as evidence_rank
from src.cie.model import UNKNOWN, is_unknown
from src.cie.provenance import Provenance, ProvenanceError, source_rank


class FactError(Exception):
    """Raised when a fact or field record is malformed."""


class FactStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    SINGLE = "SINGLE"
    AGREED = "AGREED"
    CONFLICT = "CONFLICT"


def _value_key(value: Any) -> str:
    """A stable, hashable comparison key for arbitrary fact values."""
    return json.dumps(value, sort_keys=True, default=str)


@dataclass(frozen=True)
class Fact:
    """One source's assertion about one field."""

    value: Any
    provenance: Provenance
    evidence_label: EvidenceLabel = EvidenceLabel.OBSERVED

    def __post_init__(self) -> None:
        if not isinstance(self.provenance, Provenance):
            raise FactError("a fact requires a Provenance instance")
        try:
            label = parse_label(self.evidence_label)
        except Exception as exc:  # EvidenceError
            raise FactError(f"invalid evidence label: {exc}") from exc
        object.__setattr__(self, "evidence_label", label)

    @property
    def is_real(self) -> bool:
        return not is_unknown(self.value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": None if is_unknown(self.value) else self.value,
            "evidence_label": self.evidence_label.value,
            "provenance": self.provenance.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Fact":
        try:
            provenance = Provenance.from_dict(data["provenance"])
            value = data.get("value", UNKNOWN)
            return cls(
                value=UNKNOWN if value is None else value,
                provenance=provenance,
                evidence_label=data.get("evidence_label", EvidenceLabel.OBSERVED),
            )
        except (KeyError, ProvenanceError) as exc:
            raise FactError(f"invalid fact: {exc}") from exc


@dataclass(frozen=True)
class FieldRecord:
    """All facts known about one component field, with conflict status."""

    field: str
    facts: tuple[Fact, ...] = dataclass_field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.field, str) or not self.field.strip():
            raise FactError("field name must be a non-empty string")
        for fact in self.facts:
            if not isinstance(fact, Fact):
                raise FactError("facts must be Fact instances")

    @property
    def real_facts(self) -> tuple[Fact, ...]:
        return tuple(fact for fact in self.facts if fact.is_real)

    @property
    def status(self) -> FactStatus:
        real = self.real_facts
        if not real:
            return FactStatus.UNKNOWN
        distinct = {_value_key(fact.value) for fact in real}
        if len(distinct) > 1:
            return FactStatus.CONFLICT
        return FactStatus.AGREED if len(real) > 1 else FactStatus.SINGLE

    @property
    def governing(self) -> Fact | None:
        """The most authoritative real fact (selection, never a deletion)."""
        real = self.real_facts
        if not real:
            return None

        def sort_key(item: tuple[int, Fact]) -> tuple[int, int, int, int]:
            index, fact = item
            return (
                source_rank(fact.provenance.kind),
                -evidence_rank(fact.evidence_label),
                -date.fromisoformat(fact.provenance.retrieval_date).toordinal(),
                index,
            )

        _, best = min(enumerate(real), key=sort_key)
        return best

    def to_dict(self) -> dict[str, Any]:
        governing = self.governing
        return {
            "field": self.field,
            "status": self.status.value,
            "facts": [fact.to_dict() for fact in self.facts],
            "governing": governing.to_dict() if governing else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FieldRecord":
        try:
            facts = tuple(Fact.from_dict(item) for item in data.get("facts", []))
            return cls(field=data["field"], facts=facts)
        except KeyError as exc:
            raise FactError(f"field record missing field: {exc}") from exc


def build_field_record(field: str, facts: Iterable[Fact]) -> FieldRecord:
    return FieldRecord(field=field, facts=tuple(facts))


def conflicting_fields(records: Iterable[FieldRecord]) -> list[str]:
    return [record.field for record in records if record.status is FactStatus.CONFLICT]


__all__ = [
    "Fact",
    "FactError",
    "FactStatus",
    "FieldRecord",
    "build_field_record",
    "conflicting_fields",
]