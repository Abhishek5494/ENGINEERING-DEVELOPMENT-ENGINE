"""REA investigation storage + Markdown templates (T-0701, MASTER §21).

Investigations are stored separately from CIE data under
``docs/investigations/<name>/`` with exactly seven files. Files are
generated from the investigation record so the storage and the record can
never silently disagree.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from src.rea.records import EvidenceEntry, Finding, Investigation

TEMPLATE_FILES: tuple[str, ...] = (
    "scope.md",
    "evidence.md",
    "findings.md",
    "behavior.md",
    "unknowns.md",
    "limitations.md",
    "implementation-notes.md",
)


class InvestigationExistsError(Exception):
    """Raised when writing would overwrite an existing investigation."""


def _bullets(items: Iterable[str]) -> str:
    items = [str(item) for item in items]
    if not items:
        return "_None recorded._"
    return "\n".join(f"- {item}" for item in items)


def _finding_line(finding: Finding) -> str:
    marker = " (reconstructed)" if finding.reconstructed else ""
    return f"- {finding.statement} — `{finding.label.value}`{marker}"


def _evidence_line(entry: EvidenceEntry) -> str:
    source = f" (source: {entry.source})" if entry.source else ""
    return f"- {entry.statement} — `{entry.label.value}`{source}"


def render_template(filename: str, investigation: Investigation) -> str:
    """Render one §21 Markdown file for an investigation record."""
    if filename not in TEMPLATE_FILES:
        raise ValueError(f"unknown investigation template: {filename!r}")

    title = filename[:-3].replace("-", " ").title()
    header = [
        f"# {title}",
        "",
        f"- Investigation: {investigation.name}",
        f"- Target: {investigation.target}",
        f"- Authorized: {investigation.authorized}",
        f"- Authorization basis: {investigation.authorization_basis}",
        "",
    ]

    if filename == "scope.md":
        body = [investigation.scope or "_Not yet documented._"]
    elif filename == "evidence.md":
        body = [_bullets(_evidence_line(e) for e in investigation.evidence)]
    elif filename == "findings.md":
        body = [_bullets(_finding_line(f) for f in investigation.findings)]
    elif filename == "behavior.md":
        body = [_bullets(investigation.behavior_notes)]
    elif filename == "unknowns.md":
        body = [_bullets(investigation.unknowns)]
    elif filename == "limitations.md":
        body = [_bullets(investigation.limitations)]
    else:  # implementation-notes.md
        body = [_bullets(investigation.implementation_notes)]

    return "\n".join(header + body) + "\n"


def write_investigation(
    root: str | Path,
    investigation: Investigation,
    *,
    overwrite: bool = False,
) -> Path:
    """Write the seven §21 files for an investigation and return its dir."""
    base = Path(root) / investigation.name
    if base.exists() and any(base.iterdir()) and not overwrite:
        raise InvestigationExistsError(
            f"investigation already exists: {base}"
        )
    base.mkdir(parents=True, exist_ok=True)
    for filename in TEMPLATE_FILES:
        (base / filename).write_text(
            render_template(filename, investigation), encoding="utf-8"
        )
    return base


__all__ = [
    "TEMPLATE_FILES",
    "InvestigationExistsError",
    "render_template",
    "write_investigation",
]