"""Tests for the project-state persistence library (T-0301)."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core import state as state_mod
from src.core.config import REPO_ROOT
from src.core.state import (
    REQUIRED_STATE_SECTIONS,
    TASK_STATES,
    TaskStateError,
    normalise_state,
    parse_next_task,
    parse_roadmap_tasks,
    parse_state_sections,
    read_text,
    require_state_sections,
    set_next_task_state,
    set_roadmap_task_state,
    set_state_section,
    write_text,
)

ROADMAP = REPO_ROOT / "roadmap.md"
NEXT_TASK = REPO_ROOT / "next-task.md"
PROJECT_STATE = REPO_ROOT / "project-state.md"


def test_task_states_exact_section_32() -> None:
    assert TASK_STATES == (
        "PLANNED",
        "READY",
        "IN_PROGRESS",
        "BLOCKED",
        "COMPLETE",
        "DEFERRED",
        "CANCELLED",
    )


def test_normalise_state_variants_and_rejection() -> None:
    assert normalise_state(" ready ") == "READY"
    assert normalise_state("in_progress") == "IN_PROGRESS"
    for bad in ("DONE", "", "  ", None, 5):
        with pytest.raises(TaskStateError):
            normalise_state(bad)


def test_parse_roadmap_tasks_real_file() -> None:
    tasks = parse_roadmap_tasks(read_text(ROADMAP))
    by_id = {t.id: t for t in tasks}
    assert len(tasks) >= 35
    assert by_id["T-0202"].state == "COMPLETE"
    assert by_id["T-0202"].phase == "2"
    assert by_id["T-0202"].dependencies == ("T-0001",)
    assert by_id["T-0301"].state == "COMPLETE"
    assert by_id["T-0403"].state == "COMPLETE"
    assert by_id["T-0701"].state == "COMPLETE"
    assert by_id["T-0702"].state == "COMPLETE"
    assert by_id["T-0801"].state == "COMPLETE"
    assert by_id["T-0901"].state == "READY"
    assert by_id["T-0501"].state == "BLOCKED"
    assert by_id["T-0602"].state == "BLOCKED"


def test_parse_roadmap_tasks_rejects_invalid_state() -> None:
    text = "| T-9999 | Thing | 1 | T-0001 | DONE |\n"
    with pytest.raises(TaskStateError):
        parse_roadmap_tasks(text)


def test_set_roadmap_state_idempotent_byte_identical() -> None:
    text = read_text(ROADMAP)
    task = {t.id: t for t in parse_roadmap_tasks(text)}["T-0302"]
    assert set_roadmap_task_state(text, "T-0302", task.state) == text


def test_set_roadmap_state_is_idempotent_after_reconcile() -> None:
    text = read_text(ROADMAP)
    once = set_roadmap_task_state(text, "T-0601", "BLOCKED")
    assert set_roadmap_task_state(once, "T-0601", "BLOCKED") == once


def test_set_roadmap_state_updates_cell_and_marker() -> None:
    text = read_text(ROADMAP)
    updated = set_roadmap_task_state(text, "T-0401", "IN_PROGRESS")
    assert updated != text
    by_id = {t.id: t for t in parse_roadmap_tasks(updated)}
    assert by_id["T-0401"].state == "IN_PROGRESS"
    assert (
        "**T-0401 — Component data model + schema + storage** — `IN_PROGRESS`"
        in updated
    )
    assert len(updated.splitlines()) == len(text.splitlines())


def test_set_roadmap_state_changes_only_intended_lines() -> None:
    text = read_text(ROADMAP)
    updated = set_roadmap_task_state(text, "T-0401", "BLOCKED")
    old_lines = text.splitlines()
    new_lines = updated.splitlines()
    assert len(old_lines) == len(new_lines)
    changed = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
    assert len(changed) == 2  # table row + detail marker only


def test_set_roadmap_state_rejects_unknown_and_invalid() -> None:
    text = read_text(ROADMAP)
    with pytest.raises(TaskStateError):
        set_roadmap_task_state(text, "T-9999", "READY")
    with pytest.raises(TaskStateError):
        set_roadmap_task_state(text, "T-0301", "DONE")


def test_parse_next_task_real_file() -> None:
    task = parse_next_task(read_text(NEXT_TASK))
    assert task.id == "T-0901"
    assert task.state in TASK_STATES
    assert "freecad" in task.title.lower()


def test_set_next_task_state_roundtrip_and_update() -> None:
    text = read_text(NEXT_TASK)
    task = parse_next_task(text)
    assert set_next_task_state(text, task.state) == text
    updated = set_next_task_state(text, "IN_PROGRESS")
    re = parse_next_task(updated)
    assert re.state == "IN_PROGRESS"
    assert re.id == task.id


def test_set_next_task_state_rejects_invalid() -> None:
    text = read_text(NEXT_TASK)
    with pytest.raises(TaskStateError):
        set_next_task_state(text, "DONE")
    with pytest.raises(TaskStateError):
        set_next_task_state("no state line here", "READY")


def test_parse_state_sections_real_file() -> None:
    headings = {s.heading.lower() for s in parse_state_sections(read_text(PROJECT_STATE))}
    for required in REQUIRED_STATE_SECTIONS:
        assert required in headings


def test_require_state_sections() -> None:
    require_state_sections(read_text(PROJECT_STATE))
    with pytest.raises(TaskStateError):
        require_state_sections("## Current phase\nonly one section\n")


def test_set_state_section_roundtrip_byte_identical() -> None:
    text = read_text(PROJECT_STATE)
    section = next(s for s in parse_state_sections(text) if s.heading == "Next action")
    assert set_state_section(text, "Next action", section.body) == text


def test_set_state_section_preserves_others() -> None:
    text = "## A\n\nalpha\n\n## B\n\nbeta\n"
    original = parse_state_sections(text)
    revised = parse_state_sections(set_state_section(text, "A", "ONE\n"))
    assert [s.heading for s in revised] == [s.heading for s in original]
    assert [s.body for s in revised if s.heading != "A"] == [
        s.body for s in original if s.heading != "A"
    ]
    assert next(s.body for s in revised if s.heading == "A") == "ONE\n"
    with pytest.raises(TaskStateError):
        set_state_section(text, "C", "x")


def test_set_state_section_updates_only_target() -> None:
    text = read_text(PROJECT_STATE)
    updated = set_state_section(text, "Last update", "NEW BODY\n")
    assert "NEW BODY" in updated
    other = [
        s
        for s in parse_state_sections(updated)
        if s.heading != "Last update"
    ]
    original_other = [
        s for s in parse_state_sections(text) if s.heading != "Last update"
    ]
    assert [s.body for s in other] == [s.body for s in original_other]
    with pytest.raises(TaskStateError):
        set_state_section(text, "Nonexistent", "x")


def test_read_write_text_roundtrip(tmp_path: Path) -> None:
    target = tmp_path / "f.md"
    write_text(target, "hello\nworld\n")
    assert read_text(target) == "hello\nworld\n"


def test_read_text_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(TaskStateError):
        read_text(tmp_path / "missing.md")


def test_core_reexports_state() -> None:
    from src.core import TASK_STATES as ReStates
    from src.core import TaskStateError as ReError
    from src.core import parse_roadmap_tasks as re_parse

    assert ReStates == TASK_STATES
    assert ReError is state_mod.TaskStateError
    assert callable(re_parse)
    assert len(parse_roadmap_tasks(read_text(ROADMAP))) > 0
    assert normalise_state("complete") == "COMPLETE"