"""Tests for Taiga-S1 provider-neutral contracts (T-0602) and runtime (T-0601)."""

from __future__ import annotations

import pytest

from src.core.evidence import EvidenceLabel
from src.taiga.contracts import (
    Action,
    Evidence,
    ProviderError,
    ProviderUnavailable,
    Result,
    Route,
    Score,
)
from src.taiga.registry import ProviderRegistry, get_registry, register_provider
from src.taiga.runtime import (
    GIB,
    ModelTier,
    TaigaRuntimeError,
    budget_from_system,
    runtime_evidence,
    select_runtime,
)


def test_contracts_are_frozen_dataclasses() -> None:
    action = Action(id="a1", name="modify-part")
    with pytest.raises(Exception):
        action.id = "a2"  # type: ignore[misc]
    assert action.description == ""
    assert action.metadata is None


def test_route_and_result_compose() -> None:
    action = Action(id="a1", name="modify-part")
    route = Route(action=action, scores=(Score("a1", 1.0, 0.9),))
    assert route.policy == "deterministic"
    result = Result(actions=(action,), routes=(route,), evidence=(Evidence("OBSERVED"),))
    assert result.routes[0].action is action
    assert result.evidence[0].label == "OBSERVED"


def test_provider_error_hierarchy() -> None:
    assert issubclass(ProviderUnavailable, ProviderError)


def test_registry_register_get_list() -> None:
    registry = ProviderRegistry()
    sentinel = object()
    registry.register("local", sentinel)
    assert registry.get("local") is sentinel
    assert registry.list() == ("local",)
    with pytest.raises(KeyError):
        registry.get("missing")


def test_module_registry_is_shared() -> None:
    name = "test-provider-shared"
    provider = object()
    register_provider(name, provider)
    assert get_registry().get(name) is provider
    assert name in get_registry().list()


def _system(ram_bytes: int | str, gpu: object = "UNKNOWN") -> dict:
    return {
        "ram_bytes": {"value": ram_bytes, "evidence": "OBSERVED"},
        "gpu": {"value": gpu, "evidence": "OBSERVED" if gpu != "UNKNOWN" else "UNKNOWN"},
    }


def test_budget_unwraps_pem_fields() -> None:
    budget = budget_from_system(_system(16 * GIB, gpu=["GeForce GTX 1650"]))
    assert budget.ram_bytes == 16 * GIB
    assert budget.has_gpu is True
    assert budget.vram_bytes is None
    assert budget.known is True


def test_budget_unknown_ram_is_none() -> None:
    budget = budget_from_system(_system("UNKNOWN"))
    assert budget.ram_bytes is None
    assert budget.known is False


def test_select_runtime_tiers_by_ram() -> None:
    assert select_runtime(_system(2 * GIB)).tier is ModelTier.TINY
    assert select_runtime(_system(6 * GIB)).tier is ModelTier.SMALL
    assert select_runtime(_system(12 * GIB)).tier is ModelTier.MEDIUM
    assert select_runtime(_system(32 * GIB)).tier is ModelTier.LARGE


def test_select_runtime_unknown_ram_is_unknown_label() -> None:
    selection = select_runtime(_system("UNKNOWN"))
    assert selection.tier is ModelTier.UNKNOWN
    assert selection.label is EvidenceLabel.UNKNOWN
    assert selection.available is False


def test_select_runtime_no_provider_is_unavailable() -> None:
    selection = select_runtime(_system(12 * GIB))
    assert selection.available is False
    assert selection.label is EvidenceLabel.INFERRED
    assert "UNAVAILABLE" in selection.reason


def test_select_runtime_with_providers_is_available() -> None:
    selection = select_runtime(_system(12 * GIB), providers=["local-llama"])
    assert selection.available is True
    assert selection.tier is ModelTier.MEDIUM


def test_select_runtime_accepts_registry() -> None:
    registry = ProviderRegistry()
    registry.register("local", object())
    selection = select_runtime(_system(12 * GIB), registry=registry)
    assert selection.available is True


def test_select_runtime_rejects_bad_registry() -> None:
    with pytest.raises(TaigaRuntimeError):
        select_runtime(_system(12 * GIB), registry=object())


def test_selection_to_dict_shape() -> None:
    data = select_runtime(_system(12 * GIB)).to_dict()
    assert data["tier"] == "MEDIUM"
    assert data["label"] == "INFERRED"
    assert data["budget"]["ram_bytes"] == 12 * GIB


def test_runtime_evidence_returns_label_and_detail() -> None:
    field, label, detail = runtime_evidence(select_runtime(_system(32 * GIB)))
    assert field == "taiga.model_tier"
    assert label is EvidenceLabel.INFERRED
    assert "LARGE" in detail


def test_live_select_runtime_never_crashes() -> None:
    selection = select_runtime()
    assert isinstance(selection.tier, ModelTier)
