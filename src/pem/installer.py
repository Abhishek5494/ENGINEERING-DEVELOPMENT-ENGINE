"""Idempotent, manifest-driven installation logic (T-0107, MASTER §22).

Decides and (only on explicit execute) performs installation/upgrade of
manifest tools. Guarantees:

- act only when a tool is NOT_FOUND (install) or DETECTED below a known
  ``min_version`` (upgrade);
- never act on UNKNOWN or missing probe records (inconclusive → the
  operator must investigate first);
- skip DETECTED tools already at/above minimum — a second run against a
  healthy environment performs zero actions;
- ``install_command`` is required to act; ``null`` produces a manual
  notice only (no package-manager claims until R3.3 exists);
- guarded execution: refuses (nothing performed) when any OBSERVED
  storage volume is below ``LOW_DISK_THRESHOLD_BYTES``;
- post-action re-probe: results are reported from a fresh probe, never
  assumed (MASTER §7).

Install commands live in the manifest; ``{python}`` expands to the
current interpreter at run time. This module performs no probing or
network work of its own beyond invoking the injected runner.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from src.pem.detect import detect_system
from src.pem.report import LOW_DISK_THRESHOLD_BYTES
from src.pem.tools import _below_minimum, detect_tools

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_REFUSED = 3

INSTALL_TIMEOUT_SECONDS = 900.0

Runner = Callable[[list[str]], "tuple[int, str]"]
Probe = Callable[[], "list[dict[str, Any]]"]


@dataclass
class ApplyOutcome:
    exit_code: int
    lines: list[str]
    refused: bool = False
    executed: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    manual: list[str] = field(default_factory=list)
    investigated: list[str] = field(default_factory=list)


def expand_command(command: str, python_executable: Optional[str] = None) -> list[str]:
    """Expand ``{python}`` and split a manifest install command into argv.

    Commands are trusted manifest strings with whitespace-separated
    arguments; ``{python}`` stays a single argv token so Windows
    interpreter paths are never mangled by shell-style parsing.
    """
    python = python_executable or sys.executable
    argv: list[str] = []
    for token in command.split():
        argv.append(token.replace("{python}", python))
    return argv


def _default_runner(argv: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=INSTALL_TIMEOUT_SECONDS,
    )
    return result.returncode, f"{result.stdout}\n{result.stderr}"


def low_disk_volumes(system: dict[str, Any]) -> list[tuple[str, int]]:
    """Observed volumes below the documented threshold (mount, free bytes)."""
    storage = system.get("storage", {})
    if storage.get("evidence") != "OBSERVED":
        return []
    return [
        (volume["mount"], volume["free_bytes"])
        for volume in storage.get("value", [])
        if volume["free_bytes"] < LOW_DISK_THRESHOLD_BYTES
    ]


def _action_for(entry: dict[str, Any], record: Optional[dict[str, Any]]) -> str:
    """Classify what should happen for one tool. Pure decision function."""
    if record is None:
        return "investigate"
    state = record["state"]
    if state == "UNKNOWN":
        return "investigate"
    if state == "NOT_FOUND":
        return "install" if entry.get("install_command") else "manual"
    if state == "DETECTED":
        if _below_minimum(record.get("version", ""), entry.get("min_version")):
            return "upgrade" if entry.get("install_command") else "manual"
        return "skip"
    return "investigate"


def plan_installs(
    entries: list[dict[str, Any]], records: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Structured action plan for the given (already platform-filtered) tools.

    Each row: id, tool, required, purpose, installation_method, state,
    action (skip/install/upgrade/manual/investigate), install_command,
    reason.
    """
    by_id = {record["id"]: record for record in records}
    rows: list[dict[str, Any]] = []
    for entry in entries:
        record = by_id.get(entry["id"])
        action = _action_for(entry, record)
        reason = record["reason"] if record else "no probe record"
        rows.append(
            {
                "id": entry["id"],
                "tool": entry.get("tool", entry["id"]),
                "required": entry["required"],
                "purpose": entry["purpose"],
                "installation_method": entry.get("installation_method"),
                "state": record["state"] if record else "NO_RECORD",
                "action": action,
                "install_command": entry.get("install_command"),
                "reason": reason,
            }
        )
    return rows


def _fresh_state(
    tool_id: str, probe: Probe, fallback: dict[str, Any]
) -> dict[str, Any]:
    fresh = {record["id"]: record for record in probe()}
    return fresh.get(tool_id, fallback)


def apply_installs(
    entries: list[dict[str, Any]],
    records: list[dict[str, Any]],
    *,
    runner: Optional[Runner] = None,
    system: Optional[dict[str, Any]] = None,
    probe: Optional[Probe] = None,
) -> ApplyOutcome:
    """Execute the action plan (guarded). Never claims more than a probe shows."""
    run = runner or _default_runner
    reprobe = probe or (lambda: detect_tools())

    lines: list[str] = ["install execution"]
    if system is None:
        system = detect_system()
    low = low_disk_volumes(system)
    if low:
        detail = "; ".join(f"{mount} ({free} bytes)" for mount, free in low)
        lines.append(
            "REFUSED: free disk space is below the "
            f"{LOW_DISK_THRESHOLD_BYTES}-byte threshold — {detail}. "
            "No action performed."
        )
        return ApplyOutcome(exit_code=EXIT_REFUSED, lines=lines, refused=True)

    outcome = ApplyOutcome(exit_code=EXIT_OK, lines=lines)
    rows = plan_installs(entries, records)
    for row in rows:
        if row["action"] == "skip":
            outcome.skipped.append(row["id"])
            continue
        if row["action"] == "investigate":
            outcome.investigated.append(row["id"])
            lines.append(
                f"- {row['id']}: NOT ACTED — {row['reason']} "
                "(inconclusive; investigate first)"
            )
            continue
        if row["action"] == "manual":
            outcome.manual.append(row["id"])
            lines.append(
                f"- {row['id']}: MANUAL install required per "
                f"{row['installation_method']} (no automated command recorded)"
            )
            continue

        command = row["install_command"]
        try:
            argv = expand_command(command)
        except ValueError as exc:
            lines.append(f"- {row['id']}: FAILED — command is unparseable: {exc}")
            outcome.exit_code = EXIT_FAILURE
            continue

        try:
            returncode, output = run(argv)
        except (OSError, subprocess.SubprocessError) as exc:
            lines.append(f"- {row['id']}: FAILED — could not run command: {exc}")
            outcome.exit_code = EXIT_FAILURE
            continue

        fresh = _fresh_state(row["id"], reprobe, {})
        state = fresh.get("state", "UNKNOWN")
        version = fresh.get("version", "UNKNOWN")
        tail = " ".join(output.split())[-200:]
        if returncode == 0 and state == "DETECTED":
            lines.append(
                f"- {row['id']}: {row['action'].upper()} succeeded — "
                f"probe now reports DETECTED version {version}"
            )
        else:
            outcome.exit_code = EXIT_FAILURE
            lines.append(
                f"- {row['id']}: FAILED — command exited {returncode}; "
                f"fresh probe reports {state} version {version}. "
                f"Not treated as installed. Output: {tail}"
            )
        outcome.executed.append(
            {
                "id": row["id"],
                "action": row["action"],
                "argv": argv,
                "returncode": returncode,
                "result_state": state,
                "result_version": version,
                "output": output,
            }
        )

    lines.append(
        f"summary: executed {len(outcome.executed)}, skipped "
        f"{len(outcome.skipped)}, manual {len(outcome.manual)}, "
        f"investigate {len(outcome.investigated)}"
    )
    return outcome


if __name__ == "__main__":
    from src.core.manifest import load_manifest
    from src.pem.ops import current_platform, platform_entries

    manifest = load_manifest()
    records = detect_tools()
    platform_id = current_platform()
    for row in plan_installs(platform_entries(manifest, platform_id), records):
        print(f"{row['action']:12} {row['id']}: {row['reason']}")