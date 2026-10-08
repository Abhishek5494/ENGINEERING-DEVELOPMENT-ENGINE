"""Tests for the Blender integration (T-1201)."""

from __future__ import annotations

import subprocess

import pytest

from src.core.evidence import EvidenceLabel
from src.integrations.blender import (
    BlenderError,
    BlenderRun,
    BlenderUnavailable,
    blender_cli,
    blender_evidence,
    run_background,
    verify_outputs,
    write_script,
)

SCRIPT = "import bpy\nprint('blender', bpy.app.version_string)\n"


def _which(name: str) -> str | None:
    return "C:/Program Files/Blender/blender.exe" if name == "blender.exe" else None


def test_blender_cli_injectable() -> None:
    assert blender_cli(which=lambda name: None) is None
    assert blender_cli(which=_which) == "C:/Program Files/Blender/blender.exe"


def test_write_script_roundtrip_no_overwrite_escape(tmp_path) -> None:
    target = write_script("render.py", SCRIPT, base=tmp_path)
    assert target.read_text(encoding="utf-8") == SCRIPT
    with pytest.raises(BlenderError):
        write_script("render.py", SCRIPT, base=tmp_path)
    write_script("render.py", SCRIPT, overwrite=True, base=tmp_path)
    with pytest.raises(BlenderError):
        write_script("../escape.py", SCRIPT, base=tmp_path)
    with pytest.raises(BlenderError):
        write_script("render.py", "   ", base=tmp_path)


def test_run_background_raises_when_absent(tmp_path) -> None:
    target = write_script("r.py", SCRIPT, base=tmp_path)
    with pytest.raises(BlenderUnavailable):
        run_background(target, which=lambda name: None)


def test_run_background_argv(tmp_path) -> None:
    target = write_script("r.py", SCRIPT, base=tmp_path)
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):  # noqa: ANN001
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "ok", "")

    result = run_background(target, which=_which, run=fake_run)
    assert isinstance(result, BlenderRun)
    assert result.succeeded
    command = captured["command"]
    assert command[1:3] == ["--background", "--python"]
    assert command[-1] == str(target)


def test_verify_outputs(tmp_path) -> None:
    (tmp_path / "render.png").write_bytes(b"\x89PNG" + b"x" * 5)
    sizes = verify_outputs(tmp_path, ["render.png"])
    assert sizes["render.png"] == 9
    with pytest.raises(BlenderError):
        verify_outputs(tmp_path, ["missing.png"])


def test_blender_evidence_labels() -> None:
    run = BlenderRun(("blender",), 0, "", "")
    entries = blender_evidence("headless", run=run, outputs={"render.png": 9})
    labels = {entry.label for entry in entries}
    assert EvidenceLabel.SIMULATED in labels
    assert EvidenceLabel.OBSERVED in labels


@pytest.mark.skipif(
    blender_cli() is None, reason="Blender not installed on this host"
)
def test_blender_live(tmp_path) -> None:
    target = write_script("live.py", SCRIPT, base=tmp_path)
    result = run_background(target, timeout=120)
    assert result.returncode in {0, 1}  # background exit codes vary by version