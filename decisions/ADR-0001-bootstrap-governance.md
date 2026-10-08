# ADR-0001 — Initial repository bootstrap and governance baseline

- Date: 2026-10-08
- Status: ACCEPTED
- Task: T-0001 (Phase 0)

## Context

The repository at `project/` was completely empty: no files, no Git
history, no prior implementation. MASTER.md (supplied as the governing
prompt) defines the target platform and requires, for a new repository
(§47), that governance files, directory structure and a dependency-aware
task graph be established before any feature work.

## Problem

How do we bootstrap an empty directory into a governed engineering
repository without over-building, fabricating status, or losing the
ability to recover after conversation loss?

## Options

1. **Governance-first bootstrap (chosen):** write all §27 memory files +
   §28 structure + Git baseline + a governance test, then stop; feature
   work proceeds one roadmap task at a time.
2. Scaffold generators / full project template: generate all subsystem
   skeletons and CI config immediately. Rejected: uncontrolled large
   change, fabricates structure for non-existent subsystems (§47 "smallest
   safe foundation").
3. Build PEM first, document later. Rejected: violates §47 ordering and
   §27 persistent-memory requirement; state would be conversational only.

## Decision

- Option 1. Store MASTER.md verbatim in the repository (user-approved).
- Initialize Git and commit the bootstrap as the baseline commit
  (user-approved) so §40 history/rollback works from commit #1.
- Implementation language: Python 3 (3.13.5 observed available);
  tests via pytest (9.1.1 observed available).
- `environment.json` is machine-specific and gitignored; governance
  files are tracked.
- License left undecided → separate task T-0002, blocked on human
  approval (§35).

## Rationale

- §47 mandates governance-first bootstrap on a new repository.
- Persisting MASTER.md, state and roadmap in-repo satisfies §42/§43
  (survive conversation loss; repository beats conversation).
- A governance test makes "documentation exists" checkable rather than
  aspirational (§36, §46).

## Consequences

- Positive: recoverable, auditable, testable baseline; clear execution
  boundary via next-task.md.
- Negative: no engineering capability yet; roadmap is a plan, not
  evidence of implementation.
- Risks: roadmap detail for later phases may drift as evidence arrives —
  change log in roadmap.md and new ADRs required for architectural
  changes (§31, §39).

## Rejected alternatives

- Option 2 (big-bang scaffold) — violates §47 and §58.
- Option 3 (code first) — leaves no persistent project state.
