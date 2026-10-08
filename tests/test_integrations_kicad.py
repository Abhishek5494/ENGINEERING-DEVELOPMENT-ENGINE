"""Tests for the KiCad integration (T-1001)."""

from __future__ import annotations

import subprocess

import pytest

from src.core.evidence import EvidenceLabel
from src.integrations.kicad import (
    KiCadError,
    KiCadRun,
    KiCadUnavailable,
    export_gerbers,
    kicad_cli,
    kicad_evidence,
    run_drc,
    run_erc,
    verify_artifacts,
)

CLI = "C:/KiCad/bin/kicad-cli.exe"


def _which(name: str) -> str | None:
    return CLI if name in {"kicad-cli", "kicad-cli.exe"} else None


def test_kicad_cli_injectable() -> None:
    assert kicad_cli(which=lambda name: None) is None
    assert kicad_cli(which=_which) == CLI


def test_commands_raise_when_absent(tmp_path) -> None:
    board = tmp_path / "b.kicad_pcb"
    board.write_text("(kicad_pcb)")
    sch = tmp_path / "s.kicad_sch"
    sch.write_text("(kicad_sch)")
    for call in (
        lambda: run_drc(board, tmp_path / "drc.rpt", which=lambda n: None),
        lambda: run_erc(sch, tmp_path / "erc.rpt", which=lambda name: None),
        lambda: export_gerbers(board, tmp_path / "gerbers", which=lambda name: None),
    ):
        with pytest.raises(KiCadUnavailable):
            call()


def test_run_drc_builds_expected_argv(tmp_path) -> None:
    board = tmp_path / "b.kicad_pcb"
    board.write_text("(kicad_pcb)")
    report = tmp_path / "drc.rpt"
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):  # noqa: ANN001
        captured["command"] = command
        return subprocess.CompletedProcess(command, 5, "violations", "")

    result = run_drc(board, report, which=_which, run=fake_run)
    assert isinstance(result, KiCadRun)
    assert result.returncode == 5
    assert result.command[0] == CLI
    assert result.command[1:5] == ("pcb", "drc", "--exit-code-violations", "--output")
    assert str(board) in result.command


def test_run_erc_and_gerbers_argv(tmp_path) -> None:
    board = tmp_path / "b.kicad_pcb"
    board.write_text("(kicad_pcb)")
    sch = tmp_path / "s.kicad_sch"
    sch.write_text("(kicad_sch)")
    seen: list[tuple[str, ...]] = []

    def fake_run(command, **kwargs):  # noqa: ANN001
        seen.append(tuple(command))
        return subprocess.CompletedProcess(command, 0, "", "")

    run_erc(sch, tmp_path / "r.txt", which=_which, run=fake_run)
    export_gerbers(board, tmp_path / "gerbers", which=_which, run=fake_run)
    assert seen[0][1:3] == ("sch", "erc")
    assert seen[1][1:4] == ("pcb", "export", "gerbers")


def test_run_drc_missing_board(tmp_path) -> None:
    with pytest.raises(KiCadError):
        run_drc(tmp_path / "nope.kicad_pcb", tmp_path / "r.txt", which=_which)


def test_verify_artifacts(tmp_path) -> None:
    (tmp_path / "top.gbr").write_bytes(b"G04" * 5)
    sizes = verify_artifacts(tmp_path, ["top.gbr"])
    assert sizes["top.gbr"] == 15
    with pytest.raises(KiCadError):
        verify_artifacts(tmp_path, ["bottom.gbr"])


def test_kicad_evidence_labels() -> None:
    run = KiCadRun(("kicad-cli",), 0, "", "")
    entries = kicad_evidence("pcb drc", run=run, artifacts={"r.txt": 42})
    assert all(entry.label is EvidenceLabel.OBSERVED for entry in entries)
    assert any("exit code 0" in entry.statement for entry in entries)
    assert any("r.txt: 42 bytes" in entry.statement for entry in entries)


@pytest.mark.skipif(kicad_cli() is None, reason="KiCad not installed on this host")
def test_kicad_live(tmp_path) -> None:
    board = tmp_path / "b.kicad_pcb"
    board.write_text("(kicad_pcb (version 20211014) (generator pcbnew))")
    result = run_drc(board, tmp_path / "drc.rpt", timeout=180)
    assert result.returncode in {0, 5, 6}  # KiCad exit codes for DRC