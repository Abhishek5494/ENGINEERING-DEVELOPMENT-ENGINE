"""REA investigation records (T-0701, MASTER §19–§21).

Authorization is mandatory: an investigation cannot exist without a
documented authorization basis (§20 — STOP if insufficient). Evidence
rules are enforced structurally (§19): a finding never claims recovered
pseudocode is the original source, and a reconstruction is never labelled
OBSERVED.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from src.core.evidence import EvidenceLabel, parse_label

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class AuthorizationError(Exception):
    """Raised when an investigation lacks a documented authorization."""


class EvidenceRuleError(Exception):
    """Raised when a finding violates the §19 evidence rules."""


@dataclass(frozen=True)
class EvidenceEntry:
    """A single piece of labelled evidence collected during investigation."""

    statement: str
    label: EvidenceLabel = EvidenceLabel.OBSERVED
    source: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("evidence statement must be non-empty")
        try:
            label = parse_label(self.label)
        except Exception as exc:
            raise EvidenceRuleError(f"invalid evidence label: {exc}") from exc
        object.__setattr__(self, "label", label)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "statement": self.statement,
            "label": self.label.value,
        }
        if self.source:
            data["source"] = self.source
        return data


@dataclass(frozen=True)
class Finding:
    """A conclusion drawn during investigation, with §19 guarantees."""

    statement: str
    label: EvidenceLabel = EvidenceLabel.INFERRED
    reconstructed: bool = False
    source_recovered: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.statement, str) or not self.statement.strip():
            raise ValueError("finding statement must be non-empty")
        if self.source_recovered:
            raise EvidenceRuleError(
                "recovered pseudocode/artifacts are never claimed as the "
                "original source (MASTER §19)"
            )
        try:
            label = parse_label(self.label)
        except Exception as exc:
            raise EvidenceRuleError(f"invalid evidence label: {exc}") from exc
        if self.reconstructed and label is EvidenceLabel.OBSERVED:
            raise EvidenceRuleError(
                "a reconstruction cannot be labelled OBSERVED (MASTER §19)"
            )
        object.__setattr__(self, "label", label)

    def to_dict(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "label": self.label.value,
            "reconstructed": self.reconstructed,
        }


@dataclass(frozen=True)
class Investigation:
    """A single, authorized REA investigation record."""

    name: str
    target: str
    authorized: bool
    authorization_basis: str
    scope: str = ""
    findings: tuple[Finding, ...] = field(default_factory=tuple)
    evidence: tuple[EvidenceEntry, ...] = field(default_factory=tuple)
    unknowns: tuple[str, ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)
    behavior_notes: tuple[str, ...] = field(default_factory=tuple)
    implementation_notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not _SLUG_RE.match(self.name):
            raise ValueError(
                "investigation name must be a lowercase slug [a-z0-9-]"
            )
        if not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("investigation requires a target")
        if not self.authorized:
            raise AuthorizationError(
                "investigation requires documented authorization (MASTER §20)"
            )
        if not isinstance(self.authorization_basis, str) or not self.authorization_basis.strip():
            raise AuthorizationError(
                "authorization basis is required (MASTER §20)"
            )
        for finding in self.findings:
            if not isinstance(finding, Finding):
                raise ValueError("findings must be Finding instances")
        for entry in self.evidence:
            if not isinstance(entry, EvidenceEntry):
                raise ValueError("evidence must be EvidenceEntry instances")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "target": self.target,
            "authorized": self.authorized,
            "authorization_basis": self.authorization_basis,
            "scope": self.scope,
            "findings": [finding.to_dict() for finding in self.findings],
            "evidence": [entry.to_dict() for entry in self.evidence],
            "unknowns": list(self.unknowns),
            "limitations": list(self.limitations),
            "behavior": list(self.behavior_notes),
            "implementation_notes": list(self.implementation_notes),
        }


def build_investigation(
    name: str,
    target: str,
    authorization_basis: str,
    *,
    scope: str = "",
    findings: Iterable[Finding] = (),
    evidence: Iterable[EvidenceEntry] = (),
    unknowns: Iterable[str] = (),
    limitations: Iterable[str] = (),
    behavior_notes: Iterable[str] = (),
    implementation_notes: Iterable[str] = (),
) -> Investigation:
    """Construct an authorized investigation (authorization=True)."""
    return Investigation(
        name=name,
        target=target,
        authorized=True,
        authorization_basis=authorization_basis,
        scope=scope,
        findings=tuple(findings),
        evidence=tuple(evidence),
        unknowns=tuple(unknowns),
        limitations=tuple(limitations),
        behavior_notes=tuple(behavior_notes),
        implementation_notes=tuple(implementation_notes),
    )


def with_evidence(
    investigation: Investigation,
    entries: Iterable[EvidenceEntry] = (),
    *,
    unknowns: Iterable[str] = (),
    behavior_notes: Iterable[str] = (),
    limitations: Iterable[str] = (),
) -> Investigation:
    """Return a copy with appended evidence/notes (the original is unchanged)."""
    from dataclasses import replace

    return replace(
        investigation,
        evidence=investigation.evidence + tuple(entries),
        unknowns=investigation.unknowns + tuple(unknowns),
        behavior_notes=investigation.behavior_notes + tuple(behavior_notes),
        limitations=investigation.limitations + tuple(limitations),
    )


__all__ = [
    "AuthorizationError",
    "EvidenceEntry",
    "EvidenceRuleError",
    "Finding",
    "Investigation",
    "build_investigation",
    "with_evidence",
]