"""Provider-neutral contracts (T-0602)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Sequence

EvidenceLabel = str

class ProviderError(Exception):
    pass

class ProviderUnavailable(ProviderError):
    pass

@dataclass(frozen=True)
class Evidence:
    label: EvidenceLabel
    source: str = ''
    detail: str = ''
    metadata: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class Action:
    id: str
    name: str
    description: str = ''
    metadata: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class Score:
    action_id: str
    value: float
    confidence: float = 0.0

@dataclass(frozen=True)
class Route:
    action: Action
    scores: Sequence[Score] = ()
    evidence: Optional[Evidence] = None
    policy: str = 'deterministic'

@dataclass(frozen=True)
class Result:
    actions: Sequence[Action] = ()
    routes: Sequence[Route] = ()
    evidence: Sequence[Evidence] = ()
    metadata: Optional[Dict[str, Any]] = None

class Policy(Protocol):
    def select(self, actions: Sequence[Action], context: Dict[str, Any]) -> Route:
        ...

class Capability(Protocol):
    def supports(self, context: Dict[str, Any]) -> bool:
        ...

class Provider(Protocol):
    def name(self) -> str:
        ...
    def capabilities(self) -> Sequence[Capability]:
        ...
    def route(self, actions: Sequence[Action], context: Dict[str, Any]) -> Result:
        ...

