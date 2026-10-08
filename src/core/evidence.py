"""Engineering evidence and claim primitives (T-0302, MASTER §5, §6).

Single vocabulary every subsystem uses to label engineering claims. The
eight labels are exactly those defined in MASTER §6; their relative
strength follows the truth hierarchy in §5 (see ADR-0002). This module
performs no I/O — it classifies and structures evidence; persistence is
CIE/REA's job.

Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Optional


class EvidenceError(ValueError):
    """Raised for an unknown evidence label or an invalid claim."""


class EvidenceLabel(str, Enum):
    """The eight MASTER §6 evidence classes."""

    MEASURED = "MEASURED"
    OBSERVED = "OBSERVED"
    SIMULATED = "SIMULATED"
    MANUFACTURER_SPECIFIED = "MANUFACTURER-SPECIFIED"
    CALCULATED = "CALCULATED"
    ASSUMED = "ASSUMED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


# Canonical labels ordered strongest -> weakest (ADR-0002).
EVIDENCE_LABELS: tuple[str, ...] = (
    EvidenceLabel.MEASURED.value,
    EvidenceLabel.OBSERVED.value,
    EvidenceLabel.SIMULATED.value,
    EvidenceLabel.MANUFACTURER_SPECIFIED.value,
    EvidenceLabel.CALCULATED.value,
    EvidenceLabel.ASSUMED.value,
    EvidenceLabel.INFERRED.value,
    EvidenceLabel.UNKNOWN.value,
)

# rank: higher = stronger. MEASURED=7 ... UNKNOWN=0.
_RANK: dict[EvidenceLabel, int] = {
    label: (len(EVIDENCE_LABELS) - 1 - index)
    for index, label in enumerate(EvidenceLabel)
}


def _normalise(token: Any) -> str:
    if not isinstance(token, str):
        raise EvidenceError(f"evidence label must be a string, got {type(token).__name__}")
    key = token.strip().upper().replace("_", "-").replace(" ", "-")
    key = "-".join(part for part in key.split("-") if part)
    return key


def parse_label(token: Any) -> EvidenceLabel:
    """Return the canonical `EvidenceLabel` for ``token``.

    Accepts the canonical value, the enum member, and case/separator
    variants (``manufacturer_specified``, ``manufacturer specified``).
    Anything else raises `EvidenceError`.
    """
    if isinstance(token, EvidenceLabel):
        return token
    normalised = _normalise(token)
    for label in EvidenceLabel:
        if _normalise(label.value) == normalised:
            return label
    raise EvidenceError(f"unknown evidence label: {token!r}")


def rank(label: Any) -> int:
    """Strength rank of a label (higher is stronger; UNKNOWN == 0)."""
    return _RANK[parse_label(label)]


def is_stronger(a: Any, b: Any) -> bool:
    """True when label ``a`` is strictly stronger than label ``b``."""
    return rank(a) > rank(b)


def compare(a: Any, b: Any) -> int:
    """Compare two labels: 1 if ``a`` stronger, -1 if weaker, 0 if equal."""
    ra, rb = rank(a), rank(b)
    return (ra > rb) - (ra < rb)


def strongest(claims: Iterable["Claim"]) -> Optional["Claim"]:
    """Return the strongest claim (ties resolved to the earliest)."""
    best: Optional[Claim] = None
    for claim in claims:
        if not isinstance(claim, Claim):
            raise EvidenceError("strongest() expects Claim instances")
        if best is None or claim.rank > best.rank:
            best = claim
    return best


@dataclass(frozen=True)
class Claim:
    """A single classified engineering claim.

    ``value`` may be ``None`` only when ``label`` is UNKNOWN (§7: an
    unavailable fact is UNKNOWN, never a fabricated placeholder).
    """

    field: str
    value: Any
    label: EvidenceLabel
    source: Optional[str] = None
    retrieved_at: Optional[str] = None
    note: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "label", parse_label(self.label))
        if not isinstance(self.field, str) or not self.field.strip():
            raise EvidenceError("claim field must be a non-empty string")
        if self.label is EvidenceLabel.UNKNOWN:
            if self.value is not None:
                raise EvidenceError("an UNKNOWN claim must not carry a value")
        elif self.value is None:
            raise EvidenceError("a non-UNKNOWN claim requires a value")
        for name in ("source", "retrieved_at", "note"):
            item = getattr(self, name)
            if item is not None and not isinstance(item, str):
                raise EvidenceError(f"claim {name} must be a string or None")

    @property
    def rank(self) -> int:
        return _RANK[self.label]

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready dict (label as its canonical string value)."""
        return {
            "field": self.field,
            "value": self.value,
            "label": self.label.value,
            "source": self.source,
            "retrieved_at": self.retrieved_at,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Claim":
        """Rebuild a claim from :meth:`to_dict` output."""
        if not isinstance(data, dict):
            raise EvidenceError("claim data must be a mapping")
        try:
            return cls(
                field=data["field"],
                value=data.get("value"),
                label=data["label"],
                source=data.get("source"),
                retrieved_at=data.get("retrieved_at"),
                note=data.get("note"),
            )
        except KeyError as exc:
            raise EvidenceError(f"claim missing required key: {exc}") from exc


__all__ = [
    "EVIDENCE_LABELS",
    "EvidenceError",
    "EvidenceLabel",
    "Claim",
    "compare",
    "is_stronger",
    "parse_label",
    "rank",
    "strongest",
]