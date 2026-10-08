"""Tests for shared platform operations and Windows wrappers (T-0104, §23)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from src.core.manifest import ManifestError, load_manifest
from src.pem.detect import detect_system
from src.pem.ops import (
    EXIT_ERROR,
    EXIT_OK,
    EXIT_UNHEALTHY,
    PLAN_ONLY_NOTICE,
    current_platform,
    main,
    platform_entries,
    run_healthcheck,
    run_install_plan,
    run_update_plan,
)
from src.pem.report import LOW_DISK_THRESHOLD_BYTES, REPO_ROOT

SCRIPTS_DIR = REPO_ROOT / "scripts" / "windows"
SCRIPT_NAMES = ("install.ps1", "update.ps1", "healthcheck.ps1")
POWERSHELL = shutil.which("powershell")


def _entry(tool_id: str, **overrides: Any) -> dict[str, Any]:
    entry = {
        "id": tool_id,
        "tool": tool_id,
        "purpose": f"purpose of {tool_id}",
        "required": "required",
        "supported_platforms": ["windows", "linux", "macos"],
        "min_version": None,
        "preferred_version": None,
        "detection_method": "command",
        "executable": tool_id,
        "dependencies": [],
        "installation_method": "platform package manager",
        "health_check": None,
        "capability": [],
    }
    entry.update(overrides)
    return entry


def _record(tool_id: str, **overrides: Any) -> dict[str, Any]:
    record = {
        "id": tool_id,
        "state": "DETECTED",
        "version": "1.0.0",
        "executable_path": f"C:/tools/{tool_id}.exe",
        "evidence": "OBSERVED",
        "probe": f"{tool_id} --version",
        "reason": "probe exited 0",
        "health_ok": True,
        "capability": [],
        "min_version": None,
        "required": "required",
    }
    record.update(overrides)
    return record


def _system(free_bytes: int = 100 * 1024**3) -> dict[str, Any]:
    return {
        "storage": {
            "value": [{"mount": "C:\\", "total_bytes": 1024**4, "free_bytes": free_bytes}],
            "evidence": "OBSERVED",
        }
    }


@pytest.fixture()
def manifest() -> dict[str, Any]:
    return {"schema_version": "1.0.0", "tools": [_entry("aaa")]}


# ---- platform auto-detection (MASTER §23) --------------------------------


def test_platform_detection_no_override_flag() -> None:
    detected = current_platform()
    assert detected in {"windows", "linux", "macos"}
    if sys.platform.startswith("win"):
        assert detected == "windows"


def test_platform_filter_excludes_other_platforms() -> None:
    manifest_data = {
        "schema_version": "1.0.0",
        "tools": [
            _entry("win-tool", supported_platforms=["windows"]),
            _entry("linux-tool", supported_platforms=["linux"]),
            _entry("any-tool", supported_platforms=["windows", "macos"]),
        ],
    }
    ids = [e["id"] for e in platform_entries(manifest_data, "windows")]
    assert ids == ["win-tool", "any-tool"]


# ---- healthcheck ---------------------------------------------------------


def test_healthcheck_all_healthy_returns_zero(manifest: dict[str, Any]) -> None:
    code, lines = run_healthcheck(
        manifest=manifest,
        system=_system(),
        tools=[_record("aaa")],
        platform_name="windows",
    )
    assert code == EXIT_OK
    assert any("[PASS] required tool 'aaa'" in line for line in lines)
    assert any("RESULT: HEALTHY" in line for line in lines)


def test_healthcheck_missing_required_tool_returns_one(manifest: dict[str, Any]) -> None:
    code, lines = run_healthcheck(
        manifest=manifest,
        system=_system(),
        tools=[_record("aaa", state="NOT_FOUND", health_ok=None, reason="not on PATH")],
        platform_name="windows",
    )
    assert code == EXIT_UNHEALTHY
    assert any("[FAIL] required tool 'aaa': NOT_FOUND" in line for line in lines)
    assert any("RESULT: UNHEALTHY" in line for line in lines)


def test_healthcheck_failed_health_returns_one(manifest: dict[str, Any]) -> None:
    code, _ = run_healthcheck(
        manifest=manifest,
        system=_system(),
        tools=[_record("aaa", health_ok=False)],
        platform_name="windows",
    )
    assert code == EXIT_UNHEALTHY


def test_healthcheck_low_disk_returns_one_and_names_volume(
    manifest: dict[str, Any],
) -> None:
    code, lines = run_healthcheck(
        manifest=manifest,
        system=_system(free_bytes=1024),
        tools=[_record("aaa")],
        platform_name="windows",
    )
    assert code == EXIT_UNHEALTHY
    assert any(
        "[FAIL] storage C:\\" in line and "1024 bytes free" in line for line in lines
    )


def test_healthcheck_unknown_storage_is_not_counted(
    manifest: dict[str, Any],
) -> None:
    system = {"storage": {"value": [], "evidence": "UNKNOWN"}}
    code, lines = run_healthcheck(
        manifest=manifest,
        system=system,
        tools=[_record("aaa")],
        platform_name="windows",
    )
    assert code == EXIT_OK
    assert any("[WARN] storage: UNKNOWN" in line for line in lines)


def test_healthcheck_skips_required_tool_for_other_platform() -> None:
    manifest_data = {
        "schema_version": "1.0.0",
        "tools": [_entry("aaa", supported_platforms=["linux"])],
    }
    code, lines = run_healthcheck(
        manifest=manifest_data,
        system=_system(),
        tools=[],
        platform_name="windows",
    )
    assert code == EXIT_OK
    assert not any("required tool" in line for line in lines)


def test_healthcheck_optional_tool_not_required(manifest: dict[str, Any]) -> None:
    manifest["tools"].append(_entry("bbb", required="optional"))
    code, lines = run_healthcheck(
        manifest=manifest,
        system=_system(),
        tools=[_record("aaa"), _record("bbb", state="NOT_FOUND")],
        platform_name="windows",
    )
    assert code == EXIT_OK
    assert not any("'bbb'" in line for line in lines)


# ---- install plan --------------------------------------------------------


def test_install_plan_lists_missing_required_first() -> None:
    manifest_data = {
        "schema_version": "1.0.0",
        "tools": [
            _entry("opt-tool", required="optional"),
            _entry("req-tool", required="required"),
        ],
    }
    code, lines = run_install_plan(
        manifest=manifest_data,
        tools=[
            _record("opt-tool", state="NOT_FOUND"),
            _record("req-tool", state="NOT_FOUND"),
        ],
        platform_name="windows",
    )
    assert code == EXIT_OK
    req_index = next(i for i, line in enumerate(lines) if "req-tool" in line)
    opt_index = next(i for i, line in enumerate(lines) if "opt-tool" in line)
    assert req_index < opt_index
    assert any("REQUIRED req-tool" in line for line in lines)
    assert any("OPTIONAL opt-tool" in line for line in lines)


def test_install_plan_is_plan_only_and_honest(manifest: dict[str, Any]) -> None:
    code, lines = run_install_plan(
        manifest=manifest,
        tools=[_record("aaa", state="NOT_FOUND")],
        platform_name="windows",
    )
    assert code == EXIT_OK
    joined = "\n".join(lines)
    assert PLAN_ONLY_NOTICE in joined
    assert "T-0107" in joined
    assert "0 change(s) performed" in lines[-1]


def test_install_plan_changes_nothing(
    manifest: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    before = sorted(p.name for p in tmp_path.iterdir())
    run_install_plan(
        manifest=manifest,
        tools=[_record("aaa", state="NOT_FOUND")],
        platform_name="windows",
    )
    after = sorted(p.name for p in tmp_path.iterdir())
    assert after == before


def test_update_plan_reports_versions_and_never_mutates(
    manifest: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest["tools"].append(_entry("bbb", preferred_version="2.0.0"))
    monkeypatch.chdir(tmp_path)
    before = sorted(p.name for p in tmp_path.iterdir())
    code, lines = run_update_plan(
        manifest=manifest,
        tools=[_record("aaa", version="1.5.0"), _record("bbb", state="NOT_FOUND")],
        platform_name="windows",
    )
    after = sorted(p.name for p in tmp_path.iterdir())
    assert code == EXIT_OK
    assert after == before
    joined = "\n".join(lines)
    assert "detected 1.5.0" in joined
    assert "UNKNOWN (not recorded in manifest)" in joined
    assert "bbb: NOT_FOUND — nothing to update" in joined
    assert PLAN_ONLY_NOTICE in joined


# ---- CLI -----------------------------------------------------------------


def test_importable_main() -> None:
    from src.pem.ops import main as imported

    assert imported is main


def test_main_bad_command_returns_error_code() -> None:
    assert main(["not-a-command"]) == EXIT_ERROR


def test_cli_healthcheck_exit_code_matches_host_state() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.pem.ops", "healthcheck"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode in {EXIT_OK, EXIT_UNHEALTHY}
    assert "RESULT:" in result.stdout
    system = detect_system()
    volumes = system["storage"].get("value", [])
    low = any(v["free_bytes"] < LOW_DISK_THRESHOLD_BYTES for v in volumes)
    assert result.returncode == (EXIT_UNHEALTHY if low else EXIT_OK)


def test_cli_install_and_update_exit_zero_and_are_plan_only() -> None:
    for command in ("install", "update"):
        result = subprocess.run(
            [sys.executable, "-m", "src.pem.ops", command],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == EXIT_OK, result.stderr
        assert "PLAN-ONLY" in result.stdout
        assert "T-0107" in result.stdout
        assert "0 change(s) performed" in result.stdout


def test_cli_help_documents_exit_codes() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.pem.ops", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == EXIT_OK
    assert "exit codes" in result.stdout
    assert "plan-only" in result.stdout


def test_execution_error_returns_two(monkeypatch: pytest.MonkeyPatch) -> None:
    import src.pem.ops as ops

    def boom() -> None:
        raise ManifestError("manifest unreadable")

    monkeypatch.setattr(ops, "load_manifest", boom)
    assert main(["healthcheck"]) == EXIT_ERROR


# ---- Windows wrappers ----------------------------------------------------


def test_scripts_exist() -> None:
    for name in SCRIPT_NAMES:
        assert (SCRIPTS_DIR / name).is_file(), name


def test_no_manifest_tool_id_in_wrappers_except_interpreter_bootstrap() -> None:
    """No tool list/logic in .ps1 files (AC).

    Recorded discrepancy (see audit.md): the literal AC says no manifest
    tool id appears at all, but the wrapper must invoke the Python
    interpreter, whose manifest id is `python`. Resolution: `python` is
    allowed ONLY on plumbing lines (interpreter reference); every other
    tool id must be absent.
    """
    manifest_data = load_manifest()
    tool_ids = {entry["id"] for entry in manifest_data["tools"]}
    allowed = {"python"}
    for name in SCRIPT_NAMES:
        text = (SCRIPTS_DIR / name).read_text(encoding="utf-8")
        lowered = text.lower()
        forbidden = {
            tool_id for tool_id in tool_ids - allowed if tool_id in lowered
        }
        assert not forbidden, f"{name} contains tool ids: {sorted(forbidden)}"
        for line in text.splitlines():
            low = line.lower()
            if "python" in low:
                assert (
                    "-m src.pem.ops" in low
                    or "$python" in low
                    or "python interpreter" in low
                ), f"unexpected python usage in {name}: {line.strip()}"


@pytest.mark.skipif(POWERSHELL is None, reason="powershell not on PATH")
def test_scripts_are_syntactically_valid() -> None:
    for name in SCRIPT_NAMES:
        script = SCRIPTS_DIR / name
        result = subprocess.run(
            [
                POWERSHELL,
                "-NoProfile",
                "-Command",
                "$tokens = $null; $errors = $null; $null = "
                "[System.Management.Automation.Language.Parser]::"
                f"ParseFile('{script}', [ref]$tokens, [ref]$errors); "
                "if ($errors -and $errors.Count) "
                "{ $errors | ForEach-Object { $_.Message }; exit 1 } exit 0",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"{name}: {result.stdout} {result.stderr}"


@pytest.mark.skipif(POWERSHELL is None, reason="powershell not on PATH")
def test_scripts_execute_on_this_host() -> None:
    direct = subprocess.run(
        [sys.executable, "-m", "src.pem.ops", "healthcheck"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    expected = direct.returncode
    assert expected in {EXIT_OK, EXIT_UNHEALTHY}

    for name in SCRIPT_NAMES:
        result = subprocess.run(
            [
                POWERSHELL,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(SCRIPTS_DIR / name),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if name == "healthcheck.ps1":
            assert result.returncode == expected, result.stdout + result.stderr
            assert "RESULT:" in result.stdout
        else:
            assert result.returncode == EXIT_OK, result.stdout + result.stderr
            assert "PLAN-ONLY" in result.stdout
            assert "0 change(s) performed" in result.stdout
