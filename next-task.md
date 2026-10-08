# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-1101 — Gazebo integration (robotics/physics authority)
- **State:** READY
- **Phase:** 11 — Engineering tool integrations (Gazebo = robotics/physics authority)

### Objective
Integrate Gazebo as the robotics/physics authority (MASTER §2.5/§17/§18):
load a **caller-supplied** SDF world (or URDF model) headless, run a
bounded number of simulation steps, and record the run as labelled
evidence. Gazebo performs the physics; we never fabricate simulation
results. Commands run **only when Gazebo is actually installed**; when
absent the capability reports `UNAVAILABLE` and its live test SKIPs with a
reason (§46).

### Dependencies
- T-0801 (COMPLETE — integration conventions), T-0103 (COMPLETE — PEM),
  T-0302 (COMPLETE — evidence labels).

### Affected components
- `src/integrations/gazebo.py` (new): `GAZEBO_TOOLS`, `gazebo_cli`,
  `GazeboError`, `GazeboUnavailable`, `GazeboRun`, `write_world`,
  `run_headless`, `verify_outputs`, `gazebo_evidence`.
- `src/integrations/__init__.py` (re-export new public names).
- `models/.gitkeep` (output root for worlds/models; already present).
- `tests/test_integrations_gazebo.py` (new; live test skips when Gazebo is
  absent).
- `requirements.md` (R9.x), roadmap/audit/project-state/next-task/chatmem/
  memory updates.

### Behaviour
- `gazebo_cli(which=shutil.which)` resolves `gz`/`gz.exe` (or `gazebo`/
  `gazebo.exe`) or returns `None`; injectable.
- `write_world(path, world, overwrite=False, base=...)` writes a
  caller-supplied SDF/URDF document confined to `models/` (no path escape,
  no overwrite by default).
- `run_headless(world, which=..., run=subprocess.run, iterations=...)`
  runs `gz sim -s -r --iterations <n> <world>` (server-only, headless)
  **only when available**; otherwise raises `GazeboUnavailable`. Returns
  `GazeboRun`; non-zero exit surfaced, never hidden.
- `verify_outputs(directory, names)` returns `{name: size}` and raises
  `GazeboError` when a required Gazebo-produced output is missing.
- `gazebo_evidence(operation, run=None, outputs=None)` returns
  `EvidenceEntry` objects: `SIMULATED` for the simulated run,
  `OBSERVED` for exit status and produced files.

### Constraints
- Standard library only (`shutil`, `subprocess`, `pathlib`). Gazebo is
  optional; never installed here and never a hard dependency.
- No network, no fabrication of worlds or results — inputs are
  caller-supplied; Gazebo performs the simulation.
- Writes confined to the repo (`models/`); no path escape.
- Report absence as `UNAVAILABLE` (honest skip), never a passing test.

### Acceptance criteria
1. `gazebo_cli(lambda name: None) is None`; injected `which` returns a
   path when present.
2. `write_world` writes under `models/`, refuses overwrite by default and
   rejects path traversal.
3. `run_headless` raises `GazeboUnavailable` when absent (injected); with
   injected `which` + `run` it builds a `gz sim -s -r ...` argv and
   returns `GazeboRun`.
4. `verify_outputs` returns sizes for present outputs and raises
   `GazeboError` for a missing one.
5. `gazebo_evidence` yields labelled `EvidenceEntry` (SIMULATED run,
   OBSERVED status/files).
6. `from src.integrations import ...` exposes the public names; full suite
   passes (`python -m pytest tests/ -v`).
7. A live test skips when Gazebo is absent; the reason is recorded.
8. Roadmap (T-1101 COMPLETE; T-1201 READY), requirements, project-state,
   audit (AUDIT-0026), chatmem, memory updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Live evidence: call `gazebo_cli()` (expected: Gazebo NOT installed →
  `None`); show `run_headless` refusing honestly with `GazeboUnavailable`;
  show `write_world` + `verify_outputs` on a temp file — OBSERVED, never
  claimed.
- Review `git status` / `git diff` before commit.
- After completion, pick the next READY task by §48 order (T-1201 Blender)
  and record the reason.

### Out of scope (do not pull in)
- Blender, installing Gazebo, sensor/controller code generation, robot
  kinematics authoring, or any network acquisition.