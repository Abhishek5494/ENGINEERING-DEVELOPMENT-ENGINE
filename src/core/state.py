"""Project-state persistence library (T-0301, MASTER §29, §30, §31, §32).

Reads, validates and updates the repository's own governance state:
- task states in ``roadmap.md`` (§31/§32),
- the execution boundary in ``next-task.md`` (§30),
- the sections of ``project-state.md`` (§29).

Pure text transformations: parse/update functions return new text and
never touch the filesystem; thin ``*_file`` helpers read/write a path
only when explicitly called. Updates edit existing tokens in place, so a
no-op round-trip is byte-identical.

Standard library only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# MASTER §32. Exactly these seven.
TASK_STATES: tuple[str, ...] = (
    "PLANNED",
    "READY",
    "IN_PROGRESS",
    "BLOCKED",
    "COMPLETE",
    "DEFERRED",
    "CANCELLED",
)

# MASTER §29 required project-state.md sections (case-insensitive match).
REQUIRED_STATE_SECTIONS: tuple[str, ...] = (
    "current phase",
    "overall status",
    "completed phases",
    "current task",
    "last completed task",
    "active subsystem",
    "blockers",
    "known issues",
    "architecture status",
    "environment status",
    "test status",
    "validation status",
    "next action",
    "last update",
)


class TaskStateError(ValueError):
    """Raised for an invalid state token, task id, or malformed document."""


def normalise_state(token: object) -> str:
    """Return the canonical §32 state for ``token`` or raise."""
    if not isinstance(token, str) or not token.strip():
        raise TaskStateError(f"invalid task state: {token!r}")
    key = token.strip().upper()
    if key not in TASK_STATES:
        raise TaskStateError(f"unknown task state: {token!r}")
    return key


def _state_token(cell: str) -> str:
    match = re.match(r"\s*([A-Za-z_]+)", cell)
    if not match:
        raise TaskStateError(f"task state cell has no state token: {cell!r}")
    return normalise_state(match.group(1))


# --- roadmap ---------------------------------------------------------------

_ROW_RE = re.compile(
    r"^\|\s*(T-\d{4})\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class RoadmapTask:
    id: str
    title: str
    phase: str
    dependencies: tuple[str, ...]
    state: str
    state_cell: str
    state_cell_start: int
    state_cell_end: int


def parse_roadmap_tasks(text: str) -> list[RoadmapTask]:
    """Parse the dependency table rows from ``roadmap.md`` text."""
    tasks: list[RoadmapTask] = []
    for match in _ROW_RE.finditer(text):
        cell = match.group(5)
        deps = tuple(
            part.strip() for part in match.group(4).split(",") if part.strip()
        )
        tasks.append(
            RoadmapTask(
                id=match.group(1),
                title=match.group(2),
                phase=match.group(3),
                dependencies=deps,
                state=_state_token(cell),
                state_cell=cell,
                state_cell_start=match.start(5),
                state_cell_end=match.end(5),
            )
        )
    return tasks


def set_roadmap_task_state(text: str, task_id: str, state: object) -> str:
    """Set the state of ``task_id`` in the table and its detail marker.

    Idempotent: passing the current state returns ``text`` unchanged
    (annotations such as ``BLOCKED (reason)`` are preserved).
    """
    new_state = normalise_state(state)
    target: Optional[RoadmapTask] = None
    for task in parse_roadmap_tasks(text):
        if task.id == task_id:
            target = task
            break
    if target is None:
        raise TaskStateError(f"unknown task id: {task_id!r}")

    if target.state == new_state:
        updated = text
    else:
        updated = (
            text[: target.state_cell_start] + f" {new_state} " + text[target.state_cell_end :]
        )

    marker_re = re.compile(
        r"(?m)^(\*\*" + re.escape(task_id) + r"\b[^\n]*?—\s*`)([A-Za-z_]+)(`)"
    )

    def _replace_marker(match: re.Match[str]) -> str:
        current = normalise_state(match.group(2))
        if current == new_state:
            return match.group(0)
        return match.group(1) + new_state + match.group(3)

    return marker_re.sub(_replace_marker, updated, count=1)


# --- next-task.md ----------------------------------------------------------

_NEXT_TASK_RE = re.compile(r"^##\s+Task\s+(T-\d{4})\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)
_NEXT_STATE_RE = re.compile(r"^(\s*-\s*\*\*State:\*\*\s*)([A-Za-z_]+)(\s*)$", re.MULTILINE)


@dataclass(frozen=True)
class NextTask:
    id: str
    title: str
    state: str


def parse_next_task(text: str) -> NextTask:
    """Parse the `## Task T-XXXX — …` header and its `State:` line."""
    header = _NEXT_TASK_RE.search(text)
    if not header:
        raise TaskStateError("next-task.md is missing a '## Task T-XXXX — …' header")
    state_match = _NEXT_STATE_RE.search(text)
    if not state_match:
        raise TaskStateError("next-task.md is missing a '- **State:** …' line")
    return NextTask(
        id=header.group(1),
        title=header.group(2),
        state=normalise_state(state_match.group(2)),
    )


def set_next_task_state(text: str, state: str) -> str:
    """Replace the `State:` token in ``next-task.md`` text."""
    new_state = normalise_state(state)
    if not _NEXT_STATE_RE.search(text):
        raise TaskStateError("next-task.md is missing a '- **State:** …' line")
    return _NEXT_STATE_RE.sub(
        lambda m: m.group(1) + new_state + m.group(3), text, count=1
    )


# --- project-state.md ------------------------------------------------------

_HEADER_RE = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.MULTILINE)


@dataclass(frozen=True)
class StateSection:
    heading: str
    body: str
    body_start: int
    body_end: int


def parse_state_sections(text: str) -> list[StateSection]:
    """Return the `## …` sections of ``project-state.md`` text, in order."""
    headers = list(_HEADER_RE.finditer(text))
    sections: list[StateSection] = []
    for index, header in enumerate(headers):
        body_start = header.end()
        if text[body_start : body_start + 1] == "\n":
            body_start += 1
        body_end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        sections.append(
            StateSection(
                heading=header.group(1).strip(),
                body=text[body_start:body_end],
                body_start=body_start,
                body_end=body_end,
            )
        )
    return sections


def require_state_sections(text: str) -> None:
    """Raise `TaskStateError` if any MASTER §29 section is missing."""
    present = {section.heading.strip().lower() for section in parse_state_sections(text)}
    missing = [name for name in REQUIRED_STATE_SECTIONS if name not in present]
    if missing:
        raise TaskStateError(
            "project-state.md missing required sections: " + ", ".join(missing)
        )


def set_state_section(text: str, heading: str, body: str) -> str:
    """Replace one section body; every other byte is preserved."""
    if not isinstance(body, str):
        raise TaskStateError("section body must be a string")
    target = heading.strip().lower()
    for section in parse_state_sections(text):
        if section.heading.strip().lower() == target:
            return text[: section.body_start] + body + text[section.body_end :]
    raise TaskStateError(f"unknown project-state section: {heading!r}")


# --- optional file helpers -------------------------------------------------


def read_text(path: str | Path) -> str:
    """Read a governance file as UTF-8, raising `TaskStateError` if absent."""
    resolved = Path(path)
    if not resolved.is_file():
        raise TaskStateError(f"state file not found: {resolved}")
    return resolved.read_text(encoding="utf-8")


def write_text(path: str | Path, text: str) -> None:
    """Write text as UTF-8 (explicit opt-in; nothing is auto-written)."""
    Path(path).write_text(text, encoding="utf-8", newline="")


__all__ = [
    "TASK_STATES",
    "REQUIRED_STATE_SECTIONS",
    "TaskStateError",
    "RoadmapTask",
    "NextTask",
    "StateSection",
    "normalise_state",
    "parse_roadmap_tasks",
    "set_roadmap_task_state",
    "parse_next_task",
    "set_next_task_state",
    "parse_state_sections",
    "require_state_sections",
    "set_state_section",
    "read_text",
    "write_text",
]