# Engineering Development Engine

**Autonomous, local-first engineering development platform.**

The Engineering Development Engine takes an engineering idea through research,
design, simulation, optimization, implementation and validation by
orchestrating specialized engineering tools — it is an engineering
orchestration platform, not an AI chatbot.

Governance for this repository is defined in [`MASTER.md`](MASTER.md).
That document is authoritative; this README is a summary.

## What this is

| Subsystem | Role |
|---|---|
| **Taiga-S1** | Local AI reasoning, planning, orchestration |
| **PEM** — Project Environment Manager | Cross-platform environment/dependency detection, installation, health checks |
| **CIE** — Component Intelligence Engine | Component research, evidence acquisition, provenance, conflict detection |
| **Scrapling** | Web acquisition/extraction engine used underneath CIE |
| **REA** — Reverse Engineering Engine | Authorized investigation of existing software behavior |
| **Engineering tools** | FreeCAD (mechanical), KiCad + ngspice (electronics), Python/Jupyter (math), Gazebo (robotics), Blender (visualization) |

## Principles (summary)

- **Truth hierarchy:** measured data > validated simulation > manufacturer
  specs > calculation > estimate > AI reasoning.
- **No fabricated engineering data.** Missing information is `UNKNOWN`.
- **Evidence classification** on every important claim
  (OBSERVED / MEASURED / MANUFACTURER-SPECIFIED / CALCULATED / SIMULATED /
  INFERRED / ASSUMED / UNKNOWN).
- **Local-first:** internet is optional, used only for component research,
  documentation, packages and authorized investigation.
- **Specialized tools stay authoritative in their domains.**
- **The repository is long-term memory:** `project-state.md` and
  `next-task.md` always reflect reality; conversation does not.

## Repository layout

See [`architecture.md`](architecture.md) for the full structure and
[`roadmap.md`](roadmap.md) for the dependency-aware task graph.

Key governance files: `MASTER.md`, `architecture.md`, `requirements.md`,
`roadmap.md`, `project-state.md`, `next-task.md`, `memory.md`, `chatmem.md`,
`audit.md`, `decisions/`, `docs/future-opportunities.md`.

### Canonical upstream-source registry

The single source of truth for the upstream repository URL of every
project-owned integration and specialist tool — plus its license and
version/commit verification status — is
[`config/upstream-sources.json`](config/upstream-sources.json)
(schema: [`config/upstream-sources.schema.json`](config/upstream-sources.schema.json);
loader: [`src/core/upstream.py`](src/core/upstream.py)). It is reference-only:
it stores URLs and verification status, never installation state, and never a
guessed version, commit or license (`null` = UNKNOWN). Tool detection and
installation metadata remain in
[`config/tool-manifest.json`](config/tool-manifest.json); entry ids in the two
files match where a tool exists. Cite the registry instead of repeating the
URL list elsewhere.

## Status

**The offline MVP is complete and operable via `python -m src`.** Phases 0–12
and 16 implemented for the offline scope; Phases 18 (storage isolation), 19
(dependency independence) and 20 (MVP CLI + documentation) complete; Phases
13/14 and the release audit remain blocked on the B-2 install gate and a live
Taiga-S1 provider. The MVP scope and acceptance criteria are in
[`docs/mvp.md`](docs/mvp.md).
PEM, CIE (offline data model/provenance — no live web acquisition yet),
REA, and the engineering-tool integrations (Python/Jupyter, FreeCAD, KiCad,
ngspice, Gazebo, Blender) are implemented; the external tools are not
installed on this host, so live execution is reported `UNAVAILABLE`, never
faked. Taiga-S1 has provider-neutral contracts plus resource-aware runtime
selection; no live inference provider is wired yet. Current task: see
[`next-task.md`](next-task.md). Actual state: see
[`project-state.md`](project-state.md) (last full suite: 483 passed,
8 skipped).

## Quick start (MVP)

Everything is offline and needs only Python 3.11+. From the repository root:

```bash
python -m src version                    # 0.1.0
python -m pytest tests/ -q               # 483 passed, 8 skipped
python -m src env --json                 # environment detection
python -m src workflow run --name demo   # honest stage status
python -m src --help                     # all commands
```

The unified CLI also exposes `tools`, `storage preflight`, `upstream`,
`cie identify` and `rea inspect`. See
[`docs/usage.md`](docs/usage.md) and [`docs/installation.md`](docs/installation.md)
for the full guide, [`docs/testing.md`](docs/testing.md) for tests, and
[`docs/security.md`](docs/security.md) for the security model.

## Development storage (Phase 18)

Development caches and workspaces are redirected to `D:\EngineeringWorkspace\`
so the Windows system drive cannot fill and interrupt development (pip/npm
cache, `HF_HOME`/`HF_HUB_CACHE`, session `TEMP`/`TMP`). A reusable storage
preflight guards expensive operations:

```powershell
. .\scripts\windows\dev-env.ps1                       # session temp/caches -> D:
python -m src.core.storage preflight dependency_install
```

See [`docs/storage.md`](docs/storage.md) and
[`decisions/ADR-0003-development-storage-isolation.md`](decisions/ADR-0003-development-storage-isolation.md).

## Dependencies & self-contained deployment (Phase 19)

The runtime is **standard-library only**: running the platform needs nothing
beyond Python 3.11+ — no required third-party package, no external database,
no service, and no network for core operation. The one third-party import
(PyYAML, for optional YAML config) is guarded and never required; JSON is the
primary config format. Every dependency is inventoried in
[`docs/dependencies.md`](docs/dependencies.md), and the property is enforced
by [`tests/test_dependency_independence.py`](tests/test_dependency_independence.py)
(stdlib-only imports, optional imports guarded, imports succeed without the
optional dependency, JSON runtime config). Recorded as
[`decisions/ADR-0004-dependency-independence.md`](decisions/ADR-0004-dependency-independence.md).
Bundling a portable/executable artifact is deferred (owner decision H-14).

## Development

```bash
# run the governance + platform test suite
python -m pytest tests/ -q
```

Cross-platform install/health scripts live in `scripts/windows/`,
`scripts/linux/`, `scripts/macos/` (Phase 1, implemented; the Windows wrappers
were executed on this host, the Linux/macOS wrappers are static-validated —
no POSIX shell here). The offline CLI is `python -m src <command>`.

## Documentation

- [`docs/mvp.md`](docs/mvp.md) — MVP scope, acceptance criteria, verification.
- [`docs/usage.md`](docs/usage.md) — how to run the platform (CLI + API).
- [`docs/installation.md`](docs/installation.md) — setup, offline, troubleshooting.
- [`docs/testing.md`](docs/testing.md) — how to run tests and what they cover.
- [`docs/security.md`](docs/security.md) — trust boundaries and safe operation.
- [`docs/dependencies.md`](docs/dependencies.md) — dependency inventory.
- [`docs/storage.md`](docs/storage.md) — development storage isolation.
- [`CHANGELOG.md`](CHANGELOG.md) — user-facing history.
- Governance: [`MASTER.md`](MASTER.md), [`requirements.md`](requirements.md),
  [`architecture.md`](architecture.md), [`roadmap.md`](roadmap.md),
  [`audit.md`](audit.md), [`decisions/`](decisions/),
  [`project-state.md`](project-state.md), [`next-task.md`](next-task.md).

## License

MIT — see [`LICENSE`](LICENSE) (applied under T-0002; third-party tool and
model terms are separate, see [`docs/license-impact.md`](docs/license-impact.md)).
