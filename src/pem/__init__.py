"""PEM package — Project Environment Manager (MASTER.md §22).

Current scope: system/hardware detection only (T-0101).
Tool detection, reporting and installation arrive in later tasks.

``detect_system`` is exposed lazily so that running the module directly
(``python -m src.pem.detect``) does not double-import it.
"""

from typing import Any

__all__ = ["detect_system"]


def __getattr__(name: str) -> Any:
    if name == "detect_system":
        from src.pem.detect import detect_system

        return detect_system
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
