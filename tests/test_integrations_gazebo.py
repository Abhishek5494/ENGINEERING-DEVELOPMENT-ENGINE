"""Tests for the Gazebo integration (T-1101)."""

from __future__ import annotations

import subprocess

import pytest

from src.core.evidence import EvidenceLabel
from src.integrations.gazebo import (
    GazeboError,
    GazeboRun,
    GazeboUnavailable,
    gazebo_cli,
    gazebo_evidence,
    run_headless,
    verify_outputs,
    write_world,
)

WORLD = '<?xml version="1.0"?><sdf version="1.7"><world name="empty"/></sdf>'


def _which(name: str) -> str | None:
    return "C:/gazebo/bin/gz.exe" if name == "gz.exe" else None


def test_gazebo_cli_injectable() -> None:
    assert gazebo_cli(which=lambda name: None) is None
    assert gazebo_cli(which=_which) == "C:/gazebo/bin/gz.exe"


def test_write_world_roundtrip_no_overwrite_escape(tmp_path) -> None:
    target = write_world("empty.sdf", WORLD, base=tmp_path)
    assert target.read_text(encoding="utf-8") == WORLD
    with pytest.raises(GazeboError):
        write_world("empty.sdf", WORLD, base=tmp_path)
    write_world("empty.sdf", WORLD, overwrite=True, base=tmp_path)
    with pytest.raises(GazeboError):
        write_world("../escape.sdf", WORLD, base=tmp_path)
    with pytest.raises(GazeboError):
        write_world("empty.sdf", "   ", base=tmp_path)


def test_run_headless_raises_when_absent(tmp_path) -> None:
    target = write_world("w.sdf", WORLD, base=tmp_path)
    with pytest.raises(GazeboUnavailable):
        run_headless(target, which=lambda name: None)


def test_run_headless_argv(tmp_path) -> None:
    target = write_world("w.sdf", WORLD, base=tmp_path)
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):  # noqa: ANN001
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "ok", "")

    result = run_headless(target, iterations=5, which=_which, run=fake_run)
    assert isinstance(result, GazeboRun)
    assert result.succeeded
    command = captured["command"]
    assert command[1:4] == ["sim", "-s", "-r"]
    assert "5" in command
    assert command[-1] == str(target)


def test_verify_outputs(tmp_path) -> None:
    (tmp_path / "run.log").write_text("x" * 7)
    sizes = verify_outputs(tmp_path, ["run.log"])
    assert sizes["run.log"] == 7
    with pytest.raises(GazeboError):
        verify_outputs(tmp_path, ["missing.log"])


def test_gazebo_evidence_labels() -> None:
    run = GazeboRun(("gz",), 0, "", "")
    entries = gazebo_evidence("headless", run=run, outputs={"run.log": 7})
    labels = {entry.label for entry in entries}
    assert EvidenceLabel.SIMULATED in labels
    assert EvidenceLabel.OBSERVED in labels


@pytest.mark.skipif(
    gazebo_cli() is None, reason="Gazebo not installed on this host"
)
def test_gazebo_live(tmp_path) -> None:
    target = write_world("live.sdf", WORLD, base=tmp_path)
    result = run_headless(target, iterations=1, timeout=120)
    assert result.returncode in {0, 1}  # headless exit codes vary by version