"""PEM system/hardware detection (T-0101).

Detection only: no installation, no network, no external services.
Every field returned is either evidence-backed (labelled OBSERVED) or
explicitly UNKNOWN — values are never guessed (MASTER §7, §22).

stdlib-first (platform, os, shutil, ctypes, subprocess). Each detector
returns ``None`` when it cannot obtain a real value; ``detect_system``
maps ``None`` to ``{"value": "UNKNOWN", "evidence": "UNKNOWN"}``.
"""

from __future__ import annotations

import os
import platform
import shutil
import string
import subprocess
from typing import Any, Callable, Optional

UNKNOWN = "UNKNOWN"
EVIDENCE_OBSERVED = "OBSERVED"

SYSTEM_KEYS = (
    "os_name",
    "os_version",
    "cpu",
    "architecture",
    "ram_bytes",
    "storage",
    "gpu",
)


def _field(value: Any) -> dict[str, Any]:
    """Wrap a detected value with its evidence label.

    Empty or missing results are UNKNOWN — an empty collection is not
    evidence of absence (MASTER §7).
    """
    if value is None or value == "" or value == [] or value == {}:
        return {"value": UNKNOWN, "evidence": UNKNOWN}
    if isinstance(value, int) and value <= 0:
        return {"value": UNKNOWN, "evidence": UNKNOWN}
    return {"value": value, "evidence": EVIDENCE_OBSERVED}


def _safe(func: Callable[[], Any]) -> Any:
    """Run a detector; any failure yields None → UNKNOWN, never a crash."""
    try:
        return func()
    except Exception:
        return None


def _detect_os_name() -> Optional[str]:
    name = platform.system()
    return name.strip() or None


def _detect_os_version() -> Optional[str]:
    system = platform.system()
    if system == "Windows":
        release, version, _csd, _ptype = platform.win32_ver()
        if release and version:
            return f"{release} (build {version})"
        return release or version or None
    if system == "Linux":
        try:
            with open("/etc/os-release", encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"') or None
        except OSError:
            pass
        return platform.release() or None
    if system == "Darwin":
        return platform.mac_ver()[0] or None
    return platform.release() or None


def _detect_architecture() -> Optional[str]:
    machine = platform.machine()
    try:
        bits = platform.architecture()[0]
    except Exception:
        bits = ""
    if machine and bits:
        return f"{machine}, {bits}"
    return machine or bits or None


def _detect_cpu() -> Optional[str]:
    system = platform.system()
    if system == "Windows":
        try:
            import winreg

            key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                name, _regtype = winreg.QueryValueEx(key, "ProcessorNameString")
            if isinstance(name, str) and name.strip():
                return name.strip()
        except OSError:
            pass
    elif system == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.startswith(("model name", "Hardware", "Model")):
                        value = line.split(":", 1)[1].strip()
                        if value:
                            return value
        except OSError:
            pass
    elif system == "Darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            value = result.stdout.strip()
            if result.returncode == 0 and value:
                return value
        except (OSError, subprocess.SubprocessError):
            pass
    fallback = platform.processor()
    return fallback.strip() or None


def _detect_ram_bytes() -> Optional[int]:
    system = platform.system()
    if system == "Windows":
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        if ok and status.ullTotalPhys > 0:
            return int(status.ullTotalPhys)
        return None
    # POSIX: Linux provides physical pages via sysconf; macOS does not.
    try:
        pages = os.sysconf("SC_PHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        total = int(pages) * int(page_size)
        return total if total > 0 else None
    except (ValueError, OSError, AttributeError):
        return None


def _detect_storage() -> Optional[list[dict[str, int | str]]]:
    mounts: list[str] = []
    if platform.system() == "Windows":
        for letter in string.ascii_uppercase:
            path = f"{letter}:\\"
            if os.path.isdir(path):
                mounts.append(path)
    else:
        mounts.append(os.sep)
    volumes: list[dict[str, int | str]] = []
    for mount in mounts:
        try:
            usage = shutil.disk_usage(mount)
        except OSError:
            continue
        volumes.append(
            {
                "mount": mount,
                "total_bytes": int(usage.total),
                "free_bytes": int(usage.free),
            }
        )
    return volumes or None


def _detect_gpu() -> Optional[list[str]]:
    system = platform.system()
    if system == "Windows":
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "(Get-CimInstance -ClassName Win32_VideoController).Name",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        names = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return names or None
    if system == "Linux" and shutil.which("lspci"):
        try:
            result = subprocess.run(
                ["lspci"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        names = [
            line.split(":", 2)[-1].strip()
            for line in result.stdout.splitlines()
            if "VGA compatible controller" in line or "3D controller" in line
        ]
        names = [n for n in names if n]
        return names or None
    if system == "Darwin":
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        names = [
            line.split(":", 1)[1].strip()
            for line in result.stdout.splitlines()
            if line.strip().startswith("Chipset Model:")
        ]
        names = [n for n in names if n]
        return names or None
    return None


def detect_system() -> dict[str, Any]:
    """Detect OS/CPU/RAM/storage/GPU.

    Returns a JSON-serializable mapping of the seven system keys, each an
    object ``{"value": ..., "evidence": "OBSERVED" | "UNKNOWN"}`` where
    ``value`` is ``"UNKNOWN"`` exactly when ``evidence`` is ``"UNKNOWN"``.
    Never raises.
    """
    return {
        "os_name": _field(_safe(_detect_os_name)),
        "os_version": _field(_safe(_detect_os_version)),
        "cpu": _field(_safe(_detect_cpu)),
        "architecture": _field(_safe(_detect_architecture)),
        "ram_bytes": _field(_safe(_detect_ram_bytes)),
        "storage": _field(_safe(_detect_storage)),
        "gpu": _field(_safe(_detect_gpu)),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(detect_system(), indent=2))
