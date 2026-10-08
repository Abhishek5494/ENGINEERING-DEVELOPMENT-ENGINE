"""Blender integration (T-1201, MASTER §17/§18).

Runs a caller-supplied Python script headless through
``blender --background --python`` to produce visualization artifacts under
``models/``. Blender is the visualization authority; it performs the
render. Commands run only when Blender is installed; otherwise the
capability reports UNAVAILABLE and its live test SKIPs (MASTER §46).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from src.core.config import MODELS_DIR
from src.core.evidence import EvidenceLabel
from src.rea.records import EvidenceEntry

BLENDER_TOOLS: tuple[str, ...] = ("blender", "blender.exe")


class BlenderError(Exception):
    """Raised for an unwritable script or a missing Blender artifact."""


class BlenderUnavailable(RuntimeError):
    """Raised when a render is requested but Blender is not installed."""


@dataclass(frozen=True)
class BlenderRun:
    """Outcome of an attempted headless Blender run."""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


def blender_cli(which=shutil.which) -> str | None:
    """Return the resolved Blender path, or ``None`` when absent."""
    for name in BLENDER_TOOLS:
        resolved = which(name)
        if resolved:
            return resolved
    return None


def write_script(
    path: str | Path,
    script: str,
    overwrite: bool = False,
    base: str | Path | None = None,
) -> Path:
    """Write a Blender Python script under ``base`` (default `models/`)."""
    if not script.strip():
        raise BlenderError("script must be non-empty")
    root = (Path(base) if base is not None else MODELS_DIR).resolve()
    candidate = Path(path)
    target = candidate if candidate.is_absolute() else root / candidate
    target = target.resolve()
    if target != root and root not in target.parents:
        raise BlenderError(f"refusing to write outside {root}: {target}")
    if target.exists() and not overwrite:
        raise BlenderError(f"script already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(script, encoding="utf-8")
    return target


def run_background(
    script: str | Path,
    which=shutil.which,
    run=subprocess.run,
    timeout: int = 600,
) -> BlenderRun:
    """Run a Blender Python script headless (if Blender is present)."""
    executable = blender_cli(which=which)
    if executable is None:
        raise BlenderUnavailable(
            "Blender is not installed; rendering is UNAVAILABLE"
        )
    source = Path(script)
    if not source.exists():
        raise BlenderError(f"script does not exist: {source}")
    command = (executable, "--background", "--python", str(source))
    completed = run(
        list(command),
        capture_output=True,
        text=True,
        cwd=str(source.parent),
        timeout=timeout,
    )
    return BlenderRun(
        command=command,
        returncode=int(completed.returncode),
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def verify_outputs(
    directory: str | Path, names: Sequence[str]
) -> dict[str, int]:
    """Return {filename: size} for expected artifacts; raise if any missing."""
    root = Path(directory)
    sizes: dict[str, int] = {}
    for name in names:
        artifact = root / name
        if not artifact.is_file():
            raise BlenderError(f"expected Blender artifact missing: {artifact}")
        sizes[name] = artifact.stat().st_size
    return sizes


def blender_evidence(
    operation: str,
    run: "BlenderRun | None" = None,
    outputs: "Mapping[str, int] | None" = None,
) -> tuple[EvidenceEntry, ...]:
    """Return labelled evidence about a Blender run."""
    entries: list[EvidenceEntry] = []
    if run is not None:
        entries.append(
            EvidenceEntry(
                f"Blender {operation} render exit code {run.returncode}",
                EvidenceLabel.SIMULATED,
            )
        )
    for filename, size in (outputs or {}).items():
        entries.append(
            EvidenceEntry(
                f"Blender artifact {filename}: {size} bytes",
                EvidenceLabel.OBSERVED,
            )
        )
    return tuple(entries)


__all__ = [
    "BLENDER_TOOLS",
    "BlenderError",
    "BlenderRun",
    "BlenderUnavailable",
    "blender_cli",
    "blender_evidence",
    "run_background",
    "verify_outputs",
    "write_script",
]