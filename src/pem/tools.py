"""Manifest-driven tool detection and capability states (T-0102, §22/§24).

Probes each tool registered in ``config/tool-manifest.json`` according to
its ``detection_method`` and records an evidence-backed result. Nothing is
guessed: a tool is only DETECTED when a probe actually observed it;
missing executables are NOT_FOUND; inconclusive probes are UNKNOWN
(MASTER §7, §25).

Detection only: no installation, no network, bounded probe timeouts
(MASTER §38).
"""

from __future__ import annotations

import re
import shlex
import shutil
import subprocess
from typing import Any, Optional

from src.core.manifest import CAPABILITIES, load_manifest, validate_capability_state

UNKNOWN = "UNKNOWN"
OBSERVED = "OBSERVED"

TOOL_STATES = ("DETECTED", "NOT_FOUND", "UNKNOWN")

PROBE_TIMEOUT_SECONDS = 15.0

_VERSION_PATTERN = re.compile(r"\d+(?:\.\d+)+")
_MODULE_ABSENT_MARKERS = (
    "modulenotfounderror",
    "no module named",
    "importerror",
)

#: Interpreters tried when the bare ``python`` name is absent. Many POSIX
#: distributions ship only ``python3``.
_PYTHON_ALIASES = ("python3",)


def _python_fallback() -> Optional[str]:
    """A usable interpreter when bare ``python`` is not on PATH, else None."""
    if shutil.which("python"):
        return None
    for alias in _PYTHON_ALIASES:
        found = shutil.which(alias)
        if found:
            return found
    return None


def _resolve_command(entry: dict[str, Any], command: str) -> str:
    """Substitute the resolved interpreter for a bare ``python`` probe."""
    if entry.get("executable") != "python":
        return command
    fallback = _python_fallback()
    if fallback and (command == "python" or command.startswith("python ")):
        return fallback + command[len("python"):]
    return command


def _first_version(text: str) -> Optional[str]:
    """Extract the first dotted-numeric version token actually present."""
    match = _VERSION_PATTERN.search(text)
    return match.group(0) if match else None


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def _below_minimum(version: str, minimum: Optional[str]) -> bool:
    """True only when both versions are known and version < minimum."""
    if not minimum or not version:
        return False
    try:
        got = _version_tuple(version)
        want = _version_tuple(minimum)
    except ValueError:
        return False
    length = max(len(got), len(want))
    got += (0,) * (length - len(got))
    want += (0,) * (length - len(want))
    return got < want


def _probe_command(entry: dict[str, Any]) -> Optional[str]:
    """Command string to run for this entry, or None when not probeable."""
    if entry["detection_method"] == "none":
        return None
    health_check = entry.get("health_check")
    if health_check:
        return health_check
    executable = entry.get("executable")
    if executable:
        return f"{executable} --version"
    return None


def _resolve_path(entry: dict[str, Any]) -> str:
    executable = entry.get("executable")
    if not executable:
        return UNKNOWN
    if executable == "python":
        fallback = _python_fallback()
        if fallback:
            return fallback
    found = shutil.which(executable)
    return found if found else UNKNOWN


def _record(
    entry: dict[str, Any],
    *,
    state: str,
    reason: str,
    version: str = UNKNOWN,
    executable_path: str = UNKNOWN,
    evidence: str = OBSERVED,
    probe: Optional[str] = None,
    health_ok: Optional[bool] = None,
) -> dict[str, Any]:
    return {
        "id": entry["id"],
        "state": state,
        "version": version,
        "executable_path": executable_path,
        "evidence": evidence,
        "probe": probe,
        "reason": reason,
        "health_ok": health_ok,
        "capability": list(entry.get("capability", [])),
        "min_version": entry.get("min_version"),
        "required": entry.get("required", "optional"),
    }


def _probe_tool(entry: dict[str, Any]) -> dict[str, Any]:
    command = _probe_command(entry)
    if command is None:
        return _record(
            entry,
            state="UNKNOWN",
            evidence=UNKNOWN,
            reason="detection_method 'none' — in-house component, not implemented; no probe run",
        )

    command = _resolve_command(entry, command)

    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return _record(
            entry,
            state="UNKNOWN",
            evidence=UNKNOWN,
            probe=command,
            reason=f"probe command is unparseable: {exc}",
        )

    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=PROBE_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return _record(
            entry,
            state="NOT_FOUND",
            evidence=OBSERVED,
            probe=command,
            reason=f"executable not found on PATH (argv[0]={argv[0]!r})",
        )
    except subprocess.TimeoutExpired:
        return _record(
            entry,
            state="UNKNOWN",
            evidence=UNKNOWN,
            probe=command,
            reason=f"probe timed out after {PROBE_TIMEOUT_SECONDS}s (inconclusive)",
        )
    except OSError as exc:
        return _record(
            entry,
            state="UNKNOWN",
            evidence=UNKNOWN,
            probe=command,
            reason=f"probe could not run: {exc}",
        )

    output = f"{result.stdout}\n{result.stderr}"
    version = _first_version(output)
    executable_path = _resolve_path(entry)

    if result.returncode == 0:
        return _record(
            entry,
            state="DETECTED",
            version=version if version else UNKNOWN,
            executable_path=executable_path,
            evidence=OBSERVED,
            probe=command,
            health_ok=True,
            reason="probe exited 0",
        )

    lowered = output.lower()
    if entry["detection_method"] == "python_module" and any(
        marker in lowered for marker in _MODULE_ABSENT_MARKERS
    ):
        return _record(
            entry,
            state="NOT_FOUND",
            evidence=OBSERVED,
            executable_path=executable_path,
            probe=command,
            reason="probe reported the Python module is absent",
        )

    if version:
        return _record(
            entry,
            state="DETECTED",
            version=version,
            executable_path=executable_path,
            evidence=OBSERVED,
            probe=command,
            health_ok=False,
            reason=f"version output observed but health check exited {result.returncode}",
        )

    return _record(
        entry,
        state="UNKNOWN",
        evidence=UNKNOWN,
        executable_path=executable_path,
        probe=command,
        reason=(
            f"probe exited {result.returncode} with no parseable version "
            "(inconclusive)"
        ),
    )


def detect_tools(manifest: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    """Probe every tool in the manifest. Never raises for probe failures.

    Each record: id, state (DETECTED/NOT_FOUND/UNKNOWN), version,
    executable_path, evidence (OBSERVED/UNKNOWN), probe, reason,
    health_ok, capability, min_version.
    """
    data = manifest if manifest is not None else load_manifest()
    return [_probe_tool(entry) for entry in data["tools"]]


def capability_states(tool_records: list[dict[str, Any]]) -> dict[str, str]:
    """Aggregate tool records into MASTER §22 capability states.

    Rules (first match wins):
    1. A providing tool DETECTED without a failed health check → READY.
    2. A providing tool DETECTED but health check failed or version is
       below a known minimum → LIMITED.
    3. No detections and any providing probe inconclusive (UNKNOWN) →
       UNKNOWN.
    4. All providing tools conclusively NOT_FOUND → UNAVAILABLE.
    5. Otherwise (no providers, or providers not probeable) → UNKNOWN.
    """
    result: dict[str, str] = {}
    for capability in sorted(CAPABILITIES):
        providers = [r for r in tool_records if capability in r.get("capability", [])]
        if not providers:
            state = "UNKNOWN"
        else:
            detected = [p for p in providers if p["state"] == "DETECTED"]
            healthy = [p for p in detected if p["health_ok"] is not False]
            below_min = [
                p
                for p in detected
                if _below_minimum(
                    p["version"] if p["version"] != UNKNOWN else "",
                    p.get("min_version"),
                )
            ]
            if healthy and not below_min:
                state = "READY"
            elif detected:
                state = "LIMITED"
            elif any(p["state"] == "UNKNOWN" for p in providers):
                state = "UNKNOWN"
            elif all(p["state"] == "NOT_FOUND" for p in providers):
                state = "UNAVAILABLE"
            else:
                state = "UNKNOWN"
        result[capability] = validate_capability_state(state)
    return result


if __name__ == "__main__":
    import json

    records = detect_tools()
    print(json.dumps(records, indent=2))
    print(json.dumps(capability_states(records), indent=2))
