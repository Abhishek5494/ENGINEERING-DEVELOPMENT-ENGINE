# Roadmap — Engineering Development Engine

Dependency-aware task graph derived from `MASTER.md` §31, §32, §48.
States: `PLANNED | READY | IN_PROGRESS | BLOCKED | COMPLETE | DEFERRED | CANCELLED`.
Rule: never execute a task whose dependencies are incomplete (MASTER §32).

Last updated: TASK-0001 (bootstrap).

---

## Task status summary

| ID | Title | Phase | Deps | State |
|---|---|---|---|---|
| T-0001 | Repository governance bootstrap | 0 | — | COMPLETE |
| T-0002 | License decision | 0 | T-0001 | BLOCKED (needs human approval, MASTER §35) |
| T-0101 | PEM system/hardware detection | 1 | T-0001 | COMPLETE |
| T-0102 | PEM tool detection + capability states | 1 | T-0101, T-0201 | COMPLETE |
| T-0103 | Environment report generation (environment.json + md) | 1 | T-0102 | COMPLETE |
| T-0104 | Windows scripts (install/update/healthcheck) | 1 | T-0103 | COMPLETE |
| T-0105 | Linux scripts (install/update/healthcheck) | 1 | T-0103 | COMPLETE |
| T-0106 | macOS scripts (install/update/healthcheck) | 1 | T-0103 | COMPLETE |
| T-0107 | Idempotent install logic + tests | 1 | T-0103 | COMPLETE |
| T-0201 | Tool manifest schema + config/tool-manifest.json + loader | 2 | T-0001 | COMPLETE |
| T-0202 | Shared configuration module | 2 | T-0001 | COMPLETE |
| T-0301 | Project state persistence library | 3 | T-0001, T-0202 | READY |
| T-0302 | Evidence/claim classification primitives | 3 | T-0001, T-0202 | COMPLETE |
| T-0401 | Component data model + schema + storage | 4 | T-0302 | READY |
| T-0402 | CIE URL ingestion + exact-identification flow | 4 | T-0401 | PLANNED |
| T-0403 | Provenance + source priority + conflict detection | 4 | T-0401 | PLANNED |
| T-0404 | Authoritative source search + cross-source compare | 4 | T-0402, T-0502 | PLANNED |
| T-0501 | Inspect installed Scrapling + pin dependency | 5 | T-0001 | PLANNED |
| T-0502 | Scrapling acquisition→sanitization→extraction under CIE | 5 | T-0501, T-0401 | PLANNED |
| T-0601 | Taiga-S1 runtime selection + resource awareness | 6 | T-0103, T-0301 | BLOCKED (Taiga-S1 upstream repo not supplied) |
| T-0602 | Taiga-S1 orchestration core (task routing) | 6 | T-0601, T-0301, T-0403 | BLOCKED (depends on T-0601) |
| T-0701 | REA pipeline + investigation record templates | 7 | T-0302 | READY |
| T-0702 | REA tooling integration (inspect/trace) | 7 | T-0701 | PLANNED |
| T-0801 | Python/Jupyter integration | 8 | T-0103 | PLANNED |
| T-0901 | FreeCAD integration | 9 | T-0801 | PLANNED |
| T-1001 | KiCad integration | 10 | T-0801 | PLANNED |
| T-1002 | ngspice integration | 10 | T-0801 | PLANNED |
| T-1101 | Gazebo integration | 11 | T-0801 | PLANNED |
| T-1201 | Blender integration | 12 | T-0801 | PLANNED |
| T-1301 | Unified engineering workflow (IDEA → validation) | 13 | T-0602, T-0404, T-0702, T-0901, T-1001, T-1002, T-1101, T-1201 | PLANNED |
| T-1401 | Simulation / validation / BOM pipeline | 14 | T-1301 | PLANNED |
| T-1501 | Security review + untrusted-input hardening | 15 | T-0502, T-0403 | PLANNED |
| T-1502 | Recovery-after-interruption test | 15 | T-0301 | PLANNED |
| T-1601 | Cross-platform hardening | 16 | T-0104, T-0105, T-0106 | PLANNED |
| T-1701 | Release audit vs MASTER §54 checklist | 17 | T-1401, T-1501, T-1502, T-1601 | PLANNED |

---

## Task details

### PHASE 0 — Repository + governance

**T-0001 — Repository governance bootstrap** — `IN_PROGRESS`
- Objective: establish all §27 governance files, §28 directory structure, Git baseline, and a governance verification test on an empty repository.
- Dependencies: none.
- Affected components: repo root, `docs/`, `decisions/`, `tests/`, `scripts/`, `src/`, `config/`.
- Constraints: no feature code (PEM/CIE/REA/Taiga); no invented engineering data; MASTER.md stored verbatim; minimal safe foundation only (§47).
- Acceptance criteria: all §27 files exist with substantive content; §28 directory skeleton present; `roadmap.md` contains dependency-aware task graph; `next-task.md` populated with first unblocked task; governance test passes; baseline committed; `project-state.md` truthful.
- Validation: `python -m pytest tests/ -v` green; `git status` clean after commit; `git log` shows baseline.

**T-0002 — License decision** — `BLOCKED`
- Objective: choose and record an open-source license.
- Dependencies: T-0001. Blocker: requires human approval (MASTER §35, major licensing decision).
- Affected components: LICENSE, README, ADR.
- Constraints: do not assume a license without an ADR.
- Acceptance criteria: ADR-0002 records decision; LICENSE file present if approved.
- Validation: governance test updated to require LICENSE once decision made.

### PHASE 1 — Project Environment Manager

**T-0101 — PEM system/hardware detection** — `READY`
- Objective: `src/pem/` detects OS, OS version, CPU, architecture, RAM, storage (and GPU/VRAM where detectable) using stdlib-first, cross-platform code.
- Dependencies: T-0001. Affected: `src/pem/`, `tests/`.
- Constraints: no external services; detection only — no installation; never claim unavailable data (UNKNOWN); resource-light (§38).
- Acceptance criteria: returns structured record with evidence-backed values on Windows; degrades gracefully when a field is undetectable.
- Validation: unit tests with mocked/real detection; `python -m pytest`.

**T-0102 — PEM tool detection + capability states** — `PLANNED`
- Objective: detect installed tools/versions/paths from `config/tool-manifest.json`; map to capability states READY/LIMITED/UNAVAILABLE/UNKNOWN (§22, §24).
- Dependencies: T-0101, T-0201. Affected: `src/pem/`, `config/`.
- Constraints: manifest-driven, no hard-coded dependency list; never claim installed without detection evidence.
- Acceptance criteria: detects Git + Python on this machine with correct versions; unknown tools reported UNAVAILABLE/UNKNOWN.
- Validation: unit tests; integration test against real machine for Git/Python.

**T-0103 — Environment report generation** — `COMPLETE`
- Objective: emit `environment.json` (gitignored) and `environment-report.md` per §25 including warnings/limitations/recommendations.
- Dependencies: T-0102. Affected: `src/pem/`, `.gitignore`.
- Constraints: never fabricate tool status; report must be regenerable (idempotent).
- Acceptance criteria: both outputs generated; JSON schema-validated; report lists missing dependencies honestly.
- Validation: tests assert schema, honesty rules (tool present iff detection says so).

**T-0104/0105/0106 — Platform scripts (Windows/Linux/macOS)** — `T-0104 COMPLETE; T-0105 COMPLETE; T-0106 COMPLETE`
- Objective: `scripts/<platform>/{install,update,healthcheck}` thin wrappers over shared Python (§23).
- Dependencies: T-0103. Constraints: platform auto-detection; no duplicated business logic.
- Acceptance criteria: each script exists, is syntactically valid, calls shared code, exits nonzero on failed health check.
- Validation: Windows scripts executed on this machine; Linux/macOS scripts static-validated only (no POSIX shell on this host) — no claim of execution.

**T-0107 — Idempotent install logic + tests** — `COMPLETE`
- Objective: install missing dependencies only when absent or version-below-minimum; re-run safe (§22).
- Dependencies: T-0103. Acceptance criteria: second run performs zero changes when healthy.
- Validation: test harness simulating present/absent tool states (17 installer tests); live plan + refusal evidence in AUDIT-0010.

### PHASE 2 — Configuration + tool registry

**T-0201 — Tool manifest schema + manifest + loader** — `READY`
- Objective: JSON schema covering §24 fields; `config/tool-manifest.json` entries for Git, Python, Jupyter, Taiga-S1, FreeCAD, KiCad, ngspice, Gazebo, Blender, REA, Scrapling; validated loader.
- Dependencies: T-0001. Constraints: versions UNKNOWN unless known — record MIN/PREFERRED only where justifiable; detection method must be executable.
- Acceptance criteria: manifest validates against schema; loader rejects malformed entries; all 11 tools present.
- Validation: pytest schema/round-trip tests.

**T-0202 — Shared configuration module** — `COMPLETE`
- Objective: `src/core/config.py` — paths, config loading (JSON/YAML-if-available), single source for subsystems (§49).
- Dependencies: T-0001. Acceptance criteria: resolves repo root deterministically; loads config with defaults.
- Validation: unit tests (19 new tests pass; full suite 183 passed, 2 skipped).

### PHASE 3 — Project memory

**T-0301 — Project state persistence library** — `PLANNED`
- Objective: parse/validate/update `project-state.md`, `next-task.md`, `roadmap.md` task states programmatically (§29, §30, §32).
- Dependencies: T-0001, T-0202. Acceptance criteria: read + write round-trip; rejects invalid task states.
- Validation: pytest round-trip tests.

**T-0302 — Evidence/claim classification primitives** — `COMPLETE`
- Objective: `src/core/evidence.py` — evidence labels (§6), truth-hierarchy ordering (§5), claim record structure; used by CIE/REA/Taiga.
- Dependencies: T-0001, T-0202. Acceptance criteria: enum of exactly the eight labels; ordering enforced; invalid labels rejected.
- Validation: pytest (29 new tests pass; full suite 212 passed, 2 skipped). Ordering recorded in ADR-0002.

### PHASE 4 — Component Intelligence Engine

**T-0401 — Component data model + schema + storage** — `PLANNED`: JSON schema of §12/§13 fields; SQLite/JSON store; UNKNOWN for missing; no padding fields. Validation: schema tests + store round-trip.
**T-0402 — URL ingestion + exact identification** — `PLANNED`: accepts exact product URL; identifies title/manufacturer/model/SKU/MPN/seller/specs before any generic search (§8). Validation: fixture-based tests with recorded public pages (no live network in tests).
**T-0403 — Provenance + source priority + conflicts** — `PLANNED`: every fact carries source + retrieval date; source ranking per §10; conflicting values stored with STATUS=CONFLICT (§11). Validation: conflict test with marketplace vs manufacturer values.
**T-0404 — Authoritative source search + compare** — `PLANNED`: search manufacturer/distributor docs after exact identification; compare and flag conflicts. Deps: T-0402, T-0502.

### PHASE 5 — Scrapling integration

**T-0501 — Inspect installed Scrapling + pin dependency** — `PLANNED`: install/inspect actual version + official docs/repo before writing integration code (§2.4); record findings in `memory.md`; pin version. Never assume API from memory. Validation: version recorded; import smoke test.
**T-0502 — Acquisition→sanitization→extraction pipeline** — `PLANNED`: untrusted-input handling per §14; sanitization strips active content and treats embedded instructions as data; respects §15 boundaries. Validation: malicious-fixture tests (prompt-injection page must not affect behavior).

### PHASE 6 — Taiga-S1 orchestration

**T-0601 — Runtime selection + resource awareness** — `PLANNED`: detect local inference capability (§38), select model size by RAM/VRAM, graceful degradation.
**T-0602 — Orchestration core** — `PLANNED`: routes tasks to CIE/REA/PEM/tools per §2/§4; produces engineering documentation; never pretends to be a specialist tool.

### PHASE 7 — REA integration

**T-0701 — REA pipeline + record templates** — `PLANNED`: seven-file investigation structure (§21), evidence classification (§19), authorization/scope gate (§20).
**T-0702 — REA tooling** — `PLANNED`: authorized inspect/trace capabilities; findings documented as evidence, never as original source.

### PHASE 8–12 — Engineering tool integrations

Each task: detect tool via PEM, drive via CLI/API, write outputs to `cad/`, `electronics/`, `simulations/`, `models/`, verify with tool-native validation (FreeCAD recompute, KiCad DRC/ERC, ngspice op run, Gazebo world load, Blender render headless). Integration tests run only when tool present; otherwise SKIPPED with reason (never fake).
- **T-0801** Python/Jupyter integration (notebooks under `simulations/` or `projects/`).
- **T-0901** FreeCAD (mechanical authority).
- **T-1001** KiCad (PCB authority).
- **T-1002** ngspice (circuit authority).
- **T-1101** Gazebo (robotics/physics authority).
- **T-1201** Blender (visualization authority).

### PHASE 13 — Unified engineering workflow (T-1301)
End-to-end: component URL → CIE → analysis → simulation → CAD → electronics → validation, coordinated by Taiga-S1, with evidence labels throughout (§50). Validation: one demo project under `projects/` executed locally.

### PHASE 14 — Simulation / validation / BOM pipeline (T-1401)
Model calibration loop: simulated vs measured (§1); BOM generation from component records; validation status tracking.

### PHASE 15 — Security / recovery / reliability
- **T-1501** security review: untrusted inputs, no secrets in git, §14/§15/§52 compliance audit.
- **T-1502** recovery test: interrupt + resume from repository state only (§42).

### PHASE 16 — Cross-platform hardening (T-1601)
Linux/macOS script execution evidence (VMs/CI), path handling, line endings, encoding.

### PHASE 17 — Release + final audit (T-1701)
Walk the MASTER §54 release checklist; no claim without evidence; tag release.

---

## Change log

- 2026-10-08: initial task graph created at repository bootstrap (T-0001), derived from MASTER §31/§48 against an empty repository. No prior state to reconcile.
- 2026-10-08: T-0001 marked COMPLETE — governance files + structure + governance test suite (38 passed) + Git baseline. Next task: T-0101.
- 2026-10-08: T-0101 marked COMPLETE — `src/pem/detect.py` system detection (47 tests passed: 38 governance + 9 PEM). Next READY task: T-0201 (tool manifest; unblocks T-0102).
- 2026-10-08: T-0201 marked COMPLETE — tool manifest + JSON schema + stdlib loader (68 tests passed). T-0102 now unblocked (deps T-0101 + T-0201 both COMPLETE); selected as next task over T-0202 because it is Phase 1 (earlier in §48 order).
- 2026-10-08: T-0102 marked COMPLETE — manifest-driven tool detection + capability states (90 tests passed). Host evidence: git/python DETECTED; jupyter/freecad/kicad/ngspice/gazebo/blender/scrapling NOT_FOUND; taiga-s1/rea UNKNOWN (not implemented). T-0103 now READY.
- 2026-10-08: T-0103 marked COMPLETE — `src/pem/report.py` report generation + `config/environment-report.schema.json` (110 tests passed). Both report files generated on this host and confirmed gitignored. T-0104 now READY; selected as next over T-0202 because Phase 1 precedes Phase 2 in §48 order (same rationale as the T-0102 selection), and T-0104's dependency T-0103 just completed.
- 2026-10-08: T-0104 marked COMPLETE — Windows wrappers + `src/pem/ops.py` shared operations (133 tests passed; all three .ps1 files executed on this host). Next task: T-0107 (idempotent install logic), selected over T-0105/T-0106/T-0202: same Phase 1, and shared install logic must exist before platform wrappers can do more than plan (MASTER §23 forbids duplicating business logic per platform). T-0105/T-0106 remain PLANNED and can then be added as thin wrappers; T-0202 is Phase 2 (§48 order).
- 2026-10-08: T-0107 marked COMPLETE — `src/pem/installer.py` idempotent install engine + `install_command` in manifest/schema/loader + guarded `ops install --execute` (150 tests passed: +17 installer). Live evidence: plan exit 0 (7 tools to install), `--execute` refused exit 3 (C:\ 451,891,200 bytes < 1 GiB). Next task: **T-0105 (Linux scripts)**, selected over T-0106/T-0202 — same Phase 1 as T-0104/T-0107 and earlier in §48 order; shared logic now frozen, so wrappers are trivial thin scripts (§23). T-0106 follows; T-0202 is Phase 2.
- 2026-10-08: T-0105 marked COMPLETE — `scripts/linux/{install,update,healthcheck}.sh` POSIX `sh` wrappers over the shared module (157 passed, 1 skipped: the `sh -n` syntax test is skipped because this host has no POSIX shell). Linux scripts NOT executed (no POSIX shell available) — static validation only. Next task: **T-0106 (macOS scripts)**, selected over T-1601/T-0202 per §48 phase order (finish Phase 1 platform wrappers before hardening/Phase 2).
- 2026-10-08: **Autonomous build directive received** (full-programme directive). Audited repository against it (AUDIT-0012). Repo genuine and clean at `a90df34`; no rewrites needed. **BLOCKERS recorded:** (1) Taiga-S1 upstream repository URL not supplied (directive placeholder) → T-0601/T-0602 BLOCKED; (2) real system-level tool installation (FreeCAD/KiCad/ngspice/Gazebo/Blender/Jupyter/Scrapling) requires a human approval gate for privileged/network installs (MASTER §7/§29) and C:\ is below the disk threshold → install tasks remain gated; integration code proceeds with tests that SKIP when a tool is absent (roadmap rule, no fake execution). Full remaining plan = phases 2–17.
- 2026-10-08: T-0106 marked COMPLETE — `scripts/macos/{install,update,healthcheck}.sh` POSIX `sh` wrappers; static tests generalised to cover Linux + macOS (`tests/test_scripts_unix.py`, replacing the Linux-only file). Phase 1 platform wrapper set is complete (R3.7). Next task: **T-0202 (shared configuration module)**, selected over T-1601/T-0301 per §48 phase order (Phase 2 before Phase 3/16).
- 2026-10-08: T-0202 marked COMPLETE — `src/core/config.py` single source for repo root, canonical directories and config loading (JSON always; YAML when a parser is available, honestly raising otherwise). `src/core/__init__.py` re-exports; `src/pem/report.py` and `src/core/manifest.py` repointed at `config.REPO_ROOT`/`config.MANIFEST_PATH` (duplication removed; all prior tests unchanged). 19 new tests; full suite 183 passed, 2 skipped. YAML branch executed live (PyYAML present). Next task: **T-0302 (evidence/claim classification primitives)**, selected over T-0301 because both are Phase 3 and T-0302 unblocks the critical path to CIE (T-0401) and REA (T-0701).
- 2026-10-08: T-0302 marked COMPLETE — `src/core/evidence.py`: exactly the eight §6 labels (`EvidenceLabel`), strength ordering per ADR-0002 (MEASURED > OBSERVED > SIMULATED > MANUFACTURER-SPECIFIED > CALCULATED > ASSUMED > INFERRED > UNKNOWN), `parse_label` rejecting anything else, `rank`/`is_stronger`/`compare`/`strongest`, and a validated `Claim` record (UNKNOWN forbids a value; others require one). 29 new tests; full suite 212 passed, 2 skipped. T-0401 and T-0701 now READY. Next task: **T-0301 (project state persistence library)** — Phase 3 precedes Phase 4 in §48 order and T-0301 is READY.
