"""Tests for the REA pipeline (T-0701)."""

from __future__ import annotations

import pytest

from src.rea.pipeline import (
    REA_STAGES,
    PipelineError,
    ReaPipeline,
    ReaStage,
    stage_index,
)


def test_stages_are_the_ten_pipeline_steps() -> None:
    assert len(REA_STAGES) == 10
    assert REA_STAGES[0] is ReaStage.TARGET
    assert REA_STAGES[-1] is ReaStage.VERIFY
    assert REA_STAGES[5] is ReaStage.RECONSTRUCT_UNDERSTANDING
    assert stage_index(ReaStage.TARGET) == 0
    assert stage_index("VERIFY") == 9


def test_unknown_stage_rejected() -> None:
    with pytest.raises(PipelineError):
        stage_index("HACK")


def test_pipeline_starts_before_target() -> None:
    pipeline = ReaPipeline("demo")
    assert pipeline.current is None
    assert pipeline.next_stage is ReaStage.TARGET
    assert not pipeline.is_complete


def test_pipeline_advances_in_order() -> None:
    pipeline = ReaPipeline("demo")
    assert pipeline.advance() is ReaStage.TARGET
    assert pipeline.advance(ReaStage.IDENTIFY) is ReaStage.IDENTIFY
    assert pipeline.current is ReaStage.IDENTIFY
    assert pipeline.has_reached("TARGET")
    assert not pipeline.has_reached(ReaStage.INSPECT)


def test_pipeline_refuses_to_skip_stages() -> None:
    pipeline = ReaPipeline("demo")
    pipeline.advance()  # TARGET
    with pytest.raises(PipelineError):
        pipeline.advance(ReaStage.RECONSTRUCT_UNDERSTANDING)


def test_pipeline_completes_and_then_refuses_more() -> None:
    pipeline = ReaPipeline("demo")
    for stage in REA_STAGES:
        pipeline.advance(stage)
    assert pipeline.is_complete
    assert pipeline.current is ReaStage.VERIFY
    assert pipeline.next_stage is None
    with pytest.raises(PipelineError):
        pipeline.advance()


def test_pipeline_to_dict() -> None:
    pipeline = ReaPipeline("demo")
    pipeline.advance()
    data = pipeline.to_dict()
    assert data["name"] == "demo"
    assert data["completed"] == ["TARGET"]
    assert data["current"] == "TARGET"
    assert data["next"] == "IDENTIFY"
    assert data["is_complete"] is False


def test_pipeline_requires_name() -> None:
    with pytest.raises(PipelineError):
        ReaPipeline("")