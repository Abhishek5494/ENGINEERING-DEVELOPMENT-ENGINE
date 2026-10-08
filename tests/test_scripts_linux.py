"""Tests for Linux wrapper scripts (T-0105, §23).

This host is Windows and has no POSIX shell, so validation here is
STATIC ONLY: file layout, shebang, interpreter discovery, delegation to
the shared module, exit-code propagation, and absence of tool logic.
The scripts are never executed in these tests and no runtime behavior
is claimed.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

from src.core.manifest import load_manifest
from src.pem.report import REPO_ROOT

SCRIPTS_DIR = REPO_ROOT / "scripts" / "linux"
SCRIPTS = {
    "install.sh": "install",
    "update.sh": "update",
    "healthcheck.sh": "healthcheck",
}
SH = shutil.which("sh")


def _text(name: str) -> str:
    return (SCRIPTS_DIR / name).read_text(encoding="utf-8")


def test_linux_scripts_exist() -> None:
    for name in SCRIPTS:
        assert (SCRIPTS_DIR / name).is_file(), name


def test_scripts_use_posix_shebang() -> None:
    for name in SCRIPTS:
        first = _text(name).splitlines()[0]
        assert first == "#!/usr/bin/env sh", f"{name}: {first!r}"


def test_scripts_delegate_to_shared_module() -> None:
    for name, command in SCRIPTS.items():
        text = _text(name)
        assert f"-m src.pem.ops {command}" in text, name


def test_scripts_propagate_exit_code() -> None:
    # `exec` replaces the shell, so the shared module's exit code is the
    # script's exit code (no swallowing possible).
    for name, command in SCRIPTS.items():
        lines = [
            line
            for line in _text(name).splitlines()
            if f"-m src.pem.ops {command}" in line
        ]
        assert lines, name
        assert any(line.strip().startswith("exec ") for line in lines), name


def test_scripts_discover_interpreter_honestly() -> None:
    for name in SCRIPTS:
        text = _text(name)
        assert "command -v python3" in text, name
        assert "command -v python" in text, name
        assert "python interpreter not found" in text, name
        assert "exit 2" in text, name


def test_no_manifest_tool_id_in_scripts_except_interpreter_bootstrap() -> None:
    """No tool list/logic in .sh files (same resolution as T-0104 AC5).

    The wrapper must invoke the Python interpreter, whose manifest id is
    `python`; it is allowed ONLY on plumbing lines. Every other manifest
    tool id must be absent.
    """
    manifest_data = load_manifest()
    tool_ids = {entry["id"] for entry in manifest_data["tools"]}
    allowed = {"python"}
    for name in SCRIPTS:
        text = _text(name)
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
                    or "command -v" in low
                    or "python_cmd" in low
                    or "python interpreter" in low
                ), f"unexpected python usage in {name}: {line.strip()}"


def test_scripts_have_no_hardcoded_absolute_repo_path() -> None:
    for name in SCRIPTS:
        text = _text(name)
        assert "D:\\" not in text, name
        assert "/home/" not in text, name
        assert "script_dir" in text and "repo_root" in text, name


@pytest.mark.skipif(SH is None, reason="no POSIX sh on PATH")
def test_scripts_are_syntactically_valid_when_sh_available() -> None:
    for name in SCRIPTS:
        result = subprocess.run(
            [SH, "-n", str(SCRIPTS_DIR / name)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"{name}: {result.stdout} {result.stderr}"