"""Recovery after interruption (T-1502, MASTER §42/§43).

Reconstructs the real project state from **repository evidence only** — never
from a previous AI statement or conversation memory. The entry point takes a
repository root and reads the governance documents (``MASTER.md``,
``project-state.md``, ``next-task.md``, ``roadmap.md``), then derives the
current task boundary and validates internal consistency. Any contradiction
between the documents raises `RecoveryError` instead of being silently
overwritten (§43).

Standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from src.core.config import REPO_ROOT
from src.core.state import (
    TaskStateError,
    normalise_state,
    parse_next_task,
    parse_roadmap_tasks,
    parse_state_sections,
    read_text,
    require_state_sections,
)

# MASTER §42 READ list (documents always consulted on resume).
RECOVERY_DOCUMENTS: tuple[str, ...] = (
    "MASTER.md",
    "project-state.md",
    "next-task.md",
    "roadmap.md",
)


class RecoveryError(Exception):
    """Raised when repository evidence is missing or self-contradictory."""


@dataclass(frozen=True)
class RecoveredState:
    """State reconstructed from repository evidence alone."""

    current_task_id: str
    current_task_title: str
    current_task_state: str
    task_states: Mapping[str, str]
    blockers: tuple[str, ...]

    @property
    def in_progress(self) -> tuple[str, ...]:
        return tuple(
            sorted(t for t, s in self.task_states.items() if s == "IN_PROGRESS")
        )

    @property
    def blocked(self) -> tuple[str, ...]:
        return tuple(
            sorted(t for t, s in self.task_states.items() if s == "BLOCKED")
        )


def _blockers(state_text: str) -> tuple[str, ...]:
    """Extract non-met BLOCKED lines from the project-state Blockers section."""
    for section in parse_state_sections(state_text):
        if section.heading.strip().lower() == "blockers":
            lines = [ln.strip(" -") for ln in section.body.splitlines()]
            return tuple(ln for ln in lines if ln and "BLOCKED" in ln.upper())
    return ()


def recover(root: str | Path | None = None) -> RecoveredState:
    """Reconstruct project state from repository evidence (MASTER §42).

    Reads the governance documents under ``root`` (default: the real repo
    root). Does not consult any prior conversation.
    """
    repo = Path(root) if root is not None else Path(REPO_ROOT)

    missing = [name for name in RECOVERY_DOCUMENTS if not (repo / name).is_file()]
    if missing:
        raise RecoveryError("missing recovery documents: " + ", ".join(missing))

    state_text = read_text(repo / "project-state.md")
    try:
        require_state_sections(state_text)
        boundary = parse_next_task(read_text(repo / "next-task.md"))
        roadmap = parse_roadmap_tasks(read_text(repo / "roadmap.md"))
    except TaskStateError as exc:
        raise RecoveryError(str(exc)) from exc

    task_states = {task.id: normalise_state(task.state) for task in roadmap}

    if boundary.id not in task_states:
        raise RecoveryError(f"next-task {boundary.id} is not in roadmap.md")

    return RecoveredState(
        current_task_id=boundary.id,
        current_task_title=boundary.title,
        current_task_state=boundary.state,
        task_states=task_states,
        blockers=_blockers(state_text),
    )


def recover_consistent(root: str | Path | None = None) -> RecoveredState:
    """Like `recover`, but also enforce dependency consistency.

    Raises `RecoveryError` when a READY task depends on a task that is not
    COMPLETE (it should be BLOCKED/DEFERRED instead), so a resumed run cannot
    silently proceed from an impossible state. Also refuses a boundary whose
    roadmap state is COMPLETE, and rejects an in-progress task other than the
    declared boundary.
    """
    repo = Path(root) if root is not None else Path(REPO_ROOT)
    state = recover(repo)
    tasks = {t.id: t for t in parse_roadmap_tasks(read_text(repo / "roadmap.md"))}

    if tasks[state.current_task_id].state == "COMPLETE":
        raise RecoveryError(
            f"next-task boundary {state.current_task_id} is COMPLETE; "
            "an unfinished task must be selected"
        )

    for task in tasks.values():
        if task.state == "READY":
            unmet = [
                dep
                for dep in task.dependencies
                if tasks.get(dep) is not None and tasks[dep].state != "COMPLETE"
            ]
            if unmet:
                raise RecoveryError(
                    f"{task.id} is READY but depends on incomplete "
                    + ", ".join(unmet)
                )

    if state.in_progress and state.current_task_id not in state.in_progress:
        raise RecoveryError(
            "in-progress task(s) "
            + ", ".join(state.in_progress)
            + f" disagree with the next-task boundary {state.current_task_id}"
        )
    return state


def assert_recoverable(root: str | Path | None = None) -> RecoveredState:
    """Full §42/§43 recovery check used by the continuity/release gate."""
    return recover_consistent(root)


__all__ = [
    "RECOVERY_DOCUMENTS",
    "RecoveryError",
    "RecoveredState",
    "recover",
    "recover_consistent",
    "assert_recoverable",
]