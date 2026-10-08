"""Tests for recovery-after-interruption (T-1502, MASTER §42/§43)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.config import REPO_ROOT
from src.core.recovery import (
    RECOVERY_DOCUMENTS,
    RecoveredState,
    RecoveryError,
    assert_recoverable,
    recover,
    recover_consistent,
)

MASTER = "# MASTER\n\nstub\n"

ROADMAP = """# Roadmap

| ID | Title | Phase | Depends | State |
|----|-------|-------|---------|-------|
| T-0001 | bootstrap | 0 | - | COMPLETE |
| T-0002 | next | 1 | T-0001 | READY |
| T-0003 | blocked one | 2 | T-0009 | BLOCKED (dep missing) |
"""

NEXT_TASK = """# next-task

## Task T-0002 — next
- **State:** READY
"""

STATE = """# Project State

## Current phase
1
## Overall status
ok
## Completed phases
0
## Current task
T-0002
## Last completed task
T-0001
## Active subsystem
core
## Blockers
- T-0003 BLOCKED because dep missing.
## Known issues
none
## Architecture status
ok
## Environment status
ok
## Test status
n/a
## Validation status
n/a
## Next action
go
## Last update
now
"""


def _write_repo(root: Path, *, next_task: str = NEXT_TASK, roadmap: str = ROADMAP) -> None:
    for name in RECOVERY_DOCUMENTS:
        (root / name).write_text("", encoding="utf-8")
    (root / "MASTER.md").write_text(MASTER, encoding="utf-8")
    (root / "roadmap.md").write_text(roadmap, encoding="utf-8")
    (root / "next-task.md").write_text(next_task, encoding="utf-8")
    (root / "project-state.md").write_text(STATE, encoding="utf-8")


def test_recover_from_repository_state_only(tmp_path) -> None:
    _write_repo(tmp_path)
    state = recover(tmp_path)
    assert isinstance(state, RecoveredState)
    assert state.current_task_id == "T-0002"
    assert state.current_task_title == "next"
    assert state.current_task_state == "READY"
    assert state.task_states["T-0001"] == "COMPLETE"
    assert state.blockers == ("T-0003 BLOCKED because dep missing.",)


def test_recover_missing_document_raises(tmp_path) -> None:
    _write_repo(tmp_path)
    (tmp_path / "roadmap.md").unlink()
    with pytest.raises(RecoveryError):
        recover(tmp_path)


def test_recover_missing_section_raises(tmp_path) -> None:
    _write_repo(tmp_path)
    (tmp_path / "project-state.md").write_text("# Project State\n\n## Current phase\n1\n")
    with pytest.raises(RecoveryError):
        recover(tmp_path)


def test_boundary_not_in_roadmap_raises(tmp_path) -> None:
    _write_repo(
        tmp_path,
        next_task="# next-task\n\n## Task T-9999 — ghost\n- **State:** READY\n",
    )
    with pytest.raises(RecoveryError):
        recover_consistent(tmp_path)


def test_ready_with_incomplete_dependency_raises(tmp_path) -> None:
    roadmap = ROADMAP.replace(
        "| T-0002 | next | 1 | T-0001 | READY |",
        "| T-0002 | next | 1 | T-0003 | READY |",
    )
    _write_repo(tmp_path, roadmap=roadmap)
    with pytest.raises(RecoveryError):
        recover_consistent(tmp_path)


def test_complete_boundary_raises(tmp_path) -> None:
    _write_repo(
        tmp_path,
        next_task="# next-task\n\n## Task T-0001 — bootstrap\n- **State:** READY\n",
    )
    with pytest.raises(RecoveryError):
        recover_consistent(tmp_path)


def test_live_repository_is_recoverable() -> None:
    state = assert_recoverable(REPO_ROOT)
    assert state.current_task_id in state.task_states
    assert state.current_task_state != "COMPLETE"
    assert "T-1301" in state.blocked
    assert "T-1501" in state.blocked