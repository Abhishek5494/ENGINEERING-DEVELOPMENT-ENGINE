# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0106 — macOS scripts (install/update/healthcheck)
- **State:** READY
- **Phase:** 1 — Project Environment Manager

### Objective
Add thin macOS shell wrappers `scripts/macos/{install,update,healthcheck}.sh`
over the verified shared code in `src/pem/ops.py` (MASTER §23), mirroring
the Linux wrappers from T-0105: resolve the repository root relative to
the script, discover the interpreter, delegate to the shared module, and
propagate its exit code. No business logic, no tool lists, no
detection/installation logic in the scripts. This completes the Phase 1
platform wrapper set (R3.7).

### Dependencies
- T-0104 (COMPLETE) — shared `src/pem/ops.py` command layer + wrapper precedent.
- T-0105 (COMPLETE) — Linux POSIX wrappers; identical structure applies.
- T-0107 (COMPLETE) — install `--execute` semantics frozen; wrappers only forward arguments.

### Affected components
- `scripts/macos/install.sh`, `scripts/macos/update.sh`,
  `scripts/macos/healthcheck.sh` (new)
- `tests/test_scripts_linux.py` (generalize to cover Linux + macOS) or a
  new `tests/test_scripts_macos.py`
- `requirements.md` R3.7; roadmap/audit/state closure updates

### Constraints
- POSIX `sh` scripts (`#!/usr/bin/env sh`), repo root resolved relative
  to the script path (`CDPATH= cd -P "$(dirname "$0")"` then `../..`),
  no hard-coded absolute paths.
- Interpreter discovery: prefer `python3`, fall back to `python`; if
  neither exists, print an error and exit 2. (macOS ships no `python`
  by default, so `python3` is the realistic path — do not claim
  otherwise.)
- Delegate with `exec "$python_cmd" -m src.pem.ops <command> "$@"` so the
  shared module's exit code is propagated (no swallowing).
- No manifest tool id may appear except the interpreter token
  (`python`/`python3`) on plumbing lines — same resolution as T-0104/T-0105.
- Mark the scripts executable in the git index with
  `git add --chmod=+x` and verify with `git ls-files -s` (mode 100755),
  since the Windows filesystem cannot set POSIX execute bits.
- Do NOT execute the scripts on this Windows host (no POSIX shell);
  static validation only. Never claim runtime behavior.
- No new third-party dependencies.

### Acceptance criteria
1. The three `.sh` files exist under `scripts/macos/` with a valid POSIX
   shebang and call `python -m src.pem.ops <command>`.
2. Each propagates the shared module's exit code (`exec`).
3. No manifest tool id appears except the interpreter token; no tool
  list or detection/install logic is present.
- 4. Static tests assert the above (reuse/extend the Linux test's
  checks); `sh -n` runs only if a POSIX shell exists.
- 5. Scripts are tracked executable (mode 100755) in the git index, or
  the exact limitation is recorded if the environment refuses.
- 6. `requirements.md` R3.7 updated (all three platform sets now exist;
  macOS static-only), roadmap T-0106 → COMPLETE and next task → READY.
- 7. `python -m pytest tests/ -v` passes (existing suites + new checks).
- 8. project-state.md, audit.md (new AUDIT entry with OBSERVED static
  evidence + explicit "not executed on this host"), chatmem.md updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Record static evidence and the `git ls-files -s` mode check; state
  that no POSIX shell exists and only static checks ran. Do not
  fabricate runtime output.
- Review `git status` / `git diff` before commit; commit message states
  what was tested (and what could not be executed).
- After completion: update roadmap (T-0106 → COMPLETE), project-state.md,
  audit.md, requirements.md, and rewrite this file for the next READY
  task — per §48 phase order the next candidate is **T-0202 (Phase 2,
  shared configuration module; dependency T-0001 COMPLETE)**, ahead of
  T-1601 (Phase 16 hardening). Record the choice and reason.
- Consider promoting the shared wrapper-static-check helper so
  Linux + macOS tests do not duplicate logic (optional; only if it
  reduces duplication without weakening assertions).

### Out of scope (do not pull in)
- Executing macOS scripts (no POSIX runtime on this host), cross-platform
  hardening/CI (T-1601), package-manager detection (R3.3), any change to
  `src/pem/ops.py` behavior, detectors, report generation, or the install
  engine. Do not modify the Windows or Linux wrappers.