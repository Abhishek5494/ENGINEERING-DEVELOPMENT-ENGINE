"""rea package — Reverse Engineering Engine (authorized investigations).

T-0701 establishes the ordered §18 pipeline, the authorized §19/§20
investigation record and the §21 storage templates; T-0702 adds offline
file inspection / evidence collection.
"""

from src.rea.inspection import (
    DEFAULT_READ_LIMIT,
    FileFingerprint,
    InspectionError,
    detect_file_type,
    extract_strings,
    fingerprint_file,
    inspect_target,
    probe_tools,
)
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
    with_evidence,
)
from src.rea.storage import (
    TEMPLATE_FILES,
    InvestigationExistsError,
    render_template,
    write_investigation,
)

__all__ = [
    "AuthorizationError",
    "DEFAULT_READ_LIMIT",
    "EvidenceEntry",
    "EvidenceRuleError",
    "FileFingerprint",
    "Finding",
    "InspectionError",
    "Investigation",
    "InvestigationExistsError",
    "PipelineError",
    "REA_STAGES",
    "ReaPipeline",
    "ReaStage",
    "TEMPLATE_FILES",
    "build_investigation",
    "detect_file_type",
    "extract_strings",
    "fingerprint_file",
    "inspect_target",
    "probe_tools",
    "render_template",
    "stage_index",
    "with_evidence",
    "write_investigation",
]