"""Unified engineering workflow (T-1301, PARTIAL; MASTER §48/§50).

Coordinates the end-to-end component engineering pipeline:

    IDEA -> ACQUIRE -> IDENTIFY -> MODEL -> ANALYZE -> PYTHON/JUPYTER
         -> CAD -> ELECTRONICS -> CIRCUIT -> ROBOTICS -> VISUALISE -> VALIDATE

This is an explicitly **partial** implementation of T-1301. Two stages
depend on capabilities that are BLOCKED in this repository and are surfaced
as such rather than faked (MASTER §46):

* ``ACQUIRE`` — Scrapling acquisition (T-0404/T-0502), BLOCKED by B-2.
* ``ANALYZE`` — Taiga-S1 inference not wired (T-0601/T-0602 COMPLETE, but no
  live provider is registered), so the stage is BLOCKED rather than faked.

Every other stage either executes against a real subsystem (CIE component
model, Jupyter notebook build/validate) or reports the honest status of the
external tool it needs: ``READY`` when the tool is present (available but
not driven in this offline run), ``UNAVAILABLE`` when it is absent. No stage
ever claims work it did not perform.

Standard library only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from src.core.config import PROJECTS_DIR
from src.core.evidence import EvidenceLabel, rank as evidence_rank
from src.rea.records import EvidenceEntry

Probe = Callable[..., "str | None"]


class WorkflowError(Exception):
    """Raised when a workflow cannot be defined, run, or written."""


class WorkflowStage(str, Enum):
    """Ordered stages of the MASTER §50 component -> engineering pipeline."""

    IDEA = "IDEA"
    ACQUIRE = "ACQUIRE"
    IDENTIFY = "IDENTIFY"
    MODEL = "MODEL"
    ANALYZE = "ANALYZE"
    PYTHON = "PYTHON"
    CAD = "CAD"
    ELECTRONICS = "ELECTRONICS"
    CIRCUIT = "CIRCUIT"
    ROBOTICS = "ROBOTICS"
    VISUALISE = "VISUALISE"
    VALIDATE = "VALIDATE"


WORKFLOW_STAGES: tuple[WorkflowStage, ...] = tuple(WorkflowStage)

_TOOL_LABELS: Mapping[WorkflowStage, str] = {
    WorkflowStage.PYTHON: "Python/Jupyter",
    WorkflowStage.CAD: "FreeCAD",
    WorkflowStage.ELECTRONICS: "KiCad",
    WorkflowStage.CIRCUIT: "ngspice",
    WorkflowStage.ROBOTICS: "Gazebo",
    WorkflowStage.VISUALISE: "Blender",
}

_TOOL_STAGES: tuple[WorkflowStage, ...] = tuple(_TOOL_LABELS)


class StageStatus(str, Enum):
    """Honest status of a single pipeline stage."""

    COMPLETE = "COMPLETE"
    READY = "READY"
    UNAVAILABLE = "UNAVAILABLE"
    BLOCKED = "BLOCKED"


def _default_probes() -> dict[WorkflowStage, Probe]:
    """The real PEM-backed presence probes for each tool stage."""
    from src.integrations.blender import blender_cli
    from src.integrations.freecad import freecad_available
    from src.integrations.gazebo import gazebo_cli
    from src.integrations.jupyter import jupyter_available
    from src.integrations.kicad import kicad_cli
    from src.integrations.ngspice import ngspice_cli

    return {
        WorkflowStage.PYTHON: jupyter_available,
        WorkflowStage.CAD: freecad_available,
        WorkflowStage.ELECTRONICS: kicad_cli,
        WorkflowStage.CIRCUIT: ngspice_cli,
        WorkflowStage.ROBOTICS: gazebo_cli,
        WorkflowStage.VISUALISE: blender_cli,
    }


@dataclass(frozen=True)
class StageResult:
    """Outcome of one stage, with any labelled evidence it collected."""

    stage: WorkflowStage
    status: str
    detail: str
    evidence: tuple[EvidenceEntry, ...] = ()
    blocker: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage", WorkflowStage(self.stage))
        try:
            StageStatus(self.status)
        except ValueError as exc:
            raise WorkflowError(f"invalid stage status: {self.status!r}") from exc

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "stage": self.stage.value,
            "status": self.status,
            "detail": self.detail,
        }
        if self.evidence:
            data["evidence"] = [entry.to_dict() for entry in self.evidence]
        if self.blocker:
            data["blocker"] = self.blocker
        return data


@dataclass(frozen=True)
class WorkflowReport:
    """Evidence-labelled outcome of one partial-T-1301 pipeline run."""

    name: str
    results: tuple[StageResult, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise WorkflowError("workflow report requires a name")

    def status_of(self, stage: WorkflowStage | str) -> str | None:
        for result in self.results:
            if result.stage is WorkflowStage(stage):
                return result.status
        return None

    def _stages_with(self, status: StageStatus) -> tuple[WorkflowStage, ...]:
        return tuple(r.stage for r in self.results if r.status == status.value)

    @property
    def completed(self) -> tuple[WorkflowStage, ...]:
        return self._stages_with(StageStatus.COMPLETE)

    @property
    def blocked(self) -> tuple[WorkflowStage, ...]:
        return self._stages_with(StageStatus.BLOCKED)

    @property
    def unavailable(self) -> tuple[WorkflowStage, ...]:
        return self._stages_with(StageStatus.UNAVAILABLE)

    @property
    def ready(self) -> tuple[WorkflowStage, ...]:
        return self._stages_with(StageStatus.READY)

    @property
    def evidence(self) -> tuple[EvidenceEntry, ...]:
        return tuple(entry for r in self.results for entry in r.evidence)

    @property
    def strongest_label(self) -> EvidenceLabel:
        best = EvidenceLabel.UNKNOWN
        for entry in self.evidence:
            if evidence_rank(entry.label) > evidence_rank(best):
                best = entry.label
        return best

    @property
    def validation_level(self) -> str:
        """Honest validation level: partial whenever a stage is unmet."""
        if self.blocked or self.unavailable:
            return "PARTIALLY-VALIDATED"
        return "RUNTIME-VALIDATED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "validation_level": self.validation_level,
            "completed": [s.value for s in self.completed],
            "ready": [s.value for s in self.ready],
            "blocked": [s.value for s in self.blocked],
            "unavailable": [s.value for s in self.unavailable],
            "stages": [result.to_dict() for result in self.results],
        }


# --------------------------------------------------------------------------
# Stage builders
# --------------------------------------------------------------------------


def _idea(component: Any, identification: Any) -> StageResult:
    if component is None and identification is None:
        return StageResult(
            WorkflowStage.IDEA,
            StageStatus.UNAVAILABLE.value,
            "no component or identification supplied",
        )
    return StageResult(
        WorkflowStage.IDEA, StageStatus.COMPLETE.value, "engineering intent received"
    )


def _acquire() -> StageResult:
    return StageResult(
        WorkflowStage.ACQUIRE,
        StageStatus.BLOCKED.value,
        "Scrapling acquisition unavailable (T-0404/T-0502 blocked, B-2)",
        (EvidenceEntry("network acquisition not attempted (B-2)", EvidenceLabel.UNKNOWN),),
        blocker="T-0404/T-0502: install gated (B-2)",
    )


def _identify(component: Any, identification: Any) -> StageResult:
    if identification is not None:
        name = "?"
        to_dict = getattr(identification, "to_dict", None)
        if callable(to_dict):
            payload = to_dict()
            name = payload.get("title") or payload.get("model") or payload.get("url")
        return StageResult(
            WorkflowStage.IDENTIFY,
            StageStatus.COMPLETE.value,
            "component identity accepted",
            (
                EvidenceEntry(
                    f"component identity accepted: {name!r}", EvidenceLabel.OBSERVED
                ),
            ),
        )
    if component is not None:
        return StageResult(
            WorkflowStage.IDENTIFY,
            StageStatus.COMPLETE.value,
            "component supplied directly (acquisition bypassed)",
            (EvidenceEntry("component provided without live acquisition", EvidenceLabel.ASSUMED),),
        )
    return StageResult(
        WorkflowStage.IDENTIFY, StageStatus.UNAVAILABLE.value, "nothing to identify"
    )


def _resolve_component(component: Any, identification: Any) -> Any:
    if component is not None:
        return component
    if identification is not None:
        to_component = getattr(identification, "to_component", None)
        if callable(to_component):
            return to_component()
    return None


def _model(component: Any, identification: Any) -> StageResult:
    resolved = _resolve_component(component, identification)
    if resolved is None:
        return StageResult(
            WorkflowStage.MODEL,
            StageStatus.UNAVAILABLE.value,
            "no component record to model",
        )
    identifier = getattr(resolved, "id", "?")
    fields = len(resolved.to_dict()) if hasattr(resolved, "to_dict") else 0
    return StageResult(
        WorkflowStage.MODEL,
        StageStatus.COMPLETE.value,
        f"component {identifier!r} modelled ({fields} field(s))",
        (EvidenceEntry(f"component model created: {identifier!r}", EvidenceLabel.OBSERVED),),
    )


def _analyze() -> StageResult:
    return StageResult(
        WorkflowStage.ANALYZE,
        StageStatus.BLOCKED.value,
        "Taiga-S1 engineering analysis unavailable (no live inference provider wired)",
        blocker="T-0601/T-0602: no live Taiga-S1 inference provider registered",
    )


def _python(notebook_cells: Sequence[str], kernel: str) -> StageResult:
    from src.integrations.jupyter import build_notebook, validate_notebook

    if not notebook_cells:
        return StageResult(
            WorkflowStage.PYTHON,
            StageStatus.UNAVAILABLE.value,
            "no notebook supplied",
        )
    notebook = build_notebook(notebook_cells, kernel=kernel)
    validate_notebook(notebook)
    code_cells = sum(1 for c in notebook["cells"] if c.get("cell_type") == "code")
    return StageResult(
        WorkflowStage.PYTHON,
        StageStatus.COMPLETE.value,
        f"notebook built/validated ({code_cells} code cell(s))",
        (
            EvidenceEntry(
                f"notebook structure valid: {code_cells} code cell(s), "
                f"nbformat {notebook['nbformat']}.{notebook['nbformat_minor']}",
                EvidenceLabel.OBSERVED,
            ),
        ),
    )


def _tool_stage(stage: WorkflowStage, probe: Probe | None) -> StageResult:
    label = _TOOL_LABELS[stage]
    path = probe() if probe is not None else None
    if not path:
        return StageResult(
            stage,
            StageStatus.UNAVAILABLE.value,
            f"{label} not installed ({stage.value} UNAVAILABLE)",
            (EvidenceEntry(f"{label} unavailable on this host", EvidenceLabel.OBSERVED),),
        )
    return StageResult(
        stage,
        StageStatus.READY.value,
        f"{label} available at {path} (not driven in this run)",
        (EvidenceEntry(f"{label} detected at {path}", EvidenceLabel.OBSERVED),),
    )


def _validate(results: Sequence[StageResult]) -> StageResult:
    completed = sum(1 for r in results if r.status == StageStatus.COMPLETE.value)
    blocked = sum(1 for r in results if r.status == StageStatus.BLOCKED.value)
    unavailable = sum(1 for r in results if r.status == StageStatus.UNAVAILABLE.value)
    detail = f"{completed} complete, {blocked} blocked, {unavailable} unavailable"
    label = EvidenceLabel.OBSERVED if completed else EvidenceLabel.UNKNOWN
    return StageResult(
        WorkflowStage.VALIDATE,
        StageStatus.COMPLETE.value,
        detail,
        (EvidenceEntry(f"workflow self-validation: {detail}", label),),
    )


def run_workflow(
    name: str,
    *,
    component: Any = None,
    identification: Any = None,
    notebook_cells: Sequence[str] = (),
    kernel: str = "python3",
    probes: Mapping[WorkflowStage | str, Probe] | None = None,
) -> WorkflowReport:
    """Run the partial T-1301 pipeline, returning labelled evidence.

    Unmet capabilities are reported as BLOCKED/UNAVAILABLE, never COMPLETE
    (MASTER §46). ``component``/``identification`` are the CIE inputs;
    ``notebook_cells`` drives the Python stage; ``probes`` overrides the
    default PEM probes for tool-gated stages (used by tests).
    """
    if not isinstance(name, str) or not name.strip():
        raise WorkflowError("workflow requires a name")
    overrides = {WorkflowStage(k): v for k, v in (probes or {}).items()}
    defaults = _default_probes()

    results: list[StageResult] = [
        _idea(component, identification),
        _acquire(),
        _identify(component, identification),
        _model(component, identification),
        _analyze(),
        _python(notebook_cells, kernel),
    ]
    for stage in (WorkflowStage.CAD, WorkflowStage.ELECTRONICS, WorkflowStage.CIRCUIT,
                  WorkflowStage.ROBOTICS, WorkflowStage.VISUALISE):
        results.append(_tool_stage(stage, overrides.get(stage, defaults.get(stage))))
    results.append(_validate(results))
    return WorkflowReport(name=name, results=tuple(results))


def write_project(
    report: WorkflowReport,
    *,
    root: str | Path | None = None,
    overwrite: bool = False,
    extra: Mapping[str, str] | None = None,
) -> Path:
    """Write a workflow report under ``root/<name>/`` (default ``projects/``).

    Always writes ``workflow.json``; ``extra`` maps relative filenames to
    text content. Writes are confined to ``root`` and refuse to overwrite an
    existing file unless ``overwrite`` is set.
    """
    base = Path(root) if root is not None else PROJECTS_DIR
    base = base.resolve()
    target_dir = (base / report.name).resolve()
    if target_dir != base and base not in target_dir.parents:
        raise WorkflowError(f"refusing to write outside {base}: {target_dir}")
    files: dict[str, str] = {
        "workflow.json": json.dumps(report.to_dict(), indent=2) + "\n"
    }
    for name, content in (extra or {}).items():
        candidate = (target_dir / name).resolve()
        if candidate != target_dir and target_dir not in candidate.parents:
            raise WorkflowError(f"refusing to write outside {target_dir}: {candidate}")
        files[name] = content
    for name, content in files.items():
        target = target_dir / name
        if target.exists() and not overwrite:
            raise WorkflowError(f"refusing to overwrite existing file: {target}")
    for name, content in files.items():
        target = target_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return target_dir


__all__ = [
    "StageResult",
    "StageStatus",
    "WORKFLOW_STAGES",
    "WorkflowError",
    "WorkflowReport",
    "WorkflowStage",
    "run_workflow",
    "write_project",
]
