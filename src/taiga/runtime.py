"""Resource-aware Taiga-S1 runtime selection (T-0601, MASTER §22/§38).

Deterministic and offline (standard library only). Chooses the largest
local model tier the detected hardware budget can plausibly support and
reports honestly when the budget cannot be determined or when no
inference provider is registered. No model requirement is fabricated:
the tier is a conservative ceiling derived from RAM (and noted VRAM),
labelled INFERRED (§6) — never MEASURED or OBSERVED.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional, Sequence

from src.core.evidence import EvidenceLabel, parse_label
from src.pem.detect import detect_system

GIB = 1024 ** 3

# Conservative RAM ceilings per tier. These are engineering estimates
# (MASTER §7/§38), not measured model footprints — stated as INFERRED.
_TIER_MIN_RAM: tuple[tuple[int, str], ...] = (
    (16 * GIB, "LARGE"),
    (8 * GIB, "MEDIUM"),
    (4 * GIB, "SMALL"),
    (0, "TINY"),
)


class TaigaRuntimeError(Exception):
    """Raised when a runtime selection cannot be computed."""


class ModelTier(str, Enum):
    """Local model size bands (coarse; a ceiling, not a guarantee)."""

    TINY = "TINY"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"
    LARGE = "LARGE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SystemBudget:
    """Hardware budget relevant to local inference (MASTER §38)."""

    ram_bytes: Optional[int] = None
    vram_bytes: Optional[int] = None
    has_gpu: bool = False

    @property
    def known(self) -> bool:
        return self.ram_bytes is not None


@dataclass(frozen=True)
class RuntimeSelection:
    """Outcome of resource-aware runtime selection, with its evidence label."""

    tier: ModelTier
    label: EvidenceLabel
    available: bool
    reason: str
    budget: SystemBudget

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier.value,
            "label": self.label.value,
            "available": self.available,
            "reason": self.reason,
            "budget": {
                "ram_bytes": self.budget.ram_bytes,
                "vram_bytes": self.budget.vram_bytes,
                "has_gpu": self.budget.has_gpu,
            },
        }


def _value(field: Any) -> Any:
    """Unwrap a PEM ``{"value": ..., "evidence": ...}`` field."""
    if isinstance(field, Mapping):
        return field.get("value")
    return field


def _as_positive_int(value: Any) -> Optional[int]:
    if value == "UNKNOWN" or value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def budget_from_system(system: Optional[Mapping[str, Any]] = None) -> SystemBudget:
    """Derive a :class:`SystemBudget` from a PEM system record.

    ``system`` defaults to a live ``detect_system()``. Unknown fields stay
    ``None`` — nothing is guessed (MASTER §7).
    """
    record = detect_system() if system is None else system
    gpu = _value(record.get("gpu"))
    return SystemBudget(
        ram_bytes=_as_positive_int(_value(record.get("ram_bytes"))),
        vram_bytes=_as_positive_int(_value(record.get("vram_bytes"))),
        has_gpu=bool(gpu) and gpu != "UNKNOWN",
    )


def _tier_for(ram_bytes: int) -> ModelTier:
    for threshold, name in _TIER_MIN_RAM:
        if ram_bytes >= threshold:
            return ModelTier(name)
    return ModelTier.TINY


def select_runtime(
    system: Optional[Mapping[str, Any]] = None,
    *,
    providers: Sequence[str] = (),
    registry: Any = None,
) -> RuntimeSelection:
    """Select a local model tier from the hardware budget (MASTER §38).

    ``providers`` (or a ``registry`` exposing ``list()``) are the detected
    local inference providers. When none is registered ``available`` is
    ``False`` and the result is reported as UNAVAILABLE by callers — the
    tier is still the hardware ceiling. An unknown RAM budget yields
    ``ModelTier.UNKNOWN`` / ``EvidenceLabel.UNKNOWN`` rather than a guess.
    """
    if registry is not None:
        lister = getattr(registry, "list", None)
        if not callable(lister):
            raise TaigaRuntimeError("registry must expose list()")
        providers = lister()

    budget = budget_from_system(system)
    available = bool(tuple(providers))

    if not budget.known:
        return RuntimeSelection(
            ModelTier.UNKNOWN,
            EvidenceLabel.UNKNOWN,
            available,
            "RAM budget unknown — cannot size a local model",
            budget,
        )

    tier = _tier_for(budget.ram_bytes or 0)
    reason = f"RAM ceiling {budget.ram_bytes} bytes -> {tier.value}"
    if budget.has_gpu and budget.vram_bytes is None:
        reason += "; GPU present but VRAM unknown (not used for sizing)"
    if not available:
        reason += "; no inference provider registered (runtime UNAVAILABLE)"
    return RuntimeSelection(tier, EvidenceLabel.INFERRED, available, reason, budget)


def runtime_evidence(selection: RuntimeSelection) -> tuple[str, EvidenceLabel, str]:
    """Return ``(field, label, detail)`` for a selection, for evidence records."""
    detail = getattr(selection, "reason", "")
    label = parse_label(getattr(selection, "label", EvidenceLabel.UNKNOWN))
    return ("taiga.model_tier", label, detail)


__all__ = [
    "GIB",
    "ModelTier",
    "RuntimeSelection",
    "SystemBudget",
    "TaigaRuntimeError",
    "budget_from_system",
    "runtime_evidence",
    "select_runtime",
]
