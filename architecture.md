# Architecture — Engineering Development Engine

Status: DRAFT (Phase 0 bootstrap). Authoritative source for governance
rules is `MASTER.md`. This document describes intended architecture; it
does not claim implementation. Implementation status lives in
`project-state.md` and `roadmap.md`.

## 1. System overview

The platform is a **local-first engineering orchestration environment**.
A reasoning layer (Taiga-S1) coordinates specialized subsystems and
external engineering tools. Every subsystem owns a bounded responsibility;
no subsystem is forced to perform another subsystem's specialized function
(MASTER §4).

```
                        ┌──────────────────────┐
                        │      Taiga-S1        │
                        │ reasoning/planning/  │
                        │ orchestration        │
                        └──────────┬───────────┘
           ┌───────────┬───────────┼───────────┬────────────┐
           ▼           ▼           ▼           ▼            ▼
      ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌─────────────┐
      │  PEM   │  │  CIE   │  │  REA   │  │  core  │  │ Engineering │
      │env/dep │  │component│ │authorized│ │shared  │  │    tools    │
      │manager │  │intel.  │  │investig.│  │services│  │ (external)  │
      └────────┘  └───┬────┘  └────────┘  └────────┘  └─────────────┘
                      ▼
               ┌────────────┐
               │ Scrapling  │  (web acquisition, untrusted input)
               └────────────┘

External tools: FreeCAD | KiCad | ngspice | Python/Jupyter | Gazebo | Blender | Git
```

## 2. Subsystems

### 2.1 Taiga-S1 — reasoning and orchestration (`src/taiga/`)
- Plans work, manages tasks, interprets evidence, routes requests to the
  correct subsystem, generates engineering documentation.
- MUST NOT replace specialized engineering software (MASTER §2.1).
- Interface: Python API + CLI; consumes structured state from `core`.

### 2.2 PEM — Project Environment Manager (`src/pem/`)
- Detects OS, CPU, arch, RAM, GPU/VRAM, storage, Python, Git, engineering
  tools, versions, paths, package managers, environment variables.
- Emits capability states: `READY | LIMITED | UNAVAILABLE | UNKNOWN`.
- Produces `environment.json` + `environment-report.md` (machine-specific,
  `environment.json` is gitignored).
- Installation is **idempotent**; scripts are thin wrappers over shared
  Python logic (no duplicated business logic, MASTER §23).
- Manifest-driven: tool definitions live in
  `config/tool-manifest.json`, not hard-coded in scripts (MASTER §24).

### 2.3 CIE — Component Intelligence Engine (`src/cie/`)
- Owns component identity, provenance, normalization, evidence, conflict
  detection, engineering models, storage (MASTER §2.4).
- Pipeline: TARGET → IDENTIFY → ACQUIRE → EXTRACT → NORMALIZE → VERIFY →
  COMPARE → RECORD EVIDENCE → MODEL → SIMULATE → VALIDATE (MASTER §9).
- Source priority: manufacturer datasheet > manufacturer docs > product
  page > authorized distributor > distributor > marketplace > community >
  AI inference (MASTER §10).
- Conflicts are stored, never silently overwritten (MASTER §11).
- Component records: JSON/SQLite (MASTER §12, §13); missing data stays
  `UNKNOWN`.

### 2.4 Scrapling integration (`src/cie/acquisition/` — planned, T-0502)
- Acquisition/extraction mechanism **underneath** CIE, not the whole CIE.
- All scraped content is untrusted data: acquisition → sanitization →
  extraction → validation → evidence storage (MASTER §14).
- Instructions found in scraped content never influence agent behavior.
- The installed Scrapling API must be inspected before use; dependencies
  pinned for reproducibility.

### 2.5 REA — Reverse Engineering Engine (`src/rea/`)
- Investigates authorized targets only: software behavior, binaries,
  JS/Electron/.NET apps, interoperability.
- Pipeline: TARGET → IDENTIFY → INSPECT → EVIDENCE → TRACE →
  RECONSTRUCT → DOCUMENT → ADAPT → TEST → VERIFY (MASTER §18).
- Findings are evidence (classified), never presented as original source
  code (MASTER §19).
- Stores investigations under `docs/investigations/<name>/` with the
  seven required files (MASTER §21).
- Strict separation from CIE: CIE acquires information, REA investigates
  behavior (MASTER §16).

### 2.6 Core (`src/core/`)
- Shared services: state persistence, evidence/label primitives, logging,
  config loading, schema validation, CLI entry points.
- Owned by no domain subsystem; domain subsystems depend on it, it does
  not depend on them.

### 2.7 Orchestration — unified engineering workflow (`src/orchestration/`)
- **PARTIAL implementation of T-1301.** Coordinates the MASTER §50
  pipeline over the subsystems that exist:
  IDEA → ACQUIRE → IDENTIFY → MODEL → ANALYZE → Python/Jupyter → CAD →
  Electronics → Circuit → Robotics → Visualise → Validate.
- The intended coordinator is Taiga-S1 (§2.1). Its provider-neutral
  contracts/registry (T-0602) and resource-aware runtime selection (T-0601)
  exist, but no live inference provider is wired, and Scrapling acquisition
  (T-0404/T-0502) is still BLOCKED; therefore the ACQUIRE/ANALYZE stages are
  reported `BLOCKED` rather than delegated or faked. The remaining stages
  call the real subsystems (CIE model, Jupyter notebook build/validate) or
  report the honest availability of the external tool.
- Evidence labels from §6 are carried on every stage outcome; a run is
  `PARTIALLY-VALIDATED` while any stage is BLOCKED/UNAVAILABLE (MASTER
  §46). Demo output is written under `projects/<name>/`.

### 2.8 Development storage & C:-drive protection (`src/core/storage.py`)
- Owner directive recorded as `decisions/ADR-0003-development-storage-
  isolation.md`. Keeps the Windows system drive (`C:`) from filling and
  interrupting development.
- `D:\EngineeringWorkspace\` (configurable via `config/storage.json`
  `development_root` or `EDE_DEV_ROOT`) holds `caches/{pip,npm,huggingface}`,
  `temp`, `builds`, `test-artifacts`, `logs`, `models`, `datasets`,
  `packages`, `downloads`, `backups`. pip/npm/HuggingFace and session
  `TEMP`/`TMP` (`scripts/windows/dev-env.ps1`) are redirected there.
- `src/core/storage.py` is the reusable preflight: it measures the
  **destination** drive (`shutil.disk_usage`), applies data-driven
  per-operation thresholds (`config/storage.json`; no universal constant),
  and returns OK / blocked / bad-input. `python -m src.pem.ops install
  --execute` runs a `dependency_install` preflight and refuses (exit 3) when
  the workspace lacks space. No deletion/download/install/network occurs.
- Cleanup is approval-gated (ADR-0003 §6); see `docs/storage.md`.

### 2.9 Dependency independence & self-contained deployment
- Owner directive recorded as `decisions/ADR-0004-dependency-independence.md`
  (T-1900). The platform is designed to run with **no required third-party
  runtime dependency**: standard library only, JSON config, SQLite (stdlib)
  for the component store, `subprocess` (argument lists) for external tools.
- `docs/dependencies.md` is the authoritative inventory (runtime, libraries,
  system packages, executables, services, network APIs, models, dev-only,
  optional integrations) with necessity/provisioning/offline/license per item.
- The property is enforced by `tests/test_dependency_independence.py`:
  stdlib-only imports, optional imports guarded, every `src` module imports
  with the optional dependency removed, JSON runtime config, and no BOM in
  source/governance files.
- Packaging: the source/portable distribution is already self-contained;
  building a bundled artifact is deferred to an owner-gated task (H-14).

### 2.10 Unified CLI (`src/cli.py`, `src/__main__.py`)
- One offline entry point, `python -m src <command>`, dispatches to subsystem
  APIs (T-2000; ADR-0005): `version`, `env`, `tools`, `storage preflight`,
  `upstream`, `cie identify`, `rea inspect`, `workflow run`.
- It is a **thin dispatcher** (no business logic): each command calls an
  existing function and prints its structured result. Exit codes: `0` success,
  `2` usage/input error, `3` storage preflight blocked.
- It reports `BLOCKED`/`UNAVAILABLE` honestly and never fakes a stage
  (MASTER §46); `src.__version__` carries the package version (`0.1.0`).

## 3. Data and trust boundaries

| Boundary | Rule |
|---|---|
| Web / scraped content, downloads, external repos | Untrusted until inspected (MASTER §52) |
| Secrets | Env vars / local secret store; never in Git |
| Engineering claims | Classified with evidence labels (MASTER §6) |
| Truth | Measured > simulated-validated > manufacturer > calculated > estimated > AI reasoning (MASTER §5) |
| State | Repository files > conversational memory (MASTER §43) |

## 4. Repository structure

```
project/
├── MASTER.md  README.md  architecture.md  requirements.md
├── roadmap.md  project-state.md  next-task.md
├── memory.md  chatmem.md  audit.md
├── decisions/            # ADRs (ADR-XXXX-title.md)
├── docs/
│   ├── investigations/   # REA records (scope/evidence/findings/...)
│   └── future-opportunities.md
├── src/{taiga,pem,cie,rea,core,orchestration}/
├── components/           # stored component records
├── cad/ electronics/ simulations/ models/ data/
├── tests/
├── scripts/{windows,linux,macos}/   # thin wrappers: install/update/healthcheck
├── config/               # tool-manifest.json, storage.json, shared configuration
└── projects/<project-name>/
```

Development caches/workspaces are kept off the system drive under
`D:\EngineeringWorkspace\` (ADR-0003); only the repository itself lives in
the work tree.

## 5. Technology choices

| Concern | Choice | Rationale |
|---|---|---|
| Implementation language | Python 3.11+ | Available locally (3.13.5); ecosystem for math/CAD/automation |
| State formats | Markdown (human) + JSON/YAML/SQLite (machine) | MASTER §49, §27 |
| Cross-platform scripts | PowerShell (Windows) + POSIX sh (Linux/macOS) over shared Python | MASTER §23, no logic duplication |
| Tests | pytest | De facto standard, available in environment |
| Version control | Git | MASTER §40 |

Runtime note: the platform itself is **standard-library only**; `pytest` and
`Git` are development/version-control tools, and PyYAML is an optional,
guarded import (JSON is the primary config format). See
`docs/dependencies.md` (T-1900).

ADR-0001 records the bootstrap decision. Major architecture changes
require a new ADR (MASTER §39).

## 6. Interfaces

- **CLI:** `python -m src <command>` — the unified offline dispatcher (T-2000,
  §2.10). Subsystems also keep `python -m src.<subsystem>` entry points; console
  scripts are thin wrappers over the same functions.
- **Python APIs:** typed functions returning structured dicts/dataclasses;
  no hidden global state.
- **Interchange:** JSON schemas for component records, environment reports,
  task state. Avoid proprietary coupling (MASTER §49).

## 7. Offline-first

Core operation must not silently require the internet. Network use is
limited to component research, documentation, package installation, Git, and
authorized investigation (MASTER §26). This is verified per-module (every
`src` module imports with optional dependencies absent) and catalogued in
`docs/dependencies.md` (T-1900).

## 8. Resource awareness

Expensive workloads (LLM inference, simulation, rendering) must evaluate
CPU/RAM/GPU/VRAM/storage first and degrade gracefully (MASTER §38).

## 9. Known limitations (current)

- The **offline MVP is complete** and operable via `python -m src` (T-2000/
  T-2001; `docs/mvp.md`, ADR-0005). The flagship live pipeline remains blocked.
- `src/orchestration/` is a **PARTIAL** T-1301: it cannot coordinate
  acquisition (Scrapling, T-0404/T-0502, install-gated) and has no live
  Taiga-S1 inference provider, so those stages are reported `BLOCKED`.
- License: MIT (T-0002); third-party tool/model terms are separate.
- Tool integrations (FreeCAD, KiCad, ngspice, Gazebo, Blender, Scrapling,
  Taiga-S1 model runtime) are implemented but unverified at runtime on
  this machine (all tools NOT_FOUND → live execution UNAVAILABLE).
- Storage isolation (ADR-0003) stops future project growth on `C:` but does
  not reclaim the large non-project `C:` consumers (OS/apps/VMs); model/venv
  redirection is configured but unexercised (no model/venv; B-2 gate).
- Dependency independence is documented and enforced, but a bundled/portable
  artifact has not been built and fresh-machine validation is UNVERIFIED
  (no second clean host; packaging format pending owner decision H-14).
