# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0302 — Evidence / claim classification primitives
- **State:** READY
- **Phase:** 3 — Core primitives (project memory)
- **Selected because:** both T-0301 and T-0302 are Phase 3 with deps met;
  T-0302 unblocks the critical path to CIE (T-0401) and REA (T-0701).

### Objective
Create `src/core/evidence.py`: the single, shared vocabulary for
engineering evidence used by CIE, REA and Taiga-S1 (MASTER §5, §6).
It must define exactly the eight §6 labels, a documented strength
ordering consistent with the §5 truth hierarchy, helpers to compare
labels, and a validated `Claim` record that attaches a label + source +
retrieval date to a value. Unknown/invalid labels are rejected — never
silently defaulted.

### Dependencies
- T-0001 (COMPLETE), T-0202 (COMPLETE — shared config/paths).

### Affected components
- `src/core/evidence.py` (new)
- `src/core/__init__.py` (re-export the public names)
- `tests/test_core_evidence.py` (new)
- `decisions/ADR-0002-evidence-ordering.md` (new — the §6 label ordering
  is an architectural decision because §6 lists labels but the §5
  hierarchy does not name all eight; record the mapping/rationale)
- `requirements.md` (new evidence requirement row), roadmap/audit/
  project-state/next-task/chatmem closure updates

### Exact §6 labels (canonical, verbatim)
`OBSERVED`, `MEASURED`, `MANUFACTURER-SPECIFIED`, `CALCULATED`,
`SIMULATED`, `INFERRED`, `ASSUMED`, `UNKNOWN`.
There are exactly eight; no additions, no aliases that change meaning.

### Constraints
- Standard library only. Case-insensitive / underscore-vs-hyphen input
  may be normalised on input, but stored/exposed labels are canonical.
- The strength ordering must be documented and justified against §5.
  Proposed (strongest → weakest), to be recorded in ADR-0002:
  MEASURED > OBSERVED > SIMULATED > MANUFACTURER-SPECIFIED >
  CALCULATED > ASSUMED > INFERRED > UNKNOWN.
  (`ASSUMED` above `INFERRED` follows §5: empirical estimates precede AI
  reasoning; OBSERVED is placed as direct first-hand evidence just below
  measured physical data.) An invalid label is never given a rank.
- Honesty: a claim labelled UNKNOWN carries no value claim (value must be
  `None`); presenting an inference as observation must be impossible
  through these primitives (the label is explicit and required).
- No network, no file I/O, no side effects at import.

### Acceptance criteria
1. `src/core/evidence.py` exposes `EVIDENCE_LABELS` (a length-8 tuple of
   the canonical labels in a stable order), an `EvidenceLabel` type
   (enum), `EvidenceError`, `parse_label`, `rank`, `is_stronger`,
   `compare`, `strongest`, and a `Claim` record.
2. `parse_label` accepts canonical labels (and normalised forms) and
   rejects anything else with `EvidenceError` (test covers a fabricated
   label such as `"INSTALLED"` and empty/`None`). Roadmap acceptance
   criterion: enum of exactly the eight labels.
3. `rank`/`is_stronger`/`compare` implement the ADR-0002 order with tests
   for each adjacent pair and a documented total order. Roadmap
   acceptance criterion: ordering enforced.
4. `Claim` stores `field`/`value`/`label`/`source`/`retrieved_at`/
   `note`; constructing with an invalid label raises `EvidenceError`
   (roadmap criterion: invalid labels rejected); a non-UNKNOWN claim
   with `value is None` raises (no fabricated data, §7); an UNKNOWN claim
   carries no value; claims serialize to a plain dict (JSON-ready).
5. `strongest(claims)` returns the highest-strength claim and is
   stable/tie-broken by input order; empty input → `None`.
6. `from src.core.evidence import ...` works; `src/core` re-exports.
7. Full suite passes (`python -m pytest tests/ -v`).
8. ADR-0002 + roadmap (T-0302 COMPLETE, next → T-0301 or CIE start per
   §48 order), requirements, project-state, audit (new AUDIT entry),
   chatmem, memory updated.

### Validation requirements
- Run the full suite and record the real result in audit.md.
- Live evidence: build/compare a couple of claims in a one-off command
  and record the observed ordering (OBSERVED, not claimed).
- Review `git status` / `git diff` before commit.
- After completion: next READY is T-0301 (state persistence) — then CIE
  (T-0401) which depends on T-0302. Select by §48 phase order and record
  the reason.

### Out of scope (do not pull in)
- Persisting claims/evidence to disk (that is CIE/REA storage,
  T-0401/T-0701 and REA storage tasks); source-priority ranking (§10)
  and conflict handling (§11) are CIE tasks (T-0403); no network, no
  scraping, no state-file parsing.