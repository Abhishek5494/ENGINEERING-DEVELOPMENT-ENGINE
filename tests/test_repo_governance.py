"""Governance verification tests (MASTER.md §27, §28, §29, §30, §32).

These tests make the existence and basic integrity of the project-governance
layer checkable rather than aspirational. They do NOT test engineering
subsystems, which do not exist yet.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# MASTER §27: local project memory files
MEMORY_FILES = [
    "MASTER.md",
    "README.md",
    "architecture.md",
    "requirements.md",
    "roadmap.md",
    "project-state.md",
    "next-task.md",
    "memory.md",
    "chatmem.md",
    "audit.md",
]

# MASTER §27 + §28: documentation / decisions
DOC_PATHS = [
    "docs/future-opportunities.md",
    "decisions",
]

# MASTER §28: repository structure
STRUCTURE_DIRS = [
    "src/taiga",
    "src/pem",
    "src/cie",
    "src/rea",
    "src/core",
    "components",
    "cad",
    "electronics",
    "simulations",
    "models",
    "data",
    "tests",
    "scripts/windows",
    "scripts/linux",
    "scripts/macos",
    "config",
    "docs/investigations",
    "projects",
]

TASK_STATES = {
    "PLANNED",
    "READY",
    "IN_PROGRESS",
    "BLOCKED",
    "COMPLETE",
    "DEFERRED",
    "CANCELLED",
}


@pytest.mark.parametrize("rel_path", MEMORY_FILES + DOC_PATHS)
def test_required_file_exists_and_nonempty(rel_path: str) -> None:
    path = REPO_ROOT / rel_path
    assert path.exists(), f"missing required governance file/dir: {rel_path}"
    if path.is_file():
        assert path.stat().st_size > 100, f"{rel_path} is effectively empty"


@pytest.mark.parametrize("rel_dir", STRUCTURE_DIRS)
def test_structure_dir_exists(rel_dir: str) -> None:
    assert (REPO_ROOT / rel_dir).is_dir(), f"missing structure dir: {rel_dir}"


def test_master_md_contains_governing_sections() -> None:
    text = (REPO_ROOT / "MASTER.md").read_text(encoding="utf-8")
    for marker in [
        "# 0. SYSTEM IDENTITY",
        "# 27. LOCAL PROJECT MEMORY",
        "# 30. NEXT-TASK LOCK",
        "# 46. NO FAKE COMPLETION",
        "END OF MASTER PROMPT.",
    ]:
        assert marker in text, f"MASTER.md missing section marker: {marker}"


def test_roadmap_contains_dependency_aware_task_graph() -> None:
    text = (REPO_ROOT / "roadmap.md").read_text(encoding="utf-8")
    task_ids = set(re.findall(r"\bT-\d{4}\b", text))
    assert len(task_ids) >= 10, "roadmap must define a real task graph"
    for state in TASK_STATES:
        assert state in text, f"roadmap missing task state: {state}"
    assert re.search(r"\bT-0001\b", text)
    # every task id referenced in a dependency column must itself exist
    # (\b avoids matching the "T-0010" inside "AUDIT-0010")
    for dep in set(re.findall(r"\bT-\d{4}\b", text)):
        assert dep in task_ids


def test_next_task_has_required_fields() -> None:
    text = (REPO_ROOT / "next-task.md").read_text(encoding="utf-8")
    for field in [
        "Objective",
        "Dependencies",
        "Affected components",
        "Constraints",
        "Acceptance criteria",
        "Validation requirements",
    ]:
        assert field in text, f"next-task.md missing required field: {field}"
    assert re.search(r"\bT-\d{4}\b", text), "next-task.md must name a task ID"
    states_found = set(re.findall(r"\b(?:PLANNED|READY|IN_PROGRESS|BLOCKED|"
                                  r"COMPLETE|DEFERRED|CANCELLED)\b", text))
    assert states_found, "next-task.md must declare a task state"


def test_project_state_has_required_fields() -> None:
    text = (REPO_ROOT / "project-state.md").read_text(encoding="utf-8")
    for field in [
        "Current phase",
        "Overall status",
        "Completed phases",
        "Current task",
        "Last completed task",
        "Blockers",
        "Known issues",
        "Test status",
        "Next action",
        "Last update",
    ]:
        assert field in text, f"project-state.md missing field: {field}"


def test_memory_separation() -> None:
    """§41: MEMORY is permanent knowledge, AUDIT is history,
    CHATMEM is session state — each file must serve its own role."""
    memory = (REPO_ROOT / "memory.md").read_text(encoding="utf-8").lower()
    audit = (REPO_ROOT / "audit.md").read_text(encoding="utf-8").lower()
    chatmem = (REPO_ROOT / "chatmem.md").read_text(encoding="utf-8").lower()
    assert "permanent engineering knowledge" in memory
    assert "session" in chatmem and "audit" not in chatmem.split("## ")[0]
    assert "audit" in audit and "append-only" in audit


def test_no_secret_patterns_tracked_by_gitignore() -> None:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in ["*.env", "secrets.json", "environment.json"]:
        assert pattern in gitignore, f".gitignore must exclude {pattern}"


def test_decisions_dir_has_at_least_one_adr() -> None:
    adrs = list((REPO_ROOT / "decisions").glob("ADR-*.md"))
    assert adrs, "decisions/ must contain at least one ADR"


def test_git_repository_initialized() -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0 and result.stdout.strip() == "true", (
        "repository must be a Git work tree"
    )
