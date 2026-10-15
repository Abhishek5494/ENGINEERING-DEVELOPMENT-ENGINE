"""Platform operations: healthcheck / install / update (T-0104, §23).

Thin command layer over the existing PEM detectors — no re-probing
logic, no duplicated detection code. The PowerShell scripts under
``scripts/windows/`` are wrappers around this module.

Exit codes:
    0  healthy (healthcheck) or operation completed
    1  unhealthy (healthcheck) or some install commands failed
    2  execution error (bad arguments, unreadable manifest, import failure)
    3  install --execute refused (preconditions not met, e.g. low disk)

Plan operations perform zero changes. ``install`` stays plan-only unless
``--execute`` is passed, which runs guarded, idempotent installation
logic from ``src.pem.installer`` (T-0107). The current platform is
always detected automatically (MASTER §23); there is no platform
override flag.
"""

from __future__ import annotations

import argparse
import platform as _platform
import sys
from typing import Any, Optional

from src.core.manifest import ManifestError, load_manifest
from src.core.storage import StorageError, preflight
from src.pem.detect import detect_system
from src.pem.installer import EXIT_REFUSED, apply_installs, plan_installs
from src.pem.report import LOW_DISK_THRESHOLD_BYTES
from src.pem.tools import detect_tools

EXIT_OK = 0
EXIT_UNHEALTHY = 1
EXIT_ERROR = 2

PLATFORM_NAMES = {"Windows": "windows", "Linux": "linux", "Darwin": "macos"}

PLAN_ONLY_NOTICE = (
    "PLAN-ONLY: this invocation performs no changes. The install plan is "
    "read-only unless --execute is passed (guarded, idempotent; T-0107); "
    "update remains plan-only."
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

    lines = [
        f"install plan (platform: {platform_id})",
        PLAN_ONLY_NOTICE,
        "nothing is installed automatically; review the plan below",
        "pass --execute to perform this plan (guarded; refused if disk is low)",
    ]
    rows = plan_installs(platform_entries(data, platform_id), records)
    ordered = [r for r in rows if r["required"] == "required"] + [
        r for r in rows if r["required"] != "required"
    ]
    count = 0
    for row in ordered:
        if row["action"] in {"install", "upgrade", "manual"}:
            count += 1
            lines.append(
                f"- {row['required'].upper()} {row['id']} ({row['state']}): "
                f"{row['purpose']} — installation method: "
                f"{row['installation_method']}"
            )
    lines.append(
        f"plan complete: {count} tool(s) to install, 0 change(s) performed"
    )
    return EXIT_OK, lines


def _storage_preflight_lines() -> list[str]:
    """Storage preflight for dependency installs on the configured workspace.

    Uses the reusable ``src.core.storage`` utility. When the destination
    cannot be measured (e.g. the drive does not exist on this host) it is
    reported as WARN and does not block — the existing OBSERVED-volume guard
    in ``apply_installs`` still applies.
    """
    try:
        check = preflight("dependency_install")
    except StorageError as exc:
        return [f"storage preflight: UNKNOWN — not measurable ({exc}) — not counted"]
    return [f"storage preflight: {check.message}"]


def run_install_execute(
    *,
    manifest: Optional[dict[str, Any]] = None,
    tools: Optional[list[dict[str, Any]]] = None,
    platform_name: Optional[str] = None,
    system: Optional[dict[str, Any]] = None,
    runner: Any = None,
    probe: Any = None,
) -> tuple[int, list[str]]:
    """Perform the guarded, idempotent install plan (T-0107).

    Refuses without acting (exit 3) when an observed volume is below the
    documented threshold. Never claims more than a fresh probe shows.
    """
    data = manifest if manifest is not None else load_manifest()
    records = tools if tools is not None else detect_tools(data)
    platform_id = platform_name if platform_name is not None else current_platform()

    pre_lines = _storage_preflight_lines()
    for line in pre_lines:
        if line.startswith("BLOCKED"):
            return EXIT_REFUSED, [f"platform: {platform_id}"] + pre_lines

    outcome = apply_installs(
        platform_entries(data, platform_id),
        records,
        runner=runner,
        system=system,
        probe=probe,
    )
    return outcome.exit_code, [f"platform: {platform_id}"] + pre_lines + outcome.lines


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
    "exit codes: 0 = healthy or operation completed; 1 = unhealthy "
    "(healthcheck) or failed install command; 2 = execution error; "
    "3 = install --execute refused (e.g. disk below threshold). "
    "install is plan-only unless --execute is passed."
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
    parser.add_argument(
        "--execute",
        action="store_true",
        help="install: perform the plan (guarded, idempotent); "
        "default is plan-only",
    )
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else EXIT_ERROR

    try:
        if args.execute:
            if args.command != "install":
                print(
                    "error: --execute is only valid for the 'install' command",
                    file=sys.stderr,
                )
                return EXIT_ERROR
            code, lines = run_install_execute()
        else:
            code, lines = COMMANDS[args.command]()
    except (ManifestError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
