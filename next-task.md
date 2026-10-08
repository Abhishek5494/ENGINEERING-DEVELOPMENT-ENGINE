# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-1701 — Release audit vs MASTER §54 checklist
- **State:** BLOCKED
- **Phase:** 17 — Release + final audit

### Objective
Walk the MASTER §54 release checklist and produce a release audit that
makes no claim without evidence (§46). This is the final gate and cannot
run until its dependencies are complete.

### Dependencies
- T-1401 (BLOCKED — depends on T-1301), T-1501 (BLOCKED — depends on
  T-0502), T-1502 (COMPLETE), T-1601 (COMPLETE).

### Affected components
- A future `docs/release-audit.md` (or `audit.md` section) walking §54.
- No code is added by this task; it is an evidence review.

### Constraints
- §54 requires security reviewed and **recovery tested** before release;
  recovery (T-1502) is done, but security review (T-1501) and the
  simulation/validation/BOM pipeline (T-1401) are BLOCKED. Honesty forbids
  a release audit that declares completion while those are unmet (§44/§46).

### Acceptance criteria (when unblocked)
1. Every §54 checklist item marked with its evidence (or explicit unmet).
2. No claim lacking a repository artefact.
3. Tagging/release only if all items are met.

### Validation requirements
- N/A while BLOCKED. Revisit only after T-1401 and T-1501 complete.

### Blocker resolution (to unblock the remaining work)
- **T-0502 / T-0404 / T-1501:** install Scrapling (network + approval,
  MASTER §7/§29) and raise the disk threshold — currently C:\ is below
  1 GiB and installs are gated (B-2).
- **T-0601/T-0602 / T-1301 / T-1401:** supply the Taiga-S1 upstream
  repository (B-1) so orchestration can be integrated.

### Out of scope (do not pull in)
- Declaring the release complete; bypassing the blocked dependencies.