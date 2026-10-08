"""REA offline inspection + evidence collection (T-0702, MASTER §18/§19).

Fingerprints a caller-provided, authorized file — size, hashes, detected
file type and printable strings — and probes which external inspection
tools are actually available. Results are returned as labelled
`EvidenceEntry` objects. The target is only READ, never executed, and no
assumption is made about a tool that is not present.
"""

from __future__ import annotations

import hashlib
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from src.core.evidence import EvidenceLabel
from src.rea.records import EvidenceEntry

DEFAULT_READ_LIMIT = 16 * 1024 * 1024  # 16 MiB prefix used for type/strings

DEFAULT_TOOLS: tuple[str, ...] = (
    "strings",
    "objdump",
    "readelf",
    "nm",
    "dumpbin",
)


class InspectionError(Exception):
    """Raised when a path cannot be inspected (missing, directory, ...)."""


_MACHO_MAGICS = {
    b"\xfe\xed\xfa\xce",
    b"\xce\xfa\xed\xfe",
    b"\xfe\xed\xfa\xcf",
    b"\xcf\xfa\xed\xfe",
    b"\xca\xfe\xba\xbe",
    b"\xbe\xba\xfe\xca",
}


def detect_file_type(head: bytes) -> str:
    """Classify a file from its magic bytes (stdlib only)."""
    if head.startswith(b"MZ"):
        return "PE"
    if head.startswith(b"\x7fELF"):
        return "ELF"
    if len(head) >= 4 and head[:4] in _MACHO_MAGICS:
        return "Mach-O"
    if head.startswith(b"PK\x03\x04"):
        return "ZIP"
    if head.startswith(b"%PDF"):
        return "PDF"
    return "UNKNOWN"


def extract_strings(
    data: bytes, min_length: int = 4, max_strings: int = 1000
) -> list[str]:
    """Return printable ASCII runs of at least ``min_length`` characters."""
    if min_length < 1:
        raise ValueError("min_length must be >= 1")
    pattern = rb"[\x20-\x7e]{%d,}" % min_length
    found = re.findall(pattern, data)
    return [chunk.decode("ascii") for chunk in found[: max(0, max_strings)]]


@dataclass(frozen=True)
class FileFingerprint:
    """Stable identity of a file, computed without executing it."""

    path: str
    size: int
    sha256: str
    md5: str
    file_type: str
    string_count: int
    truncated: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "size": self.size,
            "sha256": self.sha256,
            "md5": self.md5,
            "file_type": self.file_type,
            "string_count": self.string_count,
            "truncated": self.truncated,
        }


def fingerprint_file(
    path: str | Path, read_limit: int = 16 * 1024 * 1024
) -> FileFingerprint:
    """Hash and characterise a file; the file is only read, never run."""
    target = Path(path)
    if not target.exists():
        raise InspectionError(f"file does not exist: {target}")
    if not target.is_file():
        raise InspectionError(f"not a regular file: {target}")
    try:
        size = target.stat().st_size
    except OSError as exc:
        raise InspectionError(f"cannot stat file: {exc}") from exc

    sha = hashlib.sha256()
    md5 = hashlib.md5()
    try:
        with target.open("rb") as handle:
            while True:
                chunk = handle.read(65536)
                if not chunk:
                    break
                sha.update(chunk)
                md5.update(chunk)
    except OSError as exc:
        raise InspectionError(f"cannot read file: {exc}") from exc

    with target.open("rb") as handle:
        head = handle.read(min(read_limit, 64))
    with target.open("rb") as handle:
        prefix = handle.read(read_limit)

    return FileFingerprint(
        path=str(target),
        size=size,
        sha256=sha.hexdigest(),
        md5=md5.hexdigest(),
        file_type=detect_file_type(head),
        string_count=len(extract_strings(prefix, min_length=4)),
        truncated=size > read_limit,
    )


def probe_tools(
    names: "Iterable[str] | None" = None, which=shutil.which
) -> dict[str, str | None]:
    """Resolve tool names to paths (None when not available)."""
    if names is None:
        names = DEFAULT_TOOLS
    return {name: which(name) for name in names}


def inspect_target(
    path: str | Path,
    tools: "Iterable[str] | None" = None,
    which=shutil.which,
) -> tuple["EvidenceEntry", ...]:
    """Collect OBSERVED evidence about a file (identity, hashes, tooling)."""
    from src.rea.records import EvidenceEntry as _EvidenceEntry
    from src.core.evidence import EvidenceLabel as _Label

    fingerprint = fingerprint_file(path)
    entries: list[_EvidenceEntry] = [
        _EvidenceEntry(f"target file: {fingerprint.path}", _Label.OBSERVED),
        _EvidenceEntry(f"size: {fingerprint.size} bytes", _Label.OBSERVED),
        _EvidenceEntry(f"sha256: {fingerprint.sha256}", _Label.OBSERVED),
        _EvidenceEntry(f"file type: {fingerprint.file_type}", _Label.OBSERVED),
        _EvidenceEntry(
            f"printable strings (>=4 chars, first 1000): {fingerprint.string_count}",
            _Label.OBSERVED,
        ),
    ]
    if fingerprint.truncated:
        entries.append(
            _EvidenceEntry(
                "note: only the first 16 MiB were scanned for strings",
                _Label.OBSERVED,
            )
        )
    for name, resolved in probe_tools(tools, which=which).items():
        state = f"present at {resolved}" if resolved else "absent"
        entries.append(_EvidenceEntry(f"inspection tool {name}: {state}", _Label.OBSERVED))
    return tuple(entries)


__all__ = [
    "DEFAULT_READ_LIMIT",
    "FileFingerprint",
    "InspectionError",
    "detect_file_type",
    "extract_strings",
    "fingerprint_file",
    "inspect_target",
    "probe_tools",
]