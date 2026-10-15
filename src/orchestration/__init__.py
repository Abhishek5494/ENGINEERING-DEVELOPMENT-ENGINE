"""orchestration package — unified engineering workflow (T-1301, PARTIAL).

Coordinates the MASTER §50 pipeline over the subsystems that exist in this
repository. Scrapling acquisition (T-0404/T-0502) is install-gated (B-2), and
no live Taiga-S1 inference provider is wired (T-0601/T-0602 complete), so
those stages are reported as BLOCKED rather than faked.
"""

from src.orchestration.workflow import (
    StageResult,
    StageStatus,
    WORKFLOW_STAGES,
    WorkflowError,
    WorkflowReport,
    WorkflowStage,
    run_workflow,
    write_project,
)

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
