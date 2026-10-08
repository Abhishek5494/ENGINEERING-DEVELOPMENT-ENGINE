# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0102 — PEM tool detection + capability states
- **State:** READY
- **Phase:** 1 — Project Environment Manager

### Objective
Implement manifest-driven tool detection in `src/pem/tools.py`: for every
tool in `config/tool-manifest.json`, probe for it according to its
`detection_method`, record an evidence-backed result (never a guess), and
aggregate results into the §22 capability states
(READY / LIMITED / UNAVAILABLE / UNKNOWN). This is what makes PEM
manifest-driven instead of hard-coding tool knowledge (MASTER §22, §24,
§7, §25).

### Dependencies
- T-0101 (COMPLETE) — `src/pem/detect.py` exists.
- T-0201 (COMPLETE) — `src/core/manifest.py` loader + manifest exist.

### Affected components
- `src/pem/tools.py` (new)
- `tests/test_pem_detection.py` or new `tests/test_pem_tools.py`
- `memory.md` (durable findings: which tools are actually installed)
- `project-state.md` environment section

### Constraints
- Detection only — NO installation, NO network.
- One bounded probe per tool with a hard timeout (resource-light, §38);
  no shell=True; parse command strings with shlex and execute the list.
- Trust model: health-check strings come from the repo manifest (trusted
  local data), not from the web.
- Never claim a tool is installed without successful probe evidence
  (§25). Timeout/probe error → UNKNOWN, not NOT_FOUND.
- `detection_method: "none"` (taiga-s1, rea) → state UNKNOWN with reason
  "not implemented" — do not run probes for them.
- Do NOT implement environment.json / report generation (T-0103), missing
  dependency analysis (T-0103), or installation (T-0104+).

### Acceptance criteria
1. `src/pem/tools.py` exposes `detect_tools(manifest=None) -> list[dict]`
   with one record per manifest tool containing at least: `id`,
   `state` ∈ {DETECTED, NOT_FOUND, UNKNOWN}, `version` (string or
   UNKNOWN), `executable_path` (string or UNKNOWN), `evidence` ∈
   {OBSERVED, UNKNOWN}, `probe` (command string actually run or null),
   `reason` (why state was chosen).
2. `capability_states(tool_records) -> dict[str, str]` returns each of
   the eight §22 capabilities mapped to exactly one of READY / LIMITED /
   UNAVAILABLE / UNKNOWN, with rules: DETECTED tool providing it →
   READY; all providing tools conclusively probed and absent →
   UNAVAILABLE; any contributing probe inconclusive (UNKNOWN) or all
   providing tools undetectable ("none") → UNKNOWN; detected but
   version-below-known-min or failed health check → LIMITED.
   States validated through `validate_capability_state`.
3. Probes: FileNotFoundError → NOT_FOUND; timeout / non-zero exit with no
   parseable version → distinguish NOT_FOUND (executable absent) vs
   UNKNOWN (probe ran but inconclusive); version extracted only when
   actually present in output, else UNKNOWN.
4. On this host the detector must find Git and Python (OBSERVED on this
   machine) and must not claim FreeCAD/KiCad/ngspice/Gazebo/Blender
   unless their probes actually succeed.
5. Tests: mocked subprocess covering DETECTED, NOT_FOUND (missing
   executable), timeout → UNKNOWN, version parsing, capability
   aggregation rules (READY/UNAVAILABLE/UNKNOWN/ LIMITED path), and
   detection_method "none" → UNKNOWN; plus a light real-host test for
   git + python only.
6. `python -m pytest tests/ -v` passes (governance + PEM + manifest +
   new tests).
7. Importable as `from src.pem.tools import detect_tools,
   capability_states`.

### Validation requirements
- Execute the full test suite; record the real result in audit.md.
- Run tool detection live on this host once; paste a sanitized summary
  (per-tool state/version only) into audit.md as OBSERVED evidence and
  update `memory.md` + project-state environment section with the real
  results.
- Review `git status` / `git diff` before commit; commit message states
  what was tested.
- After completion: update roadmap (T-0102 → COMPLETE), project-state.md,
  audit.md, requirements.md (R3.2/R3.4), and rewrite this file for the
  next READY task (expected: T-0103 environment report, or T-0202 shared
  config if T-0103's dependency chain requires it).

### Out of scope (do not pull in)
- environment.json/environment-report.md (T-0103), installation or
  package-manager actions (T-0104+), GPU/VRAM probing, manifest edits.
