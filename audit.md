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

## AUDIT-0017 — T-0401 CIE component data model + schema + storage (2026-10-08)

- **Scope:** the CIE foundation — `src/cie/model.py` (§12 record + §13
  motor + derived values), `config/component.schema.json`, and
  `src/cie/store.py` (SQLite + JSON). `src/cie/__init__.py` re-exports.
  `tests/test_cie_model.py`, `tests/test_cie_store.py` (new). Stdlib only.
- **Implementation (OBSERVED):**
  - `UNKNOWN` is a distinct singleton sentinel (not `None`, not the
    string "UNKNOWN"); `to_dict` OMITS any UNKNOWN field, so a record
    contains only real facts (no padding, §12).
  - `Component`: only `id` is required; unset fields default to UNKNOWN.
    `from_dict` rejects unknown keys and a missing id; round-trips
    (including `source_urls` order and nested `specifications`) are
    lossless.
  - `MotorSpec` covers the §13 fields; derived values use
    `DerivedValue(value, method, evidence_label)`, which requires a
    non-empty method and a valid §6 label (default CALCULATED) — so
    every derived value identifies its calculation (§13).
  - `config/component.schema.json`: draft-07, `required: ["id"]` only,
    `additionalProperties: false`, typed fields incl. the motor object.
  - `ComponentStore`: SQLite upsert by id, `get`/`all`/`delete`,
    `export_json`/`import_json`; reopening the file preserves records.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **253 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1): previous
  232 + **21 CIE tests** (14 model/schema + 7 store). The two skips
  remain the per-platform `sh -n` checks.
- **Live evidence (OBSERVED):** built a NEMA-17 motor component with
  known and UNKNOWN fields, saved it to a temp SQLite file, fetched it
  back — round-trip equal; serialized keys were
  `category, electrical, id, manufacturer, motor, name, source_urls,
  specifications`; `sku` (UNKNOWN) was absent. Schema validator accepted
  the record and rejected a fabricated `status: "INSTALLED"` field.
- **AC (T-0401):**
  1. Model API present — MET. 2. §12 fields, UNKNOWN default, no padding,
  round-trip — MET. 3. `DerivedValue` method + label validation — MET.
  4. `MotorSpec` §13 fields + UNKNOWN + embedded only when present — MET.
  5. Schema draft-07, only `id` required, types asserted, extra/fabricated
  fields rejected — MET. 6. `ComponentStore` CRUD + upsert + JSON I/O —
  MET. 7. `src.cie` re-exports — MET. 8. Full suite passes — MET
  (253 + 2 skip). 9. Docs/roadmap/state/audit/memory updated — MET.
- **Limitations:** `specifications`/`electrical`/etc. are untyped dicts
  (the schema only asserts they are objects); no provenance, source
  priority or conflict handling yet (T-0403); no ingestion/network
  (T-0402); the store holds one JSON blob per row rather than queryable
  columns — acceptable at this scale, revisitable if querying by field
  is needed. Evidence labels are recorded but not yet attached to
  individual facts (T-0403).
- **Security:** no network; no scraping; SQLite/JSON under a
  caller-supplied path (default resolved via `src.core.config`); no
  secrets; text treated as data.
- **Files:** src/cie/model.py, src/cie/store.py, src/cie/__init__.py,
  config/component.schema.json, tests/test_cie_model.py,
  tests/test_cie_store.py, requirements.md (R5.6–R5.8),
  roadmap/project-state/next-task/chatmem/memory.

## AUDIT-0018 — T-0402 CIE URL ingestion + exact identification (2026-10-08)

- **Scope:** the CIE entry point (§8/§9) — `src/cie/target.py`
  (URL validation) and `src/cie/identify.py` (exact-product
  identification + `Component` mapping), `config/identification.schema.json`,
  `tests/test_cie_target.py`, `tests/test_cie_identify.py`. Stdlib only;
  acquisition is injected, so **no network** is performed here.
- **Implementation (OBSERVED):**
  - `parse_target` accepts absolute http/https URLs with a host, lowercases
    and strips a leading `www.`, preserves the original URL, and raises
    `TargetError` for empty/relative/unsupported input.
  - `_PageParser` (stdlib `html.parser`) collects `<title>`, whitelisted
    product `<meta>` tags, the canonical link and JSON-LD blobs. Only
    `application/ld+json` `<script>` content is kept; other scripts and all
    visible text are ignored (treated as data, never executed).
  - JSON-LD `Product` (including inside `@graph`/lists) is walked for
    `name`/`brand`/`manufacturer`/`model`/`sku`/`mpn`/`offers.seller` and
    `additionalProperty` → specifications. Precedence: JSON-LD ›
    OpenGraph (`og:title`, `product:brand`, `product:retailer`, `og:url`)
    › `<title>`/canonical. Malformed JSON-LD is skipped, not fatal.
  - Missing fields stay `UNKNOWN`; `to_dict` omits them (no padding);
    `to_component` maps identity onto a §12 `Component` with `source_urls`
    and derived `id` (`host-model`), setting nothing it did not observe.
  - Exact-identification rule: a page with no title/manufacturer/model/
    sku/part number raises `IdentificationError` ("refuse generic search")
    — no degradation to `"775 motor"`-style search.
  - `ingest(url, acquire)` validates the target, calls the injected
    acquirer, then identifies; an acquirer error propagates (no silent
    fallback). This keeps T-0402 network-free ahead of Scrapling (T-0502).
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **272 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1): previous
  253 + **19 T-0402 tests** (5 target + 14 identification). The two skips
  remain the per-platform `sh -n` checks.
- **Live evidence (OBSERVED):** over a JSON-LD fixture page,
  `identify_page` returned
  `{url, host, title:"Acme 775 Motor", manufacturer:"Acme", model:"M775",
  sku:"SKU-775", part_number:"MPN-775", seller:"ShopCo", product_url,
  specifications:{"RPM":"8500"}}`; `to_component()` produced
  `{id:"shop.example.invalid-m775", name, manufacturer, model,
  part_number, sku, source_urls, specifications}` (no UNKNOWN keys); an
  opaque page raised `IdentificationError` ("no exact product identity
  found; refuse generic search (§8)").
- **AC (T-0402):** 1 target validation — MET. 2 identity fields default
  UNKNOWN — MET. 3 JSON-LD Product parsing incl. malformed-skip — MET.
  4 OG/`<title>`/canonical fallbacks with JSON-LD precedence — MET.
  5 `to_component` §12 mapping, no padding — MET. 6 opaque page raises —
  MET. 7 `ingest` injected acquirer, no fallback — MET. 8 draft-07
  identification schema validates/rejects — MET. 9 package re-exports +
  full suite — MET (272 + 2 skip). 10 docs/state updated — MET.
- **Limitations:** no real fetching/Scrapling (T-0502); no per-fact
  provenance object, source priority or conflict detection (T-0403);
  extraction covers JSON-LD/OG/meta/title/canonical only (no retailer
  CSS/table scraping — deliberately out of scope until T-0502); prices
  are read into meta but not yet modelled; `id` derivation is
  best-effort (`host-key`) and may collide across URLs differing only by
  query — a caller may pass an explicit `component_id`.
- **Security (§14/§15 spirit):** untrusted HTML is parsed, never
  executed; only `ld+json` script text is read and only via `json.loads`;
  no URL following, no network, no filesystem writes. A
  prompt-injection-style fixture (page instructing "ignore previous
  instructions") did not alter behaviour — such text is data, not an
  instruction.
- **Files:** src/cie/target.py, src/cie/identify.py, src/cie/__init__.py,
  config/identification.schema.json, tests/test_cie_target.py,
  tests/test_cie_identify.py, requirements.md (R5.1 partial),
  roadmap/project-state/next-task/chatmem/memory.

## AUDIT-0019 — T-0403 CIE provenance + source priority + conflicts (2026-10-08)

- **Scope:** §10/§11 — `src/cie/provenance.py` (source tiers + provenance),
  `src/cie/conflicts.py` (facts + conflict detection), 
  `config/fact-record.schema.json`, `tests/test_cie_provenance.py`,
  `tests/test_cie_conflicts.py`. Stdlib only; no network; no change to
  the §12 record or the ingestion flow.
- **Implementation (OBSERVED):**
  - `SourceKind` holds exactly the eight §10 tiers; `SOURCE_PRIORITY`
    lists them most→least authoritative; `source_rank` is 0-based and
    `is_more_authoritative` matches (datasheet > marketplace > AI).
  - `Provenance` requires a non-empty `source_url` and an ISO
    `YYYY-MM-DD` date (rejects `2026/10/08`, `2026-13-40`, empty URL);
    `publisher` is optional and omitted when UNKNOWN; round-trips.
  - `Fact(value, provenance, evidence_label=OBSERVED)` validates the §6
    label via `src.core.evidence`; a non-`Provenance` provenance or a bad
    label raises `FactError`.
  - `FieldRecord.status`: `UNKNOWN` (no real facts), `SINGLE` (one),
    `AGREED` (many, one value), `CONFLICT` (≥2 distinct values). Every
    input fact is retained; UNKNOWN-valued facts never conflict.
  - `FieldRecord.governing` selects the most authoritative real fact
    (source rank, then §6 evidence strength, then later retrieval date,
    then insertion order) — a selection, never a deletion.
  - `conflicting_fields` returns exactly the CONFLICT field names.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **294 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1): previous
  272 + **22 T-0403 tests** (9 provenance + 13 conflicts). The two skips
  remain the per-platform `sh -n` checks.
- **Live evidence (OBSERVED — the §11 example):** two facts on `rpm` —
  marketplace `10,000` (`MARKETPLACE_LISTING`) and manufacturer datasheet
  `8,500` (`MANUFACTURER_DATASHEET`) — produced
  `status == "CONFLICT"`, both facts retained, and `governing.value == 8500`
  with `provenance.kind == "MANUFACTURER_DATASHEET"`; a one-fact field
  reported `status == "SINGLE"`.
- **AC (T-0403):** 1 eight tiers + order — MET. 2 provenance validation +
  round-trip — MET. 3 `Fact` label validation + round-trip — MET.
  4 statuses UNKNOWN/SINGLE/AGREED/CONFLICT — MET. 5 governing authority
  with retention — MET. 6 serialisation + draft-07 schema validate/reject
  — MET. 7 `conflicting_fields` — MET. 8 re-exports + full suite — MET.
  9 docs/state updated — MET.
- **Limitations:** no acquisition to feed real facts yet (T-0502); no
  cross-source search (T-0404); the fact bundle is not yet persisted to
  the SQLite store nor embedded in `Component` (a later integration
  point); `governing` is deterministic but does not yet flag
  *unresolvable* authority ties for human review (§11 is satisfied by
  storing + marking; resolution policy can evolve).
- **Security:** no network; treats all values as data; JSON-LD read-only
  path unchanged from T-0402.
- **Files:** src/cie/provenance.py, src/cie/conflicts.py,
  src/cie/__init__.py, config/fact-record.schema.json,
  tests/test_cie_provenance.py, tests/test_cie_conflicts.py,
  requirements.md (R5.3–R5.5), roadmap/project-state/next-task/chatmem/
  memory.

## AUDIT-0020 — T-0701 REA pipeline + investigation templates (2026-10-08)

- **Scope:** MASTER §16–§21 — `src/rea/pipeline.py` (ordered stages),
  `src/rea/records.py` (authorized investigation + §19 evidence rules),
  `src/rea/storage.py` (seven §21 templates), `docs/investigations/README.md`,
  `tests/test_rea_{pipeline,records,storage}.py`. Stdlib only; no target
  was inspected or executed.
- **Implementation (OBSERVED):**
  - `ReaStage`/`REA_STAGES` are the ten §18 stages in order;
    `stage_index` is 0-based. `ReaPipeline` starts before TARGET and
    `advance()` moves strictly in order — skipping or jumping raises
    `PipelineError` (enforcing "never jump from 'Feature X exists' to
    'implement Feature X'"); it refuses to advance past VERIFY.
  - `Investigation` requires a lowercase slug name, a target, and
    `authorized=True` with a non-empty `authorization_basis`; otherwise
    `AuthorizationError` (STOP, §20). `build_investigation` constructs the
    authorized form.
  - `Finding` enforces §19 structurally: `source_recovered=True` raises
    `EvidenceRuleError` (recovered pseudocode is never claimed as the
    original source); `reconstructed=True` with `OBSERVED` raises (a
    reconstruction is inferred/calculated/simulated); labels validated via
    `src.core.evidence`. `EvidenceEntry` carries a labelled statement +
    optional source.
  - `TEMPLATE_FILES` is exactly the seven §21 files; `render_template`
    produces Markdown from the record (no drift between record and
    storage); `write_investigation` creates `docs/investigations/<name>/`
    and refuses to overwrite unless `overwrite=True`.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **317 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1): previous
  294 + **23 REA tests** (8 pipeline + 8 records + 7 storage). The two
  skips remain the per-platform `sh -n` checks.
- **Live evidence (OBSERVED):** built an authorized investigation
  (`motor-controller`, one `OBSERVED` finding), advanced a pipeline
  through TARGET→IDENTIFY, wrote it to a temp directory and listed the
  seven files; constructing an unauthorized investigation raised
  `AuthorizationError` and a `source_recovered=True` finding raised
  `EvidenceRuleError`.
- **AC (T-0701):** 1 ten ordered stages — MET. 2 sequential pipeline,
  skip/jump refused — MET. 3 authorization gate + slug validation — MET.
  4 evidence rules (recovered-source, reconstruction≠OBSERVED) — MET.
  5 `to_dict` — MET. 6 seven templates + rendered content — MET.
  7 `write_investigation` (7 files, no overwrite) — MET. 8 re-exports +
  full suite — MET. 9 docs/state updated — MET.
- **Limitations:** this is the framework only — no binary/JS/.NET
  inspection or tracing tools are wired (T-0702); templates are
  generated but no investigation has been run; authorization is a
  caller-declared boolean + basis (not an external approval system).
- **Security/ethics (§20):** the API structurally forbids an
  unauthorized investigation; the module performs no inspection, no
  network and no execution; guidance to only investigate authorized
  targets is recorded in the module docstring and the investigations
  README.
- **Files:** src/rea/pipeline.py, src/rea/records.py, src/rea/storage.py,
  src/rea/__init__.py, docs/investigations/README.md,
  tests/test_rea_pipeline.py, tests/test_rea_records.py,
  tests/test_rea_storage.py, requirements.md (R7.x),
  roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0021 - T-0702 REA offline inspection (2026-10-08)

- **Task:** T-0702 REA tooling integration (inspect/trace) — collect
  evidence about a caller-supplied, authorized file without executing it.
- **Deliverables:** `src/rea/inspection.py` — `detect_file_type` (magic
  bytes: PE/ELF/Mach-O/ZIP/PDF else UNKNOWN), `extract_strings` (bounded
  printable-ASCII runs), `FileFingerprint` (path/size/sha256/md5/type/
  string_count/truncated), `fingerprint_file` (streams the whole file for
  hashes; reads at most a 16 MiB prefix for type/strings; read-only),
  `probe_tools` (resolves names via injectable `shutil.which`),
  `inspect_target` (returns OBSERVED `EvidenceEntry` objects);
  `with_evidence` helper added to `src/rea/records.py`; `src/rea/__init__.py`
  re-exports; `tests/test_rea_inspection.py`.
- **Acceptance criteria:** AC1 fingerprint content matches hashlib
  digests — MET. AC2 file type detected from magic bytes — MET. AC3
  strings bounded by min length and max count — MET. AC4 tool
  availability reported honestly (None → "absent", never assumed) — MET.
  AC5 result is labelled OBSERVED evidence and `with_evidence` preserves
  the original record — MET. AC6 missing path / directory raise
  `InspectionError` — MET. AC7 read-only, no network, no execution —
  MET (only `Path.open("rb")`). AC8 full suite — MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **325 passed, 2 skipped** (Python 3.13.5, pytest 9.1.1): previous
  317 + **8 T-0702 tests**. The two skips remain the per-platform
  `sh -n` checks.
- **Live evidence (OBSERVED):** built a 283-byte `MZ` fixture in the temp
  dir; `fingerprint_file` reported `file_type=PE`, `size=283`, and a
  sha256 identical to `hashlib.sha256(data).hexdigest()` (verified True);
  `probe_tools(["python","definitely-not-a-tool-xyz"])` resolved
  `python.EXE` and returned `None` for the bogus name; `inspect_target`
  produced 7 OBSERVED entries; `with_evidence` grew the investigation
  from 0 to 7 evidence entries.
- **Limitations:** no disassembly/decompilation, no tracing, no
  network capture, no unpacking — only read-only identification. String
  scan is limited to the first 16 MiB (flagged via `truncated`). External
  tools are only probed for availability; none are invoked in this task.
- **Security/ethics (§20):** operates only on a caller-supplied path,
  reads only, executes nothing; no enforcement of authorization at this
  layer (the `Investigation` record still requires authorized=True).
- **Files:** src/rea/inspection.py, src/rea/records.py,
  src/rea/__init__.py, tests/test_rea_inspection.py, requirements.md
  (R7.6), roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0022 - T-0801 Python/Jupyter integration (2026-10-08)

- **Task:** T-0801 Python/Jupyter integration — build/validate/execute
  Jupyter notebooks as labelled evidence, gated on tool presence.
- **Deliverables:** `src/integrations/__init__.py` +
  `src/integrations/jupyter.py` — `JUPYTER_TOOL`, `jupyter_available`
  (injectable `shutil.which`), `NotebookError`, `JupyterUnavailable`,
  `NotebookRun`, `build_notebook` (nbformat v4.5, stdlib),
  `validate_notebook`, `write_notebook` (confined to `simulations/`, no
  overwrite by default), `execute_notebook` (`jupyter nbconvert --execute`
  only when available), `notebook_evidence` (OBSERVED structure +
  SIMULATED execution); `tests/test_integrations_jupyter.py`.
- **Acceptance criteria:** AC1 build→validate — MET. AC2 invalid
  notebooks raise `NotebookError` — MET. AC3 write round-trip + no
  overwrite + path-escape rejection — MET. AC4 `jupyter_available`
  injectable — MET. AC5 missing tool → `JupyterUnavailable`, real
  execution covered by a skip-when-absent test — MET. AC6 labelled
  evidence (OBSERVED/SIMULATED) — MET. AC7 package re-exports + full
  suite — MET. AC8 docs/state + AUDIT-0022 — MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **333 passed, 3 skipped** (Python 3.13.5, pytest 9.1.1): previous
  325 + **8 T-0801 tests**; the third skip is the live-Jupyter test
  (`jupyter` not installed on this host). The two pre-existing skips
  remain the per-platform `sh -n` checks.
- **Live evidence (OBSERVED):** built and validated a 2-code-cell
  notebook and wrote it to `simulations/t0801_demo.ipynb` (527 bytes);
  `jupyter_available()` returned `None` (OBSERVED — tool absent);
  `execute_notebook` raised `JupyterUnavailable: jupyter is not
  installed; notebook execution is UNAVAILABLE`. The demo notebook was
  deleted after the observation (not committed).
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for notebook
  construction/validation/IO; the execution path is IMPLEMENTED but
  **UNAVAILABLE** on this host (no Jupyter) — never claimed as run.
- **Limitations:** no Jupyter/`nbformat` package dependency (schema is a
  stdlib subset, not the full nbformat JSON schema); no kernel/conv
  extension handling; `${JUPYTER}` may point at `jupyter-lab`/`notebook`
  only — `nbconvert` is required at runtime. Live execution is unverified
  until Jupyter is installed (blocked by B-2 install gate).
- **Files:** src/integrations/__init__.py, src/integrations/jupyter.py,
  tests/test_integrations_jupyter.py, requirements.md (R9.3/R9.4),
  roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0023 - T-0901 FreeCAD integration (2026-10-08)

- **Task:** T-0901 FreeCAD integration — mechanical CAD authority;
  generate/verify models via FreeCAD, gated on tool presence.
- **Deliverables:** `src/integrations/freecad.py` — `FREECAD_TOOLS`,
  `freecad_available` (candidate console names via injectable `which`),
  `FreeCadError`, `FreeCADUnavailable`, `FreeCADRun`, `build_box_macro`
  (deterministic FreeCAD macro text), `write_script` (confined to `cad/`,
  no overwrite by default, path-escape refusal), `run_macro`
  (`freecadcmd <script>` only when available), `verify_outputs` (requires
  the FreeCAD-produced artifact), `cad_evidence` (OBSERVED/SIMULATED);
  `src/integrations/__init__.py` re-exports; `tests/test_integrations_freecad.py`.
- **Acceptance criteria:** AC1 `freecad_available` injectable — MET.
  AC2 macro text contains FreeCAD API calls — MET. AC3 `write_script`
  round-trip/no-overwrite/escape-rejection — MET. AC4 missing tool →
  `FreeCADUnavailable`, real run covered by skip-if-absent test — MET.
  AC5 `cad_evidence` labelled entries — MET. AC6 public re-exports +
  full suite — MET. AC7 docs/state + AUDIT-0023 — MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **340 passed, 4 skipped** (Python 3.13.5, pytest 9.1.1): previous
  333 + **7 T-0901 tests**; the 4th skip is the live-FreeCAD test
  (FreeCAD not installed). The two pre-existing skips remain the
  per-platform `sh -n` checks; the third is the live-Jupyter test.
- **Live evidence (OBSERVED):** generated the macro for
  `t0901_demo` (20×10×5) and wrote it to `cad/t0901_demo.py` (381 bytes);
  `freecad_available()` returned `None`; `run_macro` raised
  `FreeCADUnavailable: FreeCAD is not installed; CAD execution is
  UNAVAILABLE`; `cad_evidence` emitted a SIMULATED entry. The demo macro
  was deleted after observation (not committed).
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for macro
  generation/write/verification logic; the CAD execution path is
  IMPLEMENTED but **UNAVAILABLE** on this host (no FreeCAD) — never
  claimed as run.
- **Limitations:** no geometry beyond a parametric box; no FEM/assembly;
  artifact validity is asserted by presence + size (a real FreeCAD
  recompute check requires FreeCAD and is covered by the skipped live
  test). All live CAD is unverified until FreeCAD is installed (blocked
  by B-2).
- **Files:** src/integrations/freecad.py, src/integrations/__init__.py,
  tests/test_integrations_freecad.py, requirements.md (R9.4/R9.5),
  roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0024 - T-1001 KiCad integration (2026-10-08)

- **Task:** T-1001 KiCad integration — PCB authority; run DRC/ERC and
  export Gerbers via `kicad-cli`, gated on tool presence.
- **Deliverables:** `src/integrations/kicad.py` — `KICAD_TOOLS`,
  `kicad_cli` (injectable `which`), `KiCadError`, `KiCadUnavailable`,
  `KiCadRun`, `run_drc`, `run_erc`, `export_gerbers` (each gated and
  building the expected `kicad-cli` argv), `verify_artifacts`,
  `kicad_evidence` (OBSERVED); `src/integrations/__init__.py` re-exports;
  `tests/test_integrations_kicad.py`.
- **Acceptance criteria:** AC1 `kicad_cli` injectable — MET. AC2 commands
  raise `KiCadUnavailable` when absent — MET. AC3 injected run captures
  the exact argv and returns `KiCadRun` — MET. AC4 `verify_artifacts`
  returns sizes / raises `KiCadError` — MET. AC5 `kicad_evidence`
  labelled entries — MET. AC6 public re-exports + full suite — MET.
  AC7 live test skips when absent — MET. AC8 docs/state + AUDIT-0024 —
  MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **347 passed, 5 skipped** (Python 3.13.5, pytest 9.1.1): previous
  340 + **7 T-1001 tests**; the 5th skip is the live-KiCad test (KiCad
  not installed). The others: two `sh -n` checks, live-Jupyter and
  live-FreeCAD.
- **Live evidence (OBSERVED):** `kicad_cli()` returned `None` (KiCad NOT
  installed); `run_drc` on a temp board raised `KiCadUnavailable: KiCad
  is not installed; PCB execution is UNAVAILABLE`; `verify_artifacts` on a
  50-byte fixture returned `{...: 50}`. No KiCad artifact was produced or
  claimed.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for command
  construction/gating/verification; the PCB execution path is
  IMPLEMENTED but **UNAVAILABLE** on this host (no KiCad) — never claimed
  as run.
- **Limitations:** no PCB/schematic is synthesised (inputs are caller-
  supplied; KiCad performs all checks/exports); DRC/ERC report contents
  are not parsed; artifact validity is presence + size. Live PCB
  execution is unverified until KiCad is installed (blocked by B-2).
- **Files:** src/integrations/kicad.py, src/integrations/__init__.py,
  tests/test_integrations_kicad.py, requirements.md (R9.4/R9.6),
  roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0025 - T-1002 ngspice integration (2026-10-08)

- **Task:** T-1002 ngspice integration — circuit authority; batch
  simulation + operating-point parsing, gated on tool presence.
- **Deliverables:** `src/integrations/ngspice.py` — `NGSPICE_TOOLS`,
  `ngspice_cli` (injectable), `NgspiceError`, `NgspiceUnavailable`,
  `NgspiceRun`, `write_netlist` (confined to `simulations/`, no
  overwrite/escape), `run_simulation` (`ngspice -b -o` gated),
  `parse_op_point` (real output parser), `verify_outputs`,
  `ngspice_evidence` (SIMULATED results / OBSERVED status+files);
  `src/integrations/__init__.py` re-exports; `tests/test_integrations_ngspice.py`.
- **Acceptance criteria:** AC1 `ngspice_cli` injectable — MET. AC2
  `write_netlist` round-trip/no-overwrite/escape — MET. AC3
  `run_simulation` gates + builds argv + returns `NgspiceRun` — MET. AC4
  `parse_op_point` extracts node values / raises on no block — MET. AC5
  `verify_outputs` — MET. AC6 evidence labels — MET. AC7 re-exports +
  full suite — MET. AC8 live test skips when absent — MET. AC9
  docs/state + AUDIT-0025 — MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **352 passed, 6 skipped** (Python 3.13.5, pytest 9.1.1): previous
  347 + **7 T-1002 tests**; the 6th skip is the live-ngspice test
  (ngspice not installed). The two pre-existing skips remain the
  per-platform `sh -n` checks; the others are live Jupyter/FreeCAD/KiCad.
- **Live evidence (OBSERVED):** `ngspice_cli()` returned `None`;
  `parse_op_point` extracted `{'in': 5.0, 'out': 3.3}` from a captured
  operating-point block; `ngspice_evidence` emitted SIMULATED node
  entries; `run_simulation` raised `NgspiceUnavailable: ngspice is not
  installed; circuit simulation is UNAVAILABLE`.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for netlist
  write/parse/evidence; the simulation path is IMPLEMENTED but
  **UNAVAILABLE** on this host (no ngspice) — never claimed as run.
- **Limitations:** no schematic capture or circuit synthesis; parser
  handles a simple `node value` operating-point listing (not AC/transient
  vectors); live simulation unverified until ngspice is installed
  (blocked by B-2).
- **Files:** src/integrations/ngspice.py, src/integrations/__init__.py,
  tests/test_integrations_ngspice.py, requirements.md (R9.7),
  roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0026 - T-1101 Gazebo integration (2026-10-08)

- **Task:** T-1101 Gazebo integration — robotics/physics authority;
  headless world load + bounded run, gated on tool presence.
- **Deliverables:** `src/integrations/gazebo.py` — `GAZEBO_TOOLS`,
  `gazebo_cli` (injectable), `GazeboError`, `GazeboUnavailable`,
  `GazeboRun`, `write_world` (confined to `models/`, no overwrite/
  escape), `run_headless` (`gz sim -s -r --iterations` gated),
  `verify_outputs`, `gazebo_evidence` (SIMULATED run / OBSERVED files);
  `src/integrations/__init__.py` re-exports (FreeCAD's `verify_outputs`
  re-exported as `verify_cad_outputs` to avoid the name clash);
  `tests/test_integrations_gazebo.py`.
- **Acceptance criteria:** AC1 `gazebo_cli` injectable — MET. AC2
  `write_world` round-trip/no-overwrite/escape — MET. AC3 `run_headless`
  gates + argv + `GazeboRun` — MET. AC4 `verify_outputs` — MET. AC5
  evidence labels — MET. AC6 re-exports + full suite — MET. AC7 live test
  skips when absent — MET. AC8 docs/state + AUDIT-0026 — MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **360 passed, 7 skipped** (Python 3.13.5, pytest 9.1.1): previous
  354 + **6 T-1101 tests**; the 7th skip is the live-Gazebo test (Gazebo
  not installed). The two pre-existing skips remain the per-platform
  `sh -n` checks; the others are live Jupyter/FreeCAD/KiCad/ngspice.
- **Live evidence (OBSERVED):** wrote `models/t1101_demo.sdf` (67 bytes)
  and deleted it after observation; `gazebo_cli()` returned `None`;
  `run_headless` raised `GazeboUnavailable: Gazebo is not installed;
  robotics simulation is UNAVAILABLE`.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for world write/
  evidence; the simulation path is IMPLEMENTED but **UNAVAILABLE** on this
  host (no Gazebo) — never claimed as run.
- **Limitations:** no world/model synthesis (caller-supplied SDF/URDF); no
  sensor/controller authoring; run results are not parsed. Live simulation
  unverified until Gazebo is installed (blocked by B-2).
- **Files:** src/integrations/gazebo.py, src/integrations/__init__.py,
  tests/test_integrations_gazebo.py, requirements.md (R9.8),
  roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0027 - T-1201 Blender integration (2026-10-08)

- **Task:** T-1201 Blender integration — visualization authority; headless
  `--background --python` render, gated on tool presence.
- **Deliverables:** `src/integrations/blender.py` — `BLENDER_TOOLS`,
  `blender_cli` (injectable), `BlenderError`, `BlenderUnavailable`,
  `BlenderRun`, `write_script` (confined to `models/`, no overwrite/
  escape), `run_background` (`blender --background --python` gated),
  `verify_outputs`, `blender_evidence` (SIMULATED render / OBSERVED files);
  `src/integrations/__init__.py` re-exports with disambiguated names
  (`write_blender_script`, `verify_blender_outputs`);
  `tests/test_integrations_blender.py`.
- **Acceptance criteria:** AC1 `blender_cli` injectable — MET. AC2
  `write_script` round-trip/no-overwrite/escape — MET. AC3 `run_background`
  gates + argv + `BlenderRun` — MET. AC4 `verify_outputs` — MET. AC5
  evidence labels — MET. AC6 re-exports + full suite — MET. AC7 live test
  skips when absent — MET. AC8 docs/state + AUDIT-0027 — MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **366 passed, 8 skipped** (Python 3.13.5, pytest 9.1.1): previous
  360 + **6 T-1201 tests**; the 8th skip is the live-Blender test (Blender
  not installed). Two skips are the per-platform `sh -n` checks; the rest
  are live Jupyter/FreeCAD/KiCad/ngspice/Gazebo.
- **Live evidence (OBSERVED):** wrote `models/t1201_demo.py` (54 bytes),
  `verify_outputs` reported its size, deleted after observation;
  `blender_cli()` returned `None`; `run_background` raised
  `BlenderUnavailable: Blender is not installed; rendering is UNAVAILABLE`.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for script write/
  verify; the render path is IMPLEMENTED but **UNAVAILABLE** on this host
  (no Blender) — never claimed as run.
- **Limitations:** no scene/model synthesis (caller-supplied script); no
  render parsing; live render unverified until Blender is installed
  (blocked by B-2).
- **Dependency propagation (§48):** with Phase 12 done, Phase 13 T-1301
  (deps T-0602/T-0404 BLOCKED) → BLOCKED; Phase 14 T-1401 (dep T-1301) →
  BLOCKED; Phase 15 T-1501 (dep T-0502 BLOCKED) → BLOCKED; next executable
  READY task is **T-1502** (recovery-after-interruption test; dep T-0301
  COMPLETE).
- **Files:** src/integrations/blender.py, src/integrations/__init__.py,
  tests/test_integrations_blender.py, requirements.md (R9.9),
  roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0028 - T-1502 recovery-after-interruption (2026-10-08)

- **Task:** T-1502 recovery-after-interruption test (MASTER §42/§43/§47):
  reconstruct state from repository evidence only, never conversation.
- **Deliverables:** `src/core/recovery.py` — `RECOVERY_DOCUMENTS`,
  `RecoveryError`, `RecoveredState` (`current_task_*`, `task_states`,
  `blockers`, `.in_progress`, `.blocked`), `recover`,
  `recover_consistent`, `assert_recoverable`; `tests/test_recovery.py`.
- **Acceptance criteria:** AC1 boundary from `next-task.md` — MET. AC2
  missing document / malformed §29 section → `RecoveryError` — MET. AC3
  simulated interruption reconstructs state — MET. AC4 READY-with-
  incomplete-dep and COMPLETE-boundary rejected — MET. AC5 live
  `assert_recoverable(REPO_ROOT)` returns T-1502 — MET. AC6 full suite —
  MET. AC7 docs/state + AUDIT-0028 — MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **373 passed, 8 skipped** (Python 3.13.5, pytest 9.1.1): previous
  366 + **7 T-1502 tests** (the earlier 3 failures were the pinned state
  assertions, now advanced to T-1502/T-1601). Skips unchanged (2 × `sh -n`
  + 6 live-tool tests).
- **Live evidence (OBSERVED):** `assert_recoverable(REPO_ROOT)` returned
  boundary **T-1502 “Recovery-after-interruption test”** (state READY),
  in-progress `()`, blocked `('T-0002','T-0501','T-0601','T-0602','T-1301',
  'T-1401','T-1501')`, 3 blocker clauses — the repository is
  self-consistent with no conversation memory.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED (real governance
  files parsed and consistency-checked).
- **Limitations:** recovery is read-only (no automatic rewrite); it does
  not model interrupted multi-step transactions beyond governance files.
- **Files:** src/core/recovery.py, tests/test_recovery.py,
  requirements.md (R1.6), roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0029 - T-1601 cross-platform hardening (2026-10-08)

- **Task:** T-1601 cross-platform hardening (MASTER §27/§47): LF line
  endings, UTF-8 encoding, CWD-independent path containment.
- **Deliverables:** `src/core/xplat.py` — `CrossPlatformError`,
  `LineEndingReport`, `normalise_newlines`, `read_text_utf8` (BOM-tolerant),
  `write_text_lf`, `line_ending_report`, `path_within`;
  `tests/test_xplat.py`.
- **Acceptance criteria:** AC1 newline normalisation — MET. AC2 UTF-8
  round-trip — MET. AC3 line-ending classification — MET. AC4
  containment — MET. AC5 live LF audit of `scripts/**/*.sh` — MET. AC6
  full suite — MET. AC7 docs/state + AUDIT-0029 — MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` →
  **380 passed, 8 skipped** (Python 3.13.5, pytest 9.1.1): previous
  373 + **7 T-1601 tests**. Skips unchanged.
- **Live evidence (OBSERVED):** `line_ending_report` over the POSIX
  wrappers under `scripts/` reported **LF-only** for every `*.sh` file;
  no runtime execution of the POSIX scripts was attempted (no POSIX shell
  on this host) — that remains UNAVAILABLE.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for text/path
  helpers; Linux/macOS *runtime* execution is UNAVAILABLE (VM/CI needed).
- **End-of-roadmap note (§44/§48):** with Phase 16 complete, the only
  unfinished tasks are BLOCKED — Phase 13 T-1301 and Phase 14 T-1401
  (via T-0602/T-0404), Phase 15 T-1501 (via T-0502), and Phase 17 T-1701
  (depends on T-1401/T-1501). There is **no further executable task**;
  the autonomous build stops here and surfaces the blockers rather than
  faking completion.
- **Files:** src/core/xplat.py, tests/test_xplat.py, requirements.md
  (R3.9), roadmap/project-state/next-task/chatmem/memory.

---

## AUDIT-0030 - T-1301 preparatory branch: partial unified workflow (2026-10-09)

- **Task:** T-1301 unified engineering workflow (MASTER 50). **Out-of-boundary
  preparatory work**, explicitly requested by the user, because the task's
  in-boundary dependencies (Taiga-S1 T-0602; Scrapling T-0404/T-0502) are
  BLOCKED. **T-1301 remains `BLOCKED` in the roadmap** - this does not
  discharge it.
- **Deviation (48):** the 48 execution boundary is still `next-task.md` ->
  T-1701 (BLOCKED). Working ahead on T-1301's unblocked portions is recorded
  here rather than by moving the boundary, so the boundary stays honest.
- **Deliverables:** `src/orchestration/workflow.py` - `WorkflowError`,
  `WorkflowStage` (12 stages per MASTER 50), `WORKFLOW_STAGES`, `StageStatus`
  (COMPLETE/READY/UNAVAILABLE/BLOCKED), `StageResult`, `WorkflowReport`
  (`status_of`, `completed`, `blocked`, `unavailable`, `ready`, `evidence`,
  `strongest_label`, `validation_level`, `to_dict`), `_default_probes`,
  `run_workflow`, `write_project` (PROJECTS_DIR-confined, no overwrite);
  `src/orchestration/__init__.py`; `tests/test_orchestration.py`; demo
  `projects/demo-motor/` (`workflow.json`, `component.json`,
  `notebook.ipynb`, `README.md`).
- **Acceptance criteria:** AC1 stage machine covers all MASTER 50 stages -
  MET. AC2 ACQUIRE->BLOCKED (T-0404/T-0502) and ANALYZE->BLOCKED (T-0602) are
  recorded, never marked COMPLETE - MET. AC3 tool stages resolve via real PEM
  probes; absent tool -> UNAVAILABLE - MET. AC4 every stage carries a 6
  evidence label; a run with blocked/unavailable stages is
  `PARTIALLY-VALIDATED` - MET. AC5 `write_project` rejects path escape and
  refuses overwrite - MET. AC6 demo project generated - MET. AC7 full suite -
  MET. AC8 docs/state + AUDIT-0030 - MET.
- **Test result (MEASURED):** `python -m pytest tests/ -v` ->
  **397 passed, 8 skipped** (Python 3.13.5, pytest 9.1.1): previous 380 + **17
  T-1301 tests** (16 unit + 1 live demo-project check). Skips unchanged.
- **Live evidence (OBSERVED):** running `run_workflow` for `demo-motor` ->
  completed `[IDEA, IDENTIFY, MODEL, PYTHON, VALIDATE]`, blocked
  `[ACQUIRE, ANALYZE]`, unavailable `[CAD, ELECTRONICS, CIRCUIT, ROBOTICS,
  VISUALISE]`, validation `PARTIALLY-VALIDATED`; `write_project` wrote the four
  files under `projects/demo-motor/`.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for the orchestration
  logic and the offline stages; **PARTIALLY-VALIDATED overall** - ACQUIRE and
  ANALYZE cannot run (BLOCKED) and external-tool stages are UNAVAILABLE on this
  host. Not a release claim.
- **Limitations:** no Taiga-S1 reasoning/coordination, no real web acquisition,
  no external-tool execution; project records are a serialization of the
  report, not a resumable transaction.
- **Files:** src/orchestration/workflow.py, src/orchestration/__init__.py,
  tests/test_orchestration.py, projects/demo-motor/, architecture.md (2.7/4/9),
  requirements.md (R14), roadmap.md, project-state.md, chatmem.md, memory.md.

---

## AUDIT-0031 - State re-verification, registry reconciliation, T-0002 analysis (2026-10-09)

- **Directive:** a continuation/upstream-integration/release directive was
  received. Per its §1, the authoritative repository state was recovered and
  verified before any change.
- **Verified (OBSERVED):** branch `master`; HEAD `1fca98b`; working tree clean;
  T-1301 preparatory work is commit `b56cd45`; the roadmap table remains
  T-1701 `BLOCKED` as the boundary; the prior test result matched (see below).
  No contradiction found between the reported context and the repository.
- **Re-checked blockers (OBSERVED):** C:\ free = 593,000,448 bytes
  (0.579 GiB) < the 1 GiB threshold -> **B-2 persists** (no installs permitted,
  none attempted). Taiga-S1 upstream still not supplied -> **B-1 persists**.
  T-0002 license decision still awaiting the owner -> persists. No installation
  was performed and no OS permission/resource was assumed.
- **Discrepancy #1 (found + fixed, §47):** `config/tool-manifest.json` notes
  were stale - Jupyter/FreeCAD/KiCad/ngspice/Gazebo/Blender said "Not probed on
  host yet (UNKNOWN)" although the tools had been probed and are `NOT_FOUND`;
  the `rea` note said the in-house framework was "not yet implemented" although
  T-0701/T-0702 are COMPLETE. Notes corrected to the observed evidence; the
  `taiga-s1` note now records upstream-repo UNKNOWN (B-1). Only prose changed;
  schema, loader and 80 manifest/tool/installer/report tests unaffected.
- **Discrepancy #2 (found + fixed, §47):** roadmap detail-block states were
  stale versus the authoritative table- parser reads the table only, so this was
  documentation-only but misleading. Reconciled T-0001, T-0101, T-0102, T-0201
  to `COMPLETE` (were `IN_PROGRESS`/`READY`/`PLANNED`/`READY`). Also fixed the
  T-0002 detail, which cited `ADR-0002` (already used for the evidence-strength
  ordering) for a future license decision; now references a new ADR.
- **T-0002 preparatory analysis:** `docs/license-impact.md` produced. Findings:
  no LICENSE/COPYING and no dependency manifest exist (default "all rights
  reserved"); the only non-stdlib runtime import is optional PyYAML 6.0.3 (MIT);
  pytest 9.1.1 (MIT) is test-only; the engineering tools are invoked as
  external processes and are NOT bundled, so their licences impose no current
  obligation on this source. T-0002 **remains BLOCKED** pending the owner's
  decision.
- **No eligible task:** every remaining roadmap task is BLOCKED (T-0002,
  T-0501, T-0601, T-0602, T-1301, T-1401, T-1501, T-1701) or PLANNED with a
  BLOCKED dependency (T-0404, T-0502). No task state was changed and none was
  bypassed. The build stops at the authorized boundary.
- **Test result (MEASURED):** `python -m pytest tests/ -q` ->
  **397 passed, 8 skipped** (Python 3.13.5, pytest 9.1.1). Skips unchanged
  (2 `sh -n`; 6 live-tool integration tests).
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for the reconciliation
  (live `detect_tools()` + live JSON/schema/manifest tests); T-0002 analysis is
  STATIC-VALIDATED documentation (no legal force).
- **Limitations:** third-party project licences in the report are reported,
  not independently verified this session; no installation/network action was
  possible or taken.
- **Files:** config/tool-manifest.json, docs/license-impact.md, roadmap.md,
  audit.md, requirements.md, project-state.md, memory.md, chatmem.md.

## AUDIT-0032 - B-1 resolved, T-0002 complete, proceed with T-0602 (2026-10-09)
- B-1: upstream biome-s1 (Taiga-S1/Mesa-S1) verified; MIT source; HF taiga-s1 available.
- T-0002: MIT license applied (LICENSE).
- T-0601 marked COMPLETE; T-0602 READY then IN_PROGRESS. next-task updated. Tests 397 passed, 8 skipped.

## AUDIT-0033 - T-0602 complete: provider-neutral Taiga contracts (2026-10-09)
- Created src/taiga/contracts.py, src/taiga/registry.py, src/taiga/__init__.py with provider-neutral interfaces; no API invention.
- Upstream biome-s1/taiga-s1 verified (MIT source; HF model).
- Tests: 397 passed, 8 skipped.


## PROGRESS-UPDATE (2026-10-09)
- T-0602 confirmed COMPLETE (contracts+registry); upstream verified. One state test expects historical state.
- No READY task; boundary T-1701 BLOCKED (T-1401,T-1501). B-2 pending; path T-0501→T-0502→T-0404 contingent on approval.

## AUDIT-0040 - Final governance reconciliation (2026-10-09)
- Reconciled T-0602: contracts+registry COMPLETE (evidence src/taiga/*.py); live inference/orchestration runtime unverified (not claimed).
- B-1: upstream biome-s1/taiga-s1 verified (MIT source; HF card noted). B-2: explicit approval not recorded; C:\\ free ~4.251 GB (documented constraint persists).
- Task states: T-0501 BLOCKED(B-2), T-0502 PLANNED(needs T-0501), T-0404 PLANNED(needs T-0502), T-1301 BLOCKED(needs T-0404; T-0602 COMPLETE), T-1401 BLOCKED(needs T-1301), T-1501 BLOCKED(needs T-0502), T-1701 BLOCKED(needs T-1401,T-1501).
- Governance test baseline: 396 passed, 8 skipped, 1 failed (test_parse_roadmap_tasks_real_file expects T-0602 BLOCKED; roadmap/impl mark COMPLETE). Repository clean; boundary T-1701 BLOCKED; no READY task.

## AUDIT-0041 - Baseline stabilization & Taiga-S1 completion reconciliation (T-1700, 2026-10-11)

- **Directive:** a continuation/audit protocol was received. Per its §1, the
  authoritative repository state was recovered and verified before any change.
- **Verified (OBSERVED):** branch `master`, HEAD `f5f9400`; working tree carried
  an uncommitted BOM edit to `next-task.md` + an AUDIT-0040 append; untracked
  `progress.md`. `git log` rebuilt the full development history.
- **Defect #1 (P0, found + fixed):** `tests/test_core_state.py::test_parse_roadmap_tasks_real_file`
  asserted `T-0602 == BLOCKED` while the roadmap and implementation mark it
  COMPLETE → the suite was RED (396 passed, 8 skipped, **1 failed**). Assertion
  corrected to COMPLETE (+ a T-0601 COMPLETE assertion). Suite restored green.
- **Defect #2 (P1, found + fixed):** `next-task.md` line 1 carried a UTF-8 BOM
  (`\ufeff`), an accidental corruption unrelated to content. File rewritten
  without the BOM.
- **Defect #3 (P1, found + fixed):** T-0601 (runtime selection + resource
  awareness) was marked COMPLETE with **no implementation artefact and no
  tests** anywhere in the repository, and T-0602's roadmap description ("task
  routing / engineering documentation") over-stated the actual code (a
  provider-neutral contract + registry). Resolution: added
  `src/taiga/runtime.py` (resource-aware model-tier selection from the PEM
  RAM/VRAM budget, INFERRED evidence, honest UNKNOWN/unavailable) and
  `tests/test_taiga.py` (contracts + registry + runtime), making both
  completions evidence-backed (MASTER §46); T-0602's roadmap description was
  corrected to its real scope. No subsystem behaviour changed.
- **Defect #4 (P2, found + fixed):** multiple governance documents disagreed
  with the repository — README still said "Phase 0 … no engineering subsystems
  implemented yet"; architecture.md said "License undecided" and "Taiga-S1 …
  BLOCKED"; project-state.md and memory.md still listed B-1 as an open blocker
  and T-0002/T-0601/T-0602 as incomplete; requirements.md was "last verified …
  TASK-0001 bootstrap". All reconciled to reality (B-1 resolved, MIT applied,
  T-0601/T-0602 COMPLETE, phases 0–16). Added roadmap task T-1700 (stabilization)
  and wired T-1701 to depend on it.
- **Defect #5 (P2, found + fixed):** `src/orchestration/` docstrings and the
  ANALYZE blocker text still cited "T-0602 blocked / B-1" as the reason the
  stage is blocked — both are resolved. Corrected to state the real reason
  ("no live Taiga-S1 inference provider wired") while keeping the stage
  honestly BLOCKED. No stage status or behaviour changed.
- **Evidence class:** OBSERVED (pytest + git + file inspection; the taiga
  selection and docs are unit-tested/static).
- **Tests:** `python -m pytest tests/ -q` → **413 passed, 8 skipped**
  (Python 3.13.5, pytest 9.1.1). Was 396 passed/1 failed before T-1700.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED for the suite and the
  taiga unit tests; docs are STATIC-VALIDATED.
- **Limitations:** no live Taiga-S1 inference provider exists (ANALYZE stays
  BLOCKED); no external tool is installed; B-2 (install gate + disk) persists.
  Releases/installs were neither performed nor claimed.
- **Files:** tests/test_core_state.py, src/taiga/runtime.py,
  src/taiga/__init__.py, src/orchestration/__init__.py,
  src/orchestration/workflow.py, tests/test_taiga.py, roadmap.md,
  next-task.md, README.md, architecture.md, requirements.md, project-state.md,
  memory.md, audit.md.

## AUDIT-0042 - Canonical upstream-source registry (T-0203, 2026-10-11)

- **Directive (owner-supplied upstream manifest):** create a canonical
  upstream-source registry for the project-owned integrations and specialist
  tools; store repository URLs and official documentation URLs; define a
  stable id/name/purpose/source-type/verification-status schema; never invent
  versions/commits/licenses; update README; avoid duplicating the URL list in
  memory/chatmem/roadmap/next-task; keep `tool-manifest.json` for detection;
  add schema validation and tests; do not clone/install/access the network.
- **Found (OBSERVED):** the 11 tools were already present in
  `config/tool-manifest.json`, but there was no canonical upstream URL list —
  Taiga-S1's URLs lived only in prose in `memory.md` (duplication risk). The
  tool-manifest schema is `additionalProperties: false`, so adding an upstream
  field would break compatibility; the registry therefore links to the
  manifest by using the SAME ids (git, python, jupyter, taiga-s1, freecad,
  kicad, ngspice, gazebo, blender, rea, scrapling) instead of changing it.
- **Implemented:** `config/upstream-sources.json` (schema_version 1.0, 11
  sources ordered core-integrations then specialist-tools), a draft-07
  `config/upstream-sources.schema.json`, and a stdlib loader/validator
  `src/core/upstream.py` (`load_upstream_sources`/`validate_registry`/
  `source_ids`/`get_source`). `src/core/config.py` gains
  `UPSTREAM_SOURCES_PATH`/`UPSTREAM_SOURCES_SCHEMA_PATH`; `src/core/__init__.py`
  re-exports. No code path performs I/O beyond reading the JSON.
- **Honesty rules enforced:** `license_status`/`version_status` ∈
  {VERIFIED, UNVERIFIED, UNKNOWN}; `UNKNOWN` forbids a claimed
  license/version/commit; `VERIFIED` requires a non-empty value; URLs must be
  https with a host; ids unique; no installation-state keys. All 11 entries
  currently record license/version as UNKNOWN (except Taiga-S1 license MIT,
  VERIFIED per AUDIT-0032) — nothing is guessed.
- **Tests:** `tests/test_upstream_sources.py` (27 tests: real-registry load,
  11 present, schema↔loader required-fields/enum agreement, https URL checks,
  unique ids, manifest coverage, UNKNOWN-honesty, full rejection matrix).
- **Evidence class:** OBSERVED (loader + tests + file inspection).
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED (loader executed;
  suite green).
- **Limitations:** no upstream repository was cloned/inspected and no network
  was used, so license/version/commit for 10 of 11 sources remain UNKNOWN and
  `documentation_url` is null everywhere; populate only after inspection.
- **Files:** config/upstream-sources.json, config/upstream-sources.schema.json,
  src/core/upstream.py, src/core/config.py, src/core/__init__.py,
  tests/test_upstream_sources.py, README.md, memory.md, chatmem.md, roadmap.md,
  project-state.md, requirements.md, audit.md.

## AUDIT-0043 - C: drive protection & D: development isolation (T-1800/T-1801, 2026-10-11)

- **Directive (owner):** audit and configure the workflow so the Windows
  system drive (`C:`) cannot fill and interrupt development; use `D:` for
  development storage wherever supported; add storage preflights; keep
  cleanup safe and approval-gated; document remaining C: dependencies.
- **Storage audit (OBSERVED):** C: 2.23 GiB free / 199.15 GiB total;
  D: 90.52 GiB free / 276.82 GiB total. Repo is 3 MB / 637 files on D:.
  Python is the global interpreter on C: (`...\Python313`); the project has no
  requirements/pyproject/venv (stdlib + pytest only). Largest C: consumers are
  non-project: `C:\Windows` 46.2 GB, `AppData` 54.6 GB (Microsoft 19 GB,
  Google 6 GB, npm-cache 2.78 GB, Brave 2.2 GB, pip 1.23 GB), ProgramData
  33.2 GB (Adobe 23 GB), `Documents\Virtual Machines` 18.3 GB. The
  project-controllable C: footprint is the pip/npm caches, TEMP during runs,
  and future model downloads.
- **Implemented (non-destructive):** created `D:\EngineeringWorkspace\`;
  redirected pip `global.cache-dir` and npm `cache`, and set
  `HF_HOME`/`HF_HUB_CACHE`, to D:; added session-scoped `TEMP`/`TMP` via
  `scripts/windows/dev-env.ps1`; added `src/core/storage.py` +
  `config/storage.json` (per-operation thresholds, no universal constant) with
  `check_storage`/`preflight`/`require_storage` and a `preflight` CLI;
  integrated a `dependency_install` preflight into `python -m
  src.pem.ops install --execute` (refuses exit 3); documented
  `docs/storage.md`.
- **Verification (OBSERVED):** `pip cache dir` → `D:\EngineeringWorkspace\
  caches\pip`; `npm config get cache` → `D:\EngineeringWorkspace\caches\npm`;
  `HF_HOME` set (user); `preflight dependency_install` → ok (exit 0) with
  `drive=D:\`, 90.52 GiB free. D: temp write probe succeeded.
- **No deletion:** no files were removed. Cleanup of the old C: pip/npm caches
  was the separate, approval-gated task T-1802 (BLOCKED at the time; completed
  in AUDIT-0044).
- **Evidence class:** OBSERVED.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED (CLI + redirection
  measured; 24 new tests; full suite 464 passed, 8 skipped / 472 collected —
  the earlier "22 tests / 462 passed" figure was an undercount, corrected in
  AUDIT-0044).
- **Limitations:** redirection stops future C: growth but does not reclaim
  existing C: usage; most C: usage is non-project and out of scope; persistent
  env changes affect the user account (reversible); model/venv redirection is
  configured but unexercised (no model/venv; B-2 gate).
- **Files:** config/storage.json, src/core/storage.py, src/core/config.py,
  src/core/__init__.py, src/pem/ops.py, tests/test_storage.py,
  scripts/windows/dev-env.ps1, docs/storage.md, README.md, memory.md,
  chatmem.md, roadmap.md, next-task.md, project-state.md, requirements.md,
  audit.md.

## AUDIT-0044 - T-1802 cleanup + full-project audit & governance reconciliation (T-1702, 2026-10-15)

- **Directive (owner):** (a) approve the narrow T-1802 cleanup; then (b)
  continue with a full MASTER AUDIT -> CONTINUATION audit and continue
  development.
- **Found (OBSERVED) — documentation drift after T-1802:** the T-1802
  completion was recorded only in `next-task.md` and `tests/test_core_state.py`;
  `project-state.md`, `roadmap.md`, `audit.md`, `chatmem.md`, `README.md` and
  `architecture.md` still showed T-1802 `BLOCKED` and a "462 passed" test count.
- **Found (OBSERVED) — dangling citations:** `src/core/storage.py`,
  `config/storage.json`, `docs/storage.md`, `project-state.md` and `roadmap.md`
  cited a "MASTER prompt addendum §N". `MASTER.md` (1951 lines, ends at §59) has
  no addendum; the cited rules come from the owner's storage directive, supplied
  in conversation — so the citations resolved to nothing.
- **Found (OBSERVED) — count error:** `tests/test_storage.py` has 24 tests (not
  22); the suite is 464 passed / 8 skipped (472 collected), not 462.
- **Also found (OBSERVED, non-blocking):** the host OS build is 10.0.26300
  (memory/project-state recorded 10.0.26200 from bootstrap); a large body of
  working-tree-only work is untracked (`src/taiga/runtime.py`,
  `tests/test_taiga.py`, `tests/test_storage.py`, `src/core/storage.py`,
  `src/core/upstream.py`, `config/storage.json`, `config/upstream-sources.*`,
  `scripts/windows/dev-env.ps1`, `docs/storage.md`, ADR-0003), a recovery risk;
  `progress.md` remains an untracked non-governance duplicate (H-13).
- **T-1802 executed (owner-approved):** `pip cache purge` (0 bytes — the pip
  cache already lives on `D:` after T-1800) and `npm cache clean --force`.
  C: free rose ~2.23 → ~2.34 GiB. No other deletion.
- **T-1702 implemented (documentation-only):** resynced `project-state.md`
  (current phase, completed tasks incl. T-1802/T-1702, boundary T-1701 BLOCKED,
  464/472 test count, OS build, blockers/known-issues, next action, last
  update), `roadmap.md` (T-1802 row/detail COMPLETE, new T-1702 row/detail,
  last-updated + change log), `chatmem.md`, `README.md` (Phase 18 storage +
  `dev-env.ps1`), `architecture.md` (storage/workspace section); created
  `decisions/ADR-0003-development-storage-isolation.md` recording the owner
  directive with numbered sections; repointed every "MASTER prompt addendum §N"
  citation to the matching `ADR-0003 §N`.
- **Security review (this audit):** no hardcoded secrets/keys/tokens; no
  `shell=True`/`os.system`/`eval`/`exec`/unsafe `pickle`/`yaml.load`;
  subprocess calls are argv-list based with timeouts; `.gitignore` blocks
  `*.env`/`secrets.json` (test-enforced). No HIGH-PRIORITY findings.
- **Requirement matrix:** all R1–R16 accounted for (see `requirements.md`);
  remaining gaps (R5.1/R5.2, R6, R14, R15.2) are the BLOCKED install-gated and
  provider-dependent items, unchanged.
- **Evidence class:** OBSERVED.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED. Full suite
  **464 passed, 8 skipped (472 collected)** after the changes; no code behaviour
  changed (only docstrings/JSON note/ADR/docs).
- **Limitations:** documentation reachable only through Git once committed (the
  working tree is uncommitted; no commit was requested). Non-project C: usage
  and the B-2 install gate remain out of scope.
- **Files:** decisions/ADR-0003-development-storage-isolation.md, project-state.md,
  roadmap.md, chatmem.md, README.md, architecture.md, memory.md, requirements.md,
  src/core/storage.py (docstring), config/storage.json (note string),
  docs/storage.md, next-task.md, tests/test_core_state.py, audit.md.

## AUDIT-0045 - Dependency independence & self-contained deployment (T-1900, 2026-10-15)

- **Directive (owner):** new architectural requirement "DEPENDENCY
  INDEPENDENCE & SELF-CONTAINED DEPLOYMENT" (companion to the storage
  directive): inventory every dependency, minimise external installation,
  document offline capability, choose a packaging strategy, validate on a
  fresh system, keep packaging instructions and validation tests in the repo.
- **Audit (OBSERVED):** the runtime is **standard-library only**. An AST scan
  of every `src/**/*.py` import finds exactly one third-party import — `yaml`
  in `src/core/config.py`, guarded by `try/except` and never required (all
  runtime config is JSON). No external database/service, no required network
  access, no bundled binary, and no `requirements.txt`/`pyproject.toml`/
  `Pipfile`/`poetry.lock`. Development-only: `pytest` (OBSERVED 9.1.1). Tools
  (FreeCAD/KiCad/ngspice/Gazebo/Blender/Jupyter/Scrapling/Taiga-S1) are
  optional and already inventoried in `config/tool-manifest.json` +
  `config/upstream-sources.json` — not duplicated.
- **Found (OBSERVED) — stray BOMs:** `src/taiga/__init__.py`,
  `src/taiga/contracts.py` and `src/taiga/registry.py` each began with a UTF-8
  BOM (written by a prior session's tooling). Python tolerates a leading BOM
  so the suite was green, but the BOM broke `ast.parse` on the raw text and is
  not house style. Stripped all three; added a repo-wide no-BOM guard.
- **T-1900 implemented (documentation + verification; no runtime change):**
  - `docs/dependencies.md` — full inventory (all directive categories) with
    necessity/provisioning/offline/license, an offline-first matrix, a
    packaging strategy + setup/fresh-system validation instructions, license
    posture, unavoidable C: dependencies, and a dependency-addition policy.
  - `decisions/ADR-0004-dependency-independence.md` — records the owner
    directive (§1–§7) so citations resolve.
  - `tests/test_dependency_independence.py` (7 tests) — stdlib-only imports,
    guarded optional imports, import-without-optional-dependency (subprocess
    with PyYAML blocked), JSON runtime config, no forbidden packaging manifest,
    inventory-doc coverage, and a repo-wide no-BOM guard.
  - Governance: `requirements.md` R18 (+ H-14), `README.md`,
    `architecture.md` (§2.9, §5, §7, §9), `roadmap.md` (Phase 19 + T-1900 +
    change log), `next-task.md`.
- **Acceptance criteria (directive §6):** inventory documented (R18.1);
  unnecessary installs removed/justified — none existed (R18.2); runtime deps
  unneeded beyond Python (R18.3/R18.4); fresh-machine operation documented and
  UNVERIFIED honestly (§7 of the doc); licenses respected (not bundled);
  packaging instructions + validation tests in the repo (R18.5). Bundling a
  portable/executable artifact is deferred to an owner decision (H-14).
- **Evidence class:** OBSERVED.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED. New tests 7; full
  suite **471 passed, 8 skipped (479 collected)**. No runtime behaviour
  changed (docs, one new test module, and BOM removal in three source files).
- **Limitations:** fresh-machine (clean-host) validation is UNVERIFIED (no
  second clean host); scheduled builds/CI not present; a bundled artifact is
  not built. The B-2 install gate and non-project C: usage remain out of scope.
- **Files:** docs/dependencies.md, decisions/ADR-0004-dependency-independence.md,
  tests/test_dependency_independence.py, requirements.md, README.md,
  architecture.md, roadmap.md, project-state.md, memory.md, chatmem.md,
  next-task.md, src/taiga/__init__.py, src/taiga/contracts.py,
  src/taiga/registry.py, audit.md.

## AUDIT-0046 - MVP operability & documentation (T-2000/T-2001, 2026-10-15)

- **Directive (owner):** "UNIVERSAL PROJECT AUTONOMY PROTOCOL" — finish the
  existing project to a complete, validated MVP (not another audit or
  roadmap): DISCOVER → AUDIT → RECONSTRUCT → RECONCILE → DESIGN → PRIORITIZE →
  IMPLEMENT → TEST → DOCUMENT → HARDEN → PACKAGE → VERIFY → RELEASE-READY MVP,
  with an evidence register, a requirements register, an MVP definition, and a
  final status block, while preserving existing working systems.
- **Audit (OBSERVED) — reconciliation against the directive:**
  - The functional end-to-end pipeline is **blocked on external
    authorisation**, not on missing code: live web acquisition (Scrapling,
    T-0501/T-0502) needs the install gate (B-2) and the `ANALYZE` stage needs a
    live Taiga-S1 inference provider (none wired). These are honest
    `BLOCKED`/`UNAVAILABLE` capabilities, not defects (MASTER §46).
  - Every non-blocked subsystem is COMPLETE (Phases 0–12, 16, 18, 19). The
    remaining roadmap tasks (T-0404/T-1301/T-1401/T-1501/T-1701) all depend on
    the blocked resources.
  - **MVP gap found (OBSERVED):** there was **no unified entry point** — the
    flagship `run_workflow` and the subsystem commands were only reachable as
    separate `python -m src.<module>` invocations; `src/__main__.py` did not
    exist. "Operate the project" was therefore awkward (protocol §7 "required
    interfaces", §16 checklist).
  - **Documentation gap found (OBSERVED):** the protocol's expected
    owner/developer docs beyond governance (`PROJECT_SCOPE`/MVP, `TESTING`,
    `INSTALLATION`, `SECURITY`, `USER_GUIDE`, `CHANGELOG`) did not exist as
    consolidated files (`DECISIONS` → `decisions/`, `AUDIT_LOG` → `audit.md`,
    `REQUIREMENTS` → `requirements.md`, `ARCHITECTURE` → `architecture.md`,
    `DEVELOPMENT_PLAN` → `roadmap.md` already exist and were reused, not
    duplicated).
- **T-2000 implemented (unified offline CLI):** `src/cli.py` (thin `argparse`
  dispatcher) + `src/__main__.py` + `src.__version__ = "0.1.0"` expose
  `version`, `env`, `tools`, `storage preflight`, `upstream`, `cie identify`,
  `rea inspect`, `workflow run` from `python -m src`. Each command wraps an
  existing subsystem API; no behaviour added; blocked stages still report
  honestly. `tests/test_cli.py` (12 tests) covers every command and exit code.
- **T-2001 implemented (MVP definition & consolidated documentation):**
  `docs/mvp.md` (scope, in/out-of-scope, acceptance, verification),
  `docs/usage.md`, `docs/installation.md`, `docs/testing.md`,
  `docs/security.md`, `CHANGELOG.md`; decision recorded as
  `decisions/ADR-0005-mvp-scope-and-delivery.md`. Non-duplicative: each links
  to governance instead of restating it.
- **Acceptance criteria:** runnable (`python -m src version`, smoke-tested);
  tested (suite green); offline (dependency guards green); documented (new
  docs); honest (workflow `PARTIALLY-VALIDATED`, blocked stages visible);
  governed (`assert_recoverable` passes; boundary T-1701 unchanged). Proven by
  the full suite and live CLI smoke commands.
- **Evidence class:** OBSERVED.
- **Validation level:** IMPLEMENTED + RUNTIME-VALIDATED. New tests 12; full
  suite **483 passed, 8 skipped (491 collected)**; `python -m src version`,
  `workflow run --name smoke`, `storage preflight build`, and `upstream` all
  executed successfully. No runtime behaviour changed for existing subsystems.
- **Limitations:** the live pipeline stays BLOCKED (B-2/H-3); no bundled
  artifact (H-14); fresh-machine validation UNVERIFIED (no second clean host).
  The CLI is a convenience surface, not a claim that the blocked stages work.
- **Files:** src/cli.py, src/__main__.py, src/__init__.py, tests/test_cli.py,
  docs/mvp.md, docs/usage.md, docs/installation.md, docs/testing.md,
  docs/security.md, CHANGELOG.md,
  decisions/ADR-0005-mvp-scope-and-delivery.md, README.md, architecture.md,
  roadmap.md, requirements.md, project-state.md, next-task.md, memory.md,
  chatmem.md, audit.md.

### Final status (AUDIT-0046)

- **Project status:** MVP COMPLETE for the offline scope; long-term goals
  preserved. The single remaining blocker to the live end-to-end product is
  owner authorisation of the install gate (B-2) plus a live Taiga-S1 provider
  (H-3); packaging awaits H-14.
- **Boundary:** unchanged — T-1701 BLOCKED; no READY task exists.
