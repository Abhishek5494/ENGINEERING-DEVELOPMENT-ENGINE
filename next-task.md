# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0801 — Python/Jupyter integration
- **State:** READY
- **Phase:** 8 — Engineering tool integrations

### Objective
Integrate the Python scientific/Jupyter toolchain honestly (MASTER §17
PEM detection + §18 execution): build and validate Jupyter notebooks
(nbformat v4 JSON, stdlib only) under `simulations/` or `projects/`, run
them through `jupyter nbconvert --execute` **only when Jupyter is
actually installed**, and record results as labelled evidence. When the
tool is absent the capability reports `UNAVAILABLE` and integration tests
SKIP with a reason — never a fake success (§46).

### Dependencies
- T-0103 (COMPLETE — PEM environment detection/report),
  T-0302 (COMPLETE — evidence labels).

### Affected components
- `src/integrations/__init__.py` (new package).
- `src/integrations/jupyter.py` (new): `JUPYTER_TOOL`, `jupyter_available`,
  `NotebookError`, `JupyterUnavailable`, `build_notebook`,
  `validate_notebook`, `write_notebook`, `execute_notebook`,
  `notebook_evidence`.
- `simulations/.gitkeep` (output root for generated notebooks).
- `tests/test_integrations_jupyter.py` (new; integration test skips when
  Jupyter is absent).
- `requirements.md` (Phase 8 rows), roadmap/audit/project-state/next-task/
  chatmem/memory updates.

### Behaviour
- `jupyter_available(which=shutil.which)` returns the resolved `jupyter`
  path or `None` (injectable for tests).
- `build_notebook(cells, kernel="python3")` returns a minimal valid
  nbformat 4.5 notebook dict (each `cells` item is a code string).
- `validate_notebook(obj)` raises `NotebookError` unless the object has
  `nbformat`/`nbformat_minor`/`cells` with well-formed cell dicts.
- `write_notebook(path, notebook, overwrite=False)` writes JSON under the
  `simulations/` root, refusing to overwrite by default and refusing
  paths that escape the root.
- `execute_notebook(path, timeout=...)` runs
  `jupyter nbconvert --to notebook --execute --inplace <path>` via
  `subprocess` **when Jupyter is available**; otherwise raises
  `JupyterUnavailable`. Captures return code + output; never silently
  passes on failure.
- `notebook_evidence(notebook, result=None)` returns `EvidenceEntry`
  objects: `SIMULATED` for executed outputs (computation), `OBSERVED`
  for structural validation of the notebook itself.

### Constraints
- Standard library only (`json`, `shutil`, `subprocess`, `pathlib`);
  Jupyter is an optional external tool, never a hard dependency.
- No network; no execution of arbitrary user code unless the caller
  explicitly calls `execute_notebook` and Jupyter is present.
- Read/write confined to the repo (`simulations/`); no path escape.
- Report tool absence as `UNAVAILABLE`, not as a passing test.

### Acceptance criteria
1. `build_notebook` produces a dict accepted by `validate_notebook`.
2. `validate_notebook` rejects malformed objects with `NotebookError`.
3. `write_notebook` creates the file, refuses overwrite by default, and
   rejects path traversal outside the root.
4. `jupyter_available(lambda name: None) is None`; with an injected
   `which` returning a path, it returns that path.
5. `execute_notebook` raises `JupyterUnavailable` when Jupyter is absent
   (injected); when present it is exercised by a skipped-if-absent
   integration test.
6. `notebook_evidence` yields valid labelled `EvidenceEntry` objects
   (`SIMULATED` for execution, `OBSERVED` for structure).
7. `from src.integrations import ...` exposes the public names; full
   suite passes (`python -m pytest tests/ -v`).
8. Roadmap (T-0801 COMPLETE; T-0901 READY), requirements, project-state,
   audit (AUDIT-0022), chatmem, memory updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Live evidence: build → validate → write a notebook to `simulations/`,
  print the path and byte size; call `jupyter_available()` and record the
  real (expected `None` on this host) result; show `execute_notebook`
  raising `JupyterUnavailable` with the honest message — OBSERVED.
- Review `git status` / `git diff` before commit.
- After completion, pick the next READY task by §48 order (T-0901 FreeCAD)
  and record the reason.

### Out of scope (do not pull in)
- FreeCAD/KiCad/ngspice/Gazebo/Blender (later tasks), installing Jupyter,
  remote kernels, or any network acquisition.