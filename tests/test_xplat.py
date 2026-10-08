"""Tests for cross-platform text/path hardening (T-1601)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.config import REPO_ROOT
from src.core.xplat import (
    CrossPlatformError,
    LineEndingReport,
    line_ending_report,
    normalise_newlines,
    path_within,
    read_text_utf8,
    write_text_lf,
)


def test_normalise_newlines() -> None:
    assert normalise_newlines("a\r\nb\rc\nd") == "a\nb\nc\nd"
    assert normalise_newlines("plain\n") == "plain\n"


def test_read_write_roundtrip_lf(tmp_path) -> None:
    target = write_text_lf(tmp_path / "x.txt", "a\r\nb\r\n")
    assert (tmp_path / "x.txt").read_bytes() == b"a\nb\n"
    assert read_text_utf8(target) == "a\nb\n"


def test_read_text_utf8_tolerates_bom(tmp_path) -> None:
    raw = ("\ufeffhello\r\nworld").encode("utf-8")
    (tmp_path / "bom.txt").write_bytes(raw)
    assert read_text_utf8(tmp_path / "bom.txt") == "hello\nworld"


def test_line_ending_report_classifies(tmp_path) -> None:
    (tmp_path / "lf.txt").write_bytes(b"a\nb\n")
    (tmp_path / "crlf.txt").write_bytes(b"a\r\nb\r\n")
    (tmp_path / "mixed.txt").write_bytes(b"a\r\nb\n")
    (tmp_path / "none.txt").write_bytes(b"abc")
    reports = {
        r.path: r.kind
        for r in line_ending_report(
            [tmp_path / n for n in ("lf.txt", "crlf.txt", "mixed.txt", "none.txt")]
        )
    }
    assert reports[str(tmp_path / "lf.txt")] == "lf"
    assert reports[str(tmp_path / "crlf.txt")] == "crlf"
    assert reports[str(tmp_path / "mixed.txt")] == "mixed"
    assert reports[str(tmp_path / "none.txt")] == "none"


def test_line_ending_report_missing_file_raises(tmp_path) -> None:
    with pytest.raises(CrossPlatformError):
        line_ending_report([tmp_path / "nope.txt"])


def test_path_within(tmp_path) -> None:
    inside = tmp_path / "sub" / "file.txt"
    inside.parent.mkdir()
    inside.write_text("x")
    assert path_within(inside, tmp_path)
    assert path_within("sub", tmp_path)
    assert not path_within(tmp_path / ".." / "escape.txt", tmp_path)
    assert not path_within(tmp_path.parent, tmp_path)


def test_live_scripts_are_posix_lf() -> None:
    scripts = sorted((REPO_ROOT / "scripts").rglob("*.sh"))
    assert scripts, "expected POSIX wrapper scripts to exist"
    for report in line_ending_report(scripts):
        assert report.kind == "lf", f"{report.path} is not LF-only ({report.kind})"