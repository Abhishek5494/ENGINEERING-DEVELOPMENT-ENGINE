# ADR-0005 — MVP scope & delivery strategy

- Date: 2026-10-15
- Status: ACCEPTED
- Tasks: T-2000 (unified CLI), T-2001 (MVP definition & docs) — Phase 20.
- Source of the decision: **owner directive** ("UNIVERSAL PROJECT AUTONOMY
  PROTOCOL"), supplied in conversation — finish the existing project to a
  complete, validated MVP without restarting or rewriting it. This directive is
  not part of `MASTER.md`; this ADR records the resulting scope decision so it
  has a repository-resolvable citation. It complements MASTER §30 (boundary),
  §46 (no fake completion) and §48 (build order).

## Context

The repository is a mature, offline-first engineering platform whose
non-blocked work is essentially complete. The functional end-to-end pipeline
depends on external resources that require owner authorisation: live web
acquisition (Scrapling, install gate B-2) and a live Taiga-S1 inference
provider (none wired). The owner asked for a finished MVP rather than another
audit, with a defined scope, a single usable interface, complete documentation,
and an honest final status.

## Problem

What is the "MVP" for a project whose headline end-to-end feature is blocked on
external authorisation, and how do we finish it without (a) faking blocked work,
(b) rewriting working code, or (c) breaking the "work only on the boundary task"
governance rule (MASTER §30)?

## Options

1. **Wait for B-2/H-3 and report only** — rejected: the owner explicitly asked
   for a finished deliverable, and there is real unblocked value to add.
2. **Implement live acquisition/analysis by faking or bypassing the gate** —
   rejected: violates MASTER §14/§46 and the autonomy boundaries.
3. **Define the MVP as the runnable, tested, documented offline core, and
   deliver its last missing pieces (a unified interface and complete docs)
   (chosen).**

## Decision

1. **MVP definition.** The MVP is the runnable, tested, documented **offline
   core**, not the live pipeline. Its exact scope, in/out table, acceptance
   criteria and verification are in `docs/mvp.md`.
2. **Interface.** Expose the existing subsystem APIs (including the flagship
   `run_workflow`) through one entry point, `python -m src` (T-2000), so a user
   or agent can operate the project from a single place. It is a thin
   dispatcher: no new behaviour, no faked stages.
3. **Documentation.** Consolidate the owner-facing/developer docs the protocol
   requires into non-duplicative files that link to governance rather than
   restate it: `docs/mvp.md`, `docs/usage.md`, `docs/installation.md`,
   `docs/testing.md`, `docs/security.md`, `CHANGELOG.md` (T-2001). Existing
   governance (`requirements.md`, `architecture.md`, `roadmap.md`, `audit.md`,
   `decisions/`) remains authoritative; no duplicate documents are created.
4. **Honesty.** Blocked/deferred capability stays visible: the workflow reports
   `BLOCKED`/`UNAVAILABLE`; the MVP is described as such; no full-project
   completion is claimed.
5. **Governance.** T-2000/T-2001 are recorded as completed tasks; the execution
   boundary remains the next eligible task, T-1701 (BLOCKED), per the existing
   precedent that completed tasks do not move the boundary.

## Rationale

- Non-destructive and additive: no existing behaviour changes; the runtime
  stays standard-library-only (ADR-0004 guards remain green).
- Delivers the owner's request with evidence (tests, runnable commands, docs)
  without crossing the install/model authorisation boundary.
- Keeps one source of truth per concern; avoids the duplication the protocol
  warns against.

## Consequences

- Positive: the project is operable from one command, installable and testable
  from its own docs, and its finished/unfinished scope is explicit.
- Neutral: the flagship live pipeline remains blocked; the MVP is honestly
  partial by design.
- Deferred: live acquisition/analysis (B-2/H-3) and packaging (H-14) remain the
  next owner-gated milestones.

## Enforcement

- `tests/test_cli.py` exercises every CLI command and its exit codes.
- `docs/mvp.md` states the acceptance criteria; `docs/testing.md` the evidence.
- `src.core.recovery.assert_recoverable()` keeps governance truthful.

## References

- Owner directive "Universal Project Autonomy Protocol".
- `docs/mvp.md`, `docs/usage.md`, `docs/installation.md`, `docs/testing.md`,
  `docs/security.md`, `CHANGELOG.md`, `src/cli.py`, `src/__main__.py`,
  `tests/test_cli.py`.
- MASTER §30 (boundary), §46 (no fake completion), §48 (build order), §54
  (release checklist); ADR-0001 (bootstrap), ADR-0003 (storage), ADR-0004
  (dependency independence).
