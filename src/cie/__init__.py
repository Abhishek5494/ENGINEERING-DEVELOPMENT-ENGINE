"""cie package — Component Intelligence Engine.

T-0401 component data model (§12/§13) + storage; T-0402 ingestion target +
exact identification (§8/§9); T-0403 provenance and source conflicts
(§10/§11). Later tasks add acquisition, search and comparison.
"""

from src.cie.conflicts import (
    Fact,
    FactError,
    FactStatus,
    FieldRecord,
    build_field_record,
    conflicting_fields,
)
from src.cie.identify import (
    Acquirer,
    Identification,
    IdentificationError,
    identify_page,
    ingest,
)
from src.cie.model import (
    UNKNOWN,
    Component,
    ComponentError,
    DerivedValue,
    MotorSpec,
    is_unknown,
)
from src.cie.provenance import (
    SOURCE_PRIORITY,
    Provenance,
    ProvenanceError,
    SourceKind,
    is_more_authoritative,
    source_rank,
)
from src.cie.store import ComponentStore
from src.cie.target import Target, TargetError, parse_target

__all__ = [
    "Acquirer",
    "Component",
    "ComponentError",
    "ComponentStore",
    "DerivedValue",
    "Fact",
    "FactError",
    "FactStatus",
    "FieldRecord",
    "Identification",
    "IdentificationError",
    "MotorSpec",
    "Provenance",
    "ProvenanceError",
    "SOURCE_PRIORITY",
    "SourceKind",
    "Target",
    "TargetError",
    "UNKNOWN",
    "build_field_record",
    "conflicting_fields",
    "identify_page",
    "ingest",
    "is_more_authoritative",
    "is_unknown",
    "parse_target",
    "source_rank",
]