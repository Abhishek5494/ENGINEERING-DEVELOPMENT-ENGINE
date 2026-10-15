"""Taiga-S1 provider-neutral contracts (T-0602) and runtime selection (T-0601)."""
from src.taiga.contracts import Action, Capability, Evidence, Policy, Provider, ProviderError, ProviderUnavailable, Result, Route, Score
from src.taiga.registry import ProviderRegistry, get_registry, register_provider
from src.taiga.runtime import (
    GIB,
    ModelTier,
    RuntimeSelection,
    SystemBudget,
    TaigaRuntimeError,
    budget_from_system,
    runtime_evidence,
    select_runtime,
)

__all__ = [
    'Action', 'Capability', 'Evidence', 'Policy', 'Provider', 'ProviderError',
    'ProviderUnavailable', 'Result', 'Route', 'Score', 'ProviderRegistry',
    'get_registry', 'register_provider', 'GIB', 'ModelTier', 'RuntimeSelection',
    'SystemBudget', 'TaigaRuntimeError', 'budget_from_system', 'runtime_evidence',
    'select_runtime',
]

