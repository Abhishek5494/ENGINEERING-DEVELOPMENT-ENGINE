# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0201 — Tool manifest schema + config/tool-manifest.json + loader
- **State:** READY
- **Phase:** 2 — Configuration + tool registry

### Objective
Create the machine-readable tool manifest required by MASTER §24: a JSON
schema covering every §24 field, `config/tool-manifest.json` containing
the eleven required tools (Git, Python, Jupyter, Taiga-S1, FreeCAD, KiCad,
ngspice, Gazebo, Blender, REA, Scrapling), and a validated stdlib loader
so that PEM (T-0102) can become manifest-driven instead of hard-coding
tool knowledge in installer scripts.

### Dependencies
- T-0001 (COMPLETE) — repository exists.

### Affected components
- `config/tool-manifest.json` (new)
- `config/tool-manifest.schema.json` (new)
- `src/core/manifest.py` (new loader + validation; `src/core/__init__.py`)
- `tests/test_manifest.py` (new)
- `requirements.md` R4 status columns (SPECIFIED → IMPLEMENTED)

### Constraints
- Detection/probing is OUT OF SCOPE (T-0102) — the manifest only
  *describes how* to detect; it must not claim any tool is installed.
- No fabricated versions: `min_version`/`preferred_version` must be null
  unless justified (documented in the entry or in audit.md). Observed
  host versions (Git 2.55.0, Python 3.13.5) may be recorded as
  `preferred_version` with provenance noted.
- stdlib-only loader (json); no PyYAML requirement; no network.
- Manifest must be consumed by path, not embedded in code (§24: do not
  hard-code every dependency into installer scripts).
- Taiga-S1, REA and Scrapling are in-house/not-yet-integrated components;
  represent them honestly (executable/detection marked pending, version
  null) — do not invent release versions.

### Acceptance criteria
1. `config/tool-manifest.schema.json` defines required fields for every
   §24 item: tool, purpose, required/optional, supported platforms,
   minimum version, preferred version, detection method, executable,
   dependencies, installation method, health check, capability
   requirements (plus a stable `id`).
2. `config/tool-manifest.json` contains all 11 tools and validates
   against the schema.
3. `src/core/manifest.py` exposes a loader that returns the parsed
   manifest and raises a descriptive error on: missing file, invalid
   JSON, schema violations (unknown tool id, missing field, bad type,
   unsupported required/optional value, unsupported platform, invalid
   capability state).
4. Capability states allowed in the manifest are limited to
   READY / LIMITED / UNAVAILABLE / UNKNOWN semantics where referenced
   (§22).
5. Tests cover: valid manifest loads; each rejection path above yields a
   clear exception; the 11 required tool ids are present; no entry
   asserts an installation state (no `installed`/`version` claims).
6. `python -m pytest tests/ -v` passes (governance + PEM + manifest).
7. Importable as `from src.core.manifest import load_manifest`.

### Validation requirements
- Execute `python -m pytest tests/ -v`; record the real result in
  audit.md — never claim an unrun test.
- Round-trip check: load `config/tool-manifest.json` in a test.
- Review `git status` / `git diff` before commit; commit message states
  what was tested.
- After completion: update roadmap (T-0201 → COMPLETE), project-state.md,
  audit.md, requirements.md R4 status, and rewrite this file for the next
  READY task (candidates: T-0202 shared configuration module; then
  T-0102 PEM tool detection becomes unblocked).

### Out of scope (do not pull in)
- Actual tool probing/version detection (T-0102), report generation
  (T-0103), installers (T-0104+), YAML support, shared general config
  resolution (T-0202).
