# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0202 — Shared configuration module
- **State:** READY
- **Phase:** 2 — Configuration + tool registry

### Objective
Create `src/core/config.py` as the single, deterministic source of
repository paths and configuration loading for every subsystem
(MASTER §49, §27): resolve the repository root, expose canonical
directories (`config/`, `cad/`, `electronics/`, `simulations/`,
`models/`, `data/`, `components/`, `docs/`, `projects/`), and load
configuration files (JSON always; YAML when a YAML parser is
available) with defaults and clear errors. No subsystem may hard-code
its own repo-root logic after this task.

### Dependencies
- T-0001 (COMPLETE) — repository structure exists.

### Affected components
- `src/core/config.py` (new)
- `src/core/__init__.py` (re-export the public helpers)
- `tests/test_core_config.py` (new)
- Optional, only if it removes duplication without behaviour change:
  point `src/pem/report.py` / `src/core/manifest.py` at
  `config.REPO_ROOT` instead of their own root computation.
- `requirements.md` (R13.2 / add a config requirement row if missing);
  roadmap/audit/state closure updates

### Constraints
- Standard library only (no new third-party dependency). YAML support is
  optional and must degrade honestly: if PyYAML is not importable,
  loading a `.yaml`/`.yml` file raises a clear `ConfigError` naming the
  missing parser — never silently returns empty data.
- Deterministic repo root: derive from `__file__` (do not depend on the
  current working directory).
- JSON loading with a defaults mapping: a deep merge where explicit
  values override defaults and nested dicts merge; unknown top-level keys
  from defaults are preserved. Missing file + no default → `ConfigError`.
- No secrets are read or logged. Environment variables may be read for an
  explicit opt-in override only if implemented; never write secrets.
- Keep behaviour identical wherever existing code is repointed.

### Acceptance criteria
1. `src/core/config.py` exposes `REPO_ROOT`, the canonical directory
   constants, `ConfigError`, `load_json`, and `load_config`
   (with optional defaults + YAML-if-available).
2. `REPO_ROOT` equals the project root and is independent of CWD (test
   proves it by loading a file while CWD is elsewhere).
3. JSON load returns parsed data; `load_config` merges defaults (nested
   merge verified); missing file with no default raises `ConfigError`.
4. YAML path: if a YAML parser is available it loads; otherwise a clear
   `ConfigError` is raised (test branches on availability — honest skip,
   never a fake pass).
5. If existing modules are repointed, the entire suite still passes with
   unchanged outputs (report/manifest tests remain green).
6. `python -m pytest tests/ -v` passes (existing suites + new config
   tests).
7. roadmap (T-0202 COMPLETE, next → T-0302 or T-0301 per §48 order),
   project-state.md, audit.md (new AUDIT entry), requirements.md,
   chatmem.md updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Record live evidence: print `config.REPO_ROOT` and load
  `config/tool-manifest.json` through `load_config` (OBSERVED).
- Review `git status` / `git diff` before commit; commit message states
  what was tested.
- After completion: select the next READY task by §48 phase order.
  Phase 3 tasks T-0301 (state persistence; deps T-0001+T-0202) and T-0302
  (evidence primitives; deps T-0001+T-0202) both become READY — pick the
  one that best unblocks the dependency graph and record the reason.

### Out of scope (do not pull in)
- Full YAML config merge semantics beyond the stated behaviour; secrets
  management; rewriting PEM/other subsystems beyond the optional REPO_ROOT
  repoint; any network access.