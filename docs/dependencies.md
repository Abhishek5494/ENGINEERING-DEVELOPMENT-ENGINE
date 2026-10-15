# Dependencies & self-contained deployment

Audit of every dependency this project needs, its provisioning, and how far
the project can run without network access or manual installation. Derived
from the owner directive **"Dependency independence & self-contained
deployment"**, recorded as `decisions/ADR-0004-dependency-independence.md`
(T-1900, Phase 19), and from MASTER §26 (offline-first) and §49
(interoperability).

The summary is deliberately blunt:

> **Runtime is standard-library-only.** Running the engineering platform
> requires nothing beyond a Python 3.11+ interpreter. There are **no required
> third-party packages**, no external database, no required service, no
> mandatory network access, and no bundled binary. Optional integrations
> (engineering tools, the AI model, web acquisition) are exactly that:
> optional, and currently not installed on this host.

The claims below are checked by `tests/test_dependency_independence.py`.

## 1. Runtime requirements (what you must have)

| Requirement | Value | Notes |
|---|---|---|
| Interpreter | Python **3.11+** | OBSERVED host: 3.13.5. Uses only the standard library. |
| Working directory | repository root | Modules are `python -m src.<subsystem>`; paths derive from the file location, never the CWD (`src/core/config.py`). |
| Operating system | Windows / Linux / macOS | Text/path handling hardened in `src/core/xplat.py` (T-1601). |
| Virtual environment | **not required** | There are no runtime packages to isolate. A venv is optional and, if used, should live on `D:` (ADR-0003). |

No `pip install` step is needed to run or test the core platform. The only
development tool is `pytest` (see §3).

## 2. Why this is possible

The implementation was written **standard-library only** on purpose
(MASTER §26, §49; ADR-0001). Configuration is JSON; component/evidence state
is JSON and SQLite (both in the standard library); subprocess calls use
`subprocess` with argument lists; HTTP is only ever needed by optional,
non-core features. The single third-party import in `src/` is PyYAML, and it
is **optional and guarded**:

```python
try:  # optional dependency; never required
    import yaml as _yaml
except Exception:
    _yaml = None
```

JSON is always the primary configuration format; YAML is accepted only when a
parser happens to be installed (`src/core/config.py`).

## 3. Dependency inventory

Classification key — **Necessity:** REQUIRED (core will not run without it) /
OPTIONAL (a feature is unavailable if absent) / DEVELOPMENT (needed only to
build/test). **Provisioning:** BUNDLED (ships in the repo or the interpreter) /
SYSTEM (installed on the machine) / DOWNLOADABLE (fetched on demand) /
REPLACEABLE (a standard-library substitute exists).

### Runtime / interpreter
| Dependency | Necessity | Provisioning | Offline? | License |
|---|---|---|---|---|
| Python 3.11+ interpreter & standard library | REQUIRED | SYSTEM (BUNDLED modules within it) | Yes | UNKNOWN (not verified in-repo) |

### Third-party libraries & packages
| Dependency | Necessity | Provisioning | Offline? | License |
|---|---|---|---|---|
| *(none required)* | — | — | — | — |
| PyYAML | OPTIONAL | DOWNLOADABLE | Optional import only; JSON used otherwise | UNKNOWN (not verified in-repo) |

No other third-party package is imported anywhere in `src/`.

### Standard-library modules used (BUNDLED with the interpreter)
`json`, `sqlite3`, `subprocess`, `shutil`, `pathlib`, `argparse`,
`dataclasses`, `enum`, `typing`, `re`, `hashlib`, `datetime`, `urllib.parse`,
`importlib`, `ast`, `copy`, and others. These require no installation.

### System-level packages
None beyond a working Python installation. No compiler, no package manager,
and no OS library is required for the core platform.

### External executables / command-line tools (all OPTIONAL)
These are the engineering authorities. Each is recorded in
`config/tool-manifest.json` (detection/install) and
`config/upstream-sources.json` (upstream + verification); they are **not**
duplicated here. All are currently **NOT installed** on this host, so their
live execution is honestly reported `UNAVAILABLE` (never faked).

| Tool | Category | Necessity | Provisioning | Offline capability |
|---|---|---|---|---|
| FreeCAD | CAD | OPTIONAL | SYSTEM (external install) | Fully local once installed |
| KiCad | PCB | OPTIONAL | SYSTEM | Fully local once installed |
| ngspice | Circuit simulation | OPTIONAL | SYSTEM | Fully local once installed |
| Gazebo | Robotics simulation | OPTIONAL | SYSTEM | Fully local once installed |
| Blender | Rendering | OPTIONAL | SYSTEM | Fully local once installed |
| Jupyter | Notebooks | OPTIONAL | DOWNLOADABLE (pip) | Local, but needs the Jupyter package |
| Scrapling | Web acquisition | OPTIONAL | DOWNLOADABLE (pip) | **Requires network** to fetch pages |
| Git | Version control | DEVELOPMENT | SYSTEM | Local once installed |

Installation of any of these is gated by the owner approval / network gate
(blocker **B-2**, see `requirements.md` H-1/H-2).

### Databases & supporting services
| Dependency | Necessity | Provisioning | Offline? | Notes |
|---|---|---|---|---|
| SQLite | REQUIRED (for the component store) | BUNDLED (Python `sqlite3`) | Yes | File-based; no server, no port, no credentials. |

No external database, message broker, or background service is required.

### Network APIs / services
None required. The core platform performs no network access. Network use is
confined to optional capabilities explicitly listed in MASTER §26 (component
research, documentation, package installation, Git, authorized investigation),
and to the optional Scrapling acquisition path.

### AI models & runtimes
| Dependency | Necessity | Provisioning | Offline? | Notes |
|---|---|---|---|---|
| Taiga-S1 / Biome-S1 model weights | OPTIONAL | DOWNLOADABLE | Local inference once weights are present | Not bundled and **not downloaded** (owner gate H-3; B-2). Integration code is provider-neutral (`src/taiga/`); no live inference provider is wired, so orchestration ANALYZE is honestly BLOCKED. |

No model weights are shipped in the repository or downloaded during startup.

### Build-time / development-only dependencies
| Dependency | Necessity | Provisioning | Offline? | Notes |
|---|---|---|---|---|
| pytest | DEVELOPMENT | DOWNLOADABLE (`pip install pytest`) | Local once installed | OBSERVED host: 9.1.1. Required only to run the test suite. |
| Git | DEVELOPMENT | SYSTEM | Local once installed | History/recovery only (MASTER §40). |

No linter, formatter, type checker, or build framework is required.

### Optional integrations / plugins
The tool integrations above, plus the optional Scrapling web-acquisition
path. All are implemented as gated integrations that degrade to an honest
`UNAVAILABLE`/`BLOCKED` result when their dependency is absent.

## 4. Offline-first matrix

| Capability | Works offline? | Evidence |
|---|---|---|
| Import the whole platform (`src/**`) | **Yes** | `tests/test_dependency_independence.py::test_no_module_requires_optional_dependency_to_import` (imports every module with PyYAML blocked). |
| Configuration loading (JSON) | **Yes** | `src/core/config.py`; JSON is the primary format. |
| PEM detection / environment report | **Yes** (needs a Python interpreter to be present) | `src/pem/`. |
| Evidence/claim primitives, project state, recovery | **Yes** | `src/core/`, `tests/test_recovery.py`. |
| CIE data model / store / identification from supplied HTML | **Yes** (acquisition injected; no network in the code path) | `src/cie/`, `tests/test_cie_*.py`. |
| REA offline inspection (files, hashing, string extraction) | **Yes** | `src/rea/`, `tests/test_rea_inspection.py`. |
| Engineering tool integrations | **Yes once the tool is installed** | Code is complete; live tools absent on this host. |
| ADR-0003 storage preflight | **Yes** | `src/core/storage.py`, `tests/test_storage.py`. |
| CIE web acquisition (Scrapling) | **No — network required** | BLOCKED (T-0502, B-2). |
| Taiga-S1 inference | **Local once weights supplied** | No provider wired; ANALYZE BLOCKED. |
| Installing any engineering tool | **No — network required** | Gated by B-2. |

Nothing in the **core** requires the internet. The only network-dependent
paths are optional features that are already gated.

## 5. Verification status

- **VERIFIED (this repository):** the runtime is standard-library only; every
  `src` module imports with the optional dependency removed; runtime config is
  JSON; the full suite runs offline (see `project-state.md` for the current
  count).
- **UNVERIFIED:** a *fresh machine* with only a Python 3.11+ interpreter
  installed (no clone-side pip install) and the optional tools present; a
  packaged/portable artifact; live model inference. These need either a clean
  environment or the B-2 gate and are recorded honestly as unverified.

## 6. Packaging strategy

Chosen direction (least-complexity first):

1. **Source distribution (current, default).** Clone/copy the repository, run
   with any Python 3.11+. No build step. This is already fully self-contained
   because there are no third-party runtime packages.
2. **Portable directory / zip.** The repository *is* the portable artifact;
   copy it beside a Python install (or a bundled embeddable CPython). Optional
   `scripts/<os>/` wrappers already exist.
3. **`zipapp` bundle** (`python -m zipapp`) — a single `.pyz` for the CLI
   entry points, if a single-file drop is ever wanted. Standard-library tool.
4. **PyInstaller/one-file executable** — only if a fully interpreter-free
   binary is required. This adds a build-time dependency (PyInstaller) and
   must be justified; deferred.

**Recommendation:** ship the source distribution (option 1/2). It already
meets the self-contained goal with zero runtime third-party dependencies.
Actually building a bundled artifact (options 3/4) is deferred to a dedicated
task that also needs an owner decision on the target format
(see `requirements.md`, human input H-14).

### Setup instructions (source distribution)
```powershell
# Run the platform (no install step):
python -m src.pem.report          # environment report
python -m src.core.storage preflight dependency_install

# Run the tests (development only):
python -m pytest tests/ -q
```
No `pip install` is required for either. `pytest` is the only tool you might
need to install, and only to run the tests.

## 7. Fresh-system validation procedure

To validate on a clean compatible machine:

1. Install only Python 3.11+.
2. Copy the repository (no `pip install`).
3. Run `python -m pytest tests/ -q` — expect all tests to pass/run offline
   (optional-tool tests skip honestly).
4. Run `python -m src.pem.report` — expect an `environment.json` report.
5. Confirm there is no `requirements.txt`/`pyproject.toml` that would trigger
   runtime package installs.

Results on an actual fresh machine are **UNVERIFIED** here (no second clean
host available); this procedure is the acceptance test for that step.

## 8. Licenses & notices

- The project itself is MIT (`LICENSE`; T-0002).
- Third-party **tool/model** licenses are recorded as `UNKNOWN` in
  `config/upstream-sources.json` until verified (never guessed). The one
  exception already verified is Taiga-S1/Biome-S1 (MIT).
- The Python standard library is covered by the Python license; no bundle of
  it is created by this project.
- Because nothing third-party is bundled, no third-party notice file is
  currently required. If packaging ever bundles an interpreter or a package,
  its license/notice must be added at that time (acceptance criterion §6.6 of
  the directive).

## 9. Unavoidable system (`C:`) dependencies

Per ADR-0003, the following live on `C:` and are **not** project-controllable:
Windows itself, installed applications, the global Python interpreter, and
other non-relocatable software. The project avoids adding to `C:` by keeping
caches, environments, models, and build artefacts on `D:`
(`config/storage.json`; `docs/storage.md`).

## 10. Policy — adding a new dependency

1. Prefer the standard library; prefer an existing internal implementation.
2. If a third-party dependency is unavoidable, document **why** in this file
   and in an ADR if it is architectural.
3. Add it to the inventory above with necessity/provisioning/offline/license.
4. Keep it optional and guarded if it is not truly required
   (`tests/test_dependency_independence.py` enforces the allowlist).
5. Respect its license and add a notice if it is ever bundled.
