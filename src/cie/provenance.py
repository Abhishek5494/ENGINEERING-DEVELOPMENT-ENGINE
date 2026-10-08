"""Source provenance and §10 source priority for CIE facts (T-0403).

Every CIE fact must carry where it came from (source URL + retrieval
date) and what kind of source that is. The eight source kinds are ranked
per MASTER §10; manufacturer documentation outranks marketplace listings,
which outrank AI inference.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from typing import Any

from src.cie.model import UNKNOWN, is_unknown


class ProvenanceError(Exception):
    """Raised when provenance data is missing or malformed."""


class SourceKind(str, Enum):
    """The eight source tiers of MASTER §10, most authoritative first."""

    MANUFACTURER_DATASHEET = "MANUFACTURER_DATASHEET"
    MANUFACTURER_TECHNICAL_DOCUMENTATION = "MANUFACTURER_TECHNICAL_DOCUMENTATION"
    MANUFACTURER_PRODUCT_PAGE = "MANUFACTURER_PRODUCT_PAGE"
    AUTHORIZED_DISTRIBUTOR_DOCUMENTATION = "AUTHORIZED_DISTRIBUTOR_DOCUMENTATION"
    DISTRIBUTOR_PRODUCT_DOCUMENTATION = "DISTRIBUTOR_PRODUCT_DOCUMENTATION"
    MARKETPLACE_LISTING = "MARKETPLACE_LISTING"
    COMMUNITY_INFORMATION = "COMMUNITY_INFORMATION"
    AI_INFERENCE = "AI_INFERENCE"


SOURCE_PRIORITY: tuple[SourceKind, ...] = (
    SourceKind.MANUFACTURER_DATASHEET,
    SourceKind.MANUFACTURER_TECHNICAL_DOCUMENTATION,
    SourceKind.MANUFACTURER_PRODUCT_PAGE,
    SourceKind.AUTHORIZED_DISTRIBUTOR_DOCUMENTATION,
    SourceKind.DISTRIBUTOR_PRODUCT_DOCUMENTATION,
    SourceKind.MARKETPLACE_LISTING,
    SourceKind.COMMUNITY_INFORMATION,
    SourceKind.AI_INFERENCE,
)

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_source_kind(value: Any) -> SourceKind:
    if isinstance(value, SourceKind):
        return value
    if isinstance(value, str):
        try:
            return SourceKind(value)
        except ValueError:
            pass
    raise ProvenanceError(f"unknown source kind: {value!r}")


def source_rank(kind: SourceKind | str) -> int:
    """0-based authority rank (0 = most authoritative)."""
    return SOURCE_PRIORITY.index(parse_source_kind(kind))


def is_more_authoritative(
    a: SourceKind | str, b: SourceKind | str
) -> bool:
    return source_rank(a) < source_rank(b)


@dataclass(frozen=True)
class Provenance:
    """Where a fact came from: URL, retrieval date and source kind."""

    source_url: str
    retrieval_date: str
    kind: SourceKind
    publisher: Any = UNKNOWN

    def __post_init__(self) -> None:
        if not isinstance(self.source_url, str) or not self.source_url.strip():
            raise ProvenanceError("provenance requires a source URL")
        if (
            not isinstance(self.retrieval_date, str)
            or not _DATE_RE.match(self.retrieval_date)
        ):
            raise ProvenanceError("retrieval_date must be YYYY-MM-DD")
        try:
            date.fromisoformat(self.retrieval_date)
        except ValueError as exc:
            raise ProvenanceError(f"invalid retrieval_date: {exc}") from exc
        object.__setattr__(self, "kind", parse_source_kind(self.kind))

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "source_url": self.source_url,
            "retrieval_date": self.retrieval_date,
            "kind": self.kind.value,
        }
        if not is_unknown(self.publisher):
            data["publisher"] = self.publisher
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Provenance":
        try:
            return cls(
                source_url=data["source_url"],
                retrieval_date=data["retrieval_date"],
                kind=data["kind"],
                publisher=data.get("publisher", UNKNOWN),
            )
        except KeyError as exc:
            raise ProvenanceError(f"provenance missing field: {exc}") from exc


__all__ = [
    "Provenance",
    "ProvenanceError",
    "SOURCE_PRIORITY",
    "SourceKind",
    "is_more_authoritative",
    "parse_source_kind",
    "source_rank",
]