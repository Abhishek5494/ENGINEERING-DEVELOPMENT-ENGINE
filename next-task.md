# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0105 — Linux scripts (install/update/healthcheck)
- **State:** READY
- **Phase:** 1 — Project Environment Manager

### Objective
Add thin Linux shell wrappers `scripts/linux/{install,update,healthcheck}.sh`
over the verified shared code in `src/pem/ops.py` (MASTER §23): resolve
the repository root, invoke the shared module with the current
interpreter, and propagate its exit code — no business logic, no tool
lists, no detection/installation logic in the scripts. Platform remains
auto-detected in shared code (this host will report `linux` only when
run on Linux).

### Dependencies
- T-0104 (COMPLETE) — shared `src/pem/ops.py` command layer + Windows
  wrapper precedent.
- T-0107 (COMPLETE) — install `--execute` semantics are frozen, so the
  wrappers only forward arguments.

### Affected components
- `scripts/linux/install.sh`, `scripts/linux/update.sh`,
  `scripts/linux/healthcheck.sh` (new)
- `tests/test_pem_ops.py` (extend wrapper assertions to Linux scripts)
  or a new `tests/test_scripts_linux.py`
- `requirements.md` R3.7; roadmap/audit/state closure updates

### Constraints
- Shell scripts must be POSIX `sh` (not bash-only), start with
  `#!/usr/bin/env sh`, be executable-intent, and end by exiting with the
  shared module's exit code. Resolve the repo root relative to the
  script location (no hard-coded absolute paths).
- Discover the interpreter honestly: prefer `python3`, fall back to
  `python`; if neither exists, print an error and exit 2 (execution
  error), matching the Windows wrapper's behavior.
- No manifest tool id may appear in the scripts except the interpreter
  bootstrap token (`python`/`python3`), mirroring the recorded T-0104
  discrepancy resolution.
- Do NOT execute the scripts on this Windows host; a POSIX shell is not
  available here. Validate by static checks only (file exists, shebang,
  calls the shared module, contains no tool ids/business logic). If a
  POSIX shell happens to be present, a syntax check (`sh -n`) is
  acceptable, but NEVER claim execution or correct runtime behavior.
- No new third-party dependencies.

### Acceptance criteria
1. The three `.sh` files exist under `scripts/linux/` with a valid
   POSIX shebang and call `python -m src.pem.ops <command>`.
2. Each propagates the shared module's exit code (no swallowing).
3. No manifest tool id appears except the interpreter token; no tool
   list or detection/install logic is present.
4. Static tests assert the above; if `sh` is available, `sh -n` passes
   on each script.
5. `requirements.md` R3.7 updated (Linux set now exists; still no
   execution evidence — honest qualifier), roadmap T-0105 → COMPLETE and
   T-0106 → READY/next.
6. `python -m pytest tests/ -v` passes (existing suites + new checks).
7. project-state.md, audit.md (new AUDIT entry with OBSERVED static
   evidence and an explicit "not executed on this host" statement),
   chatmem.md updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Record static/`sh -n` evidence (or state that no POSIX shell exists and
  only static checks ran). Do not fabricate runtime output.
- Review `git status` / `git diff` before commit; commit message states
  what was tested (and what could not be executed).
- After completion: update roadmap (T-0105 → COMPLETE, T-0106 → READY),
  project-state.md, audit.md, requirements.md, and rewrite this file for
  the next READY task (T-0106 macOS scripts, then T-1601 hardening /
  Phase 2 T-0202 — choose by §48 phase order and record the reason).

### Out of scope (do not pull in)
- Executing Linux scripts (no POSIX runtime on this host), macOS
  wrappers (T-0106), cross-platform hardening/CI (T-1601), package
  manager detection (R3.3), any change to `src/pem/ops.py` behavior,
  detectors, report generation, or the install engine.