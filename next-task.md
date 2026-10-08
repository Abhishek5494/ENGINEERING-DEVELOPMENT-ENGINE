# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0104 — Windows scripts (install/update/healthcheck)
- **State:** READY
- **Phase:** 1 — Project Environment Manager

### Objective
Create `scripts/windows/{install,update,healthcheck}.ps1` as thin
wrappers over shared Python code per MASTER §23, backed by a new
`src/pem/ops.py` command module that reuses the existing detectors
(`detect_system`, `detect_tools`, `capability_states`,
`build_environment`). Health check is fully functional with documented
exit codes; install/update run in explicit plan-only mode (no mutation)
until T-0107 delivers idempotent install logic — the scripts must say so
honestly (MASTER §7, §23, §29).

### Dependencies
- T-0103 (COMPLETE) — report/detector sources exist.

### Affected components
- `scripts/windows/install.ps1`, `scripts/windows/update.ps1`,
  `scripts/windows/healthcheck.ps1` (new)
- `src/pem/ops.py` (new)
- `tests/test_pem_ops.py` (new)
- `requirements.md` R3.7, R3.8; `architecture.md` status only if scope
  differs

### Constraints
- Thin wrappers only: no tool lists, no version parsing, no business
  logic in PowerShell — scripts resolve the repo root, call
  `python -m src.pem.ops <command>` with forwarded args, and propagate
  the exit code (a test asserts no manifest tool id appears in any .ps1).
- Shared code only: `src/pem/ops.py` must reuse existing detectors —
  no re-probing, no duplicated detection logic, no new third-party
  dependencies.
- Platform auto-detection: `ops` determines the current platform from
  the runtime (§23) and filters manifest entries to it; do not accept a
  platform override flag.
- Exit codes (documented in `ops.py --help` output):
  - `0` healthy — every manifest-required tool DETECTED with
    `health_ok` and every observed storage volume free ≥
    `LOW_DISK_THRESHOLD_BYTES`;
  - `1` unhealthy — at least one required tool not DETECTED or failed
    health, or a volume below the threshold (print each failing check);
  - `2` execution error (import failure, unreadable manifest).
- `install`/`update` are plan-only: they print a manifest-driven plan
  (install: missing required/optional tools; update: detected versions
  vs manifest preferred versions), perform ZERO changes, state plainly
  that mutation arrives with T-0107, and exit 0 when the plan itself
  computed successfully.
- No network, no elevation, no installation in this task.

### Acceptance criteria
1. All three `.ps1` files exist; each is parsed as syntactically valid
   by the PowerShell language parser (invoked from a test).
2. `python -m src.pem.ops healthcheck` runs on this host and returns a
   documented exit code; the printed output names each failing check
   (expected on this host: exit 1 because C:\ is below the low-disk
   threshold — OBSERVED).
3. Tests invoke the shared module as a subprocess with an injected
   fixture manifest: missing required tool → exit 1; all healthy →
   exit 0; a platform-filtered entry for another OS never appears in a
   plan.
4. All three Windows scripts are EXECUTED on this host (roadmap
   validation): `healthcheck` propagates the shared exit code;
   `install` and `update` exit 0 and print plan-only output — recorded
   as OBSERVED evidence in audit.md.
5. No manifest tool id appears in any `.ps1` (test-asserted).
6. `install`/`update` mutate nothing: test asserts no file is created
   or changed by a plan run in a temporary working directory.
7. `requirements.md` R3.7/R3.8 updated truthfully; `python -m pytest
   tests/ -v` passes (governance + PEM detection + manifest + PEM tools
   + PEM report + new ops tests).
8. Importable as `from src.pem.ops import main`.

### Validation requirements
- Execute the full suite; record the real result in audit.md.
- Execute the three Windows scripts once on this host; capture exit
  codes + sanitized output summary in audit.md as OBSERVED evidence.
- Review `git status` / `git diff` before commit; commit message states
  what was tested.
- After completion: update roadmap (T-0104 → COMPLETE, next task READY),
  project-state.md, audit.md, requirements.md, and rewrite this file for
  the next READY task (candidates: T-0107 idempotent install logic —
  Phase 1, or T-0202 shared config — Phase 2; choose by §48 phase order
  and record the reason).

### Out of scope (do not pull in)
- Actual installation/updating (T-0107), Linux/macOS scripts
  (T-0105/T-0106), package-manager detection (R3.3), GUI, network
  access, changes to detectors or the report generator.
