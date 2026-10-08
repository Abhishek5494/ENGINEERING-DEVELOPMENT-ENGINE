"""rea package — Reverse Engineering Engine (authorized investigations).

T-0701 establishes the ordered §18 pipeline, the authorized §19/§20
investigation record and the §21 storage templates. Actual tooling
integration arrives in T-0702.
"""

from src.rea.pipeline import (
    REA_STAGES,
    PipelineError,
    ReaPipeline,
    ReaStage,
    stage_index,
)
from src.rea.records import (
    AuthorizationError,
    EvidenceEntry,
    EvidenceRuleError,
    Finding,
    Investigation,
    build_investigation,
)
from src.rea.storage import (
    TEMPLATE_FILES,
    InvestigationExistsError,
    render_template,
    write_investigation,
)

__all__ = [
    "AuthorizationError",
    "EvidenceEntry",
    "EvidenceRuleError",
    "Finding",
    "Investigation",
    "InvestigationExistsError",
    "PipelineError",
    "REA_STAGES",
    "ReaPipeline",
    "ReaStage",
    "TEMPLATE_FILES",
    "build_investigation",
    "render_template",
    "stage_index",
    "write_investigation",
]