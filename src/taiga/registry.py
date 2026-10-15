"Provider registry (T-0602)"

from __future__ import annotations
from typing import Dict, Sequence
from src.taiga.contracts import Provider

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, Provider] = {}
    def register(self, name: str, provider: Provider):
        self._providers[name] = provider
    def get(self, name: str):
        return self._providers[name]
    def list(self) -> Sequence[str]:
        return tuple(self._providers.keys())

_REG = ProviderRegistry()
def get_registry() -> ProviderRegistry:
    return _REG
def register_provider(name: str, provider: Provider):
    _REG.register(name, provider)


