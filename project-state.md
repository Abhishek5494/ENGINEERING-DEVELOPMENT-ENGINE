# project-state.md

Actual repository state. Never fictional (MASTER §29). Rewritten every time
a task is completed, blocked, or state changes.

## Current phase
PHASE 1 — Project Environment Manager (in progress).

## Overall status
Governance complete; PEM detects the system, probes every manifest
tool, generates the §25 environment reports, and now runs shared
platform operations (healthcheck with real exit codes; plan-only
install/update) behind thin Windows wrappers. Next: idempotent install
logic. No engineering subsystem beyond PEM/core implemented.

## Completed phases
- PHASE 0 — Repository + governance (T-0001 COMPLETE, 2026-10-08)

## Completed tasks (last completed task listed last)
- T-0001 — Repository governance bootstrap (2026-10-08) — 38 tests.
- T-0101 — PEM system/hardware detection (2026-10-08) — live evidence in
  AUDIT-0005.
- T-0201 — Tool manifest schema + manifest + loader (2026-10-08) — live
  evidence in AUDIT-0006.
- T-0102 — PEM tool detection + capability states (2026-10-08) — live
  tool-probe evidence in AUDIT-0007.
- T-0103 — Environment report generation (2026-10-08) — 110 tests;
  both report files generated live and confirmed gitignored
  (AUDIT-0008).

## Last completed task
- T-0104 — Windows scripts + shared ops module (2026-10-08) — 133
  tests; all three .ps1 wrappers executed on this host; healthcheck
  exit 1 (low disk), install/update exit 0 plan-only; no-mutation
  proven (AUDIT-0009).

## Current task
- ID: T-0107
- Title: Idempotent install logic + tests
- State: READY (defined in next-task.md; not yet started)

## Active subsystem
- PEM: `src/pem/detect.py` (system), `src/pem/tools.py` (tool probes,
  capability states), `src/pem/report.py` (§25 report generation),
  `src/pem/ops.py` (healthcheck/install-plan/update-plan commands).
- Core: `src/core/manifest.py` (manifest loader).
- Scripts: `scripts/windows/{install,update,healthcheck}.ps1` (thin
  wrappers, executed and verified on this host).

## Blockers
- T-0002 (License decision): BLOCKED — requires human approval (MASTER §35).

## Known issues
- **No engineering toolchain installed on this host (OBSERVED,
  2026-10-08):** FreeCAD, KiCad, ngspice, Gazebo, Blender, Jupyter,
  Scrapling all NOT_FOUND. Engineering-tool tasks (T-0801+) cannot run
  until install tasks provide them or the user installs them.
- **Disk pressure on C:\ is volatile:** 6,135,808 bytes free at
  T-0103 → 459,509,760 bytes at T-0104 close (OBSERVED; automatic
  temp cleanup ran mid-test and deleted pytest tmp dirs — recorded as
  a discrepancy in AUDIT-0009). Still below the 1 GiB healthcheck
  threshold; re-check before any install execution.
- Linux/macOS probe/code paths unexecuted (Windows host) — T-1601;
  Linux/macOS wrappers not yet created (T-0105/T-0106).
- Version extraction is best-effort first dotted-numeric token (e.g.
  "2.55.0.windows.3" reported as "2.55.0").

## Architecture status
- `architecture.md`: DRAFT consistent with implemented scope.
- ADR-0001 recorded; no architectural change since bootstrap.

## Environment status
- System (OBSERVED via `detect_system()`, 2026-10-08):
  - OS: Windows 11 (build 10.0.26200), AMD64 64-bit
  - CPU: AMD Ryzen 5 5600H with Radeon Graphics
  - RAM: 6,287,331,328 bytes (~5.86 GiB as reported by the OS)
  - GPU: AMD Radeon(TM) Graphics; NVIDIA GeForce GTX 1650 (VRAM UNKNOWN)
  - Storage: C:\ 213.8 GB total / 459,509,760 bytes free (fluctuating);
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
- `python -m pytest tests/ -v` → **133 passed, 0 failed** (2026-10-08,
  Python 3.13.5, pytest 9.1.1): 38 governance + 9 PEM detection +
  21 manifest + 22 PEM tools + 20 PEM report + 23 PEM ops.
- Bugs caught by tests so far and fixed before completion: empty-list
  evidence bug (T-0101), manifest error-ordering bug (T-0201),
  §29 heading dropped from project-state rewrite (T-0102), "installed"
  wording + missing UNAVAILABLE limitations (T-0103). T-0104 reported
  test error diagnosed as environment disk-cleanup interference (not a
  code defect; AUDIT-0009).

## Validation status
- Governance validation + live OBSERVED detector/probe/report/script
  runs recorded in audit.md (AUDIT-0005..0009). Windows wrappers
  executed on host: healthcheck exit 1 (C:\ below threshold), install/
  update exit 0 plan-only, 53-file snapshot proves zero mutation.
  No engineering validation applicable.

## Next action
Start T-0107 (see next-task.md): idempotent install logic — install
missing dependencies only when absent or below minimum version;
second run performs zero changes when healthy (MASTER §22).

## Last update
2026-10-08 — T-0104 closed after 133 tests passed; Windows wrappers
executed live; reported test error root-caused to C:\ temp cleanup.
