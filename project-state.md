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
PHASE 8 — Python/Jupyter integration (COMPLETE for offline build/validate;
live execution UNAVAILABLE — Jupyter not installed).
PHASE 9 — FreeCAD integration (COMPLETE for macro generation/write;
live CAD execution UNAVAILABLE — FreeCAD not installed).
PHASE 10 — KiCad + ngspice integrations (COMPLETE for offline command/
parse logic; live PCB/circuit execution UNAVAILABLE — tools not installed).
PHASE 11 — Gazebo integration (COMPLETE for world write/headless logic;
live robotics simulation UNAVAILABLE — Gazebo not installed).
PHASE 12 — Blender integration (COMPLETE for script write/headless render
logic; live rendering UNAVAILABLE — Blender not installed).
PHASE 13/14 — Unified workflow (T-1301) and validation/BOM pipeline
(T-1401) — BLOCKED (depend on BLOCKED T-0602/T-0404).
PHASE 15 — Security review T-1501 BLOCKED (dep T-0502); recovery test
T-1502 COMPLETE (state reconstructed from repository evidence only).
PHASE 16 — Cross-platform hardening T-1601 COMPLETE (LF/UTF-8 text + path
containment; POSIX runtime evidence still UNAVAILABLE without a VM/CI).
PHASE 17 — Release audit T-1701 BLOCKED (deps T-1401/T-1501 BLOCKED). No
further executable task remains; the build stops and surfaces blockers.

## Overall status
Governance complete; Phases 1–3 complete (PEM; `src/core/config.py`,
`state.py`, `evidence.py`, `xplat.py`, `recovery.py`). Phase 4 CIE offline
scope complete: data model + schema + SQLite/JSON store (T-0401), URL
ingestion + exact identification (T-0402), provenance + source priority +
conflicts (T-0403). REA framework + offline inspection complete
(T-0701/T-0702). Engineering-tool integrations complete for offline
command/evidence logic: Jupyter (T-0801), FreeCAD (T-0901), KiCad
(T-1001), ngspice (T-1002), Gazebo (T-1101), Blender (T-1201); live
execution is UNAVAILABLE (tools not installed). Recovery-after-
interruption (T-1502) and cross-platform hardening (T-1601) complete.
Not implemented: CIE cross-source search (T-0404, needs Scrapling),
Scrapling, Taiga-S1, end-to-end orchestration (T-1301), validation/BOM
pipeline (T-1401), security review (T-1501), release audit (T-1701).
Taiga-S1 is externally BLOCKED (repo not supplied) and Scrapling is
BLOCKED on the install gate; live tool installation is gated on user
approval + disk + network. Autonomous build stopped at the blocked
boundary (no fake completion).

## Completed phases
- PHASE 0 — Repository + governance (T-0001 COMPLETE, 2026-10-08)
- PHASE 1 — PEM (T-0101..T-0107, T-0201 COMPLETE for code; live installs
  gated)
- PHASE 2 — Configuration + tool registry (T-0202 COMPLETE, 2026-10-08)
- PHASE 3 — Core primitives (T-0301, T-0302 COMPLETE, 2026-10-08)
- PHASE 4 — CIE offline scope (T-0401..T-0403 COMPLETE; T-0404 gated on
  T-0502)
- PHASE 7 — REA (T-0701/T-0702 COMPLETE; framework + offline inspection)
- PHASE 8 — Python/Jupyter integration (T-0801 COMPLETE; execution gated
  on Jupyter presence)
- PHASE 9 — FreeCAD integration (T-0901 COMPLETE; execution gated on
  FreeCAD presence)
- PHASE 10 — KiCad + ngspice integrations (T-1001/T-1002 COMPLETE;
  execution gated on tool presence)
- PHASE 11 — Gazebo integration (T-1101 COMPLETE; execution gated on
  Gazebo presence)
- PHASE 12 — Blender integration (T-1201 COMPLETE; execution gated on
  Blender presence)
- PHASE 13/14 — BLOCKED (T-1301/T-1401; deps T-0602/T-0404 BLOCKED)
- PHASE 15 — T-1501 BLOCKED (dep T-0502), T-1502 COMPLETE
- PHASE 16 — T-1601 COMPLETE (deps T-0104/T-0105/T-0106)
- PHASE 17 — T-1701 BLOCKED (deps T-1401/T-1501 BLOCKED)

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
- T-0801 — Python/Jupyter integration (2026-10-08) — AUDIT-0022.
- T-0901 — FreeCAD integration (2026-10-08) — AUDIT-0023.
- T-1001 — KiCad integration (2026-10-08) — AUDIT-0024.
- T-1002 — ngspice integration (2026-10-08) — AUDIT-0025.
- T-1101 — Gazebo integration (2026-10-08) — AUDIT-0026.
- T-1201 — Blender integration (2026-10-08) — AUDIT-0027.
- T-1502 — Recovery-after-interruption test (2026-10-08) — AUDIT-0028.
- T-1601 — Cross-platform hardening (2026-10-08) — AUDIT-0029.

## Last completed task
- T-1601 — Cross-platform hardening (2026-10-08) — 380 passed, 8 skipped;
  `src/core/xplat.py` (LF/UTF-8 text I/O, line-ending audit, path
  containment); live LF audit of `scripts/**/*.sh`. POSIX runtime evidence
  UNAVAILABLE (no POSIX shell/VM) — recorded honestly.

## Current task
- ID: T-1701
- Title: Release audit vs MASTER §54 checklist
- State: BLOCKED (depends on BLOCKED T-1401/T-1501)
- (Note: all non-blocked phases are complete. No further executable task
  remains. Remaining blockers: B-1 Taiga-S1 repo not supplied
  (T-0601/T-0602/T-1301/T-1401); B-2 install approval + C:\ below
  threshold (T-0501/T-0502/T-0404/T-1501); T-0002 license awaiting human
  approval. The release audit cannot proceed until these are resolved.)

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

- Recovery: `src/core/recovery.py` (T-1502: `recover`/
  `recover_consistent`/`assert_recoverable` reconstruct state from
  `MASTER.md`/`project-state.md`/`next-task.md`/`roadmap.md` only and
  reject contradictions — MASTER §42/§43).
- Cross-platform: `src/core/xplat.py` (T-1601: `normalise_newlines`,
  `read_text_utf8`, `write_text_lf`, `line_ending_report`, `path_within`).
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
- Integrations: `src/integrations/jupyter.py` (Python/Jupyter: nbformat v4
  build/validate, `simulations/`-confined notebook write,
  `jupyter nbconvert` execution gated on `jupyter_available`,
  `notebook_evidence`), `src/integrations/__init__.py` re-exports.
- Integrations (CAD): `src/integrations/freecad.py` (FreeCAD mechanical
  authority: parametric macro generation, `cad/`-confined macro write,
  headless `freecadcmd` run gated on `freecad_available`,
  `verify_outputs`, `cad_evidence`).
- Integrations (PCB): `src/integrations/kicad.py` (KiCad PCB authority:
  `kicad-cli` DRC/ERC/Gerber export gated on `kicad_cli`,
  `verify_artifacts`, `kicad_evidence`).
- Integrations (circuits): `src/integrations/ngspice.py` (ngspice circuit
  authority: batch `ngspice -b -o` gated on `ngspice_cli`, `write_netlist`,
  `parse_op_point`, `verify_outputs`).
- Integrations (robotics): `src/integrations/gazebo.py` (Gazebo
  robotics/physics authority: headless `gz sim -s` gated on `gazebo_cli`,
  `write_world` under `models/`, `verify_outputs`).
- Integrations (visualization): `src/integrations/blender.py` (Blender
  visualization authority: headless `blender --background --python` gated
  on `blender_cli`, `write_script` under `models/`, `verify_outputs`).

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
- `python -m pytest tests/ -v` → **380 passed, 8 skipped** (2026-10-08,
  Python 3.13.5, pytest 9.1.1): 38 governance + 9 PEM detection +
  21 manifest + 22 PEM tools + 20 PEM report + 23 PEM ops + 17 installer
  + 14 Unix-script static tests (parametrised Linux + macOS) + 19 core
  config + 29 core evidence + 20 core state + 14 CIE model/schema +
  7 CIE store + 5 CIE target + 14 CIE identify + 9 CIE provenance +
  13 CIE conflict + 8 REA pipeline + 8 REA records + 7 REA storage +
  8 REA inspection + 8 Jupyter + 7 FreeCAD + 7 KiCad + 7 ngspice +
  6 Gazebo + 6 Blender + 7 recovery + 7 cross-platform tests.
  Skipped (8): the two per-platform `sh -n` syntax checks (no POSIX
  shell on host), and the live-Jupyter, live-FreeCAD, live-KiCad,
  live-ngspice, live-Gazebo and live-Blender tests (those tools are not
  installed).
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
  `inspect_target` produced OBSERVED evidence (0→7 entries). Integrations
  (T-0801): unit-tested; live build→validate→write of a notebook to
  `simulations/` observed (527 bytes), `jupyter_available()` returned
  `None`, and `execute_notebook` raised `JupyterUnavailable` — notebook
  execution is **UNAVAILABLE** on this host, never claimed as run. FreeCAD
  (T-0901): unit-tested; live generation of a
  parametric macro written to `cad/` observed (381 bytes),
  `freecad_available()` returned `None` (FreeCAD NOT installed), and
  `run_macro` raised `FreeCADUnavailable` — CAD execution is
  **UNAVAILABLE** on this host. KiCad (T-1001): unit-tested; live
  `kicad_cli()` returned `None` (KiCad NOT installed), `verify_artifacts`
  reported a fixture's size, and `run_drc` raised `KiCadUnavailable` —
  PCB execution is **UNAVAILABLE** on this host. ngspice (T-1002):
  unit-tested; live `ngspice_cli()` returned `None` (ngspice NOT
  installed), `parse_op_point` extracted `{'in': 5.0, 'out': 3.3}` from a
  captured block, and `run_simulation` raised `NgspiceUnavailable` —
  circuit simulation is **UNAVAILABLE** on this host. Gazebo (T-1101):
  unit-tested; live `write_world` wrote an SDF under `models/` (67 bytes),
  `gazebo_cli()` returned `None` (Gazebo NOT installed), and
  `run_headless` raised `GazeboUnavailable` — robotics simulation is
  **UNAVAILABLE** on this host. Blender (T-1201): unit-tested; live
  `write_script` wrote a Python script under `models/` (54 bytes),
  `verify_outputs` reported its size, `blender_cli()` returned `None`
  (Blender NOT installed), and `run_background` raised
  `BlenderUnavailable` — rendering is **UNAVAILABLE** on this host.
  Recovery (T-1502): unit-tested; live `assert_recoverable(REPO_ROOT)`
  reconstructed boundary T-1502 with blocked set {T-0002, T-0501, T-0601,
  T-0602, T-1301, T-1401, T-1501} from repository evidence alone. Cross-platform (T-1601): unit-tested;
  live `line_ending_report` over `scripts/**/*.sh` reported LF-only; the
  POSIX wrappers remain STATIC-validated only (no POSIX shell to execute
  them). No engineering validation applicable yet.

## Next action
No further executable task remains. All non-blocked phases are complete
(1–12, T-1502 recovery, T-1601 hardening). To continue, a human must
clear the blockers:
- **B-1:** supply the Taiga-S1 upstream repository → unblocks
  T-0601/T-0602 → T-1301 → T-1401.
- **B-2:** approve network/privileged installs (Scrapling) and raise
  C:\ above the 1 GiB threshold → unblocks T-0501/T-0502 → T-0404 →
  T-1501.
- **T-0002:** license decision (§35).
When those are resolved, resume with the next executable task in §48
order; eventually T-1701 (release audit) walks the §54 checklist.

## Last update
2026-10-08 — T-1601 closed (380 passed, 8 skipped); cross-platform
  text/path hardening (`src/core/xplat.py`) is in place and the POSIX
  scripts are proven LF-only live. Phase 16 complete. Remaining tasks
  (T-1301/T-1401/T-1501/T-1701) are all BLOCKED on B-1/B-2, so the
  autonomous build stops and surfaces the blockers (no fake completion).