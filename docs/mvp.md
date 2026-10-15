# MVP Scope & Definition

This document defines the **Minimum Viable Product (MVP)** of the Engineering
Development Engine: the smallest complete, usable, verifiable product. It is
the scope contract for what is finished, what is deliberately deferred, and
how the MVP is validated.

Governance remains authoritative: [`MASTER.md`](../MASTER.md) (full vision),
[`requirements.md`](../requirements.md) (R1–R18), [`roadmap.md`](../roadmap.md)
(task graph), [`architecture.md`](../architecture.md) (design),
[`project-state.md`](../project-state.md) (actual state).

## Product purpose

An **offline-first, local-first engineering development platform** that takes
an engineering idea through research, design, simulation, optimisation,
implementation and validation by orchestrating specialised engineering tools.
It is an orchestration platform, not a chatbot. It never fabricates engineering
data: missing information is `UNKNOWN` and every claim carries an evidence
label (MASTER §5–§7, §46).

## MVP definition

> The MVP is the **runnable, tested, documented offline core**: environment
> detection and reporting; development-storage safety; the component
> intelligence data model with offline identification, provenance and
> conflict handling; the reverse-engineering offline inspection pipeline;
> Taiga-S1 provider-neutral contracts with resource-aware runtime selection;
> the unified engineering workflow that reports honest per-stage status; and
> a single command-line entry point (`python -m src`) that exposes all of it.

The functional end-to-end pipeline (live web acquisition and live AI
analysis) is **not** part of the MVP deliverable because it depends on
external resources that require owner authorisation (install gate B-2 and a
live Taiga-S1 inference provider). Those stages are implemented to the extent
possible and reported as `BLOCKED`/`UNAVAILABLE` rather than faked.

## In scope (MVP)

| Area | Deliverable | Task | Status |
|---|---|---|---|
| Core | `src/core/` config, manifest, upstream registry, storage, state, evidence, xplat, recovery | T-0202/T-0203, T-0301/T-0302, T-1601, T-1700, T-1801 | COMPLETE |
| PEM | system/tool detection, capability states, environment report, guarded installer, scripts | T-0101–T-0107, T-0201 | COMPLETE |
| CIE (offline) | component model + schema + store, exact identification, provenance, conflicts | T-0401–T-0403 | COMPLETE |
| REA | ordered pipeline, investigation records/templates, offline inspection | T-0701/T-0702 | COMPLETE |
| Taiga-S1 | provider-neutral contracts + registry, resource-aware runtime selection | T-0601/T-0602 | COMPLETE |
| Integrations | Jupyter, FreeCAD, KiCad, ngspice, Gazebo, Blender offline logic | T-0801, T-0901, T-1001/T-1002, T-1101, T-1201 | COMPLETE |
| Orchestration | unified workflow reporting honest stage status | T-1301 (partial) | PARTIAL |
| Interface | unified offline CLI (`python -m src`) | T-2000 | COMPLETE |
| Storage safety | D: development isolation + preflight | T-1800/T-1801/T-1802 | COMPLETE |
| Dependency independence | stdlib-only runtime, offline install, docs | T-1900 | COMPLETE |
| Documentation | scope, usage, installation, testing, security, changelog | T-2001 | COMPLETE |

## Out of scope (deferred / blocked)

| Deferred | Reason | Unblock |
|---|---|---|
| Live web acquisition (Scrapling, T-0501/T-0502) | Network/privileged install gate | B-2 owner approval |
| CIE cross-source search & compare (T-0404) | Depends on T-0502 | B-2 |
| Live Taiga-S1 inference (T-1301 `ANALYZE`) | No live provider wired | Provide a provider/model (H-3) |
| Live engineering-tool execution | FreeCAD/KiCad/ngspice/Gazebo/Blender/Jupyter not installed | Install tools |
| Validation/BOM pipeline (T-1401), security review (T-1501), release audit (T-1701) | Depend on the above | B-2/H-3 |
| Bundled/portable packaging | Format undecided | Owner decision H-14 |

## MVP acceptance criteria

The MVP is accepted when **all** of the following hold, each with repository
evidence (MASTER §46):

1. **Runnable** — `python -m src version` and each documented CLI command
   execute on a clean checkout with only Python 3.11+ installed.
2. **Tested** — the full suite passes; every failure is a genuine failure and
   every skip has a stated environmental reason (`docs/testing.md`).
3. **Offline** — no network access is required for core operation; the runtime
   imports with third-party packages absent (enforced by
   `tests/test_dependency_independence.py`).
4. **Documented** — installation, usage, testing and security are described
   for a new developer or agent (`docs/installation.md`, `docs/usage.md`,
   `docs/testing.md`, `docs/security.md`).
5. **Honest** — no stage claims work it did not perform; blocked capabilities
   are reported as `BLOCKED`/`UNAVAILABLE`/`UNKNOWN`.
6. **Governed** — `next-task.md` and `project-state.md` reflect reality and
   `src.core.recovery.assert_recoverable()` passes.

## How to verify the MVP

```text
python -m src version                 # runnable
python -m pytest tests/ -q            # tested
python -m src workflow run --name demo  # honest stage status
python -m src env --json              # environment detection
python -m src storage preflight build # storage safety
```

Expected: the suite is green (skips explained); the workflow reports
`PARTIALLY-VALIDATED` with `ACQUIRE`/`ANALYZE` `BLOCKED`; no command fails on a
clean machine lacking the specialist tools.

## Beyond the MVP

The long-term goals in `MASTER.md` are preserved. After B-2 and a live
Taiga-S1 provider are available, the remaining work is the live end-to-end
pipeline (T-0404 → T-1301 → T-1401), the security review (T-1501), the release
audit (T-1701), and packaging (H-14). See `docs/future-opportunities.md`.
