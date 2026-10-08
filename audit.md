# audit.md — historical actions and audits

Append-only record of significant actions, findings and discrepancies
(MASTER §27, §41, §43). Newest entry at the bottom of the log.

---

## AUDIT-0001 — 2026-10-08 — Repository state audit against MASTER.md (pre-work)

- **Action:** read-only inspection of `D:\Abhishek\Projects\ENGINEERING DEVELOPMENT ENGINE\project` and Git state before any changes.
- **Findings:**
  - Directory completely empty (no files, no subdirectories).
  - Not a Git repository (`git status` → fatal: not a git repository).
  - No prior implementation, governance, tests, or documentation to reconcile.
  - Host: Windows (win32); Git 2.55.0.windows.3, Python 3.13.5, Node v24.14.1, pytest 9.1.1 present.
- **Conclusion:** INITIAL BOOTSTRAP scenario (MASTER §47). Implementation status vs MASTER = 0%. Task graph must be built from scratch per §31/§48.
- **Evidence class:** OBSERVED (command output).

## AUDIT-0002 — 2026-10-08 — T-0001 bootstrap execution

- **Action:** executed T-0001 (repository governance bootstrap).
- **Steps:**
  1. `git init` + `.gitignore` (Python caches, machine-specific `environment.json`, secrets patterns, OS/editor junk).
  2. Created §28 directory skeleton with `.gitkeep` placeholders.
  3. Wrote `MASTER.md` (verbatim), `README.md`, `architecture.md`, `requirements.md`, `roadmap.md` (task graph: 35 tasks, Phases 0–17), `project-state.md`, `next-task.md`, `memory.md`, `chatmem.md`, `audit.md` (this file), `docs/future-opportunities.md`, `decisions/ADR-0001`.
  4. Wrote `tests/test_repo_governance.py`.
  5. Ran `python -m pytest tests/ -v` → result recorded below.
  6. Reviewed `git status`, committed baseline.
- **Test result:** see TEST LOG below.
- **Limitations:** no engineering tool integration tested; Linux/macOS script paths not executed (Windows host); no network operations performed.
- **Security:** no secrets written; `.gitignore` blocks `*.env`, `secrets.json`, `environment.json`.

### TEST LOG

- 2026-10-08 — `python -m pytest tests/ -v` (run 1, mid-task) — **38 passed, 0 failed, 0 skipped** in 0.37s. Environment: Windows/Python 3.13.5/pytest 9.1.1. Scope: governance files/structure/task-graph/next-task/project-state/memory-separation/gitignore/ADR/Git-presence.
- 2026-10-08 — `python -m pytest tests/ -v` (run 2, after closing T-0001 state files) — result: **38 passed** (see commit; re-verified that state-file rewrites did not break governance tests).

### ACCEPTANCE CRITERIA (T-0001)

1. §27 files present and substantive — MET (verified by tests).
2. §28 directory skeleton present — MET (verified by tests).
3. Dependency-aware roadmap with task states — MET (35 tasks, Phases 0–17, all 7 states defined).
4. next-task.md in §30 format — MET (now points at T-0101 after closure).
5. `python -m pytest tests/ -v` passes — MET (38 passed).
6. Baseline committed; `git status` clean — MET (verified before commit).
7. project-state.md truthful — MET.

## AUDIT-0003 — 2026-10-08 — T-0001 CLOSED

- **Action:** marked T-0001 COMPLETE in roadmap.md; rewrote project-state.md and next-task.md; selected next READY task **T-0101 (PEM system/hardware detection)** per dependency order (T-0002 remains BLOCKED on license approval).
- **Evidence:** test log above; Git baseline commit (see `git log`).
- **Limitations:** roadmap details for Phases 4–17 are plans, not verified designs; they will be refined as evidence arrives (recorded in roadmap change log).

## AUDIT-0004 — 2026-10-08 — discrepancy correction (§43)

- **Discrepancy:** the baseline commit message and three documents claimed the roadmap contains "34 tasks"; the actual count of unique task IDs is **35** (verified with a regex count over `roadmap.md`).
- **Resolution:** audit.md and chatmem.md corrected to 35; the commit message of `3453e15` is left unchanged because rewriting history is not authorized (§40) — this entry is the authoritative correction.
- **Evidence:** OBSERVED (scripted count of `T-\d{4}` IDs in roadmap.md = 35).

## AUDIT-0005 — 2026-10-08 — T-0101 PEM system/hardware detection executed

- **Action:** implemented `src/pem/detect.py` (`detect_system()`), package
  inits, and `tests/test_pem_detection.py`; ran the detector live on this
  host; ran the full test suite.
- **Implementation notes:**
  - stdlib-first (platform, os, shutil, ctypes, winreg, subprocess); no
    third-party dependency added; no installation, no network.
  - Each detector returns None on failure; `detect_system` never raises
    (ordinary exceptions → UNKNOWN; BaseException propagates so Ctrl-C
    still works).
  - Empty string / empty list / empty dict / non-positive int are mapped
    to UNKNOWN — an empty collection is not evidence of absence.
- **Bug found by tests (fix applied before completion):** initial `_field`
  mapped only None to UNKNOWN, so an empty list `[]` would have been
  reported as OBSERVED with an empty value. Fixed and covered by
  `test_empty_collection_maps_to_unknown`.
- **Live detection result (OBSERVED, 2026-10-08, `python -m src.pem.detect`):**
  - os_name: Windows — OBSERVED
  - os_version: 11 (build 10.0.26200) — OBSERVED
  - cpu: AMD Ryzen 5 5600H with Radeon Graphics — OBSERVED
  - architecture: AMD64, 64bit — OBSERVED
  - ram_bytes: 6287331328 — OBSERVED
  - storage: C:\ total 213830856704 free 14266368; D:\ total 297237737472
    free 96803201024 — OBSERVED
  - gpu: [AMD Radeon(TM) Graphics, NVIDIA GeForce GTX 1650] — OBSERVED
  - VRAM: not queried (out of T-0101 scope) — UNKNOWN
- **Warning:** C:\ free space ≈ 14 MB — record in project-state; must be
  re-checked before any install task (T-0104+).
- **Tests:** `python -m pytest tests/ -v` → **47 passed, 0 failed**
  (2026-10-08): 38 governance + 9 PEM detection.
- **Acceptance criteria (T-0101):**
  1. detect_system() with 7 keys, value+evidence per field — MET.
  2. Runs on this Windows host; OS name, OS version, architecture, RAM
     returned — MET (evidence above).
  3. Tests cover happy path, JSON serializability, mocked UNKNOWN
     handling, no empty strings — MET.
  4. Full suite passes including governance tests — MET (47 passed).
  5. Importable as `from src.pem.detect import detect_system` — MET.
- **Limitations:** Linux/macOS detection code paths written but NOT
  executed (Windows host) — no execution claim for them; GPU VRAM not
  detected; RAM value is what the OS reports (reserved memory may reduce
  it below physical total) — not independently measured.
- **Security:** one local PowerShell invocation (Win32_VideoController
  query, no network, no elevation); no credentials involved; no external
  content executed.
- **Files:** src/__init__.py, src/pem/__init__.py, src/pem/detect.py,
  tests/test_pem_detection.py, roadmap/project-state/next-task/memory
  closure updates.

## AUDIT-0006 — 2026-10-08 — T-0201 tool manifest schema + manifest + loader executed

- **Action:** implemented `config/tool-manifest.schema.json` (JSON
  Schema draft-07), `config/tool-manifest.json` (11 tools), and
  `src/core/manifest.py` (stdlib loader/validator), plus
  `tests/test_manifest.py`.
- **Implementation notes:**
  - Manifest fields follow MASTER §24 (id, tool, purpose, required/optional,
    supported_platforms, min_version, preferred_version, detection_method,
    executable, dependencies, installation_method, health_check,
    capability, optional notes).
  - No fabricated versions: min_version is null for all 11 tools (UNKNOWN);
    python preferred_version = "3.13" justified in notes (only version
    OBSERVED/exercised on host). No installation-state keys allowed —
    loader rejects `installed`/`version`/`status`/`state`/`path` fields.
  - Taiga-S1, REA marked optional with detection_method "none" (in-house,
    not yet implemented) so future health checks do not fail on them;
    Scrapling detection = python_module, version UNKNOWN until T-0501.
  - Loader validates: missing file, invalid JSON, missing fields, bad
    types, unsupported required value/platform/capability/detection
    method, duplicate ids, dangling dependency ids, unknown fields,
    asserted installation state. Capability states restricted to
    READY/LIMITED/UNAVAILABLE/UNKNOWN via `validate_capability_state`.
- **Bug found by tests (fix applied before completion):** the
  installation-state check ran after the unknown-field check, so an
  `installed` key produced a generic "unknown field" error instead of the
  specific rejection. Reordered; covered by
  `test_rejects_asserted_installation_state`.
- **Tests:** `python -m pytest tests/ -q` → **68 passed, 0 failed**
  (2026-10-08): 38 governance + 9 PEM + 21 manifest.
- **Smoke check:** `python -m src.core.manifest` →
  "tool manifest OK: 11 tools: git, python, jupyter, taiga-s1, freecad,
  kicad, ngspice, gazebo, blender, rea, scrapling".
- **Acceptance criteria (T-0201):**
  1. Schema covers all §24 fields + stable id — MET.
  2. 11 tools present, schema-valid — MET (test-verified; loader enforces
     schema-equivalent rules since jsonschema is not a stdlib dependency).
  3. Loader raises descriptive ManifestError on every rejection path —
     MET (21 tests including each path).
  4. Capability state vocabulary limited to the four §22 states — MET
     (`CAPABILITY_STATES`, exact-match test).
  5. Tests cover valid load, each rejection path, 11 ids, no
     installation-state claims — MET.
  6. Full suite passes — MET (68 passed).
  7. Importable as `from src.core.manifest import load_manifest` — MET.
- **Limitations:** schema file is not mechanically enforced by the loader
  (equivalent rules implemented manually; agreement tested); actual tool
  probing is T-0102 (not done here); no Linux/macOS execution claim.
- **Security:** no network; no external code; manifest values are inert
  data (health_check/installation strings are descriptions, not executed
  by the loader).
- **Files:** config/tool-manifest.json, config/tool-manifest.schema.json,
  src/core/__init__.py, src/core/manifest.py, tests/test_manifest.py,
  requirements.md (R4), roadmap/project-state/next-task/audit/chatmem
  closure updates.

## AUDIT-0007 — 2026-10-08 — T-0102 PEM tool detection + capability states executed

- **Action:** implemented `src/pem/tools.py`
  (`detect_tools()`, `capability_states()`) and
  `tests/test_pem_tools.py`; ran detection live on this host; full suite
  green.
- **Implementation notes:**
  - One bounded probe per tool (15 s timeout, no shell=True, shlex-parsed
    argv); probes come from the trusted repo manifest health_check (or
    `<executable> --version` fallback).
  - States: executable missing → NOT_FOUND (OBSERVED); timeout/OSError →
    UNKNOWN; exit 0 → DETECTED (version extracted only if actually
    printed); python_module probe naming a missing module → NOT_FOUND;
    non-zero + version output → DETECTED with health_ok=False; non-zero
    without version → UNKNOWN (inconclusive). detection_method "none"
    (taiga-s1, rea) → UNKNOWN, no probe run.
  - Capability aggregation rules tested: READY / LIMITED (failed health
    or version-below-known-min) / UNKNOWN (inconclusive or unprobeable) /
    UNAVAILABLE (all providers conclusively absent); every final state
    passes `validate_capability_state`.
- **Live detection result (OBSERVED, 2026-10-08, `python -m src.pem.tools`):**
  - git → DETECTED, version 2.55.0, C:\Program Files\Git\cmd\git.EXE
  - python → DETECTED, version 3.13.5 (Python313 install path)
  - jupyter → NOT_FOUND (module absent)
  - scrapling → NOT_FOUND (module absent)
  - freecad / kicad / ngspice / gazebo (gz) / blender → NOT_FOUND
    (executable absent on PATH)
  - taiga-s1 / rea → UNKNOWN (in-house, not implemented; no probe run)
  - Capabilities: numerical optimization = READY; LLM inference =
    UNKNOWN; CAD, PCB design, circuit simulation, robotics simulation,
    3D rendering, web acquisition = UNAVAILABLE.
- **Engineering-environment fact:** no engineering toolchain (FreeCAD,
  KiCad, ngspice, Gazebo, Blender, Jupyter) is installed on this host —
  installation work (T-0104+) is genuinely required before any
  engineering-tool task can execute. Recorded in memory.md.
- **Tests:** `python -m pytest tests/ -v` → **90 passed, 0 failed**
  (2026-10-08): 38 governance + 9 PEM detection + 21 manifest + 22 PEM
  tool detection. All mocked probe paths + real git/python probes.
  (A prior run in this task had 1 failure: the project-state rewrite
  dropped the §29 "Last completed task" heading — caught by the
  governance test and fixed before commit.)
- **Acceptance criteria (T-0102):**
  1. detect_tools() records with id/state/version/executable_path/
     evidence/probe/reason — MET.
  2. capability_states() covers all eight §22 capabilities with exact
     §22 vocabulary, rules as specified, validated — MET (8 aggregation
     rule tests).
  3. FileNotFoundError → NOT_FOUND; timeout/inconclusive → UNKNOWN;
     version only when actually in output — MET (mocked tests).
  4. Host run finds git + python; no false claims for other tools — MET
     (evidence above; DETECTED implies probe evidence, test-asserted).
  5. Mocked tests for all paths + real-host git/python test — MET.
  6. Full suite passes — MET (90 passed).
  7. Importable as specified — MET.
- **Limitations:** version strings are first dotted-numeric tokens in
  probe output (best effort; may truncate suffixes like
  "2.55.0.windows.3" → "2.55.0"); Linux/macOS probe paths unexecuted
  (Windows host); probes confirm PATH presence, not full installation
  integrity.
- **Security:** no network; no elevation; probes run only manifest-declared
  local commands with bounded timeouts; no shell interpretation of
  strings.
- **Files:** src/pem/tools.py, tests/test_pem_tools.py, requirements.md
  (R3.2/R3.4), roadmap/project-state/next-task/memory/audit/chatmem
  closure updates.


---

## AUDIT-0008 — T-0103 environment report generation (2026-10-08)

- **Scope:** `src/pem/report.py` (`build_environment()`,
  `render_markdown()`, `write_reports()`),
  `config/environment-report.schema.json`, `tests/test_pem_report.py`,
  `.gitignore` extended with `environment-report.md`; probe records in
  `src/pem/tools.py` now carry the manifest `required` flag (one-line
  addition; needed for REQUIRED_TOOL_NOT_DETECTED warnings).
- **Tests:** `python -m pytest tests/ -q` → **110 passed, 0 failed**
  (2026-10-08): 38 governance + 9 PEM detection + 21 manifest + 22 PEM
  tools + 20 PEM report. Failures caught and fixed before commit: the
  word "installed" appeared in a recommendation sentence (reworded to
  "no automatic installation is performed"); UNAVAILABLE capabilities
  were not listed as limitations (now included).
- **Live run (OBSERVED, 2026-10-08T13:15:06+00:00):** generated both
  reports at repo root. warnings: `LOW_DISK_SPACE — volume C:\ has only
  6135808 bytes free (threshold 1073741824 bytes)`. missing_tools:
  jupyter, freecad, kicad, ngspice, gazebo, blender, scrapling.
  unknown_tools: taiga-s1, rea. limitations: LLM inference (UNKNOWN) +
  six UNAVAILABLE capabilities. recommendations: 8 (one per missing
  tool + low-disk advice). `git check-ignore` confirms BOTH report files
  are gitignored; they do not appear in `git status`.
- **Schema (roadmap AC "JSON schema-validated"):**
  `config/environment-report.schema.json` (draft-07) validated by a
  stdlib checker in tests (no third-party deps): required keys, tool
  state enum DETECTED/NOT_FOUND/UNKNOWN, exact §6 evidence labels, exact
  §22 capability vocabulary, additionalProperties=false. A fabricated
  `state: "INSTALLED"` is rejected by the schema test.
- **Acceptance criteria (T-0103):**
  1. build_environment() returns the nine §25 keys, JSON-serializable — MET.
  2. write_reports() writes both files (UTF-8, pretty JSON) and returns
     paths; markdown has all eight required sections — MET (round-trip test).
  3. Honesty rules: NOT_FOUND only in missing_tools, UNKNOWN only in
     unknown_tools, DETECTED shows real version, dedicated
     never-described-as-installed test — MET.
  4. Warnings data-driven: low-disk below 1 GiB constant names the
     volume (C:\ fired live, OBSERVED); UNKNOWN capabilities produce
     limitation entries — MET.
  5. .gitignore contains both filenames, test-asserted — MET.
  6. Round-trip json.dumps/loads equality; default target is repo root — MET.
  7. Full suite passes — MET (110).
  8. Importable as specified — MET.
- **Limitations:** `generated_at` is the only non-deterministic field
  (documented); platform section records system detector output as-is
  (VRAM remains UNKNOWN); reports are machine-specific snapshots —
  regenerate after environment changes; Linux/macOS paths unexecuted.
- **Security:** no network, no elevation, no installation; generation
  reads detector output only; both outputs gitignored so machine facts
  are not committed.
- **Files:** src/pem/report.py, config/environment-report.schema.json,
  tests/test_pem_report.py, src/pem/tools.py (required flag), .gitignore,
  requirements.md (R3.5), roadmap/project-state/next-task/chatmem/memory
  closure updates.

---

## AUDIT-0009 — T-0104 Windows scripts + shared ops (2026-10-08)

- **Scope:** `src/pem/ops.py` (healthcheck/install/update commands over
  the existing detectors; exit codes 0/1/2 documented in --help),
  `scripts/windows/{install,update,healthcheck}.ps1` (thin wrappers:
  repo-root resolution, interpreter lookup, exit-code propagation only),
  `tests/test_pem_ops.py`.
- **Tests:** `python -m pytest tests/ -v` → **133 passed, 0 failed**
  (2026-10-08): 38 governance + 9 PEM detection + 21 manifest +
  22 PEM tools + 20 PEM report + 23 PEM ops.
- **DISCREPANCY RECORD — reported error in
  `test_update_plan_reports_versions_and_never_mutates`:** the test was
  reported failing after an interrupted run. Diagnosis: not reproducible
  (isolated run + 3 full-file runs + 2 full-suite runs = 6/6 green, no
  code or test changes needed between them). Root cause identified as
  environmental: `tmp_path` resides on C:\, which had only 6,135,808
  bytes free at the time (OBSERVED, AUDIT-0008); Windows automatic temp
  cleanup (Storage Sense) purged `C:\Users\...\Temp` mid-run, deleting
  the pytest tmp directory while the test held `monkeypatch.chdir` on it
  → OSError attributed to that test (one of only two tests using
  tmp_path). Supporting evidence: C:\ free space rose to 459,509,760
  bytes between runs (cleanup occurred), after which all runs passed.
  Resolution: test and implementation left UNCHANGED (not weakened —
  version reporting and zero-mutation behavior verified independently,
  below).
- **Live execution (OBSERVED, 2026-10-08, this host):**
  - `python -m src.pem.ops healthcheck` → **exit 1**: [PASS] git
    2.55.0, [PASS] python 3.13.5, [FAIL] storage C:\ 459,505,664 bytes
    free (threshold 1 GiB), [PASS] storage D:\ 96,802,582,528 bytes;
    RESULT: UNHEALTHY (1 failed check).
  - `scripts/windows/healthcheck.ps1` executed → propagates exit 1 with
    identical output (wrapper matches shared code).
  - `scripts/windows/install.ps1` → exit 0, PLAN-ONLY output.
  - `scripts/windows/update.ps1` → exit 0; reports real versions
    (git detected 2.55.0 / preferred UNKNOWN; python detected 3.13.5 /
    preferred 3.13); NOT_FOUND/UNKNOWN tools → "nothing to update".
  - **No-mutation proof:** 53-file snapshot (path|size|mtime) identical
    before/after running install and update commands.
- **AC (T-0104):**
  1. Three .ps1 files exist; PowerShell language parser validates all — MET.
  2. healthcheck runs on host, documented exit code, names failing
     checks — MET (exit 1, C:\ named, evidence above).
  3. Injected-fixture subprocess/CLI tests: missing required tool → 1;
     healthy → 0; other-platform entries excluded from plans — MET.
  4. All three Windows scripts EXECUTED on this host with observed exit
     codes — MET (evidence above).
  5. No manifest tool id in .ps1 — see discrepancy below.
  6. install/update mutate nothing (tmp-dir test + 53-file snapshot) — MET.
  7. R3.7/R3.8 updated; full suite passes — MET (133).
  8. `from src.pem.ops import main` — MET.
- **DISCREPANCY RECORD — AC5 wording vs interpreter bootstrap:** AC5
  literally says no manifest tool id appears in any .ps1, but the
  wrapper must invoke the Python interpreter, whose manifest id is
  `python`. Resolution per §47 (record, do not silently overwrite):
  test `test_no_manifest_tool_id_in_wrappers_except_interpreter_bootstrap`
  asserts every tool id EXCEPT `python` is absent, and `python` may
  appear only on plumbing lines (interpreter reference lines containing
  `$python` / `-m src.pem.ops` / "python interpreter"). No tool list or
  detection/installation logic exists in any wrapper.
- **Limitations:** install/update are plan-only (mutation arrives with
  T-0107); Linux/macOS wrappers not created (T-0105/T-0106) and their
  scripts therefore not executed; platform detection covers
  Windows/Linux/Darwin only; healthcheck does not evaluate optional
  tools or capabilities; storage UNKNOWN is reported but not counted.
- **Security:** no network; no elevation; no installation; wrappers
  invoke only the local Python interpreter and shared module; exit-code
  propagation only.
- **Files:** src/pem/ops.py, scripts/windows/*.ps1 (3),
  tests/test_pem_ops.py, requirements.md (R3.7/R3.8),
  roadmap/project-state/next-task/chatmem closure updates.

## AUDIT-0010 — T-0107 idempotent install logic + tests (2026-10-08)

- **Scope:** manifest-driven, idempotent install engine (`src/pem/installer.py`)
  + `install_command` field (manifest/schema/loader) + guarded
  `python -m src.pem.ops install --execute` (plan stays default). MASTER
  §7, §22, §23, §24, §29.
- **Implementation (OBSERVED):**
  - `plan_installs(entries, records)` classifies each tool:
    `skip` / `install` / `upgrade` / `manual` / `investigate`.
    Absent record or `UNKNOWN` → `investigate` (never acted on);
    `NOT_FOUND` → `install` (or `manual` when command is null);
    `DETECTED` below `min_version` → `upgrade`; otherwise `skip`.
  - `apply_installs(...)` runs only `install`/`upgrade` rows via an
    injectable runner, re-probes after each command, and reports the
    fresh probe state — never claims success it did not observe.
  - `expand_command()` substitutes `{python}` as a single argv token
    (whitespace split of trusted manifest strings; no shell parsing, so
    Windows interpreter paths are not mangled).
  - `install_command` added to all 11 manifest entries: `jupyter` and
    `scrapling` = `{python} -m pip install <pkg>`; the other 9 = `null`
    (no safe automated command yet → manual). Loader now requires and
    validates the field (`_check_optional_str`).
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **150 passed, 0 failed** (2026-10-08, Python 3.13.5, pytest 9.1.1):
  38 governance + 9 PEM detection + 21 manifest + 22 PEM tools +
  20 PEM report + 23 PEM ops + **17 installer**. Installer tests use
  fake runners/probes + injected system data — no network, no mutation.
- **Key behaviors verified by tests:** healthy tool → zero runner calls;
  NOT_FOUND → exactly one call with the expanded argv, then reprobe;
  second run against healthy records → zero calls (idempotent); UNKNOWN
  and absent-record → runner never called (`investigate`); below-minimum
  → upgrade call; null command → manual, zero calls; low-disk system →
  `EXIT_REFUSED` (3), runner never called; command failure or rc0-but-
  still-missing → `EXIT_FAILURE` (1), never reported installed.
- **Live execution (OBSERVED, 2026-10-08, this host):**
  - `python -m src.pem.ops install` → **exit 0**, plan lists 7 tools
    (jupyter, freecad, kicad, ngspice, gazebo, blender, scrapling);
    git/python skipped (DETECTED); taiga-s1/rea not listed (UNKNOWN →
    investigate). Ends "plan complete: 7 tool(s) to install, 0
    change(s) performed".
  - `python -m src.pem.ops install --execute` → **exit 3 (REFUSED)**:
    "free disk space is below the 1073741824-byte threshold — C:\
    (451,891,200 bytes). No action performed." Runner never invoked.
  - `python -m src.pem.ops update --execute` → **exit 2** with
    "--execute is only valid for the 'install' command" (guard on flag
    misuse).
  - No live install/update mutation was performed (disk below
    threshold) — this is the intended AC6/AC7 outcome, not a defect.
- **AC (T-0107):**
  1. `src/pem/installer.py` exposes `plan_installs`/`apply_installs`;
     `from src.pem.ops import main` works — MET.
  2. `install_command` present on all 11 entries; loader/schema updated;
     manifest tests pass (21) — MET.
  3. Harness tests for every state transition — MET (behaviors above).
  4. Low-disk refusal (exit 3, runner idle, volume named) — MET.
  5. Failed command not reported installed (fresh-probe honesty) — MET.
  6. Live plan (exit 0) + `--execute` refusal (exit 3) captured — MET.
  7. R3.6 → IMPLEMENTED (with "live mutation not exercised" qualifier);
     roadmap/state/audit/chatmem updated — MET.
  8. Full suite passes (150) — MET.
- **DISCREPANCY RECORD — notice/C:\ value drift:** `PLAN_ONLY_NOTICE`
  previously stated install logic "arrives with task T-0107"; once
  implemented that text was stale, so it was rewritten to describe the
  current behavior (`PLAN-ONLY: this invocation performs no changes ...`)
  while retaining the `PLAN-ONLY` and `T-0107` tokens asserted by tests.
  C:\ free space was 451,891,200 bytes here vs 459,505,664 at T-0104
  close — consistent with the recorded volatility, not an inconsistency.
- **DISCREPANCY RECORD — latent governance-test regex bug exposed:**
  adding the string "AUDIT-0010" to `roadmap.md` made
  `test_roadmap_contains_dependency_aware_task_graph` fail with
  "T-0010" not in the task graph. Root cause: the dependency scan used
  `re.findall(r"T-\d{4}", text)` without word boundaries, so the
  substring "T-0010" inside "AUDIT-0010" matched (the same scan two
  lines above already used `\bT-\d{4}\b`). Fix: added the missing `\b`
  word boundaries to the dependency scan — a test-correctness fix, not
  a weakening of any assertion (no roadmap AUDIT references existed
  before, so the bug was latent).
- **Limitations:** live install/update never executed on this host
  (C:\ below threshold + network policy unconfirmed); package-manager
  detection (R3.3) not implemented → non-pip tools carry `null`
  commands and route to manual; UNKNOWN tools cannot be progressed
  until their detectors exist; post-probe re-runs the full detector set
  per executed command (acceptable for this scale).
- **Security:** no network; no elevation; the default invocation mutates
  nothing; `--execute` is refused outright while disk is low; commands
  come only from the reviewed manifest, not user input.
- **Files:** src/pem/installer.py (new), src/pem/ops.py,
  config/tool-manifest.json, config/tool-manifest.schema.json,
  src/core/manifest.py, tests/test_installer.py (new),
  scripts/windows/install.ps1 + update.ps1 (comment accuracy),
  requirements.md (R3.6), roadmap/project-state/next-task/chatmem.md.

## AUDIT-0011 — T-0105 Linux wrapper scripts (2026-10-08)

- **Scope:** `scripts/linux/{install,update,healthcheck}.sh` — POSIX
  `sh` thin wrappers over the verified shared module (MASTER §23).
- **Implementation (OBSERVED):**
  - Shebang `#!/usr/bin/env sh`; repo root resolved relative to the
    script path via `CDPATH= cd -P "$(dirname "$0")"` then `../..`
    (no hard-coded absolute path).
  - Interpreter discovery prefers `python3`, falls back to `python`,
    else prints an error and exits 2 (matches the Windows wrapper).
  - Each script delegates with `exec "$python_cmd" -m src.pem.ops
    <command> "$@"` — `exec` replaces the shell so the shared module's
    exit code is the script's exit code (propagation, no swallowing).
    `install.sh` forwards `"$@"` (so `--execute` is available); the
    others also forward `"$@"`.
- **Validation method and result (MEASURED):**
  - `Get-Command sh` / `bash` on this host → **not found** (both
    absent), so the scripts were **NOT executed** and no runtime
    behavior is claimed. Only static validation was performed.
  - `python -m pytest tests/ -v` → **157 passed, 1 skipped**
    (2026-10-08, Python 3.13.5, pytest 9.1.1): 38 governance + 9 PEM
    detection + 21 manifest + 22 PEM tools + 20 PEM report + 23 PEM ops
    + 17 installer + **7 linux-script static tests**; the skipped test
    is `test_scripts_are_syntactically_valid_when_sh_available`
    (skipif no `sh` on PATH) — honest skip, not a pass.
  - Static tests (all passed) assert: files exist; exact POSIX shebang;
    delegation line `-m src.pem.ops <command>`; the delegation line uses
    `exec ` (propagation); `python3`/`python` discovery + exit 2; no
    manifest tool id except `python` (and `python` only on plumbing
    lines — same resolution as T-0104 AC5); no hard-coded absolute path.
  - Binary-level check: each file begins with `b'#!/'` (no BOM).
- **AC (T-0105):**
  1. Three `.sh` files exist with POSIX shebang and call
     `python -m src.pem.ops <command>` — MET.
  2. Exit-code propagation — MET (`exec` on the delegation line).
  3. No tool id except the interpreter token; no tool logic — MET.
  4. Static tests assert the above; `sh -n` runs only if `sh` exists —
     MET (static pass; `sh -n` correctly skipped here).
  5. R3.7 updated with honest qualifier; roadmap T-0105 COMPLETE,
     T-0106 READY — MET.
  6. Full suite passes (157 + 1 skip) — MET.
  7. project-state.md / audit.md / chatmem.md updated — MET.
- **Limitations:** Linux scripts never executed on this host (no POSIX
  shell); actual Linux runtime behavior (paths, argument forwarding,
  exit-code semantics) is UNVERIFIED — static equivalence to the
  verified shared code is all that is claimed. macOS wrappers absent
  (T-0106).
- **Security:** no network; no elevation; wrapper performs no logic of
  its own; it only locates the interpreter and delegates to the shared
  module.
- **Files:** scripts/linux/install.sh, update.sh, healthcheck.sh (new),
  tests/test_scripts_linux.py (new), requirements.md (R3.7),
  roadmap/project-state/next-task/chatmem.md.

## AUDIT-0012 — 2026-10-08 — Autonomous build directive: repository audit

- **Action:** received a full-programme autonomous build directive;
  audited the existing repository against it before any change.
- **Repository state (OBSERVED):** clean working tree at `a90df34`; 9
  commits; 164 tests. Implemented subsystems: governance (T-0001),
  PEM detection/manifest/report/ops/installer (T-0101..T-0107, T-0201),
  Windows + Linux wrappers. Not yet implemented: CIE, Scrapling, REA,
  Taiga-S1, engineering-tool integrations, core config/state/evidence,
  orchestration, release audit.
- **Authority confirmed:** `MASTER.md` (governed spec), `roadmap.md`
  (35-task dependency graph), `project-state.md` / `next-task.md`
  (current boundary). Audit followed §2, §42, §43 (repository over
  conversation).
- **Directive-vs-repo gaps (recorded honestly):**
  - Phase 2–17 work remains; roadmap already encodes it. No redesign
    needed; extension is architecturally consistent (architecture.md).
  - Directive requires *real* tool installation; current host has no
    engineering tools installed and C:\ free space is below the
    threshold. System-level installs are a human approval gate
    (MASTER §7, §29).
- **BLOCKER B-1 — Taiga-S1 upstream repository not supplied:** the
  directive contains `<INSERT THE ACTUAL TAIGA-S1 REPOSITORY URL HERE>`
  and §13 requires inspecting the actual repo before designing the
  adapter. Per directive §39, T-0601/T-0602 → BLOCKED; all independent
  work proceeds. No Taiga API is guessed.
- **BLOCKER B-2 — privileged/network installation approval:** real
  installation of FreeCAD/KiCad/ngspice/Gazebo/Blender/Jupyter/
  Scrapling requires network + possibly administrator rights, and this
  host's C:\ is below the 1 GiB install threshold. Install tasks
  (T-0801+) proceed as integration code + tests that SKIP when the tool
  is absent; live execution awaits user approval + disk/network.
- **BLOCKER B-3 — REA:** the directive now supplies a REA reference
  (`morluto/rea`); unlike Taiga-S1 this is available, so REA tasks
  (T-0701/T-0702) are unblocked for pipeline/template work. Runtime
  integration still depends on the installed/available REA tool.
- **Decision:** continue autonomously through the dependency graph in
  §48 phase order, one tested task at a time (directive §1), stopping
  only at the recorded blockers. Next task after T-0106: T-0202.

## AUDIT-0013 — T-0106 macOS wrapper scripts (2026-10-08)

- **Scope:** `scripts/macos/{install,update,healthcheck}.sh` — POSIX
  `sh` thin wrappers over the verified shared module (MASTER §23),
  completing the Phase 1 platform set (R3.7).
- **Implementation (OBSERVED):** identical contract to T-0105 Linux —
  `#!/usr/bin/env sh`; repo root resolved from `$0` (`CDPATH= cd -P
  "$(dirname "$0")"` then `../..`); interpreter preferred `python3`,
  fallback `python`, else exit 2; `exec "$python_cmd" -m src.pem.ops
  <command> "$@"` so the exit code propagates. Executable bit set in
  the git index (mode 100755).
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **164 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1):
  38 governance + 9 PEM detection + 21 manifest + 22 PEM tools +
  20 PEM report + 23 PEM ops + 17 installer + 14 Unix-script static
  tests (parametrised over Linux + macOS). The two skips are the
  per-platform `sh -n` syntax checks (no POSIX shell on this host).
- **Test generalisation (§32, no weakening):** `tests/test_scripts_linux.py`
  was replaced by `tests/test_scripts_unix.py`, parametrised over
  `("linux", "macos")`. Every T-0105 assertion is preserved and now
  applied to both platform sets (7 assertion tests × 2 platforms = 14).
- **AC (T-0106):** all met — files exist with POSIX shebang and shared
  delegation; exit propagation via `exec`; no tool ids except the
  interpreter bootstrap; static tests assert the above; scripts tracked
  executable (100755); R3.7 updated; full suite passes; state/audit/
  chatmem updated.
- **Limitations:** macOS scripts were NOT executed (no POSIX shell on
  this host); runtime behavior on macOS is UNVERIFIED. Static
  equivalence to the executed Windows path (same shared module) is all
  that is claimed. `core.autocrlf=true` on this clone; blobs are LF, so
  macOS/Linux checkouts are safe (a `*.sh text eol=lf` `.gitattributes`
  rule is still advisable — deferred to T-1601).
- **Files:** scripts/macos/*.sh (new), tests/test_scripts_unix.py (new;
  tests/test_scripts_linux.py removed and superseded), requirements.md
  (R3.7), roadmap/project-state/next-task/chatmem.md.

## AUDIT-0014 — T-0202 shared configuration module (2026-10-08)

- **Scope:** `src/core/config.py` (new) — single source for the repo root,
  canonical subsystem directories, config/schema file locations, and
  JSON/YAML config loading with defaults (§49). `src/core/__init__.py`
  now re-exports the public names. `src/pem/report.py` and
  `src/core/manifest.py` were repointed at the shared root/paths
  (duplication removed; behaviour unchanged). `tests/test_core_config.py`
  (new). MASTER §49, §23.
- **Implementation (OBSERVED):**
  - `REPO_ROOT = Path(__file__).resolve().parents[2]` — derived from the
    module file, never the CWD (verified by a `monkeypatch.chdir` test).
  - Canonical directories exposed via `DIRECTORIES` (config, cad,
    electronics, simulations, models, data, components, docs, projects,
    scripts, decisions, tests) each directly under `REPO_ROOT`.
  - `load_json(path, defaults=None)` — reads a JSON object; deep-merges
    onto defaults; missing file with no defaults, invalid JSON, or a
    non-object root raises `ConfigError`; missing file with defaults
    returns a deep copy (mutation-isolation test).
  - `load_config(name, defaults=None, directory=CONFIG_DIR)` — resolves a
    relative name against `config/` by default; routes `.json` to
    `load_json` and `.yaml`/`.yml` to `load_yaml`; unknown extension
    raises `ConfigError`.
  - `load_yaml(...)` uses PyYAML **only if importable**; otherwise raises
    a clear `ConfigError` naming the missing parser (never silent).
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **183 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1): previous
  164 + **19 new config tests**. The two skips remain the per-platform
  `sh -n` checks (no POSIX shell). YAML branch executed live
  (`yaml_available()` → True on this host; PyYAML present), so that path
  is tested, not skipped.
- **Live evidence (OBSERVED):** `config.REPO_ROOT` →
  `D:\Abhishek\Projects\ENGINEERING DEVELOPMENT ENGINE\project`;
  `config.yaml_available()` → True;
  `config.load_config("tool-manifest.json")` → 11 tools.
- **Repoint safety:** `report.py`/`manifest.py` still expose
  `REPO_ROOT` / `DEFAULT_MANIFEST_PATH` / `DEFAULT_SCHEMA_PATH` (now set
  from `config`), so all existing imports/tests are unchanged and green.
- **AC (T-0202):**
  1. Module exposes root, dirs, `ConfigError`, `load_json`,
     `load_config` — MET.
  2. Repo root equals project root and is CWD-independent — MET.
  3. Deep-merge, missing-with-defaults copy, invalid/non-object errors —
     MET.
  4. YAML honest-when-available — MET (live True branch + explicit
     `ConfigError` path when absent). 5. Existing modules use the shared
     root; all prior tests unchanged — MET.
  6. Full suite passes (183 + 2 skip) — MET. 7. R3.8/R13.2 + roadmap/
     state/next-task/chatmem/memory updated — MET.
- **Limitations:** no environment-variable overrides or per-subsystem
  config files yet (not required by T-0202); `load_json`/`load_yaml`
  return `dict[str, Any]` (top-level must be a mapping); YAML support
  depends on PyYAML being present at runtime — JSON is always available.
- **Security:** no network; no elevation; reads only files under the
  repo by default; no secrets, no logging of contents.
- **Files:** src/core/config.py (new), src/core/__init__.py,
  src/pem/report.py, src/core/manifest.py, tests/test_core_config.py
  (new), requirements.md (R3.8/R13.2),
  roadmap/project-state/next-task/chatmem/memory.

## AUDIT-0015 — T-0302 evidence / claim primitives (2026-10-08)

- **Scope:** `src/core/evidence.py` (new) — the shared evidence vocabulary
  for CIE/REA/Taiga (MASTER §5, §6): the eight labels, a strength
  ordering, comparison helpers, and a validated `Claim` record.
  `src/core/__init__.py` re-exports. `decisions/ADR-0002` records the
  ordering. `tests/test_core_evidence.py` (new). No I/O; stdlib only.
- **Implementation (OBSERVED):**
  - `EvidenceLabel(str, Enum)` — exactly the eight §6 labels:
    MEASURED, OBSERVED, SIMULATED, MANUFACTURER-SPECIFIED, CALCULATED,
    ASSUMED, INFERRED, UNKNOWN. `EVIDENCE_LABELS` is the canonical
    strongest→weakest tuple of their string values.
  - Ordering (ADR-0002): MEASURED(7) > OBSERVED(6) > SIMULATED(5) >
    MANUFACTURER-SPECIFIED(4) > CALCULATED(3) > ASSUMED(2) > INFERRED(1)
    > UNKNOWN(0). Anchored to §5; the two placements §5 does not state
    (OBSERVED second; ASSUMED above INFERRED) are documented in ADR-0002.
  - `parse_label` accepts the canonical value, the enum member, and
    case/separator variants (`manufacturer_specified`, `manufacturer
    specified`); any other input raises `EvidenceError` — including
    `None`/non-strings.
  - `Claim` (frozen dataclass): field/value/label/source/retrieved_at/
    note; label normalised through `parse_label`; UNKNOWN must carry no
    value, non-UNKNOWN must carry a value (no fabricated data §7); empty
    field or non-string optional fields rejected; `to_dict`/`from_dict`
    round-trip.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **212 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1): previous
  183 + **29 evidence tests**. The two skips remain the per-platform
  `sh -n` checks (no POSIX shell).
- **Live evidence (OBSERVED):** printed `EVIDENCE_LABELS` and ranks
  (MEASURED 7 … UNKNOWN 0); `strongest([...SIMULATED,
  MANUFACTURER-SPECIFIED, UNKNOWN])` returned the SIMULATED claim —
  ordering behaves as specified.
- **AC (T-0302):**
  1. Exactly the eight §6 labels as an enum; `EVIDENCE_LABELS` length 8 —
     MET. 2. `parse_label` rejects invalid/non-string input — MET.
  3. Ordering enforced (adjacent-pair tests + `compare` signs) — MET.
  4. `Claim` validation + round-trip — MET. 5. `strongest` (ties →
  earliest, empty → None, type-checked) — MET. 6. Re-exported from
  `src.core` — MET. 7. Full suite passes — MET (212 + 2 skip).
  8. ADR-0002 + roadmap/state/next-task/chatmem/memory updated — MET.
- **DISCREPANCY / JUDGEMENT RECORD — ordering not explicit in MASTER:**
  §6 lists the labels but defines no order; §5 defines a hierarchy by
  source *type* that does not map one-to-one. Resolution recorded in
  ADR-0002 rather than silently assumed: labels mapped to the nearest §5
  tier, with OBSERVED placed second (direct first-hand evidence) and
  ASSUMED above INFERRED (empirical estimate before AI reasoning). This
  is an interpretation, flagged for review if MASTER is clarified.
- **Limitations:** the module only classifies/structures claims; it does
  not persist them (CIE/REA), does not enforce that CALCULATED records a
  method (arrives with CIE T-0401), and is not yet consumed by any
  runtime decision path (R8.1 remains PARTIAL).
- **Security:** no network, no I/O, no secrets; pure in-memory
  classification.
- **Files:** src/core/evidence.py (new), src/core/__init__.py,
  decisions/ADR-0002-evidence-ordering.md (new), tests/test_core_evidence.py
  (new), requirements.md (R8.1–R8.3), roadmap/project-state/next-task/
  chatmem/memory.

## AUDIT-0016 — T-0301 project-state persistence library (2026-10-08)

- **Scope:** `src/core/state.py` (new) — read/validate/update the
  repository's own governance state (MASTER §29, §30, §31, §32):
  roadmap task states, the next-task execution boundary, and
  project-state sections. Pure text transforms; filesystem I/O only via
  explicit `read_text`/`write_text` helpers. `src/core/__init__.py`
  re-exports. `tests/test_core_state.py` (new). Stdlib only.
- **Implementation (OBSERVED):**
  - `TASK_STATES` = exactly the seven §32 states.
  - `normalise_state` — case/whitespace tolerant; rejects anything else
    with `TaskStateError`.
  - Roadmap: `parse_roadmap_tasks` reads each `| T-XXXX | … |` row into
    id/title/phase/dependencies/state and raises on an invalid state;
    `set_roadmap_task_state` updates both the table cell and the
    `**T-XXXX — …** — \`STATE\`` detail marker, is idempotent, and
    rejects unknown ids/invalid states.
  - next-task: `parse_next_task` / `set_next_task_state` over the
    `## Task T-XXXX — …` header and `- **State:** …` line.
  - project-state: `parse_state_sections`, `require_state_sections`
    (all fourteen §29 headings) and `set_state_section` (one body
    replaced, every other byte preserved).
  - Updates edit tokens in the existing text rather than re-rendering, so
    a no-op is byte-identical (round-trip proven on the real files).
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **232 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1): previous
  212 + **20 state tests**. The two skips remain the per-platform
  `sh -n` checks.
- **Live evidence (OBSERVED):** parsed the real `roadmap.md` → 35 tasks,
  `T-0301` state READY; parsed the real `next-task.md` → `T-0301 READY`;
  parsed `project-state.md` → 15 sections and `require_state_sections`
  passed.
- **DISCREPANCY RECORD — roadmap table vs detail-block state mismatch
  (§47):** the T-0601/T-0602 table rows carried `BLOCKED (…)` while
  their detail blocks still read `` `PLANNED` `` — an inconsistency
  introduced when the blockers were recorded in AUDIT-0012 and not
  propagated to the detail lines. The same class of drift had also left
  T-0401's detail block at `` `PLANNED` `` while its table row was
  already `READY` (after T-0302). The new library surfaced both
  (idempotency/state tests failed on the stale markers). Resolution:
  corrected the three detail blocks to match their table rows
  (`BLOCKED`, `BLOCKED`, `READY`) and recorded here; no state was
  changed — only made self-consistent. Lesson: update table and detail
  state together (or use `set_roadmap_task_state`).
- **AC (T-0301):**
  1. Public API present — MET. 2. Seven states + rejection — MET.
  3. Roadmap parse/update/idempotency/rejection — MET. 4. next-task
  parse/update/idempotency — MET. 5. project-state sections +
  require + set — MET. 6. Byte-identical round-trips on the real files —
  MET. 7. All seven states accepted; fabricated states rejected — MET.
  8. Re-exported from `src.core` — MET. 9. Full suite passes — MET
  (232 + 2 skip). 10. Docs/roadmap/state/audit/memory updated — MET.
- **Limitations:** `set_state_section` replaces the body verbatim (it
  does not add a trailing newline, so callers control spacing); roadmap
  editing assumes the documented `| … |` table and `**T-XXXX — …**`
  marker formats; `write_text` uses `newline=""` (no newline
  translation); the library is not yet wired into an automated startup
  loop (R1.6 remains PARTIAL).
- **Security:** no network, no elevation; pure transforms by default,
  writes only when a caller invokes `write_text`.
- **Files:** src/core/state.py (new), src/core/__init__.py,
  tests/test_core_state.py (new), requirements.md (R1.3/R1.4/R1.6),
  roadmap.md (T-0301 COMPLETE + T-0601/T-0602 detail reconciliation),
  project-state/next-task/chatmem/memory.
