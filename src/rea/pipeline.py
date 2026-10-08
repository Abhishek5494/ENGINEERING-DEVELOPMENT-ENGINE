"""REA pipeline: the ordered investigation stages (T-0701, MASTER §18).

The stages are strictly sequential. The pipeline refuses to skip or jump
ahead, enforcing the §18 rule that the system never jumps from
"Feature X exists" to "implement Feature X" without first establishing the
observable behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PipelineError(Exception):
    """Raised when the REA pipeline is advanced out of order."""


class ReaStage(str, Enum):
    TARGET = "TARGET"
    IDENTIFY = "IDENTIFY"
    INSPECT = "INSPECT"
    COLLECT_EVIDENCE = "COLLECT_EVIDENCE"
    TRACE_BEHAVIOR = "TRACE_BEHAVIOR"
    RECONSTRUCT_UNDERSTANDING = "RECONSTRUCT_UNDERSTANDING"
    DOCUMENT_FINDINGS = "DOCUMENT_FINDINGS"
    ADAPT_REIMPLEMENT = "ADAPT_REIMPLEMENT"
    TEST = "TEST"
    VERIFY = "VERIFY"


REA_STAGES: tuple[ReaStage, ...] = tuple(ReaStage)


def stage_index(stage: ReaStage | str) -> int:
    try:
        return REA_STAGES.index(ReaStage(stage))
    except (ValueError, KeyError) as exc:
        raise PipelineError(f"unknown REA stage: {stage!r}") from exc


@dataclass
class ReaPipeline:
    """Tracks progress through the ordered REA stages for one target."""

    name: str
    completed: list[ReaStage] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise PipelineError("pipeline requires a name")

    @property
    def current(self) -> ReaStage | None:
        """The most recently reached stage (None before TARGET)."""
        return self.completed[-1] if self.completed else None

    @property
    def next_stage(self) -> ReaStage | None:
        index = len(self.completed)
        return REA_STAGES[index] if index < len(REA_STAGES) else None

    @property
    def is_complete(self) -> bool:
        return len(self.completed) == len(REA_STAGES)

    def advance(self, stage: ReaStage | str | None = None) -> ReaStage:
        """Advance to the next stage, or to ``stage`` if it is the next one."""
        expected = self.next_stage
        if expected is None:
            raise PipelineError("pipeline is already complete (VERIFY reached)")
        if stage is not None:
            requested = ReaStage(stage)
            if requested is not expected:
                raise PipelineError(
                    f"cannot jump to {requested.value}; next stage is {expected.value}"
                )
        self.completed.append(expected)
        return expected

    def has_reached(self, stage: ReaStage | str) -> bool:
        return ReaStage(stage) in self.completed

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "completed": [s.value for s in self.completed],
            "current": self.current.value if self.current else None,
            "next": self.next_stage.value if self.next_stage else None,
            "is_complete": self.is_complete,
        }


__all__ = [
    "PipelineError",
    "REA_STAGES",
    "ReaPipeline",
    "ReaStage",
    "stage_index",
]