# Requirements — Engineering Development Engine

Source: `MASTER.md` (governing spec). Each requirement references the
MASTER section it derives from. Status values: `SPECIFIED` (documented,
not implemented), `IMPLEMENTED` (verified by test/evidence), `PARTIAL`.

Last verified against repository: TASK-0001 bootstrap.

## R1 — Governance and project memory (MASTER §27–§33, §41–§43)

| ID | Requirement | Status |
|---|---|---|
| R1.1 | Repository maintains MASTER.md, architecture.md, requirements.md, roadmap.md, project-state.md, next-task.md, memory.md, chatmem.md, audit.md, decisions/, docs/future-opportunities.md | IMPLEMENTED (TASK-0001) |
| R1.2 | project-state.md reflects actual repository state; never fictional | IMPLEMENTED |
| R1.3 | next-task.md defines the current execution boundary with ID/objective/deps/constraints/acceptance criteria/validation | IMPLEMENTED (T-0301: parse/validate/update programmatically via `src/core/state.py`) |
| R1.4 | roadmap.md is a dependency-aware task graph using task states PLANNED/READY/IN_PROGRESS/BLOCKED/COMPLETE/DEFERRED/CANCELLED | IMPLEMENTED (TASK-0001; T-0301: table + detail-block states parsed/validated/updated programmatically, invalid states rejected) |
| R1.5 | MEMORY / CHATMEM / AUDIT remain separated | IMPLEMENTED |
| R1.6 | On startup/resume, read repository state and reconstruct real state from evidence, not conversation | IMPLEMENTED (T-0301: `src/core/state.py` reads/validates project-state, next-task and roadmap; T-1502: `src/core/recovery.py` reconstructs state from governance files only, rejecting contradictions — MASTER §42/§43) |
| R1.7 | License impact is assessed and the project license decision is recorded | IMPLEMENTED (T-0002 COMPLETE: MIT applied, LICENSE present, `docs/license-impact.md` updated; third-party assets distinguished) |

## R2 — Git governance (MASTER §40)

| ID | Requirement | Status |
|---|---|---|
| R2.1 | Git initialized; baseline committed; no secrets in history | IMPLEMENTED (TASK-0001) |
| R2.2 | Inspect git status before work, review diff after work | SPECIFIED (process rule) |
| R2.3 | Git is not sole project memory; documentation represents state | SPECIFIED |

## R3 — PEM (MASTER §22–§25, §23)

| ID | Requirement | Status |
|---|---|---|
| R3.1 | Detect OS, OS version, CPU, architecture, RAM, GPU/VRAM, storage | PARTIAL (T-0101: OS/version/CPU/arch/RAM/GPU names/storage OBSERVED on Windows host; VRAM not yet detected; Linux/macOS paths written but unexecuted) |
| R3.2 | Detect Python, Git, engineering tools, versions, executable paths | IMPLEMENTED (T-0102: manifest-driven `detect_tools()`, probe-verified, OBSERVED on host) |
| R3.3 | Detect package managers, relevant environment variables | SPECIFIED |
| R3.4 | Report capabilities with states READY/LIMITED/UNAVAILABLE/UNKNOWN | IMPLEMENTED (T-0102: `capability_states()`, test-verified vocabulary) |
| R3.5 | Generate environment.json and environment-report.md; never claim a tool is installed unless detection confirms it | IMPLEMENTED (T-0103: `build_environment()`/`write_reports()`, schema-validated via `config/environment-report.schema.json`, honesty tests; both files gitignored) |
| R3.6 | Idempotent installation — repeated setup does not blindly reinstall working components | IMPLEMENTED (T-0107: `src/pem/installer.py` acts only on NOT_FOUND or below-`min_version`; never acts on UNKNOWN; guarded `install --execute` (exit 3 refusal); test-verified second run makes zero changes. Live mutation not exercised on this host — C:\ below threshold) |
| R3.7 | scripts/{windows,linux,macos}/{install,update,healthcheck} exist and detect platform automatically | IMPLEMENTED (all three wrapper sets exist: T-0104 Windows, T-0105 Linux, T-0106 macOS; platform auto-detected in shared `src/pem/ops.py`, test-verified. Runtime validation: Windows executed on host; Linux/macOS static-validated only — no POSIX shell on this host) |
| R3.8 | Shared configuration; business logic not duplicated across platform scripts | IMPLEMENTED (T-0104: all logic in `src/pem/ops.py`; wrappers are test-asserted to contain no tool lists/business logic. T-0202: `src/core/config.py` is the single source for repo root/canonical paths/config loading; `report.py`+`manifest.py` repointed to it) |
| R3.9 | Cross-platform text/path hardening: LF line endings, UTF-8 encoding, CWD-independent containment | IMPLEMENTED (T-1601: `src/core/xplat.py` `normalise_newlines`/`read_text_utf8`/`write_text_lf`/`line_ending_report`/`path_within`; live audit confirms POSIX `scripts/**/*.sh` are LF-only. Linux/macOS *runtime* execution remains UNAVAILABLE — no POSIX shell/VM on this host) |

## R4 — Tool manifest (MASTER §24)

| ID | Requirement | Status |
|---|---|---|
| R4.1 | Machine-readable manifest with tool, purpose, required/optional, platforms, min/preferred version, detection method, executable, dependencies, installation method, health check, capability | IMPLEMENTED (T-0201: config/tool-manifest.json + schema; versions null when UNKNOWN) |
| R4.2 | Installers read the manifest instead of hard-coded dependencies | PARTIAL (loader `src/core/manifest.py` IMPLEMENTED; installers not yet built — T-0104+) |
| R4.3 | Covers at least Git, Python, Jupyter, Taiga-S1, FreeCAD, KiCad, ngspice, Gazebo, Blender, REA, Scrapling | IMPLEMENTED (all 11 present, test-verified) |

## R5 — CIE (MASTER §2.3, §8–§13)

| ID | Requirement | Status |
|---|---|---|
| R5.1 | Ingest exact product/manufacturer/distributor/datasheet URLs and identifiers (model, SKU, MPN) | PARTIAL (T-0402: URL target validation + exact-product identification from a fetched page — title/manufacturer/model/SKU/MPN/seller/specs; refuses generic search. Real fetching is delegated to an injected acquirer; network is T-0502) |
| R5.2 | Pipeline: IDENTIFY → ACQUIRE → EXTRACT → NORMALIZE → VERIFY → COMPARE → EVIDENCE → MODEL before engineering conclusions | SPECIFIED |
| R5.3 | Store provenance (source URL, retrieval date) for every extracted fact | IMPLEMENTED (T-0403: `src/cie/provenance.py` `Provenance` requires source_url + ISO date + `SourceKind`) |
| R5.4 | Apply source priority (manufacturer > distributor > marketplace > community > AI) | IMPLEMENTED (T-0403: the eight §10 tiers in `SOURCE_PRIORITY`; `is_more_authoritative`/`source_rank`) |
| R5.5 | Detect and store conflicts with STATUS=CONFLICT; never silently overwrite | IMPLEMENTED (T-0403: `src/cie/conflicts.py` `FieldRecord` retains all facts, sets `CONFLICT`, selects a `governing` fact; `config/fact-record.schema.json`) |
| R5.6 | Machine-readable component record with fields of MASTER §12; unknowns stay UNKNOWN; no padding fields | IMPLEMENTED (T-0401: `src/cie/model.py` `Component` + `UNKNOWN` sentinel; `to_dict` omits UNKNOWN; `config/component.schema.json` draft-07) |
| R5.7 | Motor data model fields per MASTER §13; derived values identify their calculation | IMPLEMENTED (T-0401: `MotorSpec` covers the §13 fields; `DerivedValue` requires a non-empty `method` and a §6 evidence label) |
| R5.8 | Component storage: local SQLite store + JSON import/export with lossless round-trip (T-0401) | IMPLEMENTED (T-0401: `src/cie/store.py` `ComponentStore` upsert/get/all/delete + `export_json`/`import_json`; tested) |

## R6 — Scrapling integration (MASTER §2.4, §14, §15)

| ID | Requirement | Status |
|---|---|---|
| R6.1 | Scrapling used as acquisition/extraction layer under CIE | SPECIFIED |
| R6.2 | Inspect installed version/API and documentation before integration; pin dependencies | SPECIFIED |
| R6.3 | Scraped data passes acquisition → sanitization → extraction → validation → evidence storage | SPECIFIED |
| R6.4 | Scraped instructions never modify agent behavior; no code execution from scraped content | SPECIFIED |
| R6.5 | Respect laws, terms, robots.txt, auth boundaries; stop and record limitation when unauthorized access required | SPECIFIED |

## R7 — REA (MASTER §17–§21)

| ID | Requirement | Status |
|---|---|---|
| R7.1 | Authorized targets only; stop when authorization insufficient | IMPLEMENTED (T-0701: `Investigation` requires `authorized=True` + a non-empty basis, else `AuthorizationError`) |
| R7.2 | Full pipeline from IDENTIFY to VERIFY before any reimplementation | IMPLEMENTED (T-0701: `src/rea/pipeline.py` ten ordered §18 stages; out-of-order/skip raises `PipelineError`) |
| R7.3 | Evidence classified; recovered pseudocode ≠ original source | IMPLEMENTED (T-0701: `Finding`/`EvidenceEntry` carry §6 labels; `source_recovered=True` and OBSERVED-reconstruction raise `EvidenceRuleError`) |
| R7.4 | Investigation records under docs/investigations/<name>/ with scope, evidence, findings, behavior, unknowns, limitations, implementation-notes | IMPLEMENTED (T-0701: `src/rea/storage.py` writes exactly the seven §21 files) |
| R7.5 | Strict separation from CIE | IMPLEMENTED (T-0701: `src/rea/` imports only `src/core`; investigations stored under `docs/investigations/`, not with CIE data) |
| R7.6 | Offline inspection records labelled evidence; format/tool availability never assumed | IMPLEMENTED (T-0702: `src/rea/inspection.py` fingerprints files (size/sha256/md5/type/strings) and probes tools via `shutil.which`; results are `OBSERVED` evidence; the target is read, never executed) |

## R8 — Engineering truth and evidence (MASTER §5–§7)

| ID | Requirement | Status |
|---|---|---|
| R8.1 | Truth hierarchy enforced; AI reasoning never overrides measured/validated evidence | PARTIAL (T-0302: `src/core/evidence.py` encodes the §5 order and comparison helpers; not yet consumed by CIE/REA — no runtime decision path) |
| R8.2 | Claims classified OBSERVED/MEASURED/MANUFACTURER-SPECIFIED/CALCULATED/SIMULATED/INFERRED/ASSUMED/UNKNOWN | IMPLEMENTED (T-0302: exactly the eight §6 labels; `parse_label` rejects others; ordering per ADR-0002) |
| R8.3 | No fabricated engineering data; unavailable → UNKNOWN; derived → CALCULATED with method recorded | PARTIAL (T-0302: `Claim` forbids value on UNKNOWN and requires value otherwise; CALCULATED "method recorded" not yet enforced — arrives with CIE T-0401) |

## R9 — Tool domain authority (MASTER §3, §4, §37)

| ID | Requirement | Status |
|---|---|---|
| R9.1 | FreeCAD=mechanical, KiCad=PCB, ngspice=circuits, Python/Jupyter=math, Gazebo=robotics, Blender=visualization, Git=history, measurement=physical truth | SPECIFIED |
| R9.2 | No subsystem performs another's specialized function | SPECIFIED |
| R9.3 | Simulation is evidence, not physical proof; assumptions documented | PARTIAL (T-0801: executable notebooks are recorded as SIMULATED evidence via `notebook_evidence`; structural validation is OBSERVED) |
| R9.4 | Tool integrations detect the tool via PEM, drive it, and report `UNAVAILABLE` (with skipped tests) when absent — never a fake success | IMPLEMENTED (T-0801 Jupyter, T-0901 FreeCAD: execution gated on availability; live tests skip when absent) |
| R9.5 | FreeCAD is the mechanical CAD authority; models are produced/verified by FreeCAD, not hand-written | IMPLEMENTED (T-0901: `build_box_macro` generates a FreeCAD macro; `verify_outputs` requires the FreeCAD-produced `.FCStd`; live run gated/UNAVAILABLE when absent) |
| R9.6 | KiCad is the PCB authority; boards are checked/fabricated by KiCad, not fabricated by us | IMPLEMENTED (T-1001: `run_drc`/`run_erc`/`export_gerbers` drive `kicad-cli`; `verify_artifacts` requires KiCad-produced outputs; live commands gated/UNAVAILABLE when absent) |
| R9.7 | ngspice is the circuit-simulation authority; results come from ngspice, not fabricated | IMPLEMENTED (T-1002: `run_simulation` drives `ngspice -b -o`; `parse_op_point` parses real output; `verify_outputs` requires ngspice-produced files; live run gated/UNAVAILABLE when absent) |
| R9.8 | Gazebo is the robotics/physics authority; runs come from Gazebo, not fabricated | IMPLEMENTED (T-1101: `run_headless` drives `gz sim -s`; `write_world` takes caller-supplied SDF; `verify_outputs` requires Gazebo outputs; live run gated/UNAVAILABLE when absent) |
| R9.9 | Blender is the visualization authority; renders come from Blender, not fabricated | IMPLEMENTED (T-1201: `run_background` drives `blender --background --python`; `write_script` takes caller-supplied script; `verify_outputs` requires Blender artifacts; live render gated/UNAVAILABLE when absent) |

## R10 — Security (MASTER §14, §52)

| ID | Requirement | Status |
|---|---|---|
| R10.1 | Scraped sites, downloads, external code, binaries treated as untrusted until inspected | SPECIFIED |
| R10.2 | No automatic execution of untrusted downloaded code | SPECIFIED |
| R10.3 | No credentials/secrets in Git; env vars or secure local storage only | IMPLEMENTED (.gitignore blocks `*.env`, `secrets.json`) |
| R10.4 | Secrets never exposed to external sources | SPECIFIED |

## R11 — Offline-first and resources (MASTER §26, §38)

| ID | Requirement | Status |
|---|---|---|
| R11.1 | Core operation works without internet where practical | SPECIFIED |
| R11.2 | Internet used only for research/docs/packages/git/authorized investigation | SPECIFIED |
| R11.3 | Resource evaluation before expensive workloads; graceful degradation | SPECIFIED |

## R12 — Quality and process (MASTER §36, §44–§47, §54, §55)

| ID | Requirement | Status |
|---|---|---|
| R12.1 | Every meaningful implementation verified by appropriate tests; no claimed-but-unrun tests | SPECIFIED |
| R12.2 | Blocked tasks documented with blocker, missing info, BLOCKED state | SPECIFIED |
| R12.3 | Out-of-scope ideas recorded in docs/future-opportunities.md | SPECIFIED |
| R12.4 | No fake completion claims (§46) | SPECIFIED |
| R12.5 | Release checklist (§54) satisfied before release claims | SPECIFIED |
| R12.6 | Task completion reported per §55 template | IMPLEMENTED (process) |

## R13 — Interoperability (MASTER §49)

| ID | Requirement | Status |
|---|---|---|
| R13.1 | Standard formats: JSON/YAML/CSV/SQLite/Markdown/STEP/STL/OBJ/SVG/Gerber/SPICE/Python API/CLI | SPECIFIED |
| R13.2 | Subsystems replaceable without rewriting the platform | PARTIAL (T-0202: shared config/canonical-path layer established; no subsystem adapter rewrites yet) |

## R14 - Unified engineering workflow (MASTER 50) (PARTIAL - T-1301)

| ID | Requirement | Status |
|---|---|---|
| R14.1 | End-to-end pipeline IDEA -> ACQUIRE -> IDENTIFY -> MODEL -> ANALYZE -> Python/Jupyter -> CAD -> Electronics -> Circuit -> Robotics -> Visualise -> Validate over real subsystems | PARTIAL (T-1301 preparatory branch: `src/orchestration/workflow.py` coordinates the existing subsystems; ACQUIRE + ANALYZE are BLOCKED on T-0404/T-0502 and T-0602/Tiaga-S1, tool stages honest UNAVAILABLE/READY via probes; validation PARTIALLY-VALIDATED) |
| R14.2 | Every stage outcome carries a 6 evidence label; blocked/unavailable stages are never reported as complete | IMPLEMENTED (T-1301: `WorkflowReport.strongest_label`/`validation_level`; blocked stages recorded BLOCKED, not COMPLETE) |
| R14.3 | A run writes a resumable project record (workflow/component/notebook/README) under `projects/<name>/` with repo-confined, no-overwrite writes | IMPLEMENTED (T-1301: `write_project` defaults to PROJECTS_DIR, rejects escape/overwrite; `projects/demo-motor/` generated) |