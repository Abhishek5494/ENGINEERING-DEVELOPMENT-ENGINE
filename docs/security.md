# Security

Security model, trust boundaries and safe-operation rules. This is a summary;
the authoritative requirements are MASTER §14 and §52 and
[`requirements.md`](../requirements.md) R10.

## Trust boundaries

| Boundary | Trust | Handling |
|---|---|---|
| This repository | Trusted | Reviewed at bootstrap; no secrets committed. |
| Component pages / downloaded files | **Untrusted** | Treated as data only; parsed, never executed. |
| External tools (FreeCAD, KiCad, …) | Semi-trusted | Invoked by absolute path with explicit arguments. |
| Network | Optional, untrusted | Only for component research / packages / authorised investigation. |
| AI reasoning (Taiga-S1) | Lowest evidence tier | Never a source of engineering truth (MASTER §5). |

## Guarantees

- **No hardcoded secrets.** No API keys, tokens or passwords in the tree; a
  governance test enforces `.gitignore` coverage of `*.env` / `secrets.json`.
- **No unsafe execution.** No `shell=True`, `os.system`, `eval`, `exec`, or
  unsafe `pickle`/`yaml.load`. Subprocesses use argument lists with timeouts.
- **No untrusted code execution.** Acquired HTML and inspected files are
  parsed as data; they are never imported or run.
- **Confined writes.** Generated artifacts are written only inside their
  designated directories (`projects/`, `simulations/`, `cad/`, `models/`);
  path traversal outside those roots is refused.
- **Authorised investigation only.** REA requires an explicit authorisation
  record (MASTER §20) before any investigation is created.
- **Storage safety.** Expensive operations pass a free-space preflight before
  they run (`src/core/storage.py`); `install --execute` is refused when the
  destination drive is below threshold.

## Safe-operation rules for operators

1. Run `python -m src storage preflight <operation>` before an expensive task.
2. Review an install plan (`install` without `--execute`) before executing it.
3. Treat every downloaded page/file and every AI output as untrusted input.
4. Use REA only on material you are authorised to investigate.
5. Keep the development workspace off the system drive (see
   [`installation.md`](installation.md)).

## Known limitations

- **Install execution is owner-gated.** Real installs require approval
  (network/privileged); no automatic installation is performed.
- **Live tool execution is unverified** on the current host (tools absent);
  integration code is unit-tested but its live behaviour is untested here.
- **No secrets tooling** (no vault / scanning service); secrecy relies on not
  committing secrets and `.gitignore`.
- **Full security review (T-1501) is BLOCKED** on T-0502 (install gate B-2);
  this document covers the implemented surface only, not a certified audit.

## Reporting

Record a security concern as a finding with an evidence label and, if it needs
owner action, as a human input in [`requirements.md`](../requirements.md)
(R16). Do not attempt network or privileged remediation without approval.
