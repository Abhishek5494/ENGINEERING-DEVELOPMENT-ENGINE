# ADR-0004 — Dependency independence & self-contained deployment

- Date: 2026-10-15
- Status: ACCEPTED
- Task: T-1900 (Phase 19).
- Source of the decision: **owner directive** ("DEPENDENCY INDEPENDENCE &
  SELF-CONTAINED DEPLOYMENT"), supplied in conversation. This directive is
  not part of `MASTER.md`; this ADR records it so its rules have a
  repository-resolvable citation. It complements MASTER §26 (offline-first),
  §38 (resource awareness) and §49 (interoperability), and ADR-0003
  (development storage isolation).

## Context

The platform must be easy to set up, run, test, and deploy on a fresh
compatible system without users manually installing frameworks, runtimes, or
supporting components. It already happens to be standard-library-only, but
that property was **undocumented and unenforced** — a future change could
silently introduce a mandatory third-party dependency, a network call at
import time, or a requirement for a YAML parser, and nothing would catch it.

## Problem

How do we make dependency independence an **architectural requirement** that
is documented, verified, and preserved — without rewriting the working
project or introducing new dependencies to achieve it?

## Options

1. **Do nothing** — rejected: the strong runtime property would remain
   implicit and fragile.
2. **Bundle a Python runtime / build a one-file executable now** — rejected:
   adds a build-time dependency (PyInstaller) and an owner decision on target
   format; not needed to satisfy the goal (the source distribution is already
   self-contained).
3. **Audit + document + enforce with tests; defer bundling (chosen).**
   Non-destructive; records the inventory; turns the property into executable
   guards; leaves packaging as a separate, owner-gated decision.

## Decision

Adopt the owner dependency-independence directive. Its rules:

### §1 — Inventory every dependency
Classify runtime/interpreter, third-party libraries, system packages, external
executables, databases/services, network APIs, AI models/runtimes, build/dev
dependencies, and optional integrations; record required/optional/bundled/
downloadable/replaceable. Delivered as `docs/dependencies.md`.

### §2 — Minimise external installation
Prefer the standard library and existing internal implementations; never add a
third-party dependency without documented justification. The runtime stays
standard-library-only.

### §3 — Offline-first
Core operation must not require the internet; network use is confined to
optional, documented capabilities (MASTER §26). The whole `src` package must
import with optional dependencies removed.

### §4 — Packaging strategy
Prefer the simplest format that meets the goal: a source/portable
distribution (already self-contained). Bundled executables are optional and
deferred to a separate, owner-gated task.

### §5 — Fresh-system validation
Verify in a clean environment without relying on undeclared machine state;
distinguish VERIFIED from UNVERIFIED results honestly.

### §6 — Acceptance criteria
All runtime dependencies inventoried and documented; unnecessary installations
removed/justified; required dependencies bundled, auto-provisioned, or clearly
documented; clean-environment operation; offline/network documented and tested;
licenses respected; packaging instructions and validation tests kept in the
repo.

### §7 — Incremental, non-destructive
Treat this as an architectural requirement to implement incrementally, not as
permission to rewrite the project.

## Rationale

- Non-destructive: documentation + tests only; no runtime behaviour changed.
- Honest and enforceable: `tests/test_dependency_independence.py` fails if a
  non-stdlib import, an unguarded optional import, a mandatory YAML config, or
  a stray BOM appears.
- Matches the project's existing policy of evidenced, test-backed claims
  (MASTER §46).

## Consequences

- Positive: the self-contained property is now explicit, documented, and
  guarded; a fresh machine needs only Python 3.11+ to run the core platform.
- Negative: adding a legitimate third-party dependency now requires updating
  the allowlist/inventory and justifying it — intentional friction.
- Deferred: building a bundled/portable artifact (options 3/4 above) and the
  choice of distribution format (human input H-14).

## Enforcement

- `tests/test_dependency_independence.py`: stdlib-only imports, guarded
  optional imports, import-without-optional-dependency, JSON runtime config,
  no BOM, and the presence/coverage of `docs/dependencies.md`.
- `docs/dependencies.md`: the authoritative inventory and policy.

## References

- Owner directive "Dependency independence & self-contained deployment".
- `docs/dependencies.md`, `tests/test_dependency_independence.py`,
  `requirements.md` (R18), `src/core/config.py` (optional PyYAML),
  `config/upstream-sources.json`, `config/tool-manifest.json`.
- MASTER §26 (offline-first), §38 (resources), §49 (interoperability), §46
  (no fake completion); ADR-0001 (bootstrap), ADR-0003 (storage isolation).
