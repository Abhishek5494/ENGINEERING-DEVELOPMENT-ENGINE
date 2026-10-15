"""Tests for the unified offline CLI (T-2000)."""

from __future__ import annotations

import json

from src import __version__
from src.cli import main


def _json(capsys):
    return json.loads(capsys.readouterr().out)


def test_version_command(capsys):
    assert main(["version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_version_flag(capsys):
    assert main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_no_command_returns_usage_error(capsys):
    assert main([]) == 2


def test_env_json(capsys):
    assert main(["env", "--json"]) == 0
    document = _json(capsys)
    assert set(document) >= {"platform", "tools", "capabilities"}


def test_tools_json(capsys):
    assert main(["tools", "--json"]) == 0
    document = _json(capsys)
    assert document["tools"]
    assert document["capabilities"]


def test_upstream_json(capsys):
    assert main(["upstream", "--json"]) == 0
    document = _json(capsys)
    ids = [source["id"] for source in document["sources"]]
    assert "taiga-s1" in ids


def test_storage_preflight_known_operation(capsys):
    code = main(["storage", "preflight", "build"])
    assert code in (0, 3)
    check = _json(capsys)
    assert check["operation"] == "build"


def test_storage_preflight_unknown_operation(capsys):
    assert main(["storage", "preflight", "does_not_exist"]) == 2
    assert "error:" in capsys.readouterr().err


def test_cie_identify_from_local_html(capsys, tmp_path):
    html = tmp_path / "page.html"
    html.write_text(
        "<html><head><title>Bosch GSB 18V-55 Drill</title></head><body></body></html>",
        encoding="utf-8",
    )
    assert main(
        ["cie", "identify", "--url", "https://example.com/p/1", "--html", str(html)]
    ) == 0
    payload = _json(capsys)
    assert payload["url"] == "https://example.com/p/1"
    assert "title" in payload


def test_rea_inspect_local_file(capsys, tmp_path):
    target = tmp_path / "artifact.bin"
    target.write_bytes(b"ENGINEERING-" + b"A" * 64)
    assert main(["rea", "inspect", str(target)]) == 0
    entries = _json(capsys)
    assert entries
    assert any("sha256" in str(entry) for entry in entries)


def test_workflow_run_json_reports_blocked_stages(capsys):
    assert main(["workflow", "run", "--name", "cli-test", "--json"]) == 0
    report = _json(capsys)
    assert report["validation_level"] == "PARTIALLY-VALIDATED"
    assert "ACQUIRE" in report["blocked"]
    assert "ANALYZE" in report["blocked"]


def test_workflow_run_writes_project(capsys, tmp_path, monkeypatch):
    from src.orchestration import workflow

    monkeypatch.setattr(workflow, "PROJECTS_DIR", tmp_path)
    code = main(["workflow", "run", "--name", "cli-write", "--write"])
    assert code == 0
    written = tmp_path / "cli-write" / "workflow.json"
    assert written.is_file()
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["name"] == "cli-write"
