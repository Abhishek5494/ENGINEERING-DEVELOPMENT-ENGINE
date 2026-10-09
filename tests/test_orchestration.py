"""Tests for the unified engineering workflow (T-1301, PARTIAL)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.cie.identify import identify_page
from src.cie.model import Component
from src.core.evidence import EvidenceLabel
from src.orchestration import (
    StageStatus,
    WORKFLOW_STAGES,
    WorkflowError,
    WorkflowStage,
    run_workflow,
    write_project,
)

PRODUCT_HTML = """
<html><head>
  <script type="application/ld+json">
  {"@context":"https://schema.org","@graph":[
    {"@type":"Product","name":"Acme 775 Motor","brand":{"@type":"Brand","name":"Acme"},
     "sku":"SKU-775","model":"M775",
     "additionalProperty":[{"name":"Rated Voltage","value":"12 V"}]}
  ]}
  </script>
</head></html>
"""


def _component() -> Component:
    return Component(id="acme-m775", name="Acme 775 Motor", manufacturer="Acme")


def test_workflow_stages_are_ordered() -> None:
    assert WORKFLOW_STAGES == tuple(WorkflowStage)
    assert WORKFLOW_STAGES[0] is WorkflowStage.IDEA
    assert WORKFLOW_STAGES[-1] is WorkflowStage.VALIDATE
    assert WorkflowStage.ACQUIRE in WORKFLOW_STAGES
    assert WorkflowStage.ANALYZE in WORKFLOW_STAGES


def test_blocked_stages_are_reported_blocked_not_complete() -> None:
    report = run_workflow("demo", component=_component())
    assert report.status_of(WorkflowStage.ACQUIRE) == StageStatus.BLOCKED.value
    assert report.status_of(WorkflowStage.ANALYZE) == StageStatus.BLOCKED.value
    acquire = next(r for r in report.results if r.stage is WorkflowStage.ACQUIRE)
    assert acquire.blocker
    assert report.validation_level == "PARTIALLY-VALIDATED"


def test_component_supplied_completes_model_stage() -> None:
    report = run_workflow("demo", component=_component())
    assert report.status_of(WorkflowStage.IDENTIFY) == StageStatus.COMPLETE.value
    assert report.status_of(WorkflowStage.MODEL) == StageStatus.COMPLETE.value
    model = next(r for r in report.results if r.stage is WorkflowStage.MODEL)
    assert "acme-m775" in model.detail


def test_identification_input_completes_identify_and_model() -> None:
    ident = identify_page("https://shop.example.invalid/p/1", PRODUCT_HTML)
    report = run_workflow("demo", identification=ident)
    assert report.status_of(WorkflowStage.IDENTIFY) == StageStatus.COMPLETE.value
    assert report.status_of(WorkflowStage.MODEL) == StageStatus.COMPLETE.value
    assert WorkflowStage.MODEL in report.completed


def test_no_input_marks_idea_identify_model_unavailable() -> None:
    report = run_workflow("demo")
    assert report.status_of(WorkflowStage.IDEA) == StageStatus.UNAVAILABLE.value
    assert report.status_of(WorkflowStage.IDENTIFY) == StageStatus.UNAVAILABLE.value
    assert report.status_of(WorkflowStage.MODEL) == StageStatus.UNAVAILABLE.value


def test_python_stage_builds_notebook() -> None:
    report = run_workflow(
        "demo", component=_component(), notebook_cells=["a = 1\n", "print(a)\n"]
    )
    assert report.status_of(WorkflowStage.PYTHON) == StageStatus.COMPLETE.value
    python = next(r for r in report.results if r.stage is WorkflowStage.PYTHON)
    assert any(e.label is EvidenceLabel.OBSERVED for e in python.evidence)


def test_python_stage_without_cells_is_unavailable() -> None:
    report = run_workflow("demo", component=_component())
    assert report.status_of(WorkflowStage.PYTHON) == StageStatus.UNAVAILABLE.value


def test_tool_absent_is_unavailable() -> None:
    probes = {s: (lambda: None) for s in WorkflowStage}
    report = run_workflow("demo", component=_component(), probes=probes)
    for stage in (WorkflowStage.CAD, WorkflowStage.ELECTRONICS, WorkflowStage.CIRCUIT,
                  WorkflowStage.ROBOTICS, WorkflowStage.VISUALISE):
        assert report.status_of(stage) == StageStatus.UNAVAILABLE.value


def test_tool_present_is_ready_not_complete() -> None:
    probes = {WorkflowStage.CAD: lambda: "C:/FreeCAD/bin/freecadcmd.exe"}
    report = run_workflow("demo", component=_component(), probes=probes)
    assert report.status_of(WorkflowStage.CAD) == StageStatus.READY.value
    cad = next(r for r in report.results if r.stage is WorkflowStage.CAD)
    assert "freecadcmd.exe" in cad.detail
    assert WorkflowStage.CAD in report.ready


def test_validate_aggregates_and_report_evidence() -> None:
    report = run_workflow("demo", component=_component(), notebook_cells=["x = 1\n"])
    validate = next(r for r in report.results if r.stage is WorkflowStage.VALIDATE)
    assert validate.status == StageStatus.COMPLETE.value
    assert "complete" in validate.detail
    assert report.evidence
    assert report.strongest_label is EvidenceLabel.OBSERVED


def test_tagged_probes_accept_string_keys() -> None:
    report = run_workflow(
        "demo", component=_component(), probes={"CAD": lambda: "/opt/freecad"}
    )
    assert report.status_of(WorkflowStage.CAD) == StageStatus.READY.value


def test_invalid_name_rejected() -> None:
    with pytest.raises(WorkflowError):
        run_workflow("   ")


def test_report_to_dict_shape() -> None:
    report = run_workflow("demo", component=_component())
    data = report.to_dict()
    assert data["name"] == "demo"
    assert data["validation_level"] == "PARTIALLY-VALIDATED"
    assert len(data["stages"]) == len(WORKFLOW_STAGES)
    stage_names = [s["stage"] for s in data["stages"]]
    assert stage_names == [s.value for s in WORKFLOW_STAGES]


def test_write_project_roundtrip(tmp_path: Path) -> None:
    report = run_workflow("demo", component=_component(), notebook_cells=["x = 1\n"])
    target = write_project(report, root=tmp_path)
    assert target == (tmp_path / "demo").resolve()
    assert (target / "workflow.json").is_file()
    text = (target / "workflow.json").read_text(encoding="utf-8")
    assert '"validation_level": "PARTIALLY-VALIDATED"' in text


def test_write_project_extra_and_overwrite_guard(tmp_path: Path) -> None:
    report = run_workflow("demo", component=_component())
    write_project(report, root=tmp_path, extra={"notes.md": "# Notes\n"})
    assert (tmp_path / "demo" / "notes.md").read_text(encoding="utf-8") == "# Notes\n"
    with pytest.raises(WorkflowError):
        write_project(report, root=tmp_path, extra={"notes.md": "changed\n"})
    write_project(report, root=tmp_path, extra={"notes.md": "changed\n"}, overwrite=True)


def test_write_project_rejects_escape(tmp_path: Path) -> None:
    report = run_workflow("../escape", component=_component())
    with pytest.raises(WorkflowError):
        write_project(report, root=tmp_path)


def test_live_demo_project_is_partial_and_honest() -> None:
    from src.core.config import PROJECTS_DIR

    demo = PROJECTS_DIR / "demo-motor"
    assert (demo / "workflow.json").is_file(), "demo project committed under projects/"
    data = json.loads((demo / "workflow.json").read_text(encoding="utf-8"))
    assert data["validation_level"] == "PARTIALLY-VALIDATED"
    assert WorkflowStage.ACQUIRE.value in data["blocked"]
    assert WorkflowStage.ANALYZE.value in data["blocked"]
    assert WorkflowStage.PYTHON.value in data["completed"]
    assert (demo / "component.json").is_file()
    assert (demo / "notebook.ipynb").is_file()
    assert (demo / "README.md").is_file()
