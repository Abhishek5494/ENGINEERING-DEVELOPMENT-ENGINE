# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.
Format follows MASTER §27/§30 and is parsed by `src/core/state.py`
(`parse_next_task`); keep exactly one `## Task T-XXXX — …` header and one
`- **State:** …` line.

## Task T-1701 — Release audit vs MASTER §54 checklist
- **State:** BLOCKED
- **Phase:** 17 — Release + final audit

### Project state (summary)
All non-blocked work is COMPLETE (Phases 0–12, 16, 18, 19, 20; T-0002 MIT;
T-0601/T-0602 Taiga-S1; T-1502; T-1601; T-1700; T-1702; T-0203 upstream
registry; T-1800/T-1801 storage isolation; T-1802 cleanup; T-1900 dependency
independence & self-contained deployment; T-2000 unified offline CLI; T-2001
MVP definition & consolidated docs). The offline MVP is complete and operable
via `python -m src`. Suite: 483 passed, 8 skipped (491 collected). No READY
task exists. The autonomous build stopped at this boundary per MASTER §44/§48.

### Objective
Walk the MASTER §54 release checklist and produce a release audit that makes no claim without evidence (§46).

### Why this is next
It is the only remaining task in §48 order that is not COMPLETE; everything
earlier in the phase order is done or blocked on it. Its dependencies
(T-1401/T-1501) are themselves blocked on the B-2 install gate.

### Dependencies
- T-1401 (BLOCKED), T-1501 (BLOCKED), T-1502 (COMPLETE), T-1601 (COMPLETE), T-1700 (COMPLETE).

### Preconditions / Affected components
- Preconditions: T-1401 and T-1501 COMPLETE.
- Affected: `docs/release-audit.md` or a new `audit.md` section.

### Constraints
- No claim lacking repository artefacts; release only if every item is met.

### Acceptance criteria (when unblocked)
1. Every §54 checklist item marked with evidence or explicit unmet.
2. No claim lacking a repository artefact.
3. Tagging/release only if all items are met.

### Validation requirements
- N/A while BLOCKED.

### Do NOT change
- Do not mark any blocked task COMPLETE or fake a release (§46).
- Do not restructure this file's `## Task` header / `State:` line (parser contract).
- Do not perform installs/downloads/network access (B-2 gate).

### Blocker resolution
- T-1401 needs T-1301, which needs T-0404 → T-0502 → T-0501 (install gate B-2).
- T-1501 needs T-0502 (same B-2 install gate).
- **B-1 RESOLVED:** Taiga-S1 upstream verified; T-0601/T-0602 COMPLETE (`src/taiga/runtime.py`, `contracts.py`, `registry.py`). A live Taiga-S1 inference provider is still not wired, so T-1301's ANALYZE stage remains honestly BLOCKED until one is supplied.
- **B-2 (open):** approve network/privileged installs and raise C:\ above the 1 GiB threshold → unblocks T-0501 → T-0502 → T-0404 → T-1301 → T-1401/T-1501 → T-1701.
- **C: protection:** T-1800/T-1801 COMPLETE; T-1802 COMPLETE (owner-approved narrow cache cleanup); the storage directive is recorded as `decisions/ADR-0003-development-storage-isolation.md` (T-1702).
- **Dependency independence:** T-1900 COMPLETE (dependency inventory `docs/dependencies.md`; enforced by `tests/test_dependency_independence.py`; directive recorded as `decisions/ADR-0004-dependency-independence.md`). Building a bundled/portable artifact awaits owner decision H-14.
- **MVP operability & docs:** T-2000/T-2001 COMPLETE (unified offline CLI `python -m src`; `docs/mvp.md` + usage/installation/testing/security/CHANGELOG; decision recorded as `decisions/ADR-0005-mvp-scope-and-delivery.md`). The offline MVP is complete; the live pipeline stays BLOCKED (B-2/H-3).

### Following task
None. T-1701 (when eventually COMPLETE) is the final task in the roadmap; after it, a release may be tagged only if every §54 item is met.
