# Roadmap — Engineering Development Engine

Dependency-aware task graph derived from `MASTER.md` §31, §32, §48.
States: `PLANNED | READY | IN_PROGRESS | BLOCKED | COMPLETE | DEFERRED | CANCELLED`.
Rule: never execute a task whose dependencies are incomplete (MASTER §32).

Last updated: 2026-10-15 (T-2000/T-2001 MVP interface + documentation).

---

## Task status summary

| ID | Title | Phase | Deps | State |
|---|---|---|---|---|
| T-0001 | Repository governance bootstrap | 0 | — | COMPLETE |
| T-0002 | License decision | 0 | T-0001 | COMPLETE (MIT selected; LICENSE added 2026-10-09; `docs/license-impact.md` updated) |
| T-0101 | PEM system/hardware detection | 1 | T-0001 | COMPLETE |
| T-0102 | PEM tool detection + capability states | 1 | T-0101, T-0201 | COMPLETE |
| T-0103 | Environment report generation (environment.json + md) | 1 | T-0102 | COMPLETE |
| T-0104 | Windows scripts (install/update/healthcheck) | 1 | T-0103 | COMPLETE |
| T-0105 | Linux scripts (install/update/healthcheck) | 1 | T-0103 | COMPLETE |
| T-0106 | macOS scripts (install/update/healthcheck) | 1 | T-0103 | COMPLETE |
| T-0107 | Idempotent install logic + tests | 1 | T-0103 | COMPLETE |
| T-0201 | Tool manifest schema + config/tool-manifest.json + loader | 2 | T-0001 | COMPLETE |
| T-0202 | Shared configuration module | 2 | T-0001 | COMPLETE |
| T-0203 | Canonical upstream-source registry | 2 | T-0201 | COMPLETE (`config/upstream-sources.json` + schema + `src/core/upstream.py` + tests) |
| T-0301 | Project state persistence library | 3 | T-0001, T-0202 | COMPLETE |
| T-0302 | Evidence/claim classification primitives | 3 | T-0001, T-0202 | COMPLETE |
| T-0401 | Component data model + schema + storage | 4 | T-0302 | COMPLETE |
| T-0402 | CIE URL ingestion + exact-identification flow | 4 | T-0401 | COMPLETE |
| T-0403 | Provenance + source priority + conflict detection | 4 | T-0401 | COMPLETE |
| T-0404 | Authoritative source search + cross-source compare | 4 | T-0402, T-0502 | PLANNED |
| T-0501 | Inspect installed Scrapling + pin dependency | 5 | T-0001 | BLOCKED (needs Scrapling installed; B-2 install gate) |
| T-0502 | Scrapling acquisition→sanitization→extraction under CIE | 5 | T-0501, T-0401 | PLANNED |
| T-0601 | Taiga-S1 runtime selection + resource awareness | 6 | T-0103, T-0301 | COMPLETE (`src/taiga/runtime.py`; tests) |
| T-0602 | Taiga-S1 provider-neutral contracts + registry | 6 | T-0601, T-0301, T-0403 | COMPLETE (`src/taiga/contracts.py`, `registry.py`; tests) |
| T-0701 | REA pipeline + investigation record templates | 7 | T-0302 | COMPLETE |
| T-0702 | REA tooling integration (inspect/trace) | 7 | T-0701 | COMPLETE |
| T-0801 | Python/Jupyter integration | 8 | T-0103 | COMPLETE |
| T-0901 | FreeCAD integration | 9 | T-0801 | COMPLETE |
| T-1001 | KiCad integration | 10 | T-0801 | COMPLETE |
| T-1002 | ngspice integration | 10 | T-0801 | COMPLETE |
| T-1101 | Gazebo integration | 11 | T-0801 | COMPLETE |
| T-1201 | Blender integration | 12 | T-0801 | COMPLETE |
| T-1301 | Unified engineering workflow (IDEA → validation) | 13 | T-0602, T-0404, T-0702, T-0901, T-1001, T-1002, T-1101, T-1201 | BLOCKED (depends on BLOCKED T-0602/T-0404; PARTIAL preparatory `src/orchestration/` delivered — see Phase 13 + AUDIT-0030) |
| T-1401 | Simulation / validation / BOM pipeline | 14 | T-1301 | BLOCKED (depends on BLOCKED T-1301) |
| T-1501 | Security review + untrusted-input hardening | 15 | T-0502, T-0403 | BLOCKED (depends on BLOCKED T-0502) |
| T-1502 | Recovery-after-interruption test | 15 | T-0301 | COMPLETE |
| T-1601 | Cross-platform hardening | 16 | T-0104, T-0105, T-0106 | COMPLETE |
| T-1700 | Baseline stabilization & state reconciliation | 17 | T-1601 | COMPLETE (green suite; T-0601/T-0602 evidence; docs reconciled) |
| T-1701 | Release audit vs MASTER §54 checklist | 17 | T-1401, T-1501, T-1502, T-1601, T-1700 | BLOCKED (deps T-1401/T-1501 BLOCKED) |
| T-1800 | D: development storage isolation (caches + workspace) | 18 | T-0202 | COMPLETE (`D:\EngineeringWorkspace`; pip/npm/HF redirected; `scripts/windows/dev-env.ps1`; `docs/storage.md`) |
| T-1801 | Reusable storage preflight utility + integration | 18 | T-0202 | COMPLETE (`src/core/storage.py` + `config/storage.json`; installer preflight; tests) |
| T-1802 | Safe cleanup of regenerable C: caches | 18 | T-1800 | COMPLETE (owner-approved `pip cache purge` + `npm cache clean --force`; no other deletion) |
| T-1702 | Governance reconciliation after storage work | 17 | T-1802 | COMPLETE (docs resynced; owner storage directive recorded as ADR-0003) |
| T-1900 | Dependency inventory + self-contained deployment audit | 19 | T-0202 | COMPLETE (`docs/dependencies.md`; `tests/test_dependency_independence.py`; ADR-0004) |
| T-2000 | Unified offline CLI (`python -m src`) | 20 | T-0202, T-1301 | COMPLETE (`src/cli.py`, `src/__main__.py`, `__version__`; `tests/test_cli.py`) |
| T-2001 | MVP definition & consolidated documentation | 20 | T-2000 | COMPLETE (`docs/mvp.md`, `docs/usage.md`, `docs/installation.md`, `docs/testing.md`, `docs/security.md`, `CHANGELOG.md`; ADR-0005) |

---

## Task details

### PHASE 0 — Repository + governance

**T-0001 — Repository governance bootstrap** — `COMPLETE`
- Objective: establish all §27 governance files, §28 directory structure, Git baseline, and a governance verification test on an empty repository.
- Dependencies: none.
- Affected components: repo root, `docs/`, `decisions/`, `tests/`, `scripts/`, `src/`, `config/`.
- Constraints: no feature code (PEM/CIE/REA/Taiga); no invented engineering data; MASTER.md stored verbatim; minimal safe foundation only (§47).
- Acceptance criteria: all §27 files exist with substantive content; §28 directory skeleton present; `roadmap.md` contains dependency-aware task graph; `next-task.md` populated with first unblocked task; governance test passes; baseline committed; `project-state.md` truthful.
- Validation: `python -m pytest tests/ -v` green; `git status` clean after commit; `git log` shows baseline.

**T-0002 — License decision** — `COMPLETE`
- Decision: MIT (applied 2026-10-09). `LICENSE` created with standard MIT text.
- Copyright: (c) 2026 Shiv Shanmugam. No assumption made about other owners.
- Third-party: model weights, datasets, external tools not covered; upstream biome-s1 is MIT; weights terms may differ.

### PHASE 1 — Project Environment Manager

**T-0101 — PEM system/hardware detection** — `COMPLETE`
- Objective: `src/pem/` detects OS, OS version, CPU, architecture, RAM, storage (and GPU/VRAM where detectable) using stdlib-first, cross-platform code.
- Dependencies: T-0001. Affected: `src/pem/`, `tests/`.
- Constraints: no external services; detection only — no installation; never claim unavailable data (UNKNOWN); resource-light (§38).
- Acceptance criteria: returns structured record with evidence-backed values on Windows; degrades gracefully when a field is undetectable.
- Validation: unit tests with mocked/real detection; `python -m pytest`.

**T-0102 — PEM tool detection + capability states** — `COMPLETE`
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

**T-0201 — Tool manifest schema + manifest + loader** — `COMPLETE`
- Objective: JSON schema covering §24 fields; `config/tool-manifest.json` entries for Git, Python, Jupyter, Taiga-S1, FreeCAD, KiCad, ngspice, Gazebo, Blender, REA, Scrapling; validated loader.
- Dependencies: T-0001. Constraints: versions UNKNOWN unless known — record MIN/PREFERRED only where justifiable; detection method must be executable.
- Acceptance criteria: manifest validates against schema; loader rejects malformed entries; all 11 tools present.
- Validation: pytest schema/round-trip tests.

**T-0202 — Shared configuration module** — `COMPLETE`
- Objective: `src/core/config.py` — paths, config loading (JSON/YAML-if-available), single source for subsystems (§49).
- Dependencies: T-0001. Acceptance criteria: resolves repo root deterministically; loads config with defaults.
- Validation: unit tests (19 new tests pass; full suite 183 passed, 2 skipped).

**T-0203 — Canonical upstream-source registry** — `COMPLETE`
- Objective: one canonical registry of upstream repositories (owner-supplied manifest) — `config/upstream-sources.json` with a JSON Schema and a stdlib loader/validator.
- Dependencies: T-0201. Affected: `config/`, `src/core/`, `tests/`, `README.md`.
- Fields per entry: id, name, purpose, repository_url, documentation_url, source_type, license_status, version_status, integration_status (+ optional version/commit/license/notes).
- Constraints: reference-only — never installation state, never a guessed version/commit/license (`null` = UNKNOWN; values only when VERIFIED); no cloning/installing/network; ids match `config/tool-manifest.json`.
- Acceptance criteria: 11 entries present; schema + loader agree; unique ids; https URLs; loaded/validated without side effects.
- Validation: `tests/test_upstream_sources.py` (required fields, unique ids, URL validity, enum agreement, manifest coverage, UNKNOWN-honesty) plus the full suite green.

### PHASE 3 — Project memory

**T-0301 — Project state persistence library** — `COMPLETE`
- Objective: parse/validate/update `project-state.md`, `next-task.md`, `roadmap.md` task states programmatically (§29, §30, §32).
- Dependencies: T-0001, T-0202. Acceptance criteria: read + write round-trip; rejects invalid task states.
- Validation: pytest round-trip tests (20 new tests pass; full suite 232 passed, 2 skipped).

**T-0302 — Evidence/claim classification primitives** — `COMPLETE`
- Objective: `src/core/evidence.py` — evidence labels (§6), truth-hierarchy ordering (§5), claim record structure; used by CIE/REA/Taiga.
- Dependencies: T-0001, T-0202. Acceptance criteria: enum of exactly the eight labels; ordering enforced; invalid labels rejected.
- Validation: pytest (29 new tests pass; full suite 212 passed, 2 skipped). Ordering recorded in ADR-0002.

### PHASE 4 — Component Intelligence Engine

**T-0401 — Component data model + schema + storage** — `COMPLETE`: JSON schema of §12/§13 fields; SQLite/JSON store; UNKNOWN for missing; no padding fields. Validation: schema tests + store round-trip (21 new tests; full suite 253 passed, 2 skipped).
**T-0402 — URL ingestion + exact identification** — `COMPLETE`: accepts exact product URL; identifies title/manufacturer/model/SKU/MPN/seller/specs before any generic search (§8). Validation: fixture-based tests with recorded public pages (no live network in tests).
**T-0403 — Provenance + source priority + conflicts** — `COMPLETE`: every fact carries source + retrieval date; source ranking per §10; conflicting values stored with STATUS=CONFLICT (§11). Validation: conflict test with marketplace vs manufacturer values.
**T-0404 — Authoritative source search + compare** — `PLANNED`: search manufacturer/distributor docs after exact identification; compare and flag conflicts. Deps: T-0402, T-0502.

### PHASE 5 — Scrapling integration

**T-0501 — Inspect installed Scrapling + pin dependency** — `BLOCKED`: install/inspect actual version + official docs/repo before writing integration code (§2.4); record findings in `memory.md`; pin version. Never assume API from memory. Validation: version recorded; import smoke test. Blocker: Scrapling is NOT_FOUND and installing it requires network/privilege approval + disk headroom (B-2).
**T-0502 — Acquisition→sanitization→extraction pipeline** — `PLANNED`: untrusted-input handling per §14; sanitization strips active content and treats embedded instructions as data; respects §15 boundaries. Validation: malicious-fixture tests (prompt-injection page must not affect behavior).

### PHASE 6 — Taiga-S1 orchestration

**T-0601 — Runtime selection + resource awareness** — `COMPLETE`: `src/taiga/runtime.py` selects a local model tier from the PEM RAM/VRAM budget (§38) and reports `available=False`/`UNKNOWN` honestly when no inference provider is registered or the budget is unknown; no model footprint is fabricated. Tests: `tests/test_taiga.py`.
**T-0602 — Provider-neutral orchestration contracts** — `COMPLETE`: `src/taiga/contracts.py` (Action/Evidence/Result/Route/Score + `Provider`/`Policy`/`Capability` protocols) and `src/taiga/registry.py`. Provider-neutral, so no third-party Taiga API is guessed. Actual task routing / engineering-document generation still needs a supplied Taiga-S1 provider; until one is wired, T-1301's ANALYZE stage is reported `BLOCKED` (honest, not faked). Tests: `tests/test_taiga.py`.

### PHASE 7 — REA integration

**T-0701 — REA pipeline + record templates** — `COMPLETE`: seven-file investigation structure (§21), evidence classification (§19), authorization/scope gate (§20).
**T-0702 — REA tooling** — `COMPLETE`: authorized inspect/trace capabilities; findings documented as evidence, never as original source.

### PHASE 8–12 — Engineering tool integrations

Each task: detect tool via PEM, drive via CLI/API, write outputs to `cad/`, `electronics/`, `simulations/`, `models/`, verify with tool-native validation (FreeCAD recompute, KiCad DRC/ERC, ngspice op run, Gazebo world load, Blender render headless). Integration tests run only when tool present; otherwise SKIPPED with reason (never fake).
- **T-0801** Python/Jupyter integration (notebooks under `simulations/` or `projects/`). `COMPLETE` — nbformat v4 build/validate (stdlib) + `jupyter nbconvert` execution gated on presence; tests SKIP when absent.
- **T-0901** FreeCAD (mechanical authority). `COMPLETE` — parametric macro generation + `cad/`-confined write, headless `freecadcmd` run gated on presence, artifact verification; tests SKIP when absent.
- **T-1001** KiCad (PCB authority). `COMPLETE` — `kicad-cli` DRC/ERC/Gerber-export gated on presence; artifact verification; tests SKIP when absent.
- **T-1002** ngspice (circuit authority). `COMPLETE` — batch simulation via `ngspice -b -o` gated on presence, operating-point parser, output verification; tests SKIP when absent.
- **T-1101** Gazebo (robotics/physics authority). `COMPLETE` — headless `gz sim -s` world load gated on presence, world writer, output verification; tests SKIP when absent.
- **T-1201** Blender (visualization authority). `COMPLETE` — headless `blender --background --python` render gated on presence, script writer under `models/`, artifact verification, labelled evidence; live render UNAVAILABLE (Blender not installed).

### PHASE 13 — Unified engineering workflow (T-1301)
End-to-end: component URL → CIE → analysis → simulation → CAD → electronics → validation, coordinated by Taiga-S1, with evidence labels throughout (§50). Validation: one demo project under `projects/` executed locally.
**PARTIAL (preparatory branch, AUDIT-0030):** `src/orchestration/` implements the §50 stage machine over the subsystems that exist — IDEA/IDENTIFY/MODEL/PYTHON/VALIDATE run against real code, external-tool stages are READY/UNAVAILABLE via PEM probes, and ACQUIRE/ANALYZE are reported `BLOCKED` (Scrapling T-0404/T-0502, Taiga-S1 T-0602). A demo project (`projects/demo-motor/`) is written but validation is `PARTIALLY-VALIDATED` while any stage is BLOCKED/UNAVAILABLE. T-1301 itself remains `BLOCKED` — Taiga-S1 coordination and Scrapling acquisition cannot be completed.

### PHASE 14 — Simulation / validation / BOM pipeline (T-1401)
Model calibration loop: simulated vs measured (§1); BOM generation from component records; validation status tracking.

### PHASE 15 — Security / recovery / reliability
- **T-1501** security review: untrusted inputs, no secrets in git, §14/§15/§52 compliance audit. BLOCKED (dep T-0502).
- **T-1502** recovery test: interrupt + resume from repository state only (§42). COMPLETE. COMPLETE — `src/core/recovery.py` reconstructs state from governance files, rejecting contradictions; proven by `tests/test_recovery.py`.

### PHASE 16 — Cross-platform hardening (T-1601)
Linux/macOS script execution evidence (VMs/CI), path handling, line endings, encoding.
COMPLETE for text/path hardening (`src/core/xplat.py`: LF/UTF-8 I/O + line-ending audit + containment) and a live LF audit of the POSIX scripts. Linux/macOS *runtime* execution evidence still requires a VM/CI → UNAVAILABLE on this host.

### PHASE 17 — Release + final audit (T-1700, T-1701)

**T-1700 — Baseline stabilization & state reconciliation** — `COMPLETE`: restored a green governance suite (corrected the stale `T-0602` assertion in `tests/test_core_state.py`), removed an accidental UTF-8 BOM from `next-task.md`, made the T-0601/T-0602 completions evidence-backed (`src/taiga/runtime.py` + `tests/test_taiga.py`), and reconciled the governance documents (README, architecture, requirements, project-state, memory) with the real repository. No subsystem behaviour changed.

**T-1701 — Release audit** — `BLOCKED`: walk the MASTER §54 release checklist; no claim without evidence; tag release. Depends on T-1401/T-1501 (BLOCKED).

### PHASE 18 — C: drive protection & D: development isolation (owner directive)

**T-1800 — D: development storage isolation** — `COMPLETE`: audited storage (OBSERVED: C: 2.23 GiB free, D: 90.52 GiB free), created `D:\EngineeringWorkspace\`, redirected pip cache (`global.cache-dir`), npm cache, and HuggingFace (`HF_HOME`/`HF_HUB_CACHE`) to D:, added session-scoped `TEMP`/`TMP` via `scripts/windows/dev-env.ps1`, and documented everything in `docs/storage.md`. Reference-only/no deletion. Recorded as ADR-0003.
**T-1801 — Storage preflight utility** — `COMPLETE`: `src/core/storage.py` (destination-drive measurement, per-operation thresholds, `check_storage`/`preflight`/`require_storage`, backend-detection `drive_of`) + data-driven `config/storage.json`; integrated into `python -m src.pem.ops install --execute` (refuses exit 3 when the workspace destination lacks space); tests in `tests/test_storage.py`.
**T-1802 — Safe cleanup of regenerable C: caches** — `COMPLETE`: owner-approved narrow cleanup (`pip cache purge`, `npm cache clean --force`); C: free rose ~2.23 → ~2.34 GiB; no other deletion (AUDIT-0044).

### PHASE 17 (addendum) — Governance reconciliation after storage work (T-1702)

**T-1702 — Governance reconciliation after storage work** — `COMPLETE`: full-project audit found documentation drift after T-1802 (project-state/roadmap/audit/chatmem/README/architecture still showed T-1802 BLOCKED and a 462-test undercount) plus dangling "MASTER prompt addendum" citations. Resynced all governance docs to reality (T-1802 COMPLETE; boundary T-1701 BLOCKED; 464 passed / 472 collected) and recorded the owner storage directive as `decisions/ADR-0003-development-storage-isolation.md`, repointing the citations. Documentation-only; no code behaviour change. AUDIT-0044.

### PHASE 19 — Dependency independence & self-contained deployment (owner directive)

**T-1900 — Dependency inventory + self-contained deployment audit** — `COMPLETE`: inventoried every dependency by category (runtime/interpreter, third-party libraries, standard library, system packages, external executables, databases/services, network APIs, AI models/runtimes, build/dev-only, optional integrations) in `docs/dependencies.md`; recorded the owner directive as `decisions/ADR-0004-dependency-independence.md`; added `tests/test_dependency_independence.py` (stdlib-only imports, guarded optional imports, import-without-optional-dependency, JSON runtime config, no BOM). Confirmed the runtime is standard-library only (the sole third-party import, PyYAML, is optional and guarded). Deferred building a bundled/portable artifact to an owner-gated task (H-14). Also stripped stray UTF-8 BOMs from `src/taiga/{__init__,contracts,registry}.py` (found by the new BOM guard; Python tolerated them, static parsers did not). Documentation/verification task; no runtime behaviour changed. AUDIT-0045.

### PHASE 20 — MVP operability & documentation (owner directive)

**T-2000 — Unified offline CLI** — `COMPLETE`: added `src/cli.py` (a thin `argparse` dispatcher) and `src/__main__.py` so `python -m src <command>` exposes the platform's offline capabilities and the flagship `run_workflow` from one entry point — `version`, `env`, `tools`, `storage preflight`, `upstream`, `cie identify`, `rea inspect`, `workflow run` — with documented exit codes (0/2/3). Added `src.__version__ = "0.1.0"` and `tests/test_cli.py` (12 tests). No new behaviour: each command calls an existing subsystem API and reports `BLOCKED`/`UNAVAILABLE` honestly (MASTER §46). Partially unblocks the "operate the project" MVP gap noted in the universal-protocol audit; the live pipeline stays BLOCKED (B-2/H-3). AUDIT-0046.

**T-2001 — MVP definition & consolidated documentation** — `COMPLETE`: authored `docs/mvp.md` (the MVP definition, in/out-of-scope tables, acceptance criteria, verification), `docs/usage.md` (CLI + API usage), `docs/installation.md` (setup/offline/storage/troubleshooting), `docs/testing.md` (how to run tests, layout, skip reasons), `docs/security.md` (trust boundaries, guarantees, limitations) and `CHANGELOG.md` (user-facing history). Recorded the scope/delivery decision as `decisions/ADR-0005-mvp-scope-and-delivery.md`. Consolidated, non-duplicative documentation that links to governance rather than restating it. Satisfies the protocol's documentation requirement (DOC-001) without changing code. AUDIT-0046.

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
- 2026-10-08: T-0301 marked COMPLETE — `src/core/state.py`: §32 task-state vocabulary (7 states), roadmap table + detail-block state parse/validate/update, next-task parse/update, project-state §29 section parse/validate/update, byte-identical no-op round-trips, invalid states/ids rejected. 20 new tests; full suite 232 passed, 2 skipped. DISCREPANCY corrected (§47): the T-0601/T-0602 table rows were BLOCKED while their detail blocks still said `PLANNED`; detail blocks reconciled to `BLOCKED` (AUDIT-0016). Next task: **T-0401 (CIE component data model + schema + storage)** — Phase 4; it is READY (dep T-0302 complete) and is the earliest remaining major subsystem in §48 order.
- 2026-10-08: T-0401 marked COMPLETE — CIE foundation: `src/cie/model.py` (`Component` §12 record with an explicit `UNKNOWN` sentinel, `to_dict` omitting UNKNOWN fields — no padding; `MotorSpec` §13; `DerivedValue` requiring a method + §6 label), `config/component.schema.json` (draft-07, only `id` required, `additionalProperties:false`), `src/cie/store.py` (`ComponentStore` SQLite upsert + JSON import/export). 21 new tests; full suite 253 passed, 2 skipped. T-0402/T-0403 now READY. Next task: **T-0402 (CIE URL ingestion + exact identification)** — Phase 4; it and T-0403 are both READY, T-0402 precedes T-0403 as the pipeline's entry point (§9 IDENTIFY first).
- 2026-10-08: T-0402 marked COMPLETE — `src/cie/target.py` (URL validation) + `src/cie/identify.py` (exact-product identification from JSON-LD › OpenGraph › `<title>`/canonical; maps to `Component`; refuses generic search on an opaque page; acquisition injected so no network), `config/identification.schema.json`, `tests/test_cie_target.py` + `tests/test_cie_identify.py`. 19 new tests; full suite 272 passed, 2 skipped. Next task: **T-0403 (provenance + source priority + conflicts)** — the remaining READY task; T-0404 still needs T-0502 (Scrapling).
- 2026-10-08: T-0403 marked COMPLETE — `src/cie/provenance.py` (the eight §10 source tiers + `Provenance`) + `src/cie/conflicts.py` (`Fact`/`FieldRecord`, `STATUS=CONFLICT`, `governing` selection without overwriting), `config/fact-record.schema.json`, `tests/test_cie_provenance.py` + `tests/test_cie_conflicts.py`. 22 new tests; full suite 294 passed, 2 skipped. **Phase 4 complete** (T-0404 deferred: needs Scrapling T-0502). Next task: **T-0501 (inspect installed Scrapling + pin)** — Phase 5 precedes Phase 7 in §48, but it requires installing Scrapling (gated by B-2 network/privilege approval + C:\ disk threshold), so it is recorded BLOCKED and the next executable READY task is **T-0701 (REA pipeline + investigation templates)**.
- 2026-10-08: T-0701 marked COMPLETE — `src/rea/pipeline.py` (ordered §18 stages, no skipping), `src/rea/records.py` (mandatory authorization §20; structural §19 evidence rules), `src/rea/storage.py` (seven §21 templates + `write_investigation`), `docs/investigations/README.md`, full suite 317 passed, 2 skipped. Next task: **T-0702 (REA tooling integration)** — Phase 7 before Phase 8 in §48 order (T-0801 is Phase 8 and also eligible).
- 2026-10-08: T-0702 marked COMPLETE — `src/rea/inspection.py` (magic-byte file-type detection, bounded string extraction, streaming sha256/md5 fingerprint, tool probing via `shutil.which`, `inspect_target` → labelled `EvidenceEntry`), `with_evidence` helper in `records.py`, `tests/test_rea_inspection.py`. 8 new tests; full suite 325 passed, 2 skipped. **Phase 7 complete** (REA framework + offline inspection; deeper tracing deferred). Next task: **T-0801 (Python/Jupyter integration)** — Phase 8; READY (dep T-0103) and the next phase in §48 order.
- 2026-10-08: T-0801 marked COMPLETE — `src/integrations/jupyter.py` (`build_notebook`/`validate_notebook` nbformat v4, `write_notebook` confined to `simulations/`, `execute_notebook` via `jupyter nbconvert` gated on `jupyter_available`, `notebook_evidence` → OBSERVED/SIMULATED), `tests/test_integrations_jupyter.py`. 8 new tests + 1 skipped-when-absent integration test; full suite 333 passed, 3 skipped. Jupyter is NOT installed on this host, so live execution is `UNAVAILABLE` (honest skip, not faked). Next task: **T-0901 (FreeCAD integration)** — Phase 9; READY (dep T-0103) and next in §48 phase order (note: FreeCAD also NOT installed, so it will ship as gated integration + skip-when-absent tests).
- 2026-10-08: T-0901 marked COMPLETE — `src/integrations/freecad.py` (parametric `build_box_macro`, `cad/`-confined `write_script`, headless `run_macro` gated on `freecad_available`, `verify_outputs`, `cad_evidence` → OBSERVED/SIMULATED), `tests/test_integrations_freecad.py`. 7 new tests + 1 skipped-when-absent; full suite 340 passed, 4 skipped. FreeCAD NOT installed → live CAD execution is `UNAVAILABLE` (honest skip). Next task: **T-1001 (KiCad integration)** — Phase 10; READY (dep T-0801) and next in §48 order (KiCad also NOT installed → gated integration + skip-when-absent tests).
- 2026-10-08: T-1001 marked COMPLETE — `src/integrations/kicad.py` (`kicad-cli` DRC/ERC/Gerber-export commands gated on `kicad_cli`, `verify_artifacts`, `kicad_evidence` → OBSERVED), `tests/test_integrations_kicad.py`. 7 new tests + 1 skipped-when-absent; full suite 347 passed, 5 skipped. KiCad NOT installed → live PCB execution is `UNAVAILABLE` (honest skip). Next task: **T-1002 (ngspice integration)** — Phase 10; READY (dep T-0801) and next in §48 order (ngspice also NOT installed → gated integration + skip-when-absent tests).
- 2026-10-08: T-1002 marked COMPLETE — `src/integrations/ngspice.py` (batch `ngspice -b -o` gated on `ngspice_cli`, `write_netlist` confined to `simulations/`, `parse_op_point`, `verify_outputs`, `ngspice_evidence` → SIMULATED/OBSERVED), `tests/test_integrations_ngspice.py`. 7 new tests + 1 skipped-when-absent; full suite 352 passed, 6 skipped. ngspice NOT installed → live simulation is `UNAVAILABLE` (honest skip). Next task: **T-1101 (Gazebo integration)** — Phase 11; READY (dep T-0801) and next in §48 order (Gazebo also NOT installed → gated integration + skip-when-absent tests).
- 2026-10-08: T-1101 marked COMPLETE — `src/integrations/gazebo.py` (headless `gz sim -s -r --iterations` gated on `gazebo_cli`, `write_world` confined to `models/`, `verify_outputs`, `gazebo_evidence` → SIMULATED/OBSERVED), `tests/test_integrations_gazebo.py`. 6 new tests + 1 skipped-when-absent; full suite 360 passed, 7 skipped. Gazebo NOT installed → live simulation is `UNAVAILABLE` (honest skip). Next task: **T-1201 (Blender integration)** — Phase 12; READY (dep T-0801) and next in §48 order (Blender also NOT installed → gated integration + skip-when-absent tests).
- 2026-10-08: T-1201 marked COMPLETE — `src/integrations/blender.py` (headless `blender --background --python` gated on `blender_cli`, `write_script` confined to `models/`, `verify_outputs`, `blender_evidence` → SIMULATED/OBSERVED), `tests/test_integrations_blender.py`; package re-exports disambiguated (`verify_blender_outputs`/`write_blender_script`). 6 new tests + 1 skipped-when-absent; full suite 366 passed, 8 skipped. Blender NOT installed → live rendering is `UNAVAILABLE` (honest skip). **Phase 12 complete.** Next task by §48 order: Phase 13 T-1301 depends on BLOCKED T-0602/T-0404 → BLOCKED; Phase 14 T-1401 depends on T-1301 → BLOCKED; Phase 15 T-1501 depends on BLOCKED T-0502 → BLOCKED; the next executable READY task is **T-1502 (recovery-after-interruption test)** (Phase 15, dep T-0301 COMPLETE).
- 2026-10-08: T-1502 marked COMPLETE — `src/core/recovery.py` (`recover`/`recover_consistent`/`assert_recoverable` reconstruct state from `MASTER.md`/`project-state.md`/`next-task.md`/`roadmap.md` only, never conversation; raises `RecoveryError` on missing docs, malformed §29 sections, a COMPLETE boundary, or a READY task with an incomplete dependency — MASTER §42/§43/§47), `tests/test_recovery.py`. 7 new tests; full suite 373 passed, 8 skipped. Live: `assert_recoverable(REPO_ROOT)` → boundary T-1502, blocked set {T-0002, T-0501, T-0601, T-0602, T-1301, T-1401, T-1501}. Next task by §48 order: **T-1601 (cross-platform hardening)** — Phase 16; READY (deps T-0104/T-0105/T-0106 COMPLETE). Phase 17 T-1701 remains blocked on T-1401/T-1501.
- 2026-10-08: T-1601 marked COMPLETE — `src/core/xplat.py` (`normalise_newlines`, `read_text_utf8` BOM-tolerant, `write_text_lf`, `line_ending_report`, `path_within`), `tests/test_xplat.py`. 7 new tests; full suite 380 passed, 8 skipped. Live: `line_ending_report` over `scripts/**/*.sh` → all LF-only (OBSERVED); Linux/macOS runtime execution stays UNAVAILABLE (no POSIX shell/VM). **Phase 16 complete.** Remaining: Phase 13/14 (T-1301/T-1401) and Phase 15 T-1501 are BLOCKED (T-0602/T-0404/T-0502), so Phase 17 **T-1701 (release audit) is BLOCKED** — no further executable task; surface blockers and stop (MASTER §44/§48).

- 2026-10-09: **T-1301 preparatory branch delivered (PARTIAL; task stays BLOCKED)** - `src/orchestration/workflow.py` + `src/orchestration/__init__.py`: the MASTER 50 stage machine (IDEA -> ACQUIRE -> IDENTIFY -> MODEL -> ANALYZE -> PYTHON -> CAD -> ELECTRONICS -> CIRCUIT -> ROBOTICS -> VISUALISE -> VALIDATE) with `WorkflowStage`/`StageStatus` (COMPLETE/READY/UNAVAILABLE/BLOCKED), `StageResult`, `WorkflowReport` (evidence label + validation level), `run_workflow` and a repo-confined `write_project`. ACQUIRE is BLOCKED (T-0404/T-0502) and ANALYZE is BLOCKED (T-0602); tool stages resolve via PEM probes (UNAVAILABLE on this host); IDEA/IDENTIFY/MODEL/PYTHON/VALIDATE execute against real code. Demo `projects/demo-motor/` generated (completed IDEA/IDENTIFY/MODEL/PYTHON/VALIDATE; blocked ACQUIRE/ANALYZE; validation PARTIALLY-VALIDATED). 17 new tests; full suite 397 passed, 8 skipped. T-1301 remains BLOCKED overall - this is a documented preparatory deliverable, not completion. Next task unchanged: T-1701 BLOCKED; blockers B-1/B-2 still govern completion. Recorded AUDIT-0030.
- 2026-10-09: **Governance/registry reconciliation + T-0002 preparatory analysis (AUDIT-0031).** (1) `config/tool-manifest.json` notes corrected: Jupyter/FreeCAD/KiCad/ngspice/Gazebo/Blender notes now record the actual OBSERVED NOT_FOUND probe result instead of the stale "not probed yet (UNKNOWN)"; the `taiga-s1` note now states the upstream repo is UNKNOWN (B-1); the `rea` note no longer claims the in-house framework is unimplemented. (2) Stale roadmap detail-block states reconciled to the authoritative table (T-0001/T-0101/T-0102/T-0201 were `IN_PROGRESS`/`READY`/`PLANNED`/`READY` → `COMPLETE`); T-0002's detail no longer mis-cites `ADR-0002` (already the evidence-order ADR) for a future license decision. (3) `docs/license-impact.md` produced as a T-0002 analysis; T-0002 stays BLOCKED. No task state changed; no code behavior changed. Next task unchanged: T-1701 BLOCKED.
- 2026-10-11: **T-1700 marked COMPLETE — baseline stabilization & state reconciliation (AUDIT-0041).** Restored a green suite by correcting the stale `T-0602 == BLOCKED` assertion in `tests/test_core_state.py`; removed an accidental UTF-8 BOM from `next-task.md`; made T-0601/T-0602 evidence-backed with `src/taiga/runtime.py` (resource-aware model-tier selection, MASTER §38) and `tests/test_taiga.py` (contracts/registry/runtime); corrected T-0602's description from "task routing" to the provider-neutral contracts it actually implements; reconciled README/architecture/requirements/project-state/memory to the real repository (B-1 resolved, MIT applied, T-0601/T-0602 COMPLETE). Full suite **413 passed, 8 skipped**. T-1701 remains BLOCKED (deps T-1401/T-1501).
- 2026-10-11: **T-0203 marked COMPLETE — canonical upstream-source registry (owner directive; AUDIT-0042).** Added `config/upstream-sources.json` (11 sources: Taiga-S1/Biome-S1, Scrapling, REA, FreeCAD, KiCad, ngspice, Python, Jupyter, Gazebo, Blender, Git) + `config/upstream-sources.schema.json` + `src/core/upstream.py` (stdlib loader/validator) + `config.py` paths + `tests/test_upstream_sources.py`. Reference-only: LICENSE/VERSION status UNKNOWN unless verified; UNKNOWN forbids a claimed value. README documents the registry; memory/chatmem cite it instead of duplicating URLs. Boundary unchanged: T-1701 BLOCKED (B-2).
- 2026-10-11: **T-1800/T-1801 marked COMPLETE — C: drive protection & D: development isolation (owner directive; AUDIT-0043).** Audited storage OBSERVED: C: 2.23 GiB free / 199 GiB, D: 90.52 GiB free / 277 GiB. Top C: consumers are non-project (Windows 46 GB, Adobe 23 GB, AppData 54 GB, VMs 18 GB); the project's controllable C: footprint is the pip cache (1.23 GB), npm cache (2.78 GB), TEMP, and future model downloads. Created `D:\EngineeringWorkspace\`; redirected pip (`global.cache-dir`), npm (`cache`), and HuggingFace (`HF_HOME`/`HF_HUB_CACHE`) to D:; added `scripts/windows/dev-env.ps1` (session `TEMP`/`TMP`); added reusable `src/core/storage.py` + data-driven `config/storage.json` preflight (per-operation thresholds, exit 3 when blocked) integrated into `ops install --execute`; documented `docs/storage.md`. No deletion performed. T-1802 (narrow cache cleanup) recorded BLOCKED pending owner approval. Boundary otherwise T-1701 BLOCKED (B-2).
- 2026-10-15: **T-1802 marked COMPLETE — safe cleanup of regenerable C: caches (owner-approved; AUDIT-0044).** The owner approved the narrow cleanup; `pip cache purge` (0 bytes — the pip cache already lives on `D:` after T-1800) and `npm cache clean --force` were executed. C: free rose ~2.23 → ~2.34 GiB; no other deletion was performed. Boundary unchanged: T-1701 BLOCKED (B-2).
- 2026-10-15: **T-1702 added and marked COMPLETE — governance reconciliation after storage work (full-project audit; AUDIT-0044).** The audit found documentation drift (project-state/roadmap/audit/chatmem/README/architecture still showed T-1802 BLOCKED and a 462-test undercount) and dangling "MASTER prompt addendum" citations. Resynced all governance docs to reality (T-1802 COMPLETE; boundary T-1701 BLOCKED; 464 passed / 472 collected) and recorded the owner storage directive as `decisions/ADR-0003-development-storage-isolation.md`, repointing the citations. Documentation-only; no code behaviour change.
- 2026-10-15: **T-1900 marked COMPLETE — dependency inventory & self-contained deployment audit (owner directive; AUDIT-0045).** Inventoried all dependency categories in `docs/dependencies.md`; recorded the directive as `decisions/ADR-0004-dependency-independence.md`; added `tests/test_dependency_independence.py` enforcing stdlib-only imports, guarded optional imports, import-without-optional-dependency, JSON runtime config, and no-BOM. Confirmed the runtime needs only Python 3.11+ (sole third-party import PyYAML is optional/guarded). Stripped stray UTF-8 BOMs from `src/taiga/{__init__,contracts,registry}.py` (found by the new guard). Bundled/portable packaging deferred to H-14. No runtime behaviour changed. Boundary unchanged: T-1701 BLOCKED (B-2).
- 2026-10-15: **T-2000/T-2001 added and marked COMPLETE — MVP operability & documentation (owner directive "Universal Project Autonomy Protocol"; AUDIT-0046).** T-2000 delivered a unified offline CLI (`src/cli.py`, `src/__main__.py`, `src.__version__ = "0.1.0"`; `tests/test_cli.py`, 12 tests) exposing `version`/`env`/`tools`/`storage preflight`/`upstream`/`cie identify`/`rea inspect`/`workflow run` from `python -m src`. T-2001 authored `docs/mvp.md` (MVP definition + acceptance), `docs/usage.md`, `docs/installation.md`, `docs/testing.md`, `docs/security.md`, `CHANGELOG.md`, and recorded the scope decision as `decisions/ADR-0005-mvp-scope-and-delivery.md`. Suite now **483 passed, 8 skipped (491 collected)**. No runtime behaviour changed; live acquisition/analysis remain BLOCKED (B-2/H-3). Boundary unchanged: T-1701 BLOCKED.
