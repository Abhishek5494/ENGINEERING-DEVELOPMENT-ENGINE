# Testing

How the platform is tested and how to reproduce the evidence. Tests are the
primary proof of correctness (MASTER §36, §46): no claim without a test or a
recorded observation.

## Run the suite

From the repository root:

```text
python -m pytest tests/ -q
```

Expected result:

```text
483 passed, 8 skipped
```

The exact passed count grows as tasks land; the **skipped** count and reasons
are stable and explained below. On Windows, if pytest reports a `tmp`
`PermissionError` during teardown, point `TMP`/`TEMP` at a writable drive (see
[`installation.md`](installation.md)).

## Test layout

Tests live in `tests/` and mirror the subsystems. Representative suites:

| File | Covers |
|---|---|
| `test_pem_*.py` | System detection, tool detection, environment report, installer/ops. |
| `test_core_*.py` | Config, manifest, upstream registry, storage, state, evidence, xplat, recovery. |
| `test_cie_*.py` | Component model/store, target parsing, identification, provenance, conflicts. |
| `test_rea_*.py` | Pipeline, records, storage templates, offline inspection. |
| `test_taiga.py` | Provider contracts, registry, resource-aware runtime selection. |
| `test_integrations_*.py` | Jupyter, FreeCAD, KiCad, ngspice, Gazebo, Blender logic. |
| `test_orchestration.py` | Workflow stage machine and honest status. |
| `test_cli.py` | Unified CLI (T-2000). |
| `test_dependency_independence.py` | Stdlib-only imports, offline import, JSON config, no BOM. |
| `test_repo_governance.py` | Governance files and their required shape. |
| `test_recovery.py` | State reconstruction from repository evidence only. |

## Skipped tests (and why)

Eight tests skip on the current host; none is a silent failure:

- **2 × POSIX shell syntax checks** — this is a Windows host with no POSIX
  `sh`; the Linux/macOS wrapper scripts are static-verified only.
- **6 × live-tool integration tests** — FreeCAD/KiCad/ngspice/Gazebo/Blender/
  Jupyter are not installed, so live execution is `UNAVAILABLE`. The tests skip
  rather than fake a result (MASTER §46).

Every other test is a real assertion.

## What the suite guarantees

- **Governance integrity** — `next-task.md`/`project-state.md` parse and the
  repository is recoverable (`assert_recoverable`).
- **Offline-first** — every `src` module imports with optional dependencies
  absent; runtime config is JSON; no unexpected third-party import appears.
- **No fabricated data** — evidence labels are enforced and `UNKNOWN` is
  honest throughout.
- **CLI contract** — each `python -m src` command runs and returns the
  documented exit codes.

## Adding tests

- Mirror the subsystem under `tests/test_<area>_<topic>.py`.
- Prefer pure functions and `tmp_path` over real system changes.
- A test that needs an absent external tool must `pytest.skip(...)` with a
  clear reason — never assert a fabricated success.
- Keep the dependency-independence guards green: no new third-party runtime
  import, no BOM, JSON config.

See [`../roadmap.md`](../roadmap.md) for per-task validation requirements and
[`../audit.md`](../audit.md) for the recorded evidence of each task.
