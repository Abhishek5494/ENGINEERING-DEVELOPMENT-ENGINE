"""orchestration package — unified engineering workflow (T-1301, PARTIAL).

Coordinates the MASTER §50 pipeline over the subsystems that exist in this
repository. Taiga-S1 (T-0602) and Scrapling acquisition (T-0404/T-0502) are
BLOCKED, so those stages are reported as BLOCKED rather than faked.
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
