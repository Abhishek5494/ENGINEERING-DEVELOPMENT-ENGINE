# Development Storage & C:-Drive Protection (T-1800)

Goal: keep the Windows system drive (`C:`) from filling up and interrupting
development, by using `D:` for development storage wherever it is supported.
This document records the audit, the redirections applied, what remains on
`C:` and why, and how to run maintenance safely.

> Measurement rule (MASTER §7): every number below is OBSERVED at the stated
> time. Nothing on `C:` has been deleted by this work. Re-measure before
> acting on stale numbers.

## 1. Environment (OBSERVED)

- Windows 11 Home (build 10.0.26300); system drive `C:`, `C:\WINDOWS`.
- Repository: `D:\Abhishek\Projects\ENGINEERING DEVELOPMENT ENGINE\project`
  (Git work tree, `master`). Repository size: ~3 MB / 637 files (mostly
  tests; `.git` ~1.2 MB).
- Python: `C:\Users\Abhi\AppData\Local\Programs\Python\Python313` (global).
  The project has **no** `requirements.txt`/`pyproject.toml`/venv — it is
  standard-library only, with `pytest` from the global interpreter.

### Drive space at audit time

| Drive | Free | Total | Used |
|---|---|---|---|
| `C:` | 2.23 GiB | 199.15 GiB | 196.9 GiB |
| `D:` | 90.52 GiB | 276.82 GiB | 186.3 GiB |

`C:` was below 3 GiB free — a reliability risk for any install/build.

## 2. Identified causes of C: consumption (OBSERVED)

Top-level (robocopy byte totals):

| Path | Size | Project-related? |
|---|---|---|
| `C:\Windows` | 46.2 GB | No — OS-managed |
| `C:\Users\Abhi` | 82.4 GB | Mixed |
| `C:\ProgramData` | 33.2 GB | No (Adobe 23.0 GB, Microsoft 6.9 GB) |
| `C:\Program Files` | 30.4 GB | No |
| `C:\Program Files (x86)` | 18.8 GB | No |

Within `C:\Users\Abhi` (selected):

| Path | Size | Project-related? |
|---|---|---|
| `AppData\Local\Microsoft` | 19.0 GB | No |
| `AppData\Local\Google` | 6.0 GB | No |
| `AppData\Local\Programs` | 4.5 GB | No (incl. Python 1.44 GB) |
| `AppData\Local\npm-cache` | 2.78 GB | Developer cache |
| `AppData\Local\BraveSoftware` | 2.2 GB | No |
| `AppData\Local\Perplexity` | 1.67 GB | No |
| `AppData\Local\AnthropicClaude` | 1.67 GB | No |
| `AppData\Local\pip` | 1.23 GB | Yes — Python package cache |
| `Documents\Virtual Machines` | 18.3 GB | No — VM disks (do not delete) |
| `.rustup` | 1.31 GB | No |
| `.trae` | 1.23 GB | No |
| `.vscode\extensions` | 0.39 GB | IDE |
| `.cache` (incl. `huggingface` 87 MB) | 118 MB | Partial — model cache |

**Conclusion:** the overwhelming majority of `C:` usage is OS, installed
applications, browsers, games, VMs, and other toolchains — **not this
project**. The project's own controllable `C:` footprint is the global pip
cache, TEMP during runs, the globally-installed `pytest`, and future model
downloads. The pagefile is already on `D:`.

## 3. D: development workspace

```
D:\EngineeringWorkspace\
  project\        environments\   caches\{pip,npm,huggingface}\
  temp\           builds\         test-artifacts\   logs\
  models\         datasets\       packages\         downloads\   backups\
```

The layout is described in `config/storage.json` (`development_root` +
`locations`). Override the root for a process with the `EDE_DEV_ROOT`
environment variable, or edit `development_root` in that file.

## 4. Redirections applied (non-destructive)

| Tool | Setting | Location written |
|---|---|---|
| pip | `global.cache-dir` = `D:\EngineeringWorkspace\caches\pip` | `C:\Users\Abhi\AppData\Roaming\pip\pip.ini` |
| npm | `cache` = `D:\EngineeringWorkspace\caches\npm` | user `.npmrc` |
| HuggingFace | `HF_HOME`, `HF_HUB_CACHE` → `D:\EngineeringWorkspace\models\huggingface` | user environment (persistent) |

Session-only (process) redirection, e.g. `TEMP`/`TMP`, is applied by
dot-sourcing `scripts\windows\dev-env.ps1`; global `TEMP` is intentionally
**not** changed (it is Windows-managed and shared).

### Verification (OBSERVED after the change)

```
python -m pip cache dir           -> d:\engineeringworkspace\caches\pip
npm.cmd config get cache          -> D:\EngineeringWorkspace\caches\npm
HF_HOME (user env)                -> D:\EngineeringWorkspace\models\huggingface
```

Redirections do not free existing files; they stop **future** growth on
`C:`. Deleting the existing caches requires the approval step in §7.

## 5. Storage preflight (protection before expensive work)

`src/core/storage.py` provides the reusable preflight utility; thresholds
are data-driven in `config/storage.json` (different per operation).

```
python -m src.core.storage preflight dependency_install
python -m src.core.storage preflight model_download --path D:\EngineeringWorkspace\models
python -m src.core.storage preflight vm_create --margin-bytes 15000000000
```

Exit codes: `0` ok, `3` blocked (insufficient free space), `2` bad input.
The PEM install path (`python -m src.pem.ops install --execute`) now runs a
`dependency_install` preflight on the workspace root first and refuses
(exit 3) when it is blocked.

## 6. Unavoidable C: dependencies (documented, not moved)

- Windows itself (`C:\Windows`, 46 GB) and `Program Files`.
- The global Python interpreter (`~1.44 GB`) and its site-packages, incl.
  `pytest`. Moving the interpreter is out of scope (risks breaking paths).
- Installed applications, browsers, games, VM disks, and toolchains that do
  not support relocation.
- `%LOCALAPPDATA%\Temp` remains the default OS temp; the dev script uses a
  `D:` temp for project processes only.

Rationale: the objective is to remove *avoidable project-related* `C:`
consumption, not to destabilise Windows (ADR-0003 §7).

## 7. Safe cleanup policy

No automatic deletion is performed. Regenerable caches are candidates only
after approval, and only via documented commands:

```
python -m pip cache purge                       # pip downloads cache
npm.cmd cache clean --force                      # npm cache
```

Deletion requires explicit approval and must never touch source, Git
history, VM disks, models, databases, or user data. Broad recursive deletes
against `C:\` or `D:\` are prohibited.

## 8. Maintenance / repeatable setup

1. New shell session:
   `. .\scripts\windows\dev-env.ps1`
2. Re-apply persistent redirections (if a tool resets them):
   ```
   python -m pip config set global.cache-dir "D:\EngineeringWorkspace\caches\pip"
   npm.cmd config set cache "D:\EngineeringWorkspace\caches\npm"
   setx HF_HOME "D:\EngineeringWorkspace\models\huggingface"
   ```
3. Before a large operation:
   `python -m src.core.storage preflight <operation>`
4. Re-audit free space: `Get-PSDrive C,D`.

## 9. Remaining risks / limitations

- `C:` free space is determined mostly by non-project software; this work
  reduces future project growth but does not reclaim the large non-project
  consumers (which require their own, separately-approved cleanup).
- Persistent env redirections affect the user account, not just the repo;
  they are reversible.
- Model/venv redirection is configured but not yet exercised (no model or
  venv is installed; creating one is gated by B-2).
- Linux/macOS paths are unexercised on this Windows host.
