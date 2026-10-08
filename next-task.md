# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-0101 — PEM system/hardware detection
- **State:** READY
- **Phase:** 1 — Project Environment Manager

### Objective
Implement the first slice of the Project Environment Manager in
`src/pem/`: cross-platform detection of OS, OS version, CPU,
architecture, RAM, storage, and GPU/VRAM where detectable, returning a
structured record whose every field is either evidence-backed or
explicitly UNKNOWN (MASTER §22, §7).

### Dependencies
- T-0001 (COMPLETE) — governance repository exists.

### Affected components
- `src/pem/` (new module, e.g. `detect.py` + package `__init__.py`)
- `tests/test_pem_detection.py` (new)
- `memory.md` (record durable environment findings)
- Documentation: PEM section in `architecture.md` status line only if
  scope differs — do not rewrite architecture silently (§39).

### Constraints
- Detection only — NO installation, NO network, NO external services.
- stdlib-first (platform, os, shutil, subprocess); a third-party lib
  (e.g. psutil) is allowed only if justified in the commit message and
  pinned in `requirements-dev`/docs.
- Never fabricate a value: undetectable fields must be UNKNOWN, not
  guessed (§7). Never claim a tool is installed (§25) — tool detection
  is T-0102, not this task.
- Resource-light: no long-running scans (§38).
- Keep scope tight: do not implement report generation (T-0103) or
  manifest-driven tool detection (T-0102) here.

### Acceptance criteria
1. `src/pem/detect.py` exposes a function (e.g. `detect_system()`)
   returning a JSON-serializable dict with keys: `os_name`, `os_version`,
   `cpu`, `architecture`, `ram_bytes`, `storage` (total/free per volume),
   `gpu` (list), each carrying `value` + `evidence` label or
   `value: "UNKNOWN"`.
2. Runs successfully on the current Windows host and returns OS name,
   OS version, architecture, RAM.
3. Unit tests cover: happy path on this machine, JSON serializability,
   UNKNOWN handling for undetectable fields (mocked), no empty-string
   values.
4. `python -m pytest tests/ -v` passes including pre-existing governance
   tests.
5. Architecture: module importable as `from src.pem.detect import
   detect_system` (package `__init__.py` files present as needed).

### Validation requirements
- Execute `python -m pytest tests/ -v`; record real result in audit.md.
- Run the detector once on this host and paste a sanitized summary into
  audit.md as OBSERVED evidence.
- Review `git status` / `git diff` before commit; commit message states
  what was tested.
- After completion: update roadmap (T-0101 → COMPLETE), project-state.md,
  audit.md, and rewrite this file for the next READY task
  (expected: T-0201 tool manifest, since T-0102 depends on it).

### Out of scope (do not pull in)
- environment.json/report (T-0103), tool/version detection (T-0102),
  installers (T-0104+), GPU benchmarking, any engineering-tool probing
  beyond what the system detector inherently reports.
