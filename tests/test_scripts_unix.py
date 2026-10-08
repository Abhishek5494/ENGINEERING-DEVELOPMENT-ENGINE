"""Static tests for Unix wrapper scripts (Linux + macOS) — T-0105/T-0106, §23.

This host is Windows and has no POSIX shell, so validation is STATIC
ONLY: file layout, shebang, interpreter discovery, delegation to the
shared module, exit-code propagation, and absence of tool logic. The
scripts are never executed here and no runtime behavior is claimed.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from src.core.manifest import load_manifest
from src.pem.report import REPO_ROOT

SCRIPTS = {
    "install.sh": "install",
    "update.sh": "update",
    "healthcheck.sh": "healthcheck",
}
PLATFORMS = ("linux", "macos")
SH = shutil.which("sh")


def _scripts_dir(platform: str) -> Path:
    return REPO_ROOT / "scripts" / platform


def _text(platform: str, name: str) -> str:
    return (_scripts_dir(platform) / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("platform", PLATFORMS)
def test_unix_scripts_exist(platform: str) -> None:
    for name in SCRIPTS:
        assert (_scripts_dir(platform) / name).is_file(), f"{platform}/{name}"


@pytest.mark.parametrize("platform", PLATFORMS)
def test_scripts_use_posix_shebang(platform: str) -> None:
    for name in SCRIPTS:
        first = _text(platform, name).splitlines()[0]
        assert first == "#!/usr/bin/env sh", f"{platform}/{name}: {first!r}"


@pytest.mark.parametrize("platform", PLATFORMS)
def test_scripts_delegate_to_shared_module(platform: str) -> None:
    for name, command in SCRIPTS.items():
        assert f"-m src.pem.ops {command}" in _text(platform, name)


@pytest.mark.parametrize("platform", PLATFORMS)
def test_scripts_propagate_exit_code(platform: str) -> None:
    # `exec` replaces the shell, so the shared module's exit code is the
    # script's exit code (no swallowing possible).
    for name, command in SCRIPTS.items():
        lines = [
            line
            for line in _text(platform, name).splitlines()
            if f"-m src.pem.ops {command}" in line
        ]
        assert lines, f"{platform}/{name}"
        assert any(line.strip().startswith("exec ") for line in lines)


@pytest.mark.parametrize("platform", PLATFORMS)
def test_scripts_discover_interpreter_honestly(platform: str) -> None:
    for name in SCRIPTS:
        text = _text(platform, name)
        assert "command -v python3" in text
        assert "command -v python" in text
        assert "python interpreter not found" in text
        assert "exit 2" in text


@pytest.mark.parametrize("platform", PLATFORMS)
def test_no_manifest_tool_id_in_scripts_except_interpreter_bootstrap(
    platform: str,
) -> None:
    """No tool list/logic in .sh files (same resolution as T-0104 AC5).

    The wrapper must invoke the Python interpreter, whose manifest id is
    `python`; it is allowed ONLY on plumbing lines. Every other manifest
    tool id must be absent.
    """
    manifest_data = load_manifest()
    tool_ids = {entry["id"] for entry in manifest_data["tools"]}
    allowed = {"python"}
    for name in SCRIPTS:
        text = _text(platform, name)
        lowered = text.lower()
        forbidden = {
            tool_id for tool_id in tool_ids - allowed if tool_id in lowered
        }
        assert not forbidden, f"{platform}/{name} contains {sorted(forbidden)}"
        for line in text.splitlines():
            low = line.lower()
            if "python" in low:
                assert (
                    "-m src.pem.ops" in low
                    or "command -v" in low
                    or "python_cmd" in low
                    or "python interpreter" in low
                ), f"unexpected python usage in {platform}/{name}: {line.strip()}"


@pytest.mark.parametrize("platform", PLATFORMS)
def test_scripts_have_no_hardcoded_absolute_repo_path(platform: str) -> None:
    for name in SCRIPTS:
        text = _text(platform, name)
        assert "D:\\" not in text
        assert "/home/" not in text
        assert "script_dir" in text and "repo_root" in text


@pytest.mark.skipif(SH is None, reason="no POSIX sh on PATH")
@pytest.mark.parametrize("platform", PLATFORMS)
def test_scripts_are_syntactically_valid_when_sh_available(platform: str) -> None:
    for name in SCRIPTS:
        result = subprocess.run(
            [SH, "-n", str(_scripts_dir(platform) / name)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"{platform}/{name}: {result.stderr}"