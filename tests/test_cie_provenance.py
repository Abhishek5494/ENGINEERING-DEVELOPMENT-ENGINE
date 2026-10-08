"""Tests for CIE provenance + §10 source priority (T-0403)."""

from __future__ import annotations

import pytest

from src.cie.model import UNKNOWN
from src.cie.provenance import (
    SOURCE_PRIORITY,
    Provenance,
    ProvenanceError,
    SourceKind,
    is_more_authoritative,
    parse_source_kind,
    source_rank,
)


def test_source_kind_has_the_eight_tiers() -> None:
    assert len(SourceKind) == 8
    assert len(SOURCE_PRIORITY) == 8
    assert set(SOURCE_PRIORITY) == set(SourceKind)


def test_priority_order_and_rank() -> None:
    assert source_rank(SourceKind.MANUFACTURER_DATASHEET) == 0
    assert source_rank(SourceKind.AI_INFERENCE) == 7
    assert source_rank("MARKETPLACE_LISTING") == 5


def test_manufacturer_beats_marketplace_beats_ai() -> None:
    assert is_more_authoritative(
        SourceKind.MANUFACTURER_DATASHEET, SourceKind.MARKETPLACE_LISTING
    )
    assert is_more_authoritative(
        SourceKind.MARKETPLACE_LISTING, SourceKind.AI_INFERENCE
    )
    assert not is_more_authoritative(
        SourceKind.MARKETPLACE_LISTING, SourceKind.MANUFACTURER_DATASHEET
    )


def test_parse_source_kind_rejects_unknown() -> None:
    with pytest.raises(ProvenanceError):
        parse_source_kind("WIKIPEDIA")
    with pytest.raises(ProvenanceError):
        parse_source_kind(5)
    assert parse_source_kind("AI_INFERENCE") is SourceKind.AI_INFERENCE


def test_provenance_validates_and_serialises() -> None:
    prov = Provenance(
        source_url="https://maker.example.invalid/spec.pdf",
        retrieval_date="2026-10-08",
        kind=SourceKind.MANUFACTURER_DATASHEET,
    )
    assert prov.kind is SourceKind.MANUFACTURER_DATASHEET
    assert prov.to_dict() == {
        "source_url": "https://maker.example.invalid/spec.pdf",
        "retrieval_date": "2026-10-08",
        "kind": "MANUFACTURER_DATASHEET",
    }


def test_provenance_rejects_bad_url_and_date() -> None:
    with pytest.raises(ProvenanceError):
        Provenance("", "2026-10-08", SourceKind.MANUFACTURER_DATASHEET)
    with pytest.raises(ProvenanceError):
        Provenance("https://x.example.invalid", "2026/10/08", SourceKind.MARKETPLACE_LISTING)
    with pytest.raises(ProvenanceError):
        Provenance("https://x.example.invalid", "2026-13-40", SourceKind.MARKETPLACE_LISTING)


def test_provenance_publisher_optional() -> None:
    bare = Provenance("https://x.example.invalid", "2026-10-08", "MARKETPLACE_LISTING")
    assert "publisher" not in bare.to_dict()
    withpub = Provenance(
        "https://x.example.invalid", "2026-10-08", "MARKETPLACE_LISTING", publisher="ShopCo"
    )
    assert withpub.to_dict()["publisher"] == "ShopCo"


def test_provenance_roundtrip_and_missing_field() -> None:
    original = Provenance(
        "https://maker.example.invalid/s.pdf",
        "2026-10-08",
        SourceKind.MANUFACTURER_DATASHEET,
        publisher="Acme",
    )
    assert Provenance.from_dict(original.to_dict()) == original
    with pytest.raises(ProvenanceError):
        Provenance.from_dict({"source_url": "https://x.invalid"})


def test_unknown_publisher_not_serialised() -> None:
    prov = Provenance("https://x.example.invalid", "2026-10-08", "COMMUNITY_INFORMATION", publisher=UNKNOWN)
    assert "publisher" not in prov.to_dict()