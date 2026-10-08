"""Tests for the FreeCAD integration (T-0901)."""

from __future__ import annotations

import subprocess

import pytest

from src.core.evidence import EvidenceLabel
from src.integrations.freecad import (
    FreeCADRun,
    FreeCADUnavailable,
    FreeCadError,
    build_box_macro,
    cad_evidence,
    freecad_available,
    run_macro,
    verify_outputs,
    write_script,
)


def test_freecad_available_injectable() -> None:
    assert freecad_available(which=lambda name: None) is None

    def which(name: str) -> str | None:
        return "C:/FreeCAD/bin/FreeCADCmd.exe" if name == "FreeCADCmd.exe" else None

    assert freecad_available(which=which) == "C:/FreeCAD/bin/FreeCADCmd.exe"


def test_build_box_macro_uses_freecad_api() -> None:
    macro = build_box_macro("widget", 20, 10, 5)
    assert "FreeCAD.newDocument" in macro
    assert 'addObject("Part::Box"' in macro
    assert "box.Length = 20.0" in macro
    assert ".FCStd" in macro
    assert ".step" in macro
    assert build_box_macro("plain", export_step=False).count("Part.export") == 0
    with pytest.raises(FreeCadError):
        build_box_macro("  ")


def test_write_script_roundtrip_no_overwrite_and_escape(tmp_path) -> None:
    macro = build_box_macro("widget")
    target = write_script("widget.py", macro, base=tmp_path)
    assert target.read_text(encoding="utf-8") == macro
    with pytest.raises(FreeCadError):
        write_script("widget.py", macro, base=tmp_path)
    write_script("widget.py", macro, overwrite=True, base=tmp_path)
    with pytest.raises(FreeCadError):
        write_script("../escape.py", macro, base=tmp_path)
    with pytest.raises(FreeCadError):
        write_script("empty.py", "   ", base=tmp_path)


def test_run_macro_raises_when_absent(tmp_path) -> None:
    target = write_script("w.py", build_box_macro("w"), base=tmp_path)
    with pytest.raises(FreeCADUnavailable):
        run_macro(target, which=lambda name: None)


def test_run_macro_invokes_console_binary(tmp_path) -> None:
    target = write_script("w.py", build_box_macro("w"), base=tmp_path)
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):  # noqa: ANN001
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "done", "")

    result = run_macro(
        target, which=lambda name: "C:/FreeCAD/bin/FreeCADCmd.exe", run=fake_run
    )
    assert result == FreeCADRun(0, "done", "")
    assert captured["command"] == ["C:/FreeCAD/bin/FreeCADCmd.exe", str(target)]


def test_verify_outputs(tmp_path) -> None:
    (tmp_path / "widget.FCStd").write_bytes(b"FCSTD" * 10)
    sizes = verify_outputs(tmp_path, ["widget.FCStd"])
    assert sizes["widget.FCStd"] == 50
    with pytest.raises(FreeCadError):
        verify_outputs(tmp_path, ["missing.step"])


def test_cad_evidence_labels() -> None:
    entries = cad_evidence(
        "widget",
        dimensions=(20.0, 10.0, 5.0),
        run=FreeCADRun(0, "", ""),
        outputs={"widget.FCStd": 1234},
    )
    labels = {entry.label for entry in entries}
    assert EvidenceLabel.SIMULATED in labels
    assert EvidenceLabel.OBSERVED in labels
    assert all(entry.statement for entry in entries)


@pytest.mark.skipif(
    freecad_available() is None, reason="FreeCAD not installed on this host"
)
def test_freecad_live(tmp_path) -> None:
    macro = build_box_macro("live_widget")
    target = write_script("live_widget.py", macro, base=tmp_path)
    result = run_macro(target, timeout=180)
    assert result.succeeded, result.stderr
    sizes = verify_outputs(tmp_path, ["live_widget.FCStd"])
    assert sizes["live_widget.FCStd"] > 0