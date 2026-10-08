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

## Status

**Phase 0 — Repository governance bootstrap.**
No engineering subsystems implemented yet. Current task: see
[`next-task.md`](next-task.md). Actual state: see
[`project-state.md`](project-state.md).

## Development

```bash
# run the governance test suite
python -m pytest tests/ -v
```

Cross-platform install/health scripts live in `scripts/windows/`,
`scripts/linux/`, `scripts/macos/` (Phase 1, not yet implemented).

## License

TBD — see `decisions/`. Do not assume a license until one is recorded in an
ADR.
