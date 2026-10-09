# next-task.md

Current execution boundary (MASTER §30). Work ONLY on this task.

## Task T-1701 — Release audit vs MASTER §54 checklist
- **State:** BLOCKED
- **Phase:** 17 — Release + final audit

### Objective
Walk the MASTER §54 release checklist and produce a release audit that makes no claim without evidence (§46).

### Dependencies
- T-1401 (BLOCKED), T-1501 (BLOCKED), T-1502 (COMPLETE), T-1601 (COMPLETE).

### Affected components
- docs/release-audit.md or audit.md section.

### Constraints
- No claim lacking repository artefacts; release only if all items met.

### Acceptance criteria (when unblocked)
1. Every §54 checklist item marked with evidence or explicit unmet.
2. No claim lacking a repository artefact.
3. Tagging/release only if all items are met.

### Validation requirements
- N/A while BLOCKED.

### Blocker resolution
- T-0502/T-0404/T-1501: Scrapling installation (B-2) + disk.
- T-0602 is COMPLETE; T-1301/T-1401 still depend on T-0404/T-0502.
