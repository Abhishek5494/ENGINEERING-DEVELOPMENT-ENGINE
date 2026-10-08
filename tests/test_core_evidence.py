"""Tests for engineering evidence / claim primitives (T-0302)."""

from __future__ import annotations

import pytest

from src.core import evidence as ev
from src.core.evidence import (
    EVIDENCE_LABELS,
    Claim,
    EvidenceError,
    EvidenceLabel,
    compare,
    is_stronger,
    parse_label,
    rank,
    strongest,
)

CANONICAL = (
    "OBSERVED",
    "MEASURED",
    "MANUFACTURER-SPECIFIED",
    "CALCULATED",
    "SIMULATED",
    "INFERRED",
    "ASSUMED",
    "UNKNOWN",
)

# Strongest -> weakest, per ADR-0002.
ORDER = (
    "MEASURED",
    "OBSERVED",
    "SIMULATED",
    "MANUFACTURER-SPECIFIED",
    "CALCULATED",
    "ASSUMED",
    "INFERRED",
    "UNKNOWN",
)


def test_exactly_the_eight_section6_labels() -> None:
    assert len(EVIDENCE_LABELS) == 8
    assert set(EVIDENCE_LABELS) == set(CANONICAL)
    assert len(set(EVIDENCE_LABELS)) == 8
    assert {label.value for label in EvidenceLabel} == set(CANONICAL)


def test_labels_tuple_order_is_strength_order() -> None:
    assert EVIDENCE_LABELS == ORDER


def test_parse_label_canonical() -> None:
    for token in CANONICAL:
        assert parse_label(token).value == token


def test_parse_label_normalises_case_and_separators() -> None:
    assert parse_label("manufacturer-specified") is EvidenceLabel.MANUFACTURER_SPECIFIED
    assert parse_label("MANUFACTURER_SPECIFIED") is EvidenceLabel.MANUFACTURER_SPECIFIED
    assert parse_label("Manufacturer Specified") is EvidenceLabel.MANUFACTURER_SPECIFIED
    assert parse_label("  measured  ") is EvidenceLabel.MEASURED


def test_parse_label_passes_through_enum() -> None:
    assert parse_label(EvidenceLabel.SIMULATED) is EvidenceLabel.SIMULATED


@pytest.mark.parametrize("bad", ["INSTALLED", "VERIFIED", "", "   ", None, 123, "observed!"])
def test_parse_label_rejects_invalid(bad: object) -> None:
    with pytest.raises(EvidenceError):
        parse_label(bad)


def test_rank_total_order() -> None:
    ranks = [rank(token) for token in ORDER]
    assert ranks == sorted(ranks, reverse=True)
    assert len(set(ranks)) == 8
    assert rank("MEASURED") == 7
    assert rank("UNKNOWN") == 0


def test_rank_invalid_raises() -> None:
    with pytest.raises(EvidenceError):
        rank("INSTALLED")


def test_is_stronger() -> None:
    assert is_stronger("MEASURED", "UNKNOWN")
    assert not is_stronger("UNKNOWN", "MEASURED")
    assert not is_stronger("OBSERVED", "OBSERVED")


def test_compare_signs() -> None:
    assert compare("MEASURED", "UNKNOWN") == 1
    assert compare("UNKNOWN", "MEASURED") == -1
    assert compare("CALCULATED", "CALCULATED") == 0


def test_adjacent_pairs_strictly_decreasing() -> None:
    for stronger, weaker in zip(ORDER, ORDER[1:]):
        assert is_stronger(stronger, weaker)
        assert not is_stronger(weaker, stronger)


def test_strongest_returns_highest() -> None:
    claims = [
        Claim("rpm", 1000, "ASSUMED"),
        Claim("rpm", 1200, "CALCULATED"),
        Claim("rpm", 1100, "MEASURED"),
    ]
    assert strongest(claims).value == 1100


def test_strongest_stable_tie_break() -> None:
    first = Claim("x", 1, "CALCULATED", source="a")
    second = Claim("x", 2, "CALCULATED", source="b")
    assert strongest([first, second]).source == "a"


def test_strongest_empty_is_none() -> None:
    assert strongest([]) is None


def test_strongest_rejects_non_claims() -> None:
    with pytest.raises(EvidenceError):
        strongest(["not a claim"])  # type: ignore[list-item]


def test_claim_valid_and_to_dict_roundtrip() -> None:
    claim = Claim(
        field="voltage",
        value=12.0,
        label="MANUFACTURER-SPECIFIED",
        source="https://example.invalid/datasheet",
        retrieved_at="2026-10-08",
        note="nominal",
    )
    assert isinstance(claim.label, EvidenceLabel)
    data = claim.to_dict()
    assert data["label"] == "MANUFACTURER-SPECIFIED"
    assert Claim.from_dict(data) == claim


def test_claim_rejects_invalid_label() -> None:
    with pytest.raises(EvidenceError):
        Claim("v", 1, "INSTALLED")


def test_claim_non_unknown_requires_value() -> None:
    with pytest.raises(EvidenceError):
        Claim("v", None, "MEASURED")


def test_claim_unknown_must_not_carry_value() -> None:
    with pytest.raises(EvidenceError):
        Claim("v", 1, "UNKNOWN")
    assert Claim("v", None, "UNKNOWN").value is None


def test_claim_requires_non_empty_field() -> None:
    with pytest.raises(EvidenceError):
        Claim("", 1, "MEASURED")


def test_claim_optional_fields_must_be_str() -> None:
    with pytest.raises(EvidenceError):
        Claim("v", 1, "MEASURED", source=5)  # type: ignore[arg-type]


def test_claim_is_frozen() -> None:
    claim = Claim("v", 1, "MEASURED")
    with pytest.raises(Exception):
        claim.value = 2  # type: ignore[misc]


def test_core_reexports_evidence() -> None:
    from src.core import Claim as ReClaim, EVIDENCE_LABELS as ReLabels, rank as re_rank

    assert ReLabels == ev.EVIDENCE_LABELS
    assert ReClaim is ev.Claim
    assert re_rank("MEASURED") == 7