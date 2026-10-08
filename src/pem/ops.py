"""Platform operations: healthcheck / install / update (T-0104, §23).

Thin command layer over the existing PEM detectors — no re-probing
logic, no duplicated detection code. The PowerShell scripts under
``scripts/windows/`` are wrappers around this module.

Exit codes:
    0  healthy (healthcheck) or plan computed successfully (install/update)
    1  unhealthy (healthcheck): a required tool is not confirmed healthy,
       or an observed volume is below LOW_DISK_THRESHOLD_BYTES
    2  execution error (bad arguments, unreadable manifest, import failure)

``install`` and ``update`` are PLAN-ONLY: they perform zero changes and
say so. Mutation arrives with T-0107 (idempotent install logic). The
current platform is always detected automatically (MASTER §23); there is
no platform override flag.
"""

from __future__ import annotations

import argparse
import platform as _platform
import sys
from typing import Any, Optional

from src.core.manifest import ManifestError, load_manifest
from src.pem.detect import detect_system
from src.pem.report import LOW_DISK_THRESHOLD_BYTES
from src.pem.tools import detect_tools

EXIT_OK = 0
EXIT_UNHEALTHY = 1
EXIT_ERROR = 2

PLATFORM_NAMES = {"Windows": "windows", "Linux": "linux", "Darwin": "macos"}

PLAN_ONLY_NOTICE = (
    "PLAN-ONLY: no changes performed; installation/update logic arrives "
    "with task T-0107"
)


def current_platform(system_name: Optional[str] = None) -> str:
    """Detect the current platform automatically (MASTER §23)."""
    name = system_name if system_name is not None else _platform.system()
    if name not in PLATFORM_NAMES:
        raise ValueError(f"unsupported platform: {name!r}")
    return PLATFORM_NAMES[name]


def platform_entries(
    manifest: dict[str, Any], platform_name: str
) -> list[dict[str, Any]]:
    """Manifest entries supporting the given platform, in manifest order."""
    return [
        entry
        for entry in manifest["tools"]
        if platform_name in entry["supported_platforms"]
    ]


def run_healthcheck(
    *,
    manifest: Optional[dict[str, Any]] = None,
    system: Optional[dict[str, Any]] = None,
    tools: Optional[list[dict[str, Any]]] = None,
    platform_name: Optional[str] = None,
) -> tuple[int, list[str]]:
    """Evaluate health checks. Returns (exit_code, printed_lines)."""
    data = manifest if manifest is not None else load_manifest()
    sysinfo = system if system is not None else detect_system()
    records = tools if tools is not None else detect_tools(data)
    platform_id = platform_name if platform_name is not None else current_platform()
    by_id = {record["id"]: record for record in records}

    lines = [f"healthcheck (platform: {platform_id})"]
    failures = 0

    for entry in platform_entries(data, platform_id):
        if entry["required"] != "required":
            continue
        record = by_id.get(entry["id"])
        if (
            record is None
            or record["state"] != "DETECTED"
            or record["health_ok"] is not True
        ):
            reason = record["reason"] if record else "no probe record"
            lines.append(
                f"[FAIL] required tool '{entry['id']}': "
                f"{record['state'] if record else 'MISSING RECORD'} — {reason}"
            )
            failures += 1
        else:
            lines.append(
                f"[PASS] required tool '{entry['id']}': DETECTED "
                f"version {record['version']} (health check ok)"
            )

    storage = sysinfo.get("storage", {})
    if storage.get("evidence") == "OBSERVED":
        for volume in storage.get("value", []):
            mount = volume["mount"]
            free = volume["free_bytes"]
            if free < LOW_DISK_THRESHOLD_BYTES:
                lines.append(
                    f"[FAIL] storage {mount}: {free} bytes free "
                    f"(threshold {LOW_DISK_THRESHOLD_BYTES})"
                )
                failures += 1
            else:
                lines.append(
                    f"[PASS] storage {mount}: {free} bytes free "
                    f"(threshold {LOW_DISK_THRESHOLD_BYTES})"
                )
    else:
        lines.append(
            "[WARN] storage: UNKNOWN (no observed data) — not counted"
        )

    if failures:
        lines.append(f"RESULT: UNHEALTHY ({failures} failed check(s))")
        return EXIT_UNHEALTHY, lines
    lines.append("RESULT: HEALTHY")
    return EXIT_OK, lines


def run_install_plan(
    *,
    manifest: Optional[dict[str, Any]] = None,
    tools: Optional[list[dict[str, Any]]] = None,
    platform_name: Optional[str] = None,
) -> tuple[int, list[str]]:
    """Print the install plan for the current platform. Never mutates."""
    data = manifest if manifest is not None else load_manifest()
    records = tools if tools is not None else detect_tools(data)
    platform_id = platform_name if platform_name is not None else current_platform()
    by_id = {record["id"]: record for record in records}

    lines = [
        f"install plan (platform: {platform_id})",
        PLAN_ONLY_NOTICE,
        "nothing is installed automatically; review the plan below",
    ]
    entries = platform_entries(data, platform_id)
    ordered = [e for e in entries if e["required"] == "required"] + [
        e for e in entries if e["required"] != "required"
    ]
    missing = 0
    for entry in ordered:
        record = by_id.get(entry["id"])
        if record is None or record["state"] == "NOT_FOUND":
            missing += 1
            state = record["state"] if record else "MISSING RECORD"
            lines.append(
                f"- {entry['required'].upper()} {entry['id']} ({state}): "
                f"{entry['purpose']} — installation method: "
                f"{entry['installation_method']}"
            )
    lines.append(
        f"plan complete: {missing} tool(s) to install, 0 change(s) performed"
    )
    return EXIT_OK, lines


def run_update_plan(
    *,
    manifest: Optional[dict[str, Any]] = None,
    tools: Optional[list[dict[str, Any]]] = None,
    platform_name: Optional[str] = None,
) -> tuple[int, list[str]]:
    """Print the update plan for the current platform. Never mutates."""
    data = manifest if manifest is not None else load_manifest()
    records = tools if tools is not None else detect_tools(data)
    platform_id = platform_name if platform_name is not None else current_platform()
    by_id = {record["id"]: record for record in records}

    lines = [
        f"update plan (platform: {platform_id})",
        PLAN_ONLY_NOTICE,
    ]
    for entry in platform_entries(data, platform_id):
        record = by_id.get(entry["id"])
        if record is None or record["state"] != "DETECTED":
            state = record["state"] if record else "MISSING RECORD"
            lines.append(f"- {entry['id']}: {state} — nothing to update")
            continue
        preferred = entry["preferred_version"]
        lines.append(
            f"- {entry['id']}: detected {record['version']}; "
            f"preferred version: "
            f"{preferred if preferred else 'UNKNOWN (not recorded in manifest)'}"
        )
    lines.append("plan complete: 0 change(s) performed")
    return EXIT_OK, lines


COMMANDS = {
    "healthcheck": run_healthcheck,
    "install": run_install_plan,
    "update": run_update_plan,
}

EPILOG = (
    "exit codes: 0 = healthy or plan computed; 1 = unhealthy (healthcheck "
    "only); 2 = execution error. install and update are plan-only: they "
    "perform zero changes until task T-0107."
)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.pem.ops",
        description="PEM platform operations (shared code behind "
        "scripts/<platform> wrappers, MASTER §23).",
        epilog=EPILOG,
    )
    parser.add_argument(
        "command",
        choices=sorted(COMMANDS),
        help="operation to run",
    )
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else EXIT_ERROR

    try:
        code, lines = COMMANDS[args.command]()
    except (ManifestError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
