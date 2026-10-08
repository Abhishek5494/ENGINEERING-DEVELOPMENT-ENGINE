# project-state.md

Actual repository state. Never fictional (MASTER §29). Rewritten every time
a task is completed, blocked, or state changes.

## Current phase
PHASE 1 — Project Environment Manager (COMPLETE for code; installs gated).
PHASE 2 — Configuration + tool registry (COMPLETE).
PHASE 3 — Core primitives: config, state, evidence (COMPLETE).
PHASE 4 — Component Intelligence Engine (COMPLETE for offline scope:
T-0401/T-0402/T-0403; T-0404 awaits Scrapling T-0502).
PHASE 7 — REA (COMPLETE for framework + offline inspection:
T-0701/T-0702; Phase 5 T-0501 is BLOCKED on the install gate).

## Overall status
Governance complete; Phases 1–3 complete (PEM; `src/core/config.py`,
`state.py`, `evidence.py`). Phase 4 CIE offline scope complete: data model
+ schema + SQLite/JSON store (T-0401), URL ingestion + exact
identification (T-0402), provenance + source priority + conflicts
(T-0403). REA framework + offline inspection complete (T-0701/T-0702).
Not yet implemented: CIE cross-source search (T-0404, needs
Scrapling), Scrapling, Taiga-S1, engineering-tool integrations,
orchestration, release audit. Taiga-S1 is externally BLOCKED (repo not
supplied) and T-0501 is BLOCKED on the install gate; live tool
installation is gated on user approval + disk + network. Operating in
autonomous build mode (checkpoint commits per task).

## Completed phases
- PHASE 0 — Repository + governance (T-0001 COMPLETE, 2026-10-08)
- PHASE 1 — PEM (T-0101..T-0107, T-0201 COMPLETE for code; live installs
  gated)
- PHASE 2 — Configuration + tool registry (T-0202 COMPLETE, 2026-10-08)
- PHASE 3 — Core primitives (T-0301, T-0302 COMPLETE, 2026-10-08)
- PHASE 4 — CIE offline scope (T-0401..T-0403 COMPLETE; T-0404 gated on
  T-0502)
- PHASE 7 — REA (T-0701/T-0702 COMPLETE; framework + offline inspection)

## Completed tasks (last completed task listed last)
- T-0001 — Repository governance bootstrap (2026-10-08) — 38 tests.
- T-0101 — PEM system/hardware detection (2026-10-08) — AUDIT-0005.
- T-0201 — Tool manifest schema + manifest + loader (2026-10-08) — AUDIT-0006.
- T-0102 — PEM tool detection + capability states (2026-10-08) — AUDIT-0007.
- T-0103 — Environment report generation (2026-10-08) — AUDIT-0008.
- T-0104 — Windows scripts + shared ops module (2026-10-08) — AUDIT-0009.
- T-0107 — Idempotent install logic + tests (2026-10-08) — AUDIT-0010.
- T-0105 — Linux wrapper scripts (static-verified) (2026-10-08) — AUDIT-0011.
- T-0106 — macOS wrapper scripts (static-verified) (2026-10-08) — AUDIT-0013.
- T-0202 — Shared configuration module (2026-10-08) — AUDIT-0014.
- T-0302 — Evidence/claim classification primitives (2026-10-08) — AUDIT-0015.
- T-0301 — Project-state persistence library (2026-10-08) — AUDIT-0016.
- T-0401 — CIE component data model + schema + storage (2026-10-08) —
  AUDIT-0017.
- T-0402 — CIE URL ingestion + exact identification (2026-10-08) —
  AUDIT-0018.
- T-0403 — CIE provenance + source priority + conflicts (2026-10-08) —
  AUDIT-0019.
- T-0701 — REA pipeline + investigation templates (2026-10-08) —
  AUDIT-0020.
- T-0702 — REA offline inspection + evidence collection (2026-10-08) —
  AUDIT-0021.

## Last completed task
- T-0702 — REA offline inspection (2026-10-08) — 325 passed, 2 skipped;
  `src/rea/inspection.py` (read-only fingerprinting + tool probing →
  OBSERVED evidence) + `with_evidence`. REA scope for the roadmap is in
  place.

## Current task
- ID: T-0801
- Title: Python/Jupyter integration
- State: READY (defined in roadmap; next-task.md to be set)
- (Note: Phase-5 T-0501 is BLOCKED on the install gate; T-0601/T-0602
  BLOCKED — Taiga-S1 repo not supplied. See Blockers.)

## Active subsystem
- PEM: `src/pem/detect.py` (system), `src/pem/tools.py` (tool probes,
  capability states), `src/pem/report.py` (§25 report generation),
  `src/pem/installer.py` (idempotent, guarded install engine),
  `src/pem/ops.py` (healthcheck/install/update commands, `--execute`).
- Core: `src/core/manifest.py` (manifest loader; requires
  `install_command`).
- Scripts: `scripts/windows/{install,update,healthcheck}.ps1` (thin
  wrappers, executed and verified on this host);
  `scripts/linux/{install,update,healthcheck}.sh` and
  `scripts/macos/{install,update,healthcheck}.sh` (thin POSIX wrappers,
  static-verified only).

- CIE: `src/cie/model.py` (§12 `Component` + `UNKNOWN` sentinel +
  `MotorSpec` §13 + `DerivedValue`), `config/component.schema.json`
  (draft-07), `src/cie/store.py` (`ComponentStore` SQLite + JSON I/O);
  `src/cie/target.py` (URL validation) + `src/cie/identify.py` (exact
  product identification → `Component`, no network), `config/identification.schema.json`;
  `src/cie/provenance.py` (eight §10 source tiers + `Provenance`) +
  `src/cie/conflicts.py` (`Fact`/`FieldRecord`, `CONFLICT`, governing
  selection), `config/fact-record.schema.json`;
  `src/cie/__init__.py` re-exports.
- REA: `src/rea/pipeline.py` (ordered §18 stages), `src/rea/records.py`
  (authorized §19/§20 records + `with_evidence`), `src/rea/storage.py`
  (seven §21 templates), `src/rea/inspection.py` (read-only file
  fingerprinting: magic-byte type, sha256/md5, bounded strings, tool
  probing), `src/rea/__init__.py` re-exports.

## Blockers
- T-0002 (License decision): BLOCKED — requires human approval (MASTER §35).
- **B-1 Taiga-S1 upstream repository not supplied** (directive §13/§39):
  T-0601/T-0602 BLOCKED. No Taiga API is guessed; independent work
  continues.
- **B-2 Privileged/network installation approval** (MASTER §7/§29): real
  installation of engineering tools (incl. Scrapling for T-0501/T-0502)
  needs network + possibly admin and C:\ is below the disk threshold;
  install tasks proceed as code + tests that SKIP when a tool is absent,
  awaiting user approval for live runs. T-0501 is BLOCKED under this gate;
  Phase-4 T-0404 depends on T-0502.

## Known issues
- **No engineering toolchain installed on this host (OBSERVED,
  2026-10-08):** FreeCAD, KiCad, ngspice, Gazebo, Blender, Jupyter,
  Scrapling all NOT_FOUND. Engineering-tool tasks (T-0801+) cannot run
  until install tasks provide them or the user installs them.
- **Disk pressure on C:\ is volatile (OBSERVED):** 6,135,808 bytes at
  T-0103 → 459,509,760 at T-0104 close → 451,891,200 at T-0107 close.
  Still below the 1 GiB threshold, so live `install --execute` refuses
  (exit 3) on this host; re-check before any install execution.
- Linux/macOS probe/code paths unexecuted (Windows host; no POSIX shell)
  — T-1601. Linux + macOS wrappers now exist but are static-verified
  only (T-0105/T-0106).
- Version extraction is best-effort first dotted-numeric token (e.g.
  "2.55.0.windows.3" reported as "2.55.0").
- Non-pip tools carry `install_command: null` (package-manager
  detection R3.3 pending) → installer routes them to manual notice.
- UNKNOWN tools (taiga-s1, rea) lack detectors, so the installer can
  neither act on nor clear them (reported as `investigate`).

## Architecture status
- `architecture.md`: DRAFT consistent with implemented scope.
- ADR-0001 (bootstrap governance) + ADR-0002 (evidence strength order)
  recorded; no other architectural change since bootstrap.

## Environment status
- System (OBSERVED via `detect_system()`, 2026-10-08):
  - OS: Windows 11 (build 10.0.26200), AMD64 64-bit
  - CPU: AMD Ryzen 5 5600H with Radeon Graphics
  - RAM: 6,287,331,328 bytes (~5.86 GiB as reported by the OS)
  - GPU: AMD Radeon(TM) Graphics; NVIDIA GeForce GTX 1650 (VRAM UNKNOWN)
  - Storage: C:\ 213.8 GB total / 451,891,200 bytes free (fluctuating);
    D:\ 297.2 GB total / 96,802,582,528 bytes free
- Tools (OBSERVED via `detect_tools()`, 2026-10-08):
  - DETECTED: git 2.55.0, python 3.13.5
  - NOT_FOUND: jupyter, scrapling, freecad, kicad, ngspice, gazebo, blender
  - UNKNOWN (not implemented): taiga-s1, rea
- Toolchain side probes (OBSERVED): Node v24.14.1, pytest 9.1.1,
  PySide6 6.11.1.
- Capabilities: numerical optimization = READY; LLM inference = UNKNOWN;
  CAD / PCB design / circuit simulation / robotics simulation / 3D
  rendering / web acquisition = UNAVAILABLE.
- `environment.json` / `environment-report.md`: GENERATED 2026-10-08
  (OBSERVED warnings/limits in AUDIT-0008). Machine-specific, gitignored,
  regenerate with `python -m src.pem.report`.

## Test status
- `python -m pytest tests/ -v` → **325 passed, 2 skipped** (2026-10-08,
  Python 3.13.5, pytest 9.1.1): 38 governance + 9 PEM detection +
  21 manifest + 22 PEM tools + 20 PEM report + 23 PEM ops + 17 installer
  + 14 Unix-script static tests (parametrised Linux + macOS) + 19 core
  config + 29 core evidence + 20 core state + 14 CIE model/schema +
  7 CIE store + 5 CIE target + 14 CIE identify + 9 CIE provenance +
  13 CIE conflict + 8 REA pipeline + 8 REA records + 7 REA storage +
  8 REA inspection tests.
  Skipped: the two per-platform `sh -n` syntax checks (no POSIX shell on
  host).
- Bugs caught by tests so far and fixed before completion: empty-list
  evidence bug (T-0101), manifest error-ordering bug (T-0201),
  §29 heading dropped from project-state rewrite (T-0102), "installed"
  wording + missing UNAVAILABLE limitations (T-0103). T-0104 reported
  test error diagnosed as environment disk-cleanup interference (not a
  code defect; AUDIT-0009). T-0107: stale `PLAN_ONLY_NOTICE` text
  corrected and a latent word-boundary bug in the roadmap dependency
  regex fixed (AUDIT-0010).

## Validation status
- Governance validation + live OBSERVED detector/probe/report/script/
  install-engine runs recorded in audit.md (AUDIT-0005..0017). Windows
  wrappers executed on host: healthcheck exit 1 (C:\ below threshold),
  install/update exit 0 plan-only, 53-file snapshot proves zero
  mutation. Install engine: live plan exit 0; `--execute` refused
  exit 3 (disk); no live mutation attempted. Linux + macOS wrappers:
  STATIC validation only (file/shebang/delegation/tool-id checks);
  never executed (no POSIX shell on this host). Core config: unit-tested;
  live REPO_ROOT + manifest load verified; YAML branch executed (PyYAML
  present). Core evidence (T-0302): unit-tested; live ranking/strongest
  observed. Core state (T-0301): unit-tested; live parse of the real
  roadmap/next-task/project-state observed; byte-identical no-op
  round-trips proven. CIE (T-0401): unit-tested; live build→SQLite
  save→fetch round-trip observed and schema acceptance/rejection
  verified against a fabricated record. CIE (T-0402): unit-tested; live
  identification over a JSON-LD fixture observed (identity + component
  mapping) and an opaque page refused with `IdentificationError`; no
  network performed. CIE (T-0403): unit-tested; live §11 conflict
  observed — marketplace 10,000 vs datasheet 8,500 → `CONFLICT`, both
  retained, governing = datasheet. REA (T-0701): unit-tested; live
  authorized-investigation build + pipeline advance + seven-file write
  observed, with unauthorized and recovered-source cases refused. REA
  (T-0702): unit-tested; live fingerprint of a PE fixture matched an
  independent `hashlib.sha256`, tool probing reported present/absent, and
  `inspect_target` produced OBSERVED evidence (0→7 entries). No
  engineering validation applicable yet.

## Next action
Start T-0801 (Python/Jupyter integration; Phase 8, READY via T-0103):
notebook-based analysis under `simulations/`/`projects/`, recorded as
labelled evidence. Then further integrations (T-0901+), and T-0502/T-0404
once Scrapling is installable; T-0601/T-0602 remain BLOCKED.

## Last update
2026-10-08 — T-0702 closed (325 passed, 2 skipped); REA offline
inspection (file fingerprinting + tool probing → OBSERVED evidence) is in
place. T-0501 remains BLOCKED under the install gate. Next: T-0801
(Python/Jupyter integration).