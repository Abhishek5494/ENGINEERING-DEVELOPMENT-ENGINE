"""Environment report generation (T-0103, MASTER §25).

Turns detector output into `environment.json` (machine-readable) and
`environment-report.md` (human-readable). Generation only — no
installation, no network, no probing.

Honesty rules (MASTER §7, §25):
- a tool is reported present only when its record says DETECTED;
- NOT_FOUND tools are listed as missing dependencies;
- UNKNOWN tools are listed as unknown, never as present or missing;
- warnings/recommendations are data-driven suggestions; nothing is ever
  installed by this module.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from src.core.config import REPO_ROOT

UNKNOWN = "UNKNOWN"

# A volume with less free space than this produces a LOW_DISK_SPACE
# warning. 1 GiB: comfortably above typical Windows pagefile/updates
# headroom needs when bulk-installing toolchains.
LOW_DISK_THRESHOLD_BYTES = 1 * 1024**3

JSON_FILENAME = "environment.json"
MARKDOWN_FILENAME = "environment-report.md"

REPORT_KEYS = (
    "generated_at",
    "platform",
    "tools",
    "missing_tools",
    "unknown_tools",
    "capabilities",
    "warnings",
    "limitations",
    "recommendations",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _storage_warnings(system: dict[str, Any]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    storage = system.get("storage", {})
    if storage.get("evidence") != "OBSERVED":
        return warnings
    for volume in storage.get("value", []):
        mount = str(volume.get("mount", UNKNOWN))
        free = volume.get("free_bytes")
        if isinstance(free, int) and free < LOW_DISK_THRESHOLD_BYTES:
            warnings.append(
                {
                    "code": "LOW_DISK_SPACE",
                    "message": (
                        f"volume {mount} has only {free} bytes free "
                        f"(threshold {LOW_DISK_THRESHOLD_BYTES} bytes)"
                    ),
                }
            )
    return warnings


def _required_tool_warnings(tools: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Warn about tools classified 'required' that detection did not confirm."""
    warnings: list[dict[str, str]] = []
    for record in tools:
        if record.get("required") == "required" and record.get("state") != "DETECTED":
            warnings.append(
                {
                    "code": "REQUIRED_TOOL_NOT_DETECTED",
                    "message": (
                        f"required tool '{record.get('id')}' is "
                        f"{record.get('state')} (probe: {record.get('reason')})"
                    ),
                }
            )
    return warnings


def build_environment(
    system: dict[str, Any],
    tools: list[dict[str, Any]],
    capabilities: dict[str, str],
    *,
    generated_at: Optional[str] = None,
) -> dict[str, Any]:
    """Build the environment report document from detector outputs.

    `generated_at` is the only non-deterministic field (defaults to the
    current UTC timestamp); identical inputs otherwise produce identical
    output.
    """
    missing_tools = [r["id"] for r in tools if r["state"] == "NOT_FOUND"]
    unknown_tools = [r["id"] for r in tools if r["state"] == "UNKNOWN"]

    warnings = _storage_warnings(system) + _required_tool_warnings(tools)

    limitations = [
        f"capability '{capability}' is UNKNOWN — contributing tools are "
        "not probeable or not implemented yet"
        for capability, state in sorted(capabilities.items())
        if state == "UNKNOWN"
    ]
    limitations += [
        f"capability '{capability}' is UNAVAILABLE — no detected tool provides it"
        for capability, state in sorted(capabilities.items())
        if state == "UNAVAILABLE"
    ]

    recommendations: list[str] = []
    by_id = {r["id"]: r for r in tools}
    for tool_id in missing_tools:
        record = by_id[tool_id]
        provides = ", ".join(record.get("capability", [])) or "no mapped capability"
        recommendations.append(
            f"consider installing '{tool_id}' if its capability is needed "
            f"({provides}); see config/tool-manifest.json — no automatic "
            "installation is performed"
        )
    for warning in warnings:
        if warning["code"] == "LOW_DISK_SPACE":
            recommendations.append(
                "free disk space before installing additional tools "
                f"({warning['message']})"
            )

    return {
        "generated_at": generated_at or _now_iso(),
        "platform": dict(system),
        "tools": [
            {
                "id": r["id"],
                "state": r["state"],
                "version": r.get("version", UNKNOWN),
                "executable_path": r.get("executable_path", UNKNOWN),
                "evidence": r.get("evidence", UNKNOWN),
            }
            for r in tools
        ],
        "missing_tools": missing_tools,
        "unknown_tools": unknown_tools,
        "capabilities": dict(capabilities),
        "warnings": warnings,
        "limitations": limitations,
        "recommendations": recommendations,
    }


def _platform_lines(platform: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key in (
        "os_name",
        "os_version",
        "cpu",
        "architecture",
        "ram_bytes",
        "gpu",
    ):
        field = platform.get(key, {})
        lines.append(f"- {key}: `{field.get('value', UNKNOWN)}` ({field.get('evidence', UNKNOWN)})")
    storage = platform.get("storage", {})
    if storage.get("evidence") == "OBSERVED":
        for volume in storage.get("value", []):
            lines.append(
                f"- storage {volume['mount']}: total {volume['total_bytes']} bytes, "
                f"free {volume['free_bytes']} bytes (OBSERVED)"
            )
    else:
        lines.append("- storage: UNKNOWN")
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    """Render the report as GitHub-flavored Markdown."""
    lines: list[str] = [
        "# Environment Report",
        "",
        f"Generated at: `{report['generated_at']}` (UTC)",
        "",
        "Regenerate with PEM; this file is machine-specific and gitignored.",
        "Evidence classes: OBSERVED = probe-verified, UNKNOWN = not determined.",
        "",
        "## Platform",
        "",
        *_platform_lines(report["platform"]),
        "",
        "## Tools",
        "",
        "| tool | state | version | evidence |",
        "|---|---|---|---|",
    ]
    for record in report["tools"]:
        lines.append(
            f"| {record['id']} | {record['state']} | {record['version']} "
            f"| {record['evidence']} |"
        )

    lines += ["", "## Capabilities", "", "| capability | state |", "|---|---|"]
    for capability, state in sorted(report["capabilities"].items()):
        lines.append(f"| {capability} | {state} |")

    lines += ["", "## Missing dependencies", ""]
    if report["missing_tools"]:
        for tool_id in report["missing_tools"]:
            lines.append(f"- `{tool_id}` — probe did NOT find it (OBSERVED absence)")
    else:
        lines.append("(none)")

    lines += ["", "## Unknown tools", ""]
    if report["unknown_tools"]:
        for tool_id in report["unknown_tools"]:
            lines.append(f"- `{tool_id}` — state could not be determined (UNKNOWN)")
    else:
        lines.append("(none)")

    lines += ["", "## Warnings", ""]
    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- **{warning['code']}**: {warning['message']}")
    else:
        lines.append("(none)")

    lines += ["", "## Limitations", ""]
    if report["limitations"]:
        lines.extend(f"- {item}" for item in report["limitations"])
    else:
        lines.append("(none)")

    lines += ["", "## Recommendations", ""]
    if report["recommendations"]:
        lines.extend(f"- {item}" for item in report["recommendations"])
    else:
        lines.append("(none)")

    lines.append("")
    return "\n".join(lines)


def write_reports(
    report: dict[str, Any], directory: Optional[Path] = None
) -> tuple[Path, Path]:
    """Write environment.json and environment-report.md; return both paths."""
    target = Path(directory) if directory is not None else REPO_ROOT
    json_path = target / JSON_FILENAME
    md_path = target / MARKDOWN_FILENAME
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


if __name__ == "__main__":
    from src.pem.detect import detect_system
    from src.pem.tools import capability_states, detect_tools

    system = detect_system()
    tool_records = detect_tools()
    document = build_environment(system, tool_records, capability_states(tool_records))
    paths = write_reports(document)
    print(f"wrote {paths[0]}")
    print(f"wrote {paths[1]}")
