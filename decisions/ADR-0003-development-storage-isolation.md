# ADR-0003 — Development storage isolation & C:-drive protection

- Date: 2026-10-11
- Status: ACCEPTED
- Task: T-1800 (Phase 18); implemented with T-1801, documented under T-1802/T-1702.
- Source of the decision: **owner directive** ("C DRIVE PROTECTION & D DRIVE
  DEVELOPMENT ISOLATION"), supplied in conversation. This directive is *not*
  part of `MASTER.md`; this ADR records it so its numbered rules have a
  repository-resolvable citation. References elsewhere to a "MASTER prompt
  addendum §N" mean the corresponding section number below.

## Context

On this host the Windows system drive `C:` sits below the reliability
threshold used by `PEM.LOW_DISK_THRESHOLD_BYTES` (OBSERVED: ~2.2 GiB free),
which makes live installs/builds risky and can interrupt development. The
repository itself lives on `D:` (`D:\Abhishek\Projects\ENGINEERING DEVELOPMENT
ENGINE\project`). MASTER §38 (resource awareness) and §7 (no fabricated
state) already require honest resource handling; MASTER has no rule about
*where* development artefacts are stored.

## Problem

How should the workflow be configured so that `C:` cannot fill up and
interrupt development, without destabilising Windows or deleting user data?

## Options

1. **Do nothing** — rejected: `C:` is already critically low; future pip/npm
   caches and model downloads would keep growing on `C:`.
2. **Move/delete large `C:` consumers** — rejected: the top consumers
   (`C:\Windows`, installed applications, VM disks, user data) are
   non-project and out of scope; deleting them is unsafe and unapproved.
3. **Redirect project-controllable storage to `D:` + preflight expensive
   operations + approval-gated cleanup (chosen).** Non-destructive;
   reversible; keeps Windows intact.

## Decision

Adopt the owner storage directive. Its rules are:

### §1 — Goal
Keep the Windows system drive (`C:`) from filling and interrupting
development by using `D:` for development storage wherever supported.

### §2 — Measurement-based, non-destructive design
- The **destination drive is measured, never assumed** (`shutil.disk_usage`
  on the nearest existing ancestor of the target path).
- Thresholds are **data-driven** (`config/storage.json`), not a single
  hard-coded constant.
- An operation is **blocked only** when free space is below
  `required_bytes + margin_bytes + min_free_bytes`.
- The preflight performs **no** deletion, download, install, or network work.

### §3 — D: development workspace
Create `D:\EngineeringWorkspace\` with `project`, `environments`,
`caches/{pip,npm,huggingface}`, `temp`, `builds`, `test-artifacts`, `logs`,
`models`, `datasets`, `packages`, `downloads`, `backups`. The root is
configurable via `config/storage.json` (`development_root`) or the
`EDE_DEV_ROOT` environment variable.

### §4 — Redirections (non-destructive)
Redirect, where the tool supports it: pip `global.cache-dir`, npm `cache`,
HuggingFace `HF_HOME`/`HF_HUB_CACHE`, and session-scoped `TEMP`/`TMP`
(`scripts/windows/dev-env.ps1`). Global `TEMP` is intentionally not changed.

### §5 — Per-operation thresholds
There is **no single universal threshold**: operations with a larger
footprint carry a larger headroom. This is why `config/storage.json` carries
per-operation `required_bytes`/`min_free_bytes`.

### §6 — Approval-gated cleanup
No automatic deletion. Regenerable caches (`pip cache purge`,
`npm cache clean --force`) are candidates **only after explicit owner
approval**, and must never touch source, Git history, VM disks, models,
databases, or user data.

### §7 — Do not destabilise Windows
The objective is to remove **avoidable, project-related** `C:` consumption —
not to modify or destabilise the operating system or non-project software.

## Rationale

- Non-destructive and reversible (env/config changes only).
- Honest and evidence-based: every number is OBSERVED and re-measurable.
- Separates project-controllable storage from OS/application storage, which
  matches MASTER §38's resource-aware intent without violating §46.

## Consequences

- Positive: future project growth (caches, models, builds) lands on `D:`;
  expensive operations are guarded by a preflight (`python -m
  src.core.storage preflight <operation>`); the PEM install path refuses
  (exit 3) when the destination lacks space.
- Negative: redirects affect the user account (reversible); redirection does
  **not** reclaim existing `C:` usage; model/venv redirection is configured
  but unexercised (no model/venv; gated by the B-2 install gate).
- Not affected: Windows, installed applications, the global Python
  interpreter, and other non-relocatable software remain on `C:`.

## Rejected alternatives

- Option 1 (do nothing) — leaves `C:` growing from project caches.
- Option 2 (delete/move non-project consumers) — unsafe, out of scope, and
  unapproved (would violate MASTER §35 human-approval gates).

## References

- `config/storage.json`, `src/core/storage.py` (T-1801),
  `scripts/windows/dev-env.ps1`, `docs/storage.md` (T-1800),
  `D:\EngineeringWorkspace\`.
- MASTER §38 (resource awareness), §35 (approval gates), §46 (no fake
  completion), §7 (no fabricated state).
