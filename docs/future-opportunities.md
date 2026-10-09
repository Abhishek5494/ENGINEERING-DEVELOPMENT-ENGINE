# Future Opportunities

Deferred ideas recorded per MASTER §45. Nothing here is implemented
unless a roadmap task explicitly picks it up. Entry fields: idea, reason,
subsystem, value, prerequisites, priority, status.

---

## FUTURE-0001 — CI pipeline for governance + PEM tests
- Idea: run pytest on Windows/Linux/macOS automatically on every commit.
- Reason: cross-platform claims need cross-platform evidence; current host is Windows only.
- Subsystem: PEM / process.
- Value: catches platform regressions early; provides execution evidence for T-1501/T-1601.
- Prerequisites: T-0104–T-0106 scripts, hosted or local runner.
- Priority: MEDIUM.
- Status: PLANNED (not scheduled in current roadmap).

## FUTURE-0002 — SQLite index of component records
- Idea: queryable index over `components/*.json` for fast cross-project component reuse.
- Reason: file-per-component works early; scale needs an index.
- Subsystem: CIE.
- Value: faster lookups, duplicate detection across projects.
- Prerequisites: T-0401 (component model + storage).
- Priority: LOW.
- Status: PLANNED.

## FUTURE-0003 — Taiga-S1 model runtime benchmark harness
- Idea: benchmark candidate local LLMs against engineering tasks with RAM/VRAM budgeting.
- Reason: resource-aware model selection (§38) needs measured data, not assumptions.
- Subsystem: Taiga-S1.
- Value: evidence-based runtime selection; graceful degradation policy.
- Prerequisites: T-0601.
- Priority: MEDIUM.
- Status: PLANNED.

## FUTURE-0004 — Scrapling MCP integration
- Idea: use Scrapling's MCP capability for AI-agent acquisition if it provides architectural benefit.
- Reason: MASTER §2.4 allows it when beneficial; not needed until Taiga-S1 + CIE both exist.
- Subsystem: CIE / Taiga-S1.
- Value: cleaner agent-acquisition interface.
- Prerequisites: T-0502, T-0602; must inspect installed Scrapling docs first.
- Priority: LOW.
- Status: PLANNED.

## FUTURE-0006 — License catalog + ADR policy
- Idea: create a short ADR template for licence decisions and a "dependency licences" note (invoked-but-not-bundled) to avoid future confusion.
- Reason: T-0002 is a human gate and third-party tools are not bundled; an explicit policy prevents accidental licence claims.
- Subsystem: governance.
- Value: reduces legal ambiguity and improves release auditability (MASTER §54).
- Prerequisites: T-0002 finalised (policy can be drafted beforehand).
- Priority: LOW.
- Status: PLANNED.
