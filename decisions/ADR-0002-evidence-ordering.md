# ADR-0002 — Evidence strength ordering

- Date: 2026-10-08
- Status: ACCEPTED
- Task: T-0302 (Phase 3)

## Context

MASTER §6 defines exactly eight evidence classes (OBSERVED, MEASURED,
MANUFACTURER-SPECIFIED, CALCULATED, SIMULATED, INFERRED, ASSUMED,
UNKNOWN) but does not give them a numeric order. MASTER §5 defines a
truth hierarchy by *source type*:

1. Measured physical data
2. Validated simulation
3. Manufacturer specifications
4. Deterministic calculations
5. Empirical estimates
6. AI reasoning

CIE, REA and Taiga-S1 need one shared, enforceable ordering so that a
weaker claim never silently overrides a stronger one (§33 requires
evidence-driven decisions). Without a single ordering, each subsystem
could rank conflicting claims differently.

## Problem

How should the eight §6 labels be ordered so that "strongest evidence
wins" is deterministic and consistent with §5, given that the two lists
do not map one-to-one?

## Options

1. **Expose no ordering** — let callers decide. Rejected: guarantees
   divergent conflict resolution between subsystems (§16, §51).
2. **Total order mapped to §5 (chosen).** Anchor each label to the
   nearest §5 tier and document the two judgement calls.
3. **Treat OBSERVED as strictly strongest.** Rejected: §5 explicitly
   ranks *measured physical data* first, and measurement is a stronger
   form of observation.

## Decision

Strongest → weakest, encoded in `src/core/evidence.py` (`EVIDENCE_LABELS`,
`rank`):

    MEASURED > OBSERVED > SIMULATED > MANUFACTURER-SPECIFIED
             > CALCULATED > ASSUMED > INFERRED > UNKNOWN

- MEASURED = §5.1, SIMULATED = §5.2, MANUFACTURER-SPECIFIED = §5.3,
  CALCULATED = §5.4, ASSUMED = §5.5 (empirical estimates), INFERRED =
  §5.6 (AI reasoning), UNKNOWN = no evidence (weakest).
- OBSERVED is placed second, directly beneath MEASURED: it is direct,
  first-hand evidence (e.g. a tool probe result or a value read from a
  page) — the raw material from which measurements are formed, but
  without the rigour of a measurement.
- ASSUMED is placed above INFERRED because §5 ranks empirical estimates
  (5) before AI reasoning (6); a stated assumption at least declares its
  basis, whereas inference is derived reasoning.

## Rationale

- Keeps one deterministic total order shared by every subsystem.
- Every tier is traceable to §5; the two placements that §5 does not
  state explicitly (OBSERVED, INFERRED/ASSUMED relative order) are
  documented here so they can be reviewed rather than guessed.
- Reversing §5 (putting AI reasoning above measurement) is impossible:
  the ordering enforces the §5 mandate that AI reasoning never overrides
  measured/validated evidence.

## Consequences

- Positive: `strongest()`, `is_stronger()` and conflict resolution have a
  single defined meaning platform-wide.
- Negative: two placements are judgement calls; if MASTER is clarified,
  this ADR is superseded and `EVIDENCE_LABELS`/`_RANK` change once.
- Not affected: labels remain exactly the eight §6 strings; this ADR adds
  only their relative strength, never a new label.

## Rejected alternatives

- Option 1 (no order) — permits inconsistent conflict resolution.
- Option 3 (OBSERVED first) — contradicts §5.1.