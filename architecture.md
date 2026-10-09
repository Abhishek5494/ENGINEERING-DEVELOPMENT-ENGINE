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

### 2.4 Scrapling integration (`src/cie/acquisition/`)
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
- The intended coordinator is Taiga-S1 (§2.1); because Taiga-S1 (T-0602)
  and Scrapling acquisition (T-0404/T-0502) are BLOCKED, those stages are
  reported `BLOCKED` rather than delegated or faked. The remaining stages
  call the real subsystems (CIE model, Jupyter notebook build/validate) or
  report the honest availability of the external tool.
- Evidence labels from §6 are carried on every stage outcome; a run is
  `PARTIALLY-VALIDATED` while any stage is BLOCKED/UNAVAILABLE (MASTER
  §46). Demo output is written under `projects/<name>/`.

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
├── config/               # tool-manifest.json, shared configuration
└── projects/<project-name>/
```

## 5. Technology choices

| Concern | Choice | Rationale |
|---|---|---|
| Implementation language | Python 3.11+ | Available locally (3.13.5); ecosystem for math/CAD/automation |
| State formats | Markdown (human) + JSON/YAML/SQLite (machine) | MASTER §49, §27 |
| Cross-platform scripts | PowerShell (Windows) + POSIX sh (Linux/macOS) over shared Python | MASTER §23, no logic duplication |
| Tests | pytest | De facto standard, available in environment |
| Version control | Git | MASTER §40 |

ADR-0001 records the bootstrap decision. Major architecture changes
require a new ADR (MASTER §39).

## 6. Interfaces

- **CLI:** `python -m src.<subsystem>` / console scripts (to be defined
  per subsystem in its own task).
- **Python APIs:** typed functions returning structured dicts/dataclasses;
  no hidden global state.
- **Interchange:** JSON schemas for component records, environment reports,
  task state. Avoid proprietary coupling (MASTER §49).

## 7. Offline-first

Core operation must not silently require the internet. Network use is
limited to component research, documentation, package installation, Git,
and authorized investigation (MASTER §26).

## 8. Resource awareness

Expensive workloads (LLM inference, simulation, rendering) must evaluate
CPU/RAM/GPU/VRAM/storage first and degrade gracefully (MASTER §38).

## 9. Known limitations (current)

- `src/orchestration/` is a **PARTIAL** T-1301: it cannot coordinate
  acquisition (Scrapling, T-0404/T-0502) or Taiga-S1 reasoning (T-0602)
  because both are BLOCKED, so those stages are reported `BLOCKED`.
- License undecided.
- Tool integrations (FreeCAD, KiCad, ngspice, Gazebo, Blender, Scrapling,
  Taiga-S1 model runtime) are implemented but unverified at runtime on
  this machine (all tools NOT_FOUND → live execution UNAVAILABLE).
