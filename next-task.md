# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0107 — Idempotent install logic + tests
- **State:** READY
- **Phase:** 1 — Project Environment Manager

### Objective
Deliver manifest-driven, idempotent installation logic per MASTER §22:
act only when a tool is absent (NOT_FOUND) or detected below a known
minimum version; never act on UNKNOWN; re-run safe — a second run
performs zero changes when the environment is healthy. Wire it into
`python -m src.pem.ops install --execute` (plan mode stays the
default), with guarded execution and honest post-install re-probing
(MASTER §7, §22, §23, §29).

### Dependencies
- T-0103 (COMPLETE) — detectors/report constants exist.
- T-0104 (COMPLETE) — `src/pem/ops.py` command layer exists.

### Affected components
- `src/pem/installer.py` (new)
- `src/pem/ops.py` (add `--execute` flag to install; keep default =
  plan)
- `config/tool-manifest.json`, `config/tool-manifest.schema.json`,
  `src/core/manifest.py` (new per-entry field `install_command`:
  string or null — structured, machine-readable install command;
  required on every entry so schema and loader stay in sync)
- `tests/test_installer.py` (new)
- `requirements.md` R3.6; roadmap/audit/state closure updates

### Constraints
- Manifest-driven only: install commands live in
  `install_command` entries (template `{python}` expands to the current
  interpreter at run time); no hard-coded tool list in code. Where no
  safe command can be justified yet (GUI installers, package-manager
  tools pending R3.3), the value is `null` and the engine reports
  "manual install per <installation_method>" without acting.
- Populated now (justified, not fabricated): pip-installable tools
  (python_module detection) get `{python} -m pip install <package>`;
  everything else `null` with an honest note — no package-manager
  claims until R3.3 exists.
- Idempotency rules (test-asserted): DETECTED and not below minimum →
  skip (zero actions); DETECTED below `min_version` → run
  `install_command` (upgrade case); NOT_FOUND → run
  `install_command` if present, else manual-notice; **UNKNOWN → never
  act** (inconclusive probes require investigation first).
- Guarded execution: `--execute` refuses (distinct documented exit
  code **3**, nothing performed) when any OBSERVED storage volume is
  below `LOW_DISK_THRESHOLD_BYTES`; `--execute` never runs without the
  explicit flag; plan mode remains the default and stays unchanged.
- Evidence-based verification: after each executed command the engine
  re-probes the tool and reports the resulting state with its probe
  evidence; a failed command is reported as failed with the observed
  exit code — never claimed installed (MASTER §7).
- Injectability: the command runner and detectors are injectable
  parameters so tests simulate present/absent/below-minimum states with
  a fake runner (roadmap validation) — tests never touch the network,
  never install anything, never modify the environment.
- Exit codes: 0 = plan/execute completed (or all healthy), 1 = some
  commands failed (post-probe still unhealthy), 2 = execution error,
  3 = execute refused (preconditions not met, e.g. low disk).
- No new third-party dependencies.

### Acceptance criteria
1. `src/pem/installer.py` exposes `plan_installs(...)` and
   `apply_installs(...)` importable as specified in the module
   docstring; `from src.pem.ops import main` still works.
2. Manifest: all 11 entries carry `install_command` (string or null);
   schema + loader enforce it (existing schema/loader agreement tests
   must keep passing with the new field).
3. Harness tests (fake runner): healthy run → zero runner calls;
   absent tool with command → exactly one call with the expanded argv;
   second run after simulated success → zero calls (idempotent);
   UNKNOWN → never called; below-minimum → called; null command →
   manual notice, no call.
4. Guarded execution: injected low-disk system → exit 3, runner never
   called, message names the volume.
5. Post-probe honesty: simulated failed command → summary reports the
   observed nonzero exit and the tool's resulting NOT_FOUND state;
   nothing claims success.
6. Live host evidence (OBSERVED, recorded in audit.md): plan mode
   unchanged (exit 0, lists missing tools); `install --execute` on this
   host **refuses with exit 3** naming C:\ (below threshold) — proving
   the guard without touching the network or installing anything.
7. `requirements.md` R3.6 → IMPLEMENTED (with the honest qualifier
   that live mutation was not exercised on this host); roadmap,
   project-state.md, audit.md, chatmem.md updated.
8. `python -m pytest tests/ -v` passes (governance + PEM detection +
   manifest + PEM tools + PEM report + PEM ops + new installer tests).

### Validation requirements
- Execute the full suite; record the real result in audit.md.
- Run plan mode and `--execute` (expect refusal) once on this host;
  capture exit codes + sanitized output in audit.md as OBSERVED evidence.
- Review `git status` / `git diff` before commit; commit message states
  what was tested.
- After completion: update roadmap (T-0107 → COMPLETE, next task
  READY), project-state.md, audit.md, requirements.md, and rewrite this
  file for the next READY task (candidates: T-0105/T-0106 Linux/macOS
  wrappers — now trivial thin wrappers over verified shared code, or
  T-0202 shared config — Phase 2; choose by §48 phase order and record
  the reason).

### Out of scope (do not pull in)
- Actually installing/updating anything on this host (disk + network
  policy unconfirmed), package-manager detection (R3.3), uninstall,
  Linux/macOS wrappers (T-0105/T-0106), GUI installer automation,
  changes to detectors or report generation.
