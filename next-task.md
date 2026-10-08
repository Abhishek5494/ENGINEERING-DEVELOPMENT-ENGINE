# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0702 — REA tooling integration (inspect/trace)
- **State:** READY
- **Phase:** 7 — Reverse Engineering Engine (REA)

### Objective
Give the REA pipeline real, offline inspection capability (MASTER §18
`INSPECT` / `COLLECT EVIDENCE`): fingerprint a **caller-provided,
authorized** file (size, hashes, detected file type, printable strings),
probe which external inspection tools are actually available, and record
the results as labelled `EvidenceEntry` objects on an `Investigation`.
The target is only *read* — never executed. Everything is stdlib-first;
external tools are optional and honestly reported when absent.

### Dependencies
- T-0701 (COMPLETE — pipeline + investigation records + storage),
  T-0302 (COMPLETE — evidence labels).

### Affected components
- `src/rea/inspection.py` (new): `FileFingerprint`, `fingerprint_file`,
  `detect_file_type`, `extract_strings`, `probe_tools`, `inspect_target`,
  `InspectionError`.
- `src/rea/records.py` (extend): reuse `EvidenceEntry`; add a helper
  `with_evidence(investigation, entries, unknowns=(), behavior_notes=())`
  that returns a new `Investigation` with appended evidence.
- `src/rea/__init__.py` (re-export new public names).
- `tests/test_rea_inspection.py` (new).
- `requirements.md` (R7.x), roadmap/audit/project-state/next-task/chatmem/
  memory updates.

### Behaviour
- `detect_file_type(head)` recognises at least PE (`MZ`), ELF (`\x7fELF`),
  Mach-O, ZIP, and PDF from magic bytes; otherwise `"UNKNOWN"`.
- `extract_strings(data, min_length=4, max_strings=...)` returns printable
  ASCII runs (stdlib, bounded) — the target's own bytes are treated as
  data.
- `fingerprint_file(path)` returns size + sha256 (+ md5) + file type +
  bounded string count; it refuses directories/missing files with
  `InspectionError`.
- `probe_tools(names)` maps a tool-name list to resolved paths via
  `shutil.which` (missing → `None`), so an investigation never claims a
  tool it does not have.
- `inspect_target(path, tools=None)` returns a tuple of `EvidenceEntry`
  (all `OBSERVED`): file identity (path, size), sha256, detected type,
  string count, and one entry per probed tool reporting present/absent.
- `with_evidence(...)` composes an updated `Investigation`.

### Constraints
- Standard library only (`hashlib`, `shutil`, `struct`, `pathlib`, `re`).
  No network, no execution of the target, no disassembly performed here —
  external tools are only *detected*, not run, in this task.
- Never claim a tool result that was not produced (§46): absent tools are
  reported as absent/UNKNOWN, not assumed.
- Read at most a bounded prefix/size (default 16 MiB) and record the cap
  as a limitation rather than silently truncating.
- Only operate on a path the caller passes; no directory walking of the
  system, no secret extraction (§20).

### Acceptance criteria
1. `detect_file_type` classifies PE/ELF/Mach-O/ZIP/PDF and returns
   `"UNKNOWN"` for arbitrary bytes.
2. `extract_strings` finds embedded ASCII strings and respects
   `min_length`/`max_strings`.
3. `fingerprint_file` returns a `FileFingerprint` with the correct size
   and a stable sha256 (verified against `hashlib` on a temp file) and the
   detected type; missing file / directory raises `InspectionError`.
4. `probe_tools` returns a path for an existing tool (e.g. `python`) and
   `None` for a bogus name.
5. `inspect_target` returns `OBSERVED` `EvidenceEntry` objects covering
   identity, sha256, type, string count and tool availability; every entry
   is a valid `EvidenceEntry`.
6. `with_evidence` returns a new `Investigation` whose evidence is the old
   plus the new, leaving the original unchanged.
7. `from src.rea import ...` exposes the new names; full suite passes
   (`python -m pytest tests/ -v`).
8. Roadmap (T-0702 COMPLETE; T-0801 READY), requirements, project-state,
   audit (AUDIT-0021), chatmem, memory updated.

### Validation requirements
- Run the full suite; record the real result in audit.md.
- Live evidence: fingerprint a temp file with known bytes, print its type,
  size and sha256, and show `inspect_target` producing evidence entries;
  show `probe_tools(["python", "definitely-not-a-tool-xyz"])` resolving one
  and not the other — OBSERVED, not claimed.
- Review `git status` / `git diff` before commit.
- After completion, pick the next READY task by §48 order (T-0801 Python/
  Jupyter is Phase 8 and READY) and record the reason.

### Out of scope (do not pull in)
- Running/disassembling/executing targets, dynamic tracing, debugging,
  attaching to processes (a later, separately-authorized capability),
  Taiga orchestration, engineering integrations. No CLI/UI.