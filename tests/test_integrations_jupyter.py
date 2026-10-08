"""Tests for the Python/Jupyter integration (T-0801)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from src.core.evidence import EvidenceLabel
from src.integrations.jupyter import (
    JupyterUnavailable,
    NotebookError,
    NotebookRun,
    build_notebook,
    execute_notebook,
    jupyter_available,
    notebook_evidence,
    validate_notebook,
    write_notebook,
)

RUN = """
import json
from pathlib import Path
Path("out.json").write_text(json.dumps({"answer": 6 * 7}))
""".strip()


def test_build_notebook_is_valid() -> None:
    notebook = build_notebook(["x = 1\nprint(x)", "x + 1"])
    validate_notebook(notebook)  # must not raise
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) == 2
    assert all(c["cell_type"] == "code" for c in notebook["cells"])


def test_validate_rejects_bad_objects() -> None:
    with pytest.raises(NotebookError):
        validate_notebook([])  # not a mapping
    with pytest.raises(NotebookError):
        validate_notebook({"nbformat": 4, "cells": []})  # no nbformat_minor
    with pytest.raises(NotebookError):
        validate_notebook(
            {"nbformat": 4, "nbformat_minor": 5, "cells": [{"cell_type": "bogus"}]}
        )


def test_write_notebook_roundtrip_and_no_overwrite(tmp_path) -> None:
    notebook = build_notebook(["print('hi')"])
    target = write_notebook("demo/nb.ipynb", notebook, base=tmp_path)
    assert target.exists()
    reloaded = json.loads(target.read_text(encoding="utf-8"))
    validate_notebook(reloaded)
    with pytest.raises(NotebookError):
        write_notebook("demo/nb.ipynb", notebook, base=tmp_path)
    # overwrite allowed when asked
    write_notebook("demo/nb.ipynb", notebook, overwrite=True, base=tmp_path)


def test_write_notebook_refuses_escape(tmp_path) -> None:
    notebook = build_notebook(["print('hi')"])
    with pytest.raises(NotebookError):
        write_notebook("../escaped.ipynb", notebook, base=tmp_path)


def test_jupyter_available_injectable() -> None:
    assert jupyter_available(which=lambda name: None) is None
    assert jupyter_available(which=lambda name: "C:/x/jupyter.exe") == "C:/x/jupyter.exe"


def test_execute_notebook_raises_when_absent(tmp_path) -> None:
    notebook = build_notebook(["1 + 1"])
    target = write_notebook("nb.ipynb", notebook, base=tmp_path)
    with pytest.raises(JupyterUnavailable):
        execute_notebook(target, which=lambda name: None)


def test_execute_notebook_invokes_nbconvert(tmp_path) -> None:
    notebook = build_notebook(["1 + 1"])
    target = write_notebook("nb.ipynb", notebook, base=tmp_path)
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):  # noqa: ANN001
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, "ok", "")

    result = execute_notebook(
        target, which=lambda name: "C:/x/jupyter.exe", run=fake_run
    )
    assert result == NotebookRun(0, "ok", "")
    assert result.succeeded
    assert captured["command"][0] == "C:/x/jupyter.exe"
    assert "nbconvert" in captured["command"]
    assert "--execute" in captured["command"]


def test_notebook_evidence_labels() -> None:
    notebook = build_notebook(["1 + 1"])
    structural = notebook_evidence(notebook)
    assert len(structural) == 1
    assert structural[0].label is EvidenceLabel.OBSERVED
    with_run = notebook_evidence(notebook, NotebookRun(0, "ok", ""))
    assert with_run[-1].label is EvidenceLabel.SIMULATED


@pytest.mark.skipif(
    jupyter_available() is None, reason="jupyter not installed on this host"
)
def test_execute_notebook_live(tmp_path) -> None:
    notebook = build_notebook([RUN], metadata={"kernelspec": {
        "display_name": "Python 3", "language": "python", "name": "python3"}})
    target = write_notebook("live.ipynb", notebook, base=tmp_path)
    result = execute_notebook(target, timeout=120)
    assert result.succeeded, result.stderr