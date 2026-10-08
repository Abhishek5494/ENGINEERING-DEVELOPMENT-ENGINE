"""KiCad integration (T-1001, MASTER §17/§18).

Drives the KiCad command-line interface (``kicad-cli``) to run DRC/ERC and
export fabrication artifacts into ``electronics/``. KiCad is the PCB
authority: it performs the checks and produces the outputs. Commands run
only when ``kicad-cli`` is installed; otherwise the capability reports
UNAVAILABLE and its live tests SKIP (MASTER §46).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from src.core.evidence import EvidenceLabel
from src.rea.records import EvidenceEntry

KICAD_TOOLS: tuple[str, ...] = ("kicad-cli", "kicad-cli.exe")


class KiCadError(Exception):
    """Raised for a missing input or a missing KiCad-produced artifact."""


class KiCadUnavailable(RuntimeError):
    """Raised when a KiCad command is requested but KiCad is not installed."""


@dataclass(frozen=True)
class KiCadRun:
    """Outcome of an attempted kicad-cli command."""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


def kicad_cli(which=shutil.which) -> str | None:
    """Return the resolved ``kicad-cli`` path, or ``None`` when absent."""
    for name in KICAD_TOOLS:
        resolved = which(name)
        if resolved:
            return resolved
    return None


def _run(
    args: Sequence[str],
    which,
    run,
    timeout: int,
    cwd: str | Path | None,
) -> KiCadRun:
    executable = kicad_cli(which=which)
    if executable is None:
        raise KiCadUnavailable(
            "KiCad is not installed; PCB execution is UNAVAILABLE"
        )
    command = (executable, *args)
    completed = run(
        list(command),
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd is not None else None,
        timeout=timeout,
    )
    return KiCadRun(
        command=tuple(command),
        returncode=int(completed.returncode),
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def run_drc(
    board: str | Path,
    report: str | Path,
    which=shutil.which,
    run=subprocess.run,
    timeout: int = 600,
) -> KiCadRun:
    """Run a design-rule check on a board, writing a report."""
    board_path = Path(board)
    if not board_path.exists():
        raise KiCadError(f"board not found: {board}")
    return _run(
        ["pcb", "drc", "--exit-code-violations", "--output", str(report), str(board)],
        which,
        run,
        timeout,
        cwd=str(board_path.parent),
    )


def run_erc(
    schematic: str | Path,
    report: str | Path,
    which=shutil.which,
    run=subprocess.run,
    timeout: int = 600,
) -> KiCadRun:
    """Run an electrical-rule check on a schematic."""
    source = Path(schematic)
    if not source.exists():
        raise KiCadError(f"schematic does not exist: {source}")
    return _run(
        ["sch", "erc", "--exit-code-violations", "--output", str(report), str(source)],
        which,
        run,
        timeout,
        cwd=str(source.parent),
    )


def export_gerbers(
    board: str | Path,
    out_dir: str | Path,
    which=shutil.which,
    run=subprocess.run,
    timeout: int = 600,
) -> KiCadRun:
    """Export Gerber fabrication files for a board."""
    source = Path(board)
    if not source.exists():
        raise KiCadError(f"board does not exist: {source}")
    return _run(
        ["pcb", "export", "gerbers", "--output", str(out_dir), str(source)],
        which,
        run,
        timeout,
        cwd=str(source.parent),
    )


def verify_artifacts(
    directory: str | Path, names: Sequence[str]
) -> dict[str, int]:
    """Return {filename: size} for expected artifacts; raise if any missing."""
    root = Path(directory)
    sizes: dict[str, int] = {}
    for name in names:
        artifact = root / name
        if not artifact.is_file():
            raise KiCadError(f"expected KiCad artifact missing: {artifact}")
        sizes[name] = artifact.stat().st_size
    return sizes


def kicad_evidence(
    operation: str,
    run: KiCadRun | None = None,
    artifacts: Mapping[str, int] | None = None,
) -> tuple[EvidenceEntry, ...]:
    """Return labelled evidence about a KiCad operation."""
    entries: list[EvidenceEntry] = []
    if run is not None:
        entries.append(
            EvidenceEntry(
                f"kicad-cli {operation} exit code {run.returncode}",
                EvidenceLabel.OBSERVED,
            )
        )
    for filename, size in (artifacts or {}).items():
        entries.append(
            EvidenceEntry(
                f"KiCad artifact {filename}: {size} bytes",
                EvidenceLabel.OBSERVED,
            )
        )
    return tuple(entries)


__all__ = [
    "KICAD_TOOLS",
    "KiCadError",
    "KiCadRun",
    "KiCadUnavailable",
    "export_gerbers",
    "kicad_cli",
    "kicad_evidence",
    "run_drc",
    "run_erc",
    "verify_artifacts",
]