"""Engineering-tool integrations (MASTER §17/§18, Phases 8–12).

Each integration detects its external tool via PEM, drives it through a
CLI/API when present, and records outputs as labelled evidence. When a
tool is absent the capability reports UNAVAILABLE and its integration
tests SKIP — a tool is never assumed available.
"""

from src.integrations.jupyter import (
    JUPYTER_TOOL,
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