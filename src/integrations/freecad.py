"""FreeCAD integration (T-0901, MASTER §17/§18).

Generates deterministic FreeCAD macro scripts (standard library only) that
build a parametric solid, recompute it, and export `.FCStd` + `.step`
artifacts under ``cad/``. Execution runs through the FreeCAD console binary
only when FreeCAD is installed; otherwise the capability reports
UNAVAILABLE and its live test SKIPs (MASTER §46).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.core.config import CAD_DIR
from src.core.evidence import EvidenceLabel
from src.rea.records import EvidenceEntry

FREECAD_TOOLS: tuple[str, ...] = (
    "FreeCADCmd",
    "freecadcmd",
    "FreeCADCmd.exe",
    "freecadcmd.exe",
)


class FreeCadError(Exception):
    """Raised for an invalid macro or a missing CAD artifact."""


class FreeCADUnavailable(RuntimeError):
    """Raised when execution is requested but FreeCAD is not installed."""


@dataclass(frozen=True)
class FreeCADRun:
    """Outcome of an attempted FreeCAD macro run."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


def freecad_available(which=shutil.which) -> str | None:
    """Return the resolved FreeCAD console path, or ``None`` when absent."""
    for name in FREECAD_TOOLS:
        resolved = which(name)
        if resolved:
            return resolved
    return None


def build_box_macro(
    name: str,
    length: float = 10.0,
    width: float = 10.0,
    height: float = 10.0,
    export_step: bool = True,
) -> str:
    """Return the text of a FreeCAD macro building one parametric box."""
    if not name or not name.strip():
        raise FreeCadError("name must be non-empty")
    lines = [
        "import os",
        "import FreeCAD",
        "import Part",
        "",
        f"_name = {name!r}",
        "_out_dir = os.path.dirname(os.path.abspath(__file__))",
        "doc = FreeCAD.newDocument(_name)",
        'box = doc.addObject("Part::Box", "Box")',
        f"box.Length = {float(length)!r}",
        f"box.Width = {float(width)!r}",
        f"box.Height = {float(height)!r}",
        "doc.recompute()",
        'doc.saveAs(os.path.join(_out_dir, _name + ".FCStd"))',
    ]
    if export_step:
        lines.append(
            'Part.export([box], os.path.join(_out_dir, _name + ".step"))'
        )
    lines.append("")
    return "\n".join(lines)


def write_script(
    path: str | Path,
    script: str,
    overwrite: bool = False,
    base: str | Path | None = None,
) -> Path:
    """Write a FreeCAD macro under ``base`` (default `cad/`), safely."""
    if not script.strip():
        raise FreeCadError("script must be non-empty")
    root = (Path(base) if base is not None else CAD_DIR).resolve()
    candidate = Path(path)
    target = candidate if candidate.is_absolute() else root / candidate
    target = target.resolve()
    if target != root and root not in target.parents:
        raise FreeCadError(f"refusing to write outside {root}: {target}")
    if target.exists() and not overwrite:
        raise FreeCadError(f"script already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(script, encoding="utf-8")
    return target


def run_macro(
    script: str | Path,
    timeout: int = 600,
    which=shutil.which,
    run=subprocess.run,
    cwd: str | Path | None = None,
) -> FreeCADRun:
    """Run a FreeCAD macro headless via the console binary (if present)."""
    freecad = freecad_available(which=which)
    if freecad is None:
        raise FreeCADUnavailable(
            "FreeCAD is not installed; CAD execution is UNAVAILABLE"
        )
    target = Path(script)
    if not target.exists():
        raise FreeCadError(f"macro does not exist: {target}")
    completed = run(
        [freecad, str(target)],
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd is not None else str(target.parent),
        timeout=timeout,
    )
    return FreeCADRun(
        returncode=int(completed.returncode),
        stdout=completed.stdout,
        stderr=completed.stderr,
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
            raise FreeCadError(f"expected CAD artifact missing: {artifact}")
        sizes[name] = artifact.stat().st_size
    return sizes


def cad_evidence(
    name: str,
    dimensions: tuple[float, float, float] | None = None,
    run: FreeCADRun | None = None,
    outputs: Mapping[str, int] | None = None,
) -> tuple[EvidenceEntry, ...]:
    """Return labelled evidence about a generated CAD model."""
    entries: list[EvidenceEntry] = []
    if dimensions is not None:
        length, width, height = dimensions
        entries.append(
            EvidenceEntry(
                f"generated CAD model '{name}' "
                f"({length} x {width} x {height} mm)",
                EvidenceLabel.SIMULATED,
            )
        )
    if run is not None:
        entries.append(
            EvidenceEntry(
                f"FreeCAD macro exit code {run.returncode}",
                EvidenceLabel.OBSERVED,
            )
        )
    for filename, size in (outputs or {}).items():
        entries.append(
            EvidenceEntry(
                f"CAD artifact {filename}: {size} bytes",
                EvidenceLabel.OBSERVED,
            )
        )
    return tuple(entries)


__all__ = [
    "FREECAD_TOOLS",
    "FreeCadError",
    "FreeCADRun",
    "FreeCADUnavailable",
    "build_box_macro",
    "cad_evidence",
    "freecad_available",
    "run_macro",
    "verify_outputs",
    "write_script",
]