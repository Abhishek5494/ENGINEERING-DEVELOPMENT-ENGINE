# Changelog

High-level, user-facing history of the Engineering Development Engine.
Per-task evidence lives in [`audit.md`](audit.md); the task graph lives in
[`roadmap.md`](roadmap.md). Dates are the recorded completion dates.

The format follows the spirit of [Keep a Changelog](https://keepachangelog.com/);
the project has not yet cut a tagged release; the current version is `0.1.0`
(unreleased).

## [Unreleased]

### Added
- **Unified offline CLI** (`python -m src`, T-2000): `version`, `env`, `tools`,
  `storage preflight`, `upstream`, `cie identify`, `rea inspect`, and
  `workflow run`, with documented exit codes (`docs/usage.md`).
- **MVP scope definition** (`docs/mvp.md`, T-2001) and consolidated docs:
  `docs/usage.md`, `docs/installation.md`, `docs/testing.md`,
  `docs/security.md`, and this changelog.
- Package version constant `src.__version__ = "0.1.0"`.

### Earlier milestones
- 2026-10-15 — **T-1900** dependency independence & self-contained deployment
  audit: `docs/dependencies.md`, `tests/test_dependency_independence.py`,
  `decisions/ADR-0004`. Confirmed the runtime is standard-library only.
- 2026-10-15 — **T-1702** governance reconciliation; storage directive
  recorded as `decisions/ADR-0003`.
- 2026-10-15 — **T-1802** owner-approved cleanup of regenerable C: caches.
- 2026-10-11 — **T-1800/T-1801** D: development-surface isolation and reusable
  storage preflight (`config/storage.json`, `src/core/storage.py`).
- 2026-10-11 — **T-0203** canonical upstream-source registry
  (`config/upstream-sources.json` + `src/core/upstream.py`).
- 2026-10-11 — **T-1700** baseline stabilisation and state reconciliation.
- 2026-10-09 — **T-0601/T-0602** Taiga-S1 resource-aware runtime selection and
  provider-neutral contracts/registry.
- 2026-10-09 — **T-0002** license decided: MIT.
- 2026-10-08 — Phases 0–12, 15–16: governance bootstrap, PEM, core primitives,
  CIE offline scope, REA, engineering-tool integrations, recovery test,
  cross-platform hardening.

### Deferred / blocked
- Live web acquisition (Scrapling, T-0501/T-0502) — install gate B-2.
- Live Taiga-S1 inference (T-1301 `ANALYZE`) — no provider wired (H-3).
- Validation/BOM pipeline (T-1401), security review (T-1501), release audit
  (T-1701) — depend on the above.
- Bundled/portable packaging — owner decision H-14.
