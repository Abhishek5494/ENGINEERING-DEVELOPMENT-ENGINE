# project-state.md

Actual repository state. Never fictional (MASTER §29). Rewritten every time
a task is completed, blocked, or state changes.

## Current phase
PHASE 1 — Project Environment Manager (COMPLETE for code; installs gated).
PHASE 2 — Configuration + tool registry (COMPLETE).
PHASE 3 — Core primitives: config, state, evidence (COMPLETE).
PHASE 4 — Component Intelligence Engine (in progress: T-0401 done).

## Overall status
Governance complete; Phases 1–3 complete (PEM; `src/core/config.py`,
`state.py`, `evidence.py`). Phase 4 CIE started: component data model +
schema + SQLite/JSON store (T-0401) done. Not yet implemented: CIE
ingestion/provenance (T-0402/T-0403), Scrapling, REA, Taiga-S1,
engineering-tool integrations, orchestration, release audit. Taiga-S1 is
externally BLOCKED (repo not supplied); live tool installation is gated
on user approval + disk + network. Operating in autonomous build mode
(checkpoint commits per task).

## Completed phases
- PHASE 0 — Repository + governance (T-0001 COMPLETE, 2026-10-08)
- PHASE 1 — PEM (T-0101..T-0107, T-0201 COMPLETE for code; live installs
  gated)
- PHASE 2 — Configuration + tool registry (T-0202 COMPLETE, 2026-10-08)
- PHASE 3 — Core primitives (T-0301, T-0302 COMPLETE, 2026-10-08)

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

## Last completed task
- T-0401 — CIE component data model + schema + storage (2026-10-08) —
  253 passed, 2 skipped; `src/cie/model.py` (§12/§13, UNKNOWN sentinel,
  no padding), `config/component.schema.json`, `src/cie/store.py`
  (SQLite + JSON). CIE foundation in place.

## Current task
- ID: T-0402
- Title: CIE URL ingestion + exact-identification flow
- State: READY (defined in next-task.md; not yet started)
- (Note: T-0601/T-0602 BLOCKED — Taiga-S1 repo not supplied. See Blockers.)

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
  `src/cie/__init__.py` re-exports.

## Blockers
- T-0002 (License decision): BLOCKED — requires human approval (MASTER §35).
- **B-1 Taiga-S1 upstream repository not supplied** (directive §13/§39):
  T-0601/T-0602 BLOCKED. No Taiga API is guessed; independent work
  continues.
- **B-2 Privileged/network installation approval** (MASTER §7/§29): real
  installation of engineering tools needs network + possibly admin and
  C:\ is below the disk threshold; install tasks proceed as code + tests
  that SKIP when a tool is absent, awaiting user approval for live runs.

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
- `python -m pytest tests/ -v` → **253 passed, 2 skipped** (2026-10-08,
  Python 3.13.5, pytest 9.1.1): 38 governance + 9 PEM detection +
  21 manifest + 22 PEM tools + 20 PEM report + 23 PEM ops + 17 installer
  + 14 Unix-script static tests (parametrised Linux + macOS) + 19 core
  config + 29 core evidence + 20 core state + 14 CIE model/schema +
  7 CIE store tests. Skipped: the two per-platform `sh -n` syntax
  checks (no POSIX shell on host).
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
  verified against a fabricated record. No engineering validation
  applicable yet.

## Next action
Start T-0402 (see next-task.md): CIE URL ingestion + exact-identification
flow — turn a supplied product/manufacturer URL into a candidate
component id/attributes, refusing to act on ambiguous identity (§9).
Then T-0403 (provenance + source priority + conflicts), Scrapling and REA
per §48 order; T-0601/T-0602 remain BLOCKED pending the Taiga-S1 repo.

## Last update
2026-10-08 — T-0401 closed (253 passed, 2 skipped); CIE foundation
(model + schema + SQLite/JSON store) added; T-0402/T-0403 now READY.
Next: T-0402 (CIE URL ingestion + exact identification).