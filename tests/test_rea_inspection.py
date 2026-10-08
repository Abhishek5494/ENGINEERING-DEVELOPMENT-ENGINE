"""Tests for REA offline inspection (T-0702)."""

from __future__ import annotations

import hashlib

import pytest

from src.core.evidence import EvidenceLabel
from src.rea.inspection import (
    FileFingerprint,
    InspectionError,
    detect_file_type,
    extract_strings,
    fingerprint_file,
    inspect_target,
    probe_tools,
)
from src.rea.records import EvidenceEntry, build_investigation, with_evidence


def test_detect_file_type() -> None:
    assert detect_file_type(b"MZ\x90\x00") == "PE"
    assert detect_file_type(b"\x7fELF\x02\x01") == "ELF"
    assert detect_file_type(b"\xcf\xfa\xed\xfe") == "Mach-O"
    assert detect_file_type(b"PK\x03\x04rest") == "ZIP"
    assert detect_file_type(b"%PDF-1.7") == "PDF"
    assert detect_file_type(b"\x00\x01\x02\x03") == "UNKNOWN"


def test_extract_strings_respects_limits() -> None:
    data = b"\x00hello\x00ab\x00worldwide\x00"
    found = extract_strings(data, min_length=4)
    assert "hello" in found
    assert "ab" not in found  # too short
    limited = extract_strings(data, min_length=4, max_strings=1)
    assert len(limited) == 1


def test_fingerprint_matches_hashlib(tmp_path) -> None:
    payload = b"REA test payload\n" * 100
    target = tmp_path / "sample.bin"
    target.write_bytes(payload)
    fingerprint = fingerprint_file(target)
    assert isinstance(fingerprint, FileFingerprint)
    assert fingerprint.size == len(payload)
    assert fingerprint.sha256 == hashlib.sha256(payload).hexdigest()
    assert fingerprint.md5 == hashlib.md5(payload).hexdigest()
    assert fingerprint.file_type == "UNKNOWN"
    assert fingerprint.string_count >= 1
    assert fingerprint.truncated is False


def test_fingerprint_detects_pdf(tmp_path) -> None:
    target = tmp_path / "doc.pdf"
    target.write_bytes(b"%PDF-1.7\n%stuff\n")
    assert fingerprint_file(target).file_type == "PDF"


def test_fingerprint_rejects_missing_and_directory(tmp_path) -> None:
    with pytest.raises(InspectionError):
        fingerprint_file(tmp_path / "nope.bin")
    with pytest.raises(InspectionError):
        fingerprint_file(tmp_path)


def test_probe_tools_with_injected_which() -> None:
    resolved = probe_tools(
        ["python", "definitely-not-a-tool-xyz"],
        which=lambda name: "C:/x/python.exe" if name == "python" else None,
    )
    assert resolved["python"] == "C:/x/python.exe"
    assert resolved["definitely-not-a-tool-xyz"] is None


def test_inspect_target_produces_observed_evidence(tmp_path) -> None:
    target = tmp_path / "thing.bin"
    target.write_bytes(b"MZ" + b"\x00" * 10 + b"HelloString")
    entries = inspect_target(
        target,
        tools=["python", "definitely-not-a-tool-xyz"],
        which=lambda name: "C:/x/python.exe" if name == "python" else None,
    )
    assert all(isinstance(entry, EvidenceEntry) for entry in entries)
    assert all(entry.label is EvidenceLabel.OBSERVED for entry in entries)
    joined = " | ".join(entry.statement for entry in entries)
    assert "file type: PE" in joined
    assert "sha256:" in joined
    assert "tool python: present" in joined
    assert "definitely-not-a-tool-xyz: absent" in joined


def test_with_evidence_appends_and_preserves_original() -> None:
    investigation = build_investigation("demo", "thing.bin", "authorized")
    entry = EvidenceEntry("observed thing", EvidenceLabel.OBSERVED)
    updated = with_evidence(investigation, [entry], unknowns=["what is X?"])
    assert len(investigation.evidence) == 0  # original untouched
    assert updated.evidence == (entry,)
    assert updated.unknowns == ("what is X?",)
    assert updated is not investigation