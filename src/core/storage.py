"""Storage preflight and the D:-drive development workspace (T-1800/T-1801).

Reusable, standard-library storage checks used to protect expensive
development operations (dependency installs, model downloads, builds,
dataset extraction, container/VM creation) from exhausting a drive — in
particular the Windows system drive ``C:``.

Design rules (ADR-0003 §2/§5; MASTER §7/§49):

- the destination drive is measured, never assumed: the path is resolved to
  the nearest existing ancestor and ``shutil.disk_usage`` reports its free
  space;
- thresholds are data-driven (``config/storage.json``), not hard-coded as a
  single universal constant — large operations carry larger headroom;
- an operation is blocked only when free space is below
  ``required_bytes + margin_bytes + min_free_bytes``; a warning is surfaced
  with the concrete drive/directory that needs attention;
- the module performs **no** deletion, download, install, or network work.

The Windows system-drive path ``LOW_DISK_THRESHOLD_BYTES`` used by the PEM
report/installer (1 GiB) is the same order of magnitude as this module's
``DEFAULT_MIN_FREE_BYTES``; this module generalises it per operation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional

from src.core.config import STORAGE_CONFIG_PATH, load_json

#: Fallback headroom when a caller does not specify one (1 GiB).
DEFAULT_MIN_FREE_BYTES: int = 1 * 1024**3

#: Environment variable that overrides ``development_root`` for the process.
DEVELOPMENT_ROOT_ENV: str = "EDE_DEV_ROOT"

__all__ = [
    "DEFAULT_MIN_FREE_BYTES",
    "DEVELOPMENT_ROOT_ENV",
    "STORAGE_CONFIG_PATH",
    "DiskUsage",
    "InsufficientStorageError",
    "StorageCheck",
    "StorageError",
    "check_storage",
    "development_root",
    "disk_usage",
    "drive_of",
    "format_bytes",
    "free_bytes",
    "load_storage_config",
    "location",
    "main",
    "preflight",
    "require_storage",
]

_BYTE_UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB")

_DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": "1.0",
    "development_root": "D:/EngineeringWorkspace",
    "min_free_bytes_default": DEFAULT_MIN_FREE_BYTES,
    "locations": {},
    "operations": {},
}


class StorageError(ValueError):
    """Raised when storage configuration or a measurement is invalid."""


class InsufficientStorageError(StorageError):
    """Raised by ``require_storage`` when an operation must not proceed."""

    def __init__(self, check: "StorageCheck") -> None:
        super().__init__(check.message)
        self.check = check


@dataclass(frozen=True)
class DiskUsage:
    """Free/total/used bytes for the volume backing a path (OBSERVED)."""

    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "total_bytes": self.total_bytes,
            "used_bytes": self.used_bytes,
            "free_bytes": self.free_bytes,
        }


@dataclass(frozen=True)
class StorageCheck:
    """Outcome of a storage preflight for one operation (OBSERVED)."""

    operation: str
    path: str
    drive: str
    free_bytes: int
    required_bytes: int
    min_free_bytes: int
    margin_bytes: int
    needed_bytes: int
    shortfall_bytes: int
    ok: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "path": self.path,
            "drive": self.drive,
            "free_bytes": self.free_bytes,
            "required_bytes": self.required_bytes,
            "min_free_bytes": self.min_free_bytes,
            "margin_bytes": self.margin_bytes,
            "needed_bytes": self.needed_bytes,
            "shortfall_bytes": self.shortfall_bytes,
            "ok": self.ok,
            "message": self.message,
        }


# --------------------------------------------------------------------------
# Measurement
# --------------------------------------------------------------------------


def format_bytes(value: int | float) -> str:
    """Human-readable binary size, e.g. ``2.23 GiB``."""
    size = float(value)
    sign = "-" if size < 0 else ""
    size = abs(size)
    for unit in _BYTE_UNITS:
        if size < 1024.0 or unit == _BYTE_UNITS[-1]:
            if unit == "B":
                return f"{sign}{int(size)} {unit}"
            return f"{sign}{size:.2f} {unit}"
        size /= 1024.0
    return f"{sign}{size:.2f} {_BYTE_UNITS[-1]}"  # pragma: no cover


def _nearest_existing(path: Path) -> Path:
    candidate = path
    while not candidate.exists():
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    return candidate


def drive_of(path: str | Path) -> str:
    """The volume anchor for a path (``D:\\`` on Windows, ``/`` on POSIX)."""
    anchor = Path(path).resolve().anchor
    return anchor or os.sep


def disk_usage(path: str | Path) -> DiskUsage:
    """Measure the volume that backs ``path`` (nearest existing ancestor).

    Raises:
        StorageError: the backing volume cannot be measured.
    """
    target = _nearest_existing(Path(path))
    try:
        usage = shutil.disk_usage(target)
    except OSError as exc:
        raise StorageError(f"cannot measure storage at {target}: {exc}") from exc
    return DiskUsage(
        path=str(target),
        total_bytes=int(usage.total),
        used_bytes=int(usage.used),
        free_bytes=int(usage.free),
    )


def free_bytes(path: str | Path) -> int:
    """Free bytes on the volume backing ``path``."""
    return disk_usage(path).free_bytes


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------


def load_storage_config(path: Optional[str | Path] = None) -> dict[str, Any]:
    """Load ``config/storage.json``, merged onto safe defaults."""
    resolved = STORAGE_CONFIG_PATH if path is None else Path(path)
    return load_json(resolved, defaults=_DEFAULT_CONFIG)


def development_root(config: Optional[Mapping[str, Any]] = None) -> Path:
    """Absolute development workspace root on D: (or ``EDE_DEV_ROOT``)."""
    override = os.environ.get(DEVELOPMENT_ROOT_ENV)
    if override:
        return Path(override)
    data = config if config is not None else load_storage_config()
    return Path(str(data["development_root"]))


def location(name: str, config: Optional[Mapping[str, Any]] = None) -> Path:
    """Absolute path of a named workspace location (e.g. ``pip_cache``)."""
    data = config if config is not None else load_storage_config()
    locations = data.get("locations", {})
    if name not in locations:
        known = ", ".join(sorted(locations)) or "(none configured)"
        raise StorageError(f"unknown storage location {name!r}; known: {known}")
    return development_root(data) / str(locations[name])


# --------------------------------------------------------------------------
# Preflight
# --------------------------------------------------------------------------


def check_storage(
    operation: str,
    path: Optional[str | Path] = None,
    *,
    required_bytes: int = 0,
    min_free_bytes: int = DEFAULT_MIN_FREE_BYTES,
    margin_bytes: int = 0,
    config: Optional[Mapping[str, Any]] = None,
) -> StorageCheck:
    """Check free space on the destination drive for ``operation``.

    The operation is permitted when
    ``free >= required_bytes + margin_bytes + min_free_bytes``.
    """
    if required_bytes < 0 or margin_bytes < 0 or min_free_bytes < 0:
        raise StorageError("byte amounts must be non-negative")
    data = config if config is not None else load_storage_config()
    destination = Path(path) if path is not None else development_root(data)
    free = free_bytes(destination)
    needed = int(required_bytes) + int(margin_bytes) + int(min_free_bytes)
    shortfall = max(0, needed - free)
    drive = drive_of(destination)
    ok = free >= needed
    if ok:
        message = (
            f"{operation}: OK — {format_bytes(free)} free on {drive} "
            f">= {format_bytes(needed)} required "
            f"(min free {format_bytes(min_free_bytes)})"
        )
    else:
        message = (
            f"{operation}: BLOCKED — only {format_bytes(free)} free on {drive}, "
            f"need {format_bytes(needed)} "
            f"({format_bytes(shortfall)} short). "
            f"Free space on {drive} or point development_root "
            f"({DEVELOPMENT_ROOT_ENV}) at a drive with space. "
            f"Destination: {destination}"
        )
    return StorageCheck(
        operation=operation,
        path=str(destination),
        drive=drive,
        free_bytes=free,
        required_bytes=int(required_bytes),
        min_free_bytes=int(min_free_bytes),
        margin_bytes=int(margin_bytes),
        needed_bytes=needed,
        shortfall_bytes=shortfall,
        ok=ok,
        message=message,
    )


def preflight(
    operation: str,
    path: Optional[str | Path] = None,
    *,
    config: Optional[Mapping[str, Any]] = None,
    margin_bytes: int = 0,
) -> StorageCheck:
    """Preflight a named operation using its configured thresholds."""
    data = config if config is not None else load_storage_config()
    operations = data.get("operations", {})
    if operation not in operations:
        known = ", ".join(sorted(operations)) or "(none configured)"
        raise StorageError(f"unknown operation {operation!r}; known: {known}")
    spec = operations[operation]
    return check_storage(
        operation,
        path,
        required_bytes=int(spec.get("required_bytes", 0)),
        min_free_bytes=int(spec.get("min_free_bytes", data.get(
            "min_free_bytes_default", DEFAULT_MIN_FREE_BYTES))),
        margin_bytes=margin_bytes,
        config=data,
    )


def require_storage(
    operation: str,
    path: Optional[str | Path] = None,
    *,
    config: Optional[Mapping[str, Any]] = None,
    margin_bytes: int = 0,
) -> StorageCheck:
    """Like ``preflight`` but raises ``InsufficientStorageError`` when blocked."""
    check = preflight(operation, path, config=config, margin_bytes=margin_bytes)
    if not check.ok:
        raise InsufficientStorageError(check)
    return check


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.core.storage",
        description="Storage preflight for development operations "
        "(ADR-0003 section 5).",
    )
    parser.add_argument("command", choices=["preflight"], help="operation")
    parser.add_argument("operation", help="operation name from config/storage.json")
    parser.add_argument("--path", default=None, help="destination path (default: development_root)")
    parser.add_argument("--margin-bytes", type=int, default=0, help="extra temporary space")
    args = parser.parse_args(argv)

    try:
        check = preflight(args.operation, args.path, margin_bytes=args.margin_bytes)
    except StorageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(check.to_dict(), indent=2))
    return 0 if check.ok else 3


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
