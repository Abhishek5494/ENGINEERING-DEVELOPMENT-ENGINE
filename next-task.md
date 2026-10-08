# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0301 — Project state persistence library
- **State:** READY
- **Phase:** 3 — Core primitives (project memory)

### Objective
Create `src/core/state.py`: a standard-library library that reads,
validates and updates the repository's own governance state
programmatically — the task states in `roadmap.md` (§31, §32), the
execution boundary in `next-task.md` (§30), and the sections of
`project-state.md` (§29). This makes state changes testable and
consistent instead of hand-edited, and lets later orchestration read
real state rather than trusting conversation (§42, §43).

### Dependencies
- T-0001 (COMPLETE), T-0202 (COMPLETE — shared paths).

### Affected components
- `src/core/state.py` (new)
- `src/core/__init__.py` (re-export the public names)
- `tests/test_core_state.py` (new)
- `requirements.md` (R1.x task-state requirement status), roadmap/audit/
  project-state/next-task/chatmem closure updates

### Data/vocabulary (exact)
- Task states (§32), exactly seven: `PLANNED`, `READY`, `IN_PROGRESS`,
  `BLOCKED`, `COMPLETE`, `DEFERRED`, `CANCELLED`.
- `project-state.md` sections (§29), the fourteen required headings:
  current phase, overall status, completed phases, current task, last
  completed task, active subsystem, blockers, known issues, architecture
  status, environment status, test status, validation status, next
  action, last update.

### Constraints
- Standard library only (`re`, `pathlib`, `dataclasses`). No new deps.
- **Round-trip safe:** reading a governance file and writing it back with
  no change must produce byte-identical text. Updating a single state
  changes only that token/cell/section; everything else is preserved
  verbatim. Implement this by editing tokens in the existing text, not by
  re-rendering the whole file.
- Invalid task-state tokens are rejected with `TaskStateError` (never
  silently coerced). `normalise_state` may accept case-insensitive input
  but returns the canonical upper-case token.
- Missing file, missing required section, or unknown task id ⇒ clear
  `TaskStateError`. Never fabricate content.
- No network, no mutation unless an explicit update function is called;
  update functions return new text (pure), with thin helpers that write
  to a path only when asked.

### Acceptance criteria
1. `src/core/state.py` exposes `TASK_STATES`, `REQUIRED_STATE_SECTIONS`,
   `TaskStateError`, `normalise_state`, `parse_roadmap_tasks`,
   `set_roadmap_task_state`, `parse_next_task`, `set_next_task_state`,
   `parse_state_sections`, `set_state_section`, `require_state_sections`.
2. `TASK_STATES` has exactly the seven §32 states; `normalise_state`
   accepts case/whitespace variants and rejects others.
3. Roadmap: `parse_roadmap_tasks` returns one record per `| T-XXXX | … |`
   row with `id`, `title`, `phase`, `dependencies`, `state`; a row with an
   invalid state raises `TaskStateError`; `set_roadmap_task_state` updates
   the table cell **and** the matching `**T-XXXX — …** — \`STATE\`` detail
   marker, is idempotent (same state ⇒ byte-identical output), and raises
   for an unknown id or invalid state.
4. next-task: `parse_next_task` returns `id`, `title`, `state` from the
   `## Task T-XXXX — …` + `- **State:** …` lines; `set_next_task_state`
   replaces only the state token and is idempotent.
5. project-state: `parse_state_sections` returns ordered `(heading, body)`
   records; `require_state_sections` raises when any of the fourteen §29
   headings is missing; `set_state_section` replaces one section body and
   preserves all others byte-for-byte.
6. Round-trip tests: for the three real repository files, parse→write with
   no change is byte-identical; a single update changes only the intended
   bytes (asserted by diffing lines).
7. All seven §32 states are accepted; at least one fabricated state (e.g.
   `DONE`) is rejected in every update function.
8. `from src.core.state import ...` works; `src/core` re-exports.
9. Full suite passes (`python -m pytest tests/ -v`).
10. Roadmap (T-0301 COMPLETE; next task per §48 order — CIE T-0401 is
    READY and is the earliest major subsystem), requirements, project-
    state, audit (new AUDIT entry), chatmem, memory updated.

### Validation requirements
- Run the full suite and record the real result in audit.md.
- Live evidence: parse the real `roadmap.md` and print the T-0302 state +
  count of tasks; parse the real `next-task.md`; list `project-state.md`
  section headings — all OBSERVED, not claimed.
- Review `git status` / `git diff` before commit.
- After completion: next READY is likely CIE T-0401 (Phase 4); record the
  §48-order reason, or T-0701 if a Phase ordering decision favours REA.

### Out of scope (do not pull in)
- Auto-committing, auto-writing the files (callers decide); parsing
  arbitrary Markdown beyond the documented patterns; CIE/REA content; any
  change to the §32 vocabulary; orchestration logic.