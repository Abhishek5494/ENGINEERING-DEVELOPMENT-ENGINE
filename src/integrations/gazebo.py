"""Gazebo integration (T-1101, MASTER §17/§18).

Loads a caller-supplied SDF world/URDF model and runs Gazebo headless
(server-only) for a bounded number of steps, recording the run as labelled
evidence. Gazebo is the robotics/physics authority: it performs the
simulation. Commands run only when Gazebo is installed; otherwise the
capability reports UNAVAILABLE and its live test SKIPs (MASTER §46).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePath
from typing import Mapping, Sequence

from src.core.config import MODELS_DIR
from src.core.evidence import EvidenceLabel
from src.rea.records import EvidenceEntry

GAZEBO_TOOLS: tuple[str, ...] = ("gz", "gz.exe", "gazebo", "gazebo.exe")


class GazeboError(Exception):
    """Raised for an unwritable world or a missing Gazebo-produced output."""


class GazeboUnavailable(RuntimeError):
    """Raised when a run is requested but Gazebo is not installed."""


@dataclass(frozen=True)
class GazeboRun:
    """Outcome of an attempted headless Gazebo run."""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


def gazebo_cli(which=shutil.which) -> str | None:
    """Return the resolved Gazebo console path, or ``None`` when absent."""
    for name in GAZEBO_TOOLS:
        resolved = which(name)
        if resolved:
            return resolved
    return None


def write_world(
    path: str | Path,
    world: str,
    overwrite: bool = False,
    base: str | Path | None = None,
) -> Path:
    """Write an SDF/URDF document under ``base`` (default `models/`)."""
    if not world.strip():
        raise GazeboError("world must be non-empty")
    root = (Path(base) if base is not None else MODELS_DIR).resolve()
    candidate = Path(path)
    target = candidate if candidate.is_absolute() else root / candidate
    target = target.resolve()
    if target != root and root not in target.parents:
        raise GazeboError(f"refusing to write outside {root}: {target}")
    if target.exists() and not overwrite:
        raise GazeboError(f"world already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(world, encoding="utf-8")
    return target


def run_headless(
    world: str | Path,
    iterations: int = 1000,
    which=shutil.which,
    run=subprocess.run,
    timeout: int = 600,
) -> GazeboRun:
    """Run Gazebo server-only (headless) for a bounded number of steps."""
    executable = gazebo_cli(which=which)
    if executable is None:
        raise GazeboUnavailable(
            "Gazebo is not installed; robotics simulation is UNAVAILABLE"
        )
    source = Path(world)
    if not source.exists():
        raise GazeboError(f"world does not exist: {source}")
    if iterations < 0:
        raise GazeboError("iterations must be >= 0")
    stem = Path(executable).stem.lower()
    if stem.startswith("gz"):
        command = (
            executable,
            "sim",
            "-s",
            "-r",
            "--iterations",
            str(iterations),
            str(source),
        )
    else:
        command = (executable, "-s", "--iterations", str(iterations), str(source))
    completed = run(
        list(command),
        capture_output=True,
        text=True,
        cwd=str(source.parent),
        timeout=timeout,
    )
    return GazeboRun(
        command=command,
        returncode=int(completed.returncode),
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def verify_outputs(
    directory: str | Path, names: Sequence[str]
) -> dict[str, int]:
    """Return {filename: size} for expected outputs; raise if any missing."""
    root = Path(directory)
    sizes: dict[str, int] = {}
    for name in names:
        artifact = root / name
        if not artifact.is_file():
            raise GazeboError(f"expected Gazebo output missing: {artifact}")
        sizes[name] = artifact.stat().st_size
    return sizes


def gazebo_evidence(
    operation: str,
    run: "GazeboRun | None" = None,
    outputs: "Mapping[str, int] | None" = None,
) -> tuple[EvidenceEntry, ...]:
    """Return labelled evidence about a Gazebo run."""
    entries: list[EvidenceEntry] = []
    if run is not None:
        entries.append(
            EvidenceEntry(
                f"Gazebo {operation} simulation exit code {run.returncode}",
                EvidenceLabel.SIMULATED,
            )
        )
    for filename, size in (outputs or {}).items():
        entries.append(
            EvidenceEntry(
                f"Gazebo output {filename}: {size} bytes",
                EvidenceLabel.OBSERVED,
            )
        )
    return tuple(entries)


__all__ = [
    "GAZEBO_TOOLS",
    "GazeboError",
    "GazeboRun",
    "GazeboUnavailable",
    "gazebo_cli",
    "gazebo_evidence",
    "run_headless",
    "verify_outputs",
    "write_world",
]