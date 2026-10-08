"""cie package — Component Intelligence Engine.

T-0401 establishes the component data model (§12/§13) and local storage.
Ingestion, provenance and source handling arrive in later tasks.
"""

from src.cie.model import (
    UNKNOWN,
    Component,
    ComponentError,
    DerivedValue,
    MotorSpec,
    is_unknown,
)
from src.cie.store import ComponentStore

__all__ = [
    "UNKNOWN",
    "Component",
    "ComponentError",
    "DerivedValue",
    "MotorSpec",
    "is_unknown",
    "ComponentStore",
]