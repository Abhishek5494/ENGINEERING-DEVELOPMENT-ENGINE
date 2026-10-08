"""Tests for the ngspice integration (T-1002)."""

from __future__ import annotations

import subprocess

import pytest

from src.core.evidence import EvidenceLabel
from src.integrations.ngspice import (
    NgspiceError,
    NgspiceRun,
    NgspiceUnavailable,
    ngspice_cli,
    ngspice_evidence,
    parse_op_point,
    run_simulation,
    verify_outputs,
    write_netlist,
)

CLI = "C:/ngspice/bin/ngspice.exe"

NETLIST = "* rc low-pass\nv1 in 0 dc 5\nr1 in out 1k\nc1 out 0 1u\n.end\n"

OP_SAMPLE = """
No. of Data Rows : 1
Node                                   Voltage
----                                   -------
in                                         5.000000
out                                        3.300000
"""


def _which(name: str) -> str | None:
    return "C:/ngspice/bin/ngspice.exe" if name == "ngspice.exe" else None


def test_ngspice_cli_injectable() -> None:
    assert ngspice_cli(which=lambda name: None) is None
    assert ngspice_cli(which=_which) == "C:/ngspice/bin/ngspice.exe"


def test_write_netlist_roundtrip_no_overwrite_escape(tmp_path) -> None:
    target = write_netlist("circuit.cir", NETLIST, base=tmp_path)
    assert target.read_text(encoding="utf-8") == NETLIST
    with pytest.raises(NgspiceError):
        write_netlist("circuit.cir", NETLIST, base=tmp_path)
    write_netlist("circuit.cir", NETLIST, overwrite=True, base=tmp_path)
    with pytest.raises(NgspiceError):
        write_netlist("../escape.cir", NETLIST, base=tmp_path)
    with pytest.raises(NgspiceError):
        write_netlist("empty.cir", "  ", base=tmp_path)


def test_run_simulation_raises_when_absent(tmp_path) -> None:
    target = write_netlist("c.cir", NETLIST, base=tmp_path)
    with pytest.raises(NgspiceUnavailable):
        run_simulation(target, tmp_path / "out.log", which=lambda name: None)


def test_run_simulation_argv(tmp_path) -> None:
    target = write_netlist("c.cir", NETLIST, base=tmp_path)
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):  # noqa: ANN001
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "ok", "")

    result = run_simulation(
        target, tmp_path / "out.log", which=_which, run=fake_run
    )
    assert isinstance(result, NgspiceRun)
    assert result.succeeded
    assert captured["command"][1:3] == ["-b", "-o"]
    assert captured["command"][-1] == str(target)


def test_parse_op_point() -> None:
    values = parse_op_point(OP_SAMPLE)
    assert values == {"in": 5.0, "out": 3.3}
    with pytest.raises(NgspiceError):
        parse_op_point("just some text\nno numbers here")


def test_verify_outputs(tmp_path) -> None:
    (tmp_path / "out.log").write_text("x" * 12)
    sizes = verify_outputs(tmp_path, ["out.log"])
    assert sizes["out.log"] == 12
    with pytest.raises(NgspiceError):
        verify_outputs(tmp_path, ["missing.log"])


def test_ngspice_evidence_labels() -> None:
    run = NgspiceRun(("ngspice",), 0, "", "")
    entries = ngspice_evidence(
        "op",
        run=run,
        results={"out": 3.3},
        outputs={"out.log": 42},
    )
    labels = {entry.label for entry in entries}
    assert EvidenceLabel.SIMULATED in labels
    assert EvidenceLabel.OBSERVED in labels
    assert any("out = 3.3 V" in entry.statement for entry in entries)


@pytest.mark.skipif(
    ngspice_cli() is None, reason="ngspice not installed on this host"
)
def test_ngspice_live(tmp_path) -> None:
    target = write_netlist("live.cir", NETLIST, base=tmp_path)
    out = tmp_path / "live.log"
    result = run_simulation(target, out, timeout=120)
    assert result.succeeded, result.stderr
    verify_outputs(tmp_path, ["live.log"])