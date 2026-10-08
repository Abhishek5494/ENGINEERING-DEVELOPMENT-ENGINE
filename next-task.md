# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0103 — Environment report generation (environment.json + md)
- **State:** READY
- **Phase:** 1 — Project Environment Manager

### Objective
Combine `detect_system()` (T-0101), `detect_tools()` and
`capability_states()` (T-0102) into the two §25 deliverables:
`environment.json` (machine-readable) and `environment-report.md`
(human-readable), including missing dependencies, capability status,
warnings, limitations and recommendations — with every claim traceable
to probe evidence and zero fabricated values (MASTER §25, §7, §29).

### Dependencies
- T-0102 (COMPLETE) — detection sources exist.

### Affected components
- `src/pem/report.py` (new) + `src/pem/__init__.py` export if useful
- `tests/test_pem_report.py` (new)
- `.gitignore` (add `environment-report.md` alongside `environment.json`)
- `requirements.md` R3.5, `architecture.md` status only if scope differs

### Constraints
- Generation only — no installation, no network, no probing beyond
  calling the existing detectors.
- `environment.json` and `environment-report.md` are machine-specific,
  regenerable artifacts: BOTH gitignored (never committed).
- A tool may be reported present ONLY if its record says
  `state == "DETECTED"` (§25: never claim installed unless detection
  confirms).
- NOT_FOUND tools appear under missing dependencies; UNKNOWN tools must
  be listed as unknown, not as missing-or-present.
- Warnings must be data-driven (e.g. disk free below a documented
  threshold, required tool absent), recommendations phrased as
  suggestions — the generator never installs anything.
- Output must be deterministic given identical inputs (inject inputs for
  testability; timestamps allowed but field-documented).
- No new third-party dependencies.

### Acceptance criteria
1. `src/pem/report.py` exposes `build_environment(system, tools,
   capabilities, *, generated_at=None) -> dict` returning a
   JSON-serializable document with at least: `generated_at`,
   `platform` (OS/arch/CPU/RAM/GPU/storage from system records),
   `tools` (per-tool id/state/version/path/evidence), `missing_tools`,
   `unknown_tools`, `capabilities`, `warnings`, `limitations`,
   `recommendations`.
2. `write_reports(report, directory=None)` writes `environment.json`
   (pretty-printed, UTF-8) and `environment-report.md` (human-readable
   with sections: Platform, Tools, Capabilities, Missing dependencies,
   Warnings, Limitations, Recommendations) and returns both paths.
3. Honesty rules (tests): a NOT_FOUND tool must appear in
   `missing_tools` and must NOT be described as installed anywhere; an
   UNKNOWN tool appears in `unknown_tools` only; DETECTED tools show
   their real version; a fabricated "installed" claim in output fails a
   dedicated test.
4. Warnings: free-space below threshold (documented constant, e.g.
   1 GiB) produces a warning naming the volume; at least one warning is
   produced on this host (C:\ is nearly full, OBSERVED). Unknown-capable
   capabilities (e.g. LLM inference) produce a limitation entry.
5. `.gitignore` contains `environment.json` and
   `environment-report.md`; a test asserts both.
6. Round-trip: `json.dumps` works; reloading the written
   `environment.json` reproduces the dict; report paths are inside the
   repo root by default.
7. `python -m pytest tests/ -v` passes (governance + PEM detection +
   manifest + PEM tools + new report tests).
8. Importable as `from src.pem.report import build_environment,
   write_reports`.

### Validation requirements
- Execute the full suite; record the real result in audit.md.
- Generate both reports once on this host; paste a sanitized summary of
  the warnings/missing tools into audit.md as OBSERVED evidence; confirm
  `git status` does NOT show them (gitignore works).
- Review `git status` / `git diff` before commit; commit message states
  what was tested.
- After completion: update roadmap (T-0103 → COMPLETE), project-state.md,
  audit.md, requirements.md (R3.5, R25-report items), and rewrite this
  file for the next READY task (expected: T-0104 Windows scripts, or
  T-0202 shared config — choose by dependency order and record the
  reason).

### Out of scope (do not pull in)
- Install/update/health scripts (T-0104+), package-manager detection
  (R3.3 / future task), GPU/VRAM probing, manifest or detector changes,
  committing generated reports.
