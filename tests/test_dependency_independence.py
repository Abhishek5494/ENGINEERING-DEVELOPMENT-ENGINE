"""Dependency-independence guards (T-1900; owner directive; MASTER §26, §49).

These tests turn the project's "self-contained, standard-library-only,
offline-capable runtime" claim into an executable check instead of an
aspiration:

* every top-level module imported by ``src/`` is either the standard library,
  the ``src`` package itself, or an explicitly-allowed *optional* import;
* every allowlisted optional import is guarded so its absence never breaks
  importing the package;
* importing every ``src`` module succeeds with the optional dependency absent,
  i.e. no module needs a third-party package (or the network) merely to load;
* the runtime configuration files are JSON, so no optional YAML parser is
  required to run the project.

The inventory and rationale live in ``docs/dependencies.md`` (recorded as
``decisions/ADR-0004-dependency-independence.md``).
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
DEPS_DOC = REPO_ROOT / "docs" / "dependencies.md"

# Third-party imports permitted in ``src/`` only when guarded (optional).
OPTIONAL_ALLOWLIST = frozenset({"yaml"})

STDLIB = frozenset(sys.stdlib_module_names)
ALLOWED_ROOTS = STDLIB | {"src", "__future__"}


def _read_source(path: Path) -> str:
    # utf-8-sig mirrors Python's tolerance of a leading UTF-8 BOM when it
    # imports a module; the BOM must not break static parsing here.
    return path.read_text(encoding="utf-8-sig")


def _src_files() -> Iterator[Path]:
    return iter(sorted(SRC.rglob("*.py")))


def _imported_roots(tree: ast.AST) -> list[tuple[str, int]]:
    """Return ``(top_level_module, lineno)`` for every import in ``tree``."""
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append((alias.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import -> part of the src package
                found.append(("src", node.lineno))
            elif node.module:
                found.append((node.module.split(".")[0], node.lineno))
    return found


def _guarded_import_lines(tree: ast.AST) -> set[int]:
    """Line numbers of imports that sit inside a ``try`` statement."""
    guarded: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for sub in ast.walk(node):
                if isinstance(sub, (ast.Import, ast.ImportFrom)):
                    guarded.add(sub.lineno)
    return guarded


def test_src_imports_are_stdlib_or_allowed() -> None:
    offenders: dict[str, list[str]] = {}
    for path in _src_files():
        tree = ast.parse(_read_source(path), filename=str(path))
        for root, lineno in _imported_roots(tree):
            if root in ALLOWED_ROOTS or root in OPTIONAL_ALLOWLIST:
                continue
            offenders.setdefault(root, []).append(
                f"{path.relative_to(REPO_ROOT)}:{lineno}"
            )
    assert not offenders, f"non-stdlib/non-allowed imports in src/: {offenders}"


def test_optional_imports_are_guarded() -> None:
    unguarded: list[str] = []
    for path in _src_files():
        tree = ast.parse(_read_source(path), filename=str(path))
        guarded = _guarded_import_lines(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module.split(".")[0]] if (node.module and not node.level) else []
            else:
                continue
            for name in names:
                if name in OPTIONAL_ALLOWLIST and node.lineno not in guarded:
                    unguarded.append(
                        f"{path.relative_to(REPO_ROOT)}:{node.lineno}: {name}"
                    )
    assert not unguarded, f"unguarded optional imports: {unguarded}"


def test_no_module_requires_optional_dependency_to_import() -> None:
    """Every src module imports with PyYAML absent (simulated)."""
    code = (
        "import sys\n"
        "sys.modules['yaml'] = None\n"  # 'import yaml' now raises ImportError
        "import importlib, pkgutil\n"
        "import src\n"
        "mods = sorted(m.name for m in pkgutil.walk_packages(src.__path__, 'src.'))\n"
        "for name in mods:\n"
        "    importlib.import_module(name)\n"
        "print('OK', len(mods))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        "importing src failed without the optional dependency:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert result.stdout.strip().startswith("OK"), result.stdout


def test_runtime_config_files_are_json() -> None:
    """No optional YAML parser may be required to load runtime config."""
    from src.core.config import (
        MANIFEST_PATH,
        STORAGE_CONFIG_PATH,
        UPSTREAM_SOURCES_PATH,
    )

    for path in (MANIFEST_PATH, UPSTREAM_SOURCES_PATH, STORAGE_CONFIG_PATH):
        assert path.suffix == ".json", path
        assert path.is_file(), path


def test_no_packaging_file_forces_undeclared_runtime_installs() -> None:
    """The repository must not ship a manifest that installs runtime deps."""
    forbidden = ["requirements.txt", "Pipfile", "Pipfile.lock", "poetry.lock"]
    present = [name for name in forbidden if (REPO_ROOT / name).exists()]
    assert not present, (
        "unexpected packaging manifest(s) implying third-party runtime "
        f"installs: {present}"
    )


def test_dependency_inventory_document_exists_and_covers_categories() -> None:
    assert DEPS_DOC.is_file(), "docs/dependencies.md is missing"
    text = DEPS_DOC.read_text(encoding="utf-8").lower()
    for category in (
        "runtime",
        "third-party",
        "standard library",
        "system",
        "executable",
        "database",
        "network",
        "model",
        "development",
        "optional",
        "offline",
        "packaging",
    ):
        assert category in text, f"docs/dependencies.md does not cover {category!r}"


def _text_sources() -> Iterator[Path]:
    suffixes = {".py", ".md", ".json", ".ps1", ".sh", ".txt", ".cfg", ".toml", ".ini"}
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        parts = set(path.parts)
        if ".git" in parts or "__pycache__" in parts:
            continue
        yield path


def test_no_source_or_governance_file_has_a_bom() -> None:
    """A UTF-8 BOM breaks static parsing and is not part of the house style."""
    offenders: list[str] = []
    for path in _text_sources():
        with path.open("rb") as handle:
            if handle.read(3) == b"\xef\xbb\xbf":
                offenders.append(str(path.relative_to(REPO_ROOT)))
    assert not offenders, f"UTF-8 BOM found in: {offenders}"

