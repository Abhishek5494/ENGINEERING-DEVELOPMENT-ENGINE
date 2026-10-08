# chatmem.md — current session context

Session state (MASTER §41). Repository files are more authoritative than
this file; on conflict, trust the repository (§43).

## Session
- Date: 2026-10-08
- Mode: **autonomous build** — a full-programme directive was received;
  execute the roadmap task-by-task without asking the user what to do,
  stopping only at recorded blockers (Taiga-S1 repo missing; privileged
  install approval).

## History this conversation
1. Bootstrap: created §27 governance files, §28 structure, 35-task
   roadmap, T-0001.
2. T-0101 PEM system/hardware detection.
3. T-0201 tool manifest + schema + loader.
4. T-0102 PEM tool detection + capability states.
5. T-0103 environment report generation.
6. T-0104 Windows scripts + shared ops module.
7. T-0107 idempotent, guarded install logic + tests.
8. T-0105 Linux POSIX wrapper scripts (static-verified).
9. T-0106 macOS POSIX wrapper scripts (static-verified) — Phase 1
   platform set complete; autonomous build directive audited.
10. T-0202 shared configuration module (`src/core/config.py`); PEM
    report/manifest repointed at it.

## Commit map
- `3453e15` + `78b1270` — T-0001 governance baseline.
- `c639ce8` — T-0101; `73c0005` — T-0201; `ffbdaed` — T-0102;
  `52bec6f` — T-0103; `1445c77` — T-0104; `bac844a` — T-0107;
  `a90df34` — T-0105.
- (pending) — T-0106 macOS wrappers + directive audit; T-0202.

## Key facts to carry forward
- Host: Windows 11, PowerShell 5.1, Python 3.13.5, pytest 9.1.1. Repo
  root `D:\Abhishek\Projects\ENGINEERING DEVELOPMENT ENGINE\project`.
- No POSIX shell on this host → Linux/macOS shell scripts are
  STATIC-validated only; never claim runtime (§46).
- No engineering tools installed (FreeCAD/KiCad/ngspice/Gazebo/Blender/
  Jupyter/Scrapling NOT_FOUND); C:\ below the 1 GiB threshold → live
  installs gated on user approval (§7/§29).
- BLOCKER B-1: Taiga-S1 upstream repo not supplied → T-0601/T-0602
  BLOCKED. BLOCKER B-2: privileged/network install approval.
- Shared code is the single source of truth; platform scripts are thin
  wrappers only (§23). Installer: act only on NOT_FOUND or below-min;
  never on UNKNOWN/absent; null command → manual; skip healthy.
- Exit codes: 0 ok, 1 unhealthy/failed command, 2 execution error,
  3 refused (execute precondition).
- Autonomy rules: after each task update state/audit/docs, review diff,
  commit, pick next READY task by §48 phase order, continue (§56).

## Next task
- `next-task.md` → **T-0302 evidence/claim classification primitives**
  (Phase 3; selected over T-0301 as it unblocks CIE T-0401 + REA T-0701).
  Then T-0301 (state persistence), CIE (T-0401+), Scrapling (T-0501+),
  REA (T-0701+), engineering integrations (T-0801+). Taiga (T-0601/T-0602)
  stays BLOCKED until the repo is supplied.

## Reminders
- Never claim untested/unrun work (§46); record discrepancies, never
  silently overwrite (§47). Report per §55; stop only at true blockers.