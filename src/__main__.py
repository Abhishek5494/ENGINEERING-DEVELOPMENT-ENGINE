"""Console entry point for ``python -m src`` (T-2000).

Delegates to :func:`src.cli.main` so the unified CLI can be run as
``python -m src <command>``.
"""

from __future__ import annotations

from src.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
