"""Cross-platform text/path hardening (T-1601, MASTER §27/§47).

Small, dependency-free helpers that make repository text and path handling
identical on Windows and POSIX: newline normalisation, UTF-8 I/O, a line-
ending audit, and containment checks for the repo-confined writers.

Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


class CrossPlatformError(ValueError):
    """Raised for an unreadable file or an invalid containment argument."""


def normalise_newlines(text: str) -> str:
    """Convert CRLF and lone CR to LF; LF stays LF."""
    if not isinstance(text, str):
        raise CrossPlatformError("text must be a string")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def read_text_utf8(path: str | Path) -> str:
    """Read a file as UTF-8 (tolerating a BOM), returning LF-normalised text."""
    resolved = Path(path)
    try:
        raw = resolved.read_bytes()
    except OSError as exc:
        raise CrossPlatformError(f"cannot read {resolved}: {exc}") from exc
    text = raw.decode("utf-8-sig")
    return normalise_newlines(text)


def write_text_lf(path: str | Path, text: str) -> Path:
    """Write UTF-8 text with LF-only newlines (no platform translation)."""
    normalised = normalise_newlines(text)
    target = Path(path)
    target.write_bytes(normalised.encode("utf-8"))
    return target


@dataclass(frozen=True)
class LineEndingReport:
    """Observed line-ending classification for one file."""

    path: str
    kind: str  # "none" | "lf" | "crlf" | "mixed"
    size: int


def line_ending_report(paths: Iterable[str | Path]) -> tuple[LineEndingReport, ...]:
    """Classify the line endings of each file (OBSERVED)."""
    reports: list[LineEndingReport] = []
    for item in paths:
        resolved = Path(item)
        try:
            raw = resolved.read_bytes()
        except OSError as exc:
            raise CrossPlatformError(f"cannot read {resolved}: {exc}") from exc
        has_crlf = b"\r\n" in raw
        stripped = raw.replace(b"\r\n", b"")
        has_cr = b"\r" in stripped
        has_lf = b"\n" in stripped
        if has_crlf and (has_cr or has_lf):
            kind = "mixed"
        elif has_crlf:
            kind = "crlf"
        elif has_cr or has_lf:
            kind = "lf"
        else:
            kind = "none"
        reports.append(
            LineEndingReport(path=str(resolved), kind=kind, size=len(raw))
        )
    return tuple(reports)


def path_within(path: str | Path, root: str | Path) -> bool:
    """Return True when ``path`` lies inside ``root`` (lexical, no escape)."""
    resolved_root = Path(root).resolve()
    candidate = Path(path)
    resolved = candidate.resolve() if candidate.is_absolute() else (
        resolved_root / candidate
    ).resolve()
    return resolved == resolved_root or resolved_root in resolved.parents


__all__ = [
    "CrossPlatformError",
    "LineEndingReport",
    "line_ending_report",
    "normalise_newlines",
    "path_within",
    "read_text_utf8",
    "write_text_lf",
]