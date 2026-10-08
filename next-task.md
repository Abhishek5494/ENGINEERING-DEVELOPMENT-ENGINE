# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0901 — FreeCAD integration
- **State:** READY
- **Phase:** 9 — Engineering tool integrations (FreeCAD = mechanical authority)

### Objective
Integrate FreeCAD as the mechanical CAD authority (MASTER §2.5/§17/§18):
build a FreeCAD macro/script (stdlib Python text generated here, run by
FreeCAD), write outputs to `cad/`, and verify with a FreeCAD-native step
(the model is generated/normalised by FreeCAD, not by us). Execution runs
through `freecadcmd` **only when FreeCAD is actually installed**; when it
is absent the capability reports `UNAVAILABLE` and integration tests SKIP
with a reason — never a fake success (§46).

### Dependencies
- T-0103 (COMPLETE — PEM environment detection/report),
  T-0302 (COMPLETE — evidence labels).

### Affected components
- `src/integrations/freecad.py` (new): `FREECAD_TOOLS`, `freecad_cmd`,
  `FreeCadError`, `FreeCADUnavailable`, `build_box_macro`,
  `write_macro`, `run_macro`, `cad_evidence`.
- `src/integrations/__init__.py` (re-export new public names).
- `cad/.gitkeep` (output root; already present).
- `tests/test_integrations_freecad.py` (new; live test skips when FreeCAD
  is absent).
- `requirements.md` (R9.x), roadmap/audit/project-state/next-task/chatmem/
  memory updates.

### Behaviour
- `freecad_available(which=shutil.which)` resolves a FreeCAD console
  executable from candidates (`FreeCADCmd`, `freecadcmd`, `FreeCADCmd.exe`,
  `freecadcmd.exe`) or returns `None`; injectable for tests.
- `build_document_script(...)` returns the text of a deterministic FreeCAD
  macro that creates a simple solid (e.g. a Part box with given
  dimensions), recomputes it, saves `<name>.FCStd` and exports a `.step`
  into a target directory.
- `write_script(path, script, overwrite=False, base=...)` writes the
  macro under a repo-confined root (default `cad/`), refusing path escape
  and (by default) overwrite.
- `run_macro(script, ..., which=..., run=subprocess.run)` runs
  `freecadcmd <script>` **when FreeCAD is available**; otherwise raises
  `FreeCADUnavailable`. Returns a `FreeCADRun` (returncode/stdout/stderr).
- `verify_outputs(directory, names)` returns sizes of expected CAD files
  and raises `CadError` when a required artifact is missing (tool-native
  verification proxy: FreeCAD must actually have produced the file).
- `cad_evidence(...)` returns `EvidenceEntry` objects: `OBSERVED` for the
  produced artifact's existence/size, `SIMULATED` for the generated model,
  plus a documented limitation when FreeCAD is absent.

### Constraints
- Standard library only (`shutil`, `subprocess`, `json`, `pathlib`).
  FreeCAD is optional; never a hard dependency and never installed here.
- No network; no execution of arbitrary code except the caller-invoked
  FreeCAD macro when FreeCAD is present.
- All writes confined to the repo (`cad/`); no path escape.
- Report absence as `UNAVAILABLE` (honest skip), never a passing test.

### Acceptance criteria
1. `freecad_available(lambda name: None) is None`; with an injected
   `which` returning a path it returns that path.
2. `build_macro`/`build_document_script` returns non-empty Python text
  containing the FreeCAD API calls.
3. `write_macro` writes under `cad/`, refuses overwrite by default and
  rejects path traversal.
4. `run_macro` raises `FreeCADUnavailable` when FreeCAD is absent
  (injected); when present it is exercised by a skip-if-absent
  integration test that verifies a real `.FCStd` is produced.
- 5. `cad_evidence` yields valid labelled `EvidenceEntry` objects.
- 6. `from src.integrations import ...` exposes the public names; full
  suite passes (`python -m pytest tests/ -v`).
- 7. Roadmap (T-0901 COMPLETE; T-1001 READY), requirements, project-state,
  audit (AUDIT-0023), chatmem, memory updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Live evidence: generate a macro and write it under `cad/`; call
  `freecad_available()` and record the real result (expected: FreeCAD NOT
  installed → mostly `None`); show the gated execution/validation path
  refusing honestly (`FreeCADUnavailable`) — OBSERVED, never claimed.
- Review `git status` / `git diff` before commit.
- After completion, pick the next READY task by §48 order (T-1001 KiCad)
  and record the reason.

### Out of scope (do not pull in)
- KiCad/ngspice/Gazebo/Blender, installing FreeCAD, FEM/analysis,
  assemblies, or any network acquisition.