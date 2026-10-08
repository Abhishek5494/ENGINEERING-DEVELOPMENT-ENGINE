"""Tests for the CIE ingestion target (T-0402)."""

from __future__ import annotations

import pytest

from src.cie.target import Target, TargetError, parse_target


def test_parse_target_basic() -> None:
    target = parse_target("https://shop.example.invalid/p/123?x=1")
    assert isinstance(target, Target)
    assert target.scheme == "https"
    assert target.host == "shop.example.invalid"
    assert target.path == "/p/123"
    assert target.url == "https://shop.example.invalid/p/123?x=1"


def test_parse_target_normalises_host() -> None:
    assert parse_target("HTTP://WWW.Example.COM/x").host == "example.com"
    assert parse_target("http://example.com").scheme == "http"


def test_parse_target_strips_surrounding_whitespace() -> None:
    assert parse_target("  https://example.com/a  ").url == "https://example.com/a"


def test_parse_target_to_dict() -> None:
    data = parse_target("https://example.com/a").to_dict()
    assert data == {
        "url": "https://example.com/a",
        "scheme": "https",
        "host": "example.com",
        "path": "/a",
    }


def test_parse_target_rejects_bad_input() -> None:
    for bad in ("", "   ", "notaurl", "ftp://example.com/x", "https://", None, 5):
        try:
            parse_target(bad)
        except TargetError:
            continue
        raise AssertionError(f"expected TargetError for {bad!r}")