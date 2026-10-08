"""ngspice integration (T-1002, MASTER §17/§18).

Drives ngspice in batch mode (``ngspice -b -o``) to simulate a
caller-supplied SPICE netlist and parses the operating point. ngspice is
the circuit authority: it performs the simulation. Commands run only when
ngspice is installed; otherwise the capability reports UNAVAILABLE and its
live test SKIPs (MASTER §46).
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from src.core.config import SIMULATIONS_DIR
from src.core.evidence import EvidenceLabel
from src.rea.records import EvidenceEntry

NGSPICE_TOOLS: tuple[str, ...] = (
    "ngspice",
    "ngspice.exe",
    "ngspice_con",
    "ngspice_con.exe",
)

_NUMBER = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_OP_LINE = re.compile(rf"^\s*(?P<node>[A-Za-z_][\w.\[\]!-]*)\s+(?P<value>{_NUMBER})\s*$")
_HEADER_TOKENS = {"node", "voltage", "----", "no.", "of", "data", "rows"}


class NgspiceError(Exception):
    """Raised for an unwritable netlist or a missing/undecipherable output."""


class NgspiceUnavailable(RuntimeError):
    """Raised when a simulation is requested but ngspice is not installed."""


@dataclass(frozen=True)
class NgspiceRun:
    """Outcome of an attempted ngspice batch run."""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


def ngspice_cli(which=shutil.which) -> str | None:
    """Return the resolved ngspice console path, or ``None`` when absent."""
    for name in NGSPICE_TOOLS:
        resolved = which(name)
        if resolved:
            return resolved
    return None


def write_netlist(
    path: str | Path,
    netlist: str,
    overwrite: bool = False,
    base: str | Path | None = None,
) -> Path:
    """Write a SPICE netlist under ``base`` (default `simulations/`)."""
    if not netlist.strip():
        raise NgspiceError("netlist must be non-empty")
    root = (Path(base) if base is not None else SIMULATIONS_DIR).resolve()
    candidate = Path(path)
    target = candidate if candidate.is_absolute() else root / candidate
    target = target.resolve()
    if target != root and root not in target.parents:
        raise NgspiceError(f"refusing to write outside {root}: {target}")
    if target.exists() and not overwrite:
        raise NgspiceError(f"netlist already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(netlist, encoding="utf-8")
    return target


def run_simulation(
    netlist: str | Path,
    output: str | Path,
    which=shutil.which,
    run=subprocess.run,
    timeout: int = 600,
) -> NgspiceRun:
    """Run an ngspice batch simulation, writing output to ``output``."""
    executable = ngspice_cli(which=which)
    if executable is None:
        raise NgspiceUnavailable(
            "ngspice is not installed; circuit simulation is UNAVAILABLE"
        )
    source = Path(netlist)
    if not source.exists():
        raise NgspiceError(f"netlist does not exist: {source}")
    command = (executable, "-b", "-o", str(output), str(source))
    completed = run(
        list(command),
        capture_output=True,
        text=True,
        cwd=str(source.parent),
        timeout=timeout,
    )
    return NgspiceRun(
        command=command,
        returncode=int(completed.returncode),
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def parse_op_point(text: str) -> dict[str, float]:
    """Parse an ngspice operating-point listing into {node: voltage}."""
    results: dict[str, float] = {}
    for line in text.splitlines():
        match = _OP_LINE.match(line)
        if not match:
            continue
        node = match.group("node")
        if node.lower() in _HEADER_TOKENS:
            continue
        try:
            results[node] = float(match.group("value"))
        except ValueError:
            continue
    if not results:
        raise NgspiceError("no operating-point block found in output")
    return results


def verify_outputs(
    directory: str | Path, names: Sequence[str]
) -> dict[str, int]:
    """Return {filename: size} for expected outputs; raise if any missing."""
    root = Path(directory)
    sizes: dict[str, int] = {}
    for name in names:
        artifact = root / name
        if not artifact.is_file():
            raise NgspiceError(f"expected ngspice output missing: {artifact}")
        sizes[name] = artifact.stat().st_size
    return sizes


def ngspice_evidence(
    analysis: str,
    run: "NgspiceRun | None" = None,
    results: Mapping[str, float] | None = None,
    outputs: Mapping[str, int] | None = None,
) -> tuple[EvidenceEntry, ...]:
    """Return labelled evidence about an ngspice simulation."""
    entries: list[EvidenceEntry] = []
    if run is not None:
        entries.append(
            EvidenceEntry(
                f"ngspice {analysis} exit code {run.returncode}",
                EvidenceLabel.OBSERVED,
            )
        )
    for node, value in (results or {}).items():
        entries.append(
            EvidenceEntry(
                f"simulated operating point {node} = {value:g} V",
                EvidenceLabel.SIMULATED,
            )
        )
    for filename, size in (outputs or {}).items():
        entries.append(
            EvidenceEntry(
                f"ngspice output {filename}: {size} bytes",
                EvidenceLabel.OBSERVED,
            )
        )
    return tuple(entries)


__all__ = [
    "NGSPICE_TOOLS",
    "NgspiceError",
    "NgspiceRun",
    "NgspiceUnavailable",
    "ngspice_cli",
    "ngspice_evidence",
    "parse_op_point",
    "run_simulation",
    "verify_outputs",
    "write_netlist",
]