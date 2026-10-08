"""Python/Jupyter integration (T-0801, MASTER §17/§18).

Builds and validates nbformat v4 notebooks with the standard library and
executes them through ``jupyter nbconvert`` *only when Jupyter is
actually installed*. Results are returned as labelled evidence; when
Jupyter is absent the capability reports UNAVAILABLE rather than faking
success (MASTER §46).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.core.config import SIMULATIONS_DIR
from src.core.evidence import EvidenceLabel
from src.rea.records import EvidenceEntry

JUPYTER_TOOL = "jupyter"
NBFORMAT_MAJOR = 4
NBFORMAT_MINOR = 5


class NotebookError(Exception):
    """Raised for an invalid notebook or an unsafe/oversized write."""


class JupyterUnavailable(RuntimeError):
    """Raised when execution is requested but Jupyter is not installed."""


@dataclass(frozen=True)
class NotebookRun:
    """Outcome of an attempted notebook execution."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


def jupyter_available(which=shutil.which) -> str | None:
    """Return the resolved ``jupyter`` path, or ``None`` when absent."""
    return which(JUPYTER_TOOL)


def _code_cell(source: str) -> dict[str, Any]:
    lines = source.splitlines(keepends=True) or [""]
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines,
    }


def build_notebook(
    cells: Sequence[str],
    kernel: str = "python3",
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a minimal valid nbformat v4 notebook from code-cell sources."""
    if metadata is None:
        metadata = {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": kernel,
            },
            "language_info": {"name": "python"},
        }
    return {
        "cells": [_code_cell(cell) for cell in cells],
        "metadata": dict(metadata),
        "nbformat": NBFORMAT_MAJOR,
        "nbformat_minor": NBFORMAT_MINOR,
    }


def validate_notebook(notebook: Any) -> None:
    """Raise ``NotebookError`` unless ``notebook`` is a well-formed v4 nb."""
    if not isinstance(notebook, Mapping):
        raise NotebookError("notebook must be a mapping")
    if not isinstance(notebook.get("nbformat"), int):
        raise NotebookError("notebook.nbformat must be an integer")
    if not isinstance(notebook.get("nbformat_minor"), int):
        raise NotebookError("notebook.nbformat_minor must be an integer")
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        raise NotebookError("notebook.cells must be a list")
    for index, cell in enumerate(cells):
        if not isinstance(cell, Mapping):
            raise NotebookError(f"cell[{index}] must be a mapping")
        kind = cell.get("cell_type")
        if kind not in {"code", "markdown", "raw"}:
            raise NotebookError(f"cell[{index}].cell_type is invalid: {kind!r}")
        source = cell.get("source")
        if isinstance(source, str):
            continue
        if not isinstance(source, list) or not all(
            isinstance(line, str) for line in source
        ):
            raise NotebookError(f"cell[{index}].source must be str or list[str]")
        if kind == "code":
            if not isinstance(cell.get("outputs"), list):
                raise NotebookError(f"cell[{index}].outputs must be a list")


def write_notebook(
    path: str | Path,
    notebook: Mapping[str, Any],
    overwrite: bool = False,
    base: str | Path | None = None,
) -> Path:
    """Write a notebook under ``base`` (default `simulations/`), safely."""
    root = Path(base) if base is not None else SIMULATIONS_DIR
    root = root.resolve()
    candidate = Path(path)
    target = candidate if candidate.is_absolute() else root / candidate
    target = target.resolve()
    if target != root and root not in target.parents:
        raise NotebookError(f"refusing to write outside {root}: {target}")
    validate_notebook(notebook)
    if target.exists() and not overwrite:
        raise NotebookError(f"notebook already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    return target


def execute_notebook(
    path: str | Path,
    timeout: int = 600,
    which=shutil.which,
    run=subprocess.run,
    cwd: str | Path | None = None,
) -> NotebookRun:
    """Execute a notebook in place via ``jupyter nbconvert`` (if present)."""
    jupyter = jupyter_available(which=which)
    if jupyter is None:
        raise JupyterUnavailable(
            f"{JUPYTER_TOOL} is not installed; notebook execution is UNAVAILABLE"
        )
    target = Path(path)
    if not target.exists():
        raise NotebookError(f"notebook does not exist: {target}")
    command = [
        jupyter,
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--inplace",
        str(target),
        f"--ExecutePreprocessor.timeout={timeout}",
    ]
    completed = run(
        command,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd is not None else str(target.parent),
    )
    return NotebookRun(
        returncode=int(completed.returncode),
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def notebook_evidence(
    notebook: Mapping[str, Any], run: "NotebookRun | None" = None
) -> tuple[EvidenceEntry, ...]:
    """Describe a notebook as labelled evidence (structure + execution)."""
    validate_notebook(notebook)
    code_cells = [c for c in notebook["cells"] if c.get("cell_type") == "code"]
    entries: list[EvidenceEntry] = [
        EvidenceEntry(
            f"notebook structure valid: {len(code_cells)} code cell(s), "
            f"nbformat {notebook['nbformat']}.{notebook['nbformat_minor']}",
            EvidenceLabel.OBSERVED,
        )
    ]
    if run is not None:
        outputs = sum(
            len(c.get("outputs", [])) for c in code_cells
        )
        entries.append(
            EvidenceEntry(
                f"notebook execution exit code {run.returncode}; "
                f"{outputs} cell output block(s) produced",
                EvidenceLabel.SIMULATED,
            )
        )
    return tuple(entries)


__all__ = [
    "JUPYTER_TOOL",
    "JupyterUnavailable",
    "NotebookError",
    "NotebookRun",
    "build_notebook",
    "execute_notebook",
    "jupyter_available",
    "notebook_evidence",
    "validate_notebook",
    "write_notebook",
]