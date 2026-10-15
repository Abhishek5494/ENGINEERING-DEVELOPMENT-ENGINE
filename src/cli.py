"""Unified offline command-line interface (T-2000; MASTER §49).

``python -m src <command>`` exposes the platform's offline capabilities and
the partial end-to-end engineering workflow through one entry point. Every
command is a thin, honest wrapper over an existing subsystem API: nothing is
faked and network/install-gated stages are reported as ``BLOCKED`` /
``UNAVAILABLE`` rather than as success (MASTER §46).

Subsystems keep their own ``python -m src.<module>`` entry points; this
dispatcher only aggregates them so a user or automated agent can operate the
project from a single place.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

from src import __version__


def _print_json(payload: Any) -> None:
    """Print ``payload`` as UTF-8-safe, human-readable JSON."""
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


# --------------------------------------------------------------------------
# Command handlers. Each returns a process exit code.
# --------------------------------------------------------------------------


def _cmd_version(_args: argparse.Namespace) -> int:
    print(f"engineering-development-engine {__version__}")
    return 0


def _cmd_env(args: argparse.Namespace) -> int:
    from src.pem.detect import detect_system
    from src.pem.report import build_environment, render_markdown, write_reports
    from src.pem.tools import capability_states, detect_tools

    system = detect_system()
    records = detect_tools()
    document = build_environment(system, records, capability_states(records))

    if args.write:
        json_path, md_path = write_reports(document)
        print(f"wrote {json_path}")
        print(f"wrote {md_path}")
        return 0
    if args.json:
        _print_json(document)
        return 0
    print(render_markdown(document))
    return 0


def _cmd_tools(args: argparse.Namespace) -> int:
    from src.pem.tools import capability_states, detect_tools

    records = detect_tools()
    capabilities = capability_states(records)
    if args.json:
        _print_json({"tools": records, "capabilities": capabilities})
        return 0
    for record in records:
        version = record.get("version") or ""
        print(f"{record['id']:<16} {record['state']:<12} {version}")
    print()
    for name, state in sorted(capabilities.items()):
        print(f"{name:<24} {state}")
    return 0


def _cmd_storage(args: argparse.Namespace) -> int:
    from src.core.storage import StorageError, preflight

    try:
        check = preflight(args.operation, args.path, margin_bytes=args.margin_bytes)
    except StorageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _print_json(check.to_dict())
    return 0 if check.ok else 3


def _cmd_upstream(args: argparse.Namespace) -> int:
    from src.core.upstream import load_upstream_sources, source_ids

    registry = load_upstream_sources()
    if args.json:
        _print_json(registry)
        return 0
    ids = source_ids(registry)
    print(f"upstream registry OK: {len(ids)} sources: {', '.join(ids)}")
    return 0


def _cmd_cie_identify(args: argparse.Namespace) -> int:
    from src.cie.identify import identify_page

    if args.html:
        html = Path(args.html).read_text(encoding="utf-8", errors="replace")
    else:
        html = sys.stdin.read()
    identification = identify_page(args.url, html)
    _print_json(identification.to_dict())
    return 0


def _cmd_rea_inspect(args: argparse.Namespace) -> int:
    from src.rea.inspection import inspect_target

    entries = inspect_target(args.path)
    _print_json([entry.to_dict() for entry in entries])
    return 0


def _cmd_workflow_run(args: argparse.Namespace) -> int:
    from src.orchestration import run_workflow, write_project
    from src.orchestration.workflow import WorkflowError

    cells: list[str] = []
    if args.code:
        cells.append(Path(args.code).read_text(encoding="utf-8", errors="replace"))

    report = run_workflow(args.name, notebook_cells=cells, kernel=args.kernel)

    if args.write:
        try:
            target = write_project(report, overwrite=args.overwrite)
        except WorkflowError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"wrote {target}")

    if args.json:
        _print_json(report.to_dict())
        return 0

    print(f"workflow {report.name!r} - {report.validation_level}")
    for result in report.results:
        line = f"  {result.status:<12} {result.stage.value:<12} {result.detail}"
        if result.blocker:
            line += f"  [blocker: {result.blocker}]"
        print(line)
    return 0


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the ``python -m src`` argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m src",
        description="Engineering development platform — unified offline CLI (T-2000).",
    )
    parser.add_argument(
        "--version", action="store_true", help="print the platform version and exit"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("version", help="print the platform version").set_defaults(
        func=_cmd_version
    )

    p_env = sub.add_parser("env", help="detect the environment and build a report")
    p_env.add_argument("--json", action="store_true", help="emit JSON")
    p_env.add_argument(
        "--write", action="store_true", help="write environment.json and -report.md"
    )
    p_env.set_defaults(func=_cmd_env)

    p_tools = sub.add_parser("tools", help="list detected tools and capability states")
    p_tools.add_argument("--json", action="store_true", help="emit JSON")
    p_tools.set_defaults(func=_cmd_tools)

    p_storage = sub.add_parser("storage", help="development storage operations")
    storage_sub = p_storage.add_subparsers(dest="storage_command")
    p_preflight = storage_sub.add_parser("preflight", help="check an operation")
    p_preflight.add_argument("operation", help="operation name from config/storage.json")
    p_preflight.add_argument("--path", default=None, help="destination path")
    p_preflight.add_argument("--margin-bytes", type=int, default=0)
    p_preflight.set_defaults(func=_cmd_storage)
    p_storage.set_defaults(func=None)

    p_upstream = sub.add_parser("upstream", help="upstream source registry")
    p_upstream.add_argument("--json", action="store_true", help="emit JSON")
    p_upstream.set_defaults(func=_cmd_upstream)

    p_cie = sub.add_parser("cie", help="Component Intelligence Engine")
    cie_sub = p_cie.add_subparsers(dest="cie_command")
    p_identify = cie_sub.add_parser(
        "identify", help="identify a component from supplied local HTML"
    )
    p_identify.add_argument("--url", required=True, help="source URL of the page")
    p_identify.add_argument(
        "--html", default=None, help="HTML file to read (default: stdin)"
    )
    p_identify.set_defaults(func=_cmd_cie_identify)
    p_cie.set_defaults(func=None)

    p_rea = sub.add_parser("rea", help="Reverse Engineering Engine (authorized)")
    rea_sub = p_rea.add_subparsers(dest="rea_command")
    p_inspect = rea_sub.add_parser("inspect", help="fingerprint a local file")
    p_inspect.add_argument("path", help="file to inspect")
    p_inspect.set_defaults(func=_cmd_rea_inspect)
    p_rea.set_defaults(func=None)

    p_workflow = sub.add_parser("workflow", help="end-to-end engineering workflow")
    workflow_sub = p_workflow.add_subparsers(dest="workflow_command")
    p_run = workflow_sub.add_parser("run", help="run the partial workflow")
    p_run.add_argument("--name", required=True, help="workflow/project name")
    p_run.add_argument(
        "--code", default=None, help="Python file used as a notebook cell"
    )
    p_run.add_argument("--kernel", default="python3")
    p_run.add_argument("--json", action="store_true", help="emit JSON")
    p_run.add_argument("--write", action="store_true", help="write the project directory")
    p_run.add_argument("--overwrite", action="store_true")
    p_run.set_defaults(func=_cmd_workflow_run)
    p_workflow.set_defaults(func=None)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for ``python -m src`` and the ``main`` console function."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if getattr(args, "version", False):
        return _cmd_version(args)

    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 2
    return func(args)


__all__ = ["build_parser", "main"]
