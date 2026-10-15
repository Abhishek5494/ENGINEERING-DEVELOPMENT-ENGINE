# Installation & Setup

This guide gets a new machine from a clean checkout to a working, testable
platform. It is offline-first: no network is required for the core.

## Requirements

| Requirement | Minimum | Notes |
|---|---|---|
| Python | 3.11+ (tested on 3.13.5) | Runtime is **standard library only**. |
| Git | any recent | Required to clone and for the `git` tool probe. |
| Operating system | Windows 10/11, Linux, macOS | Scripts provided for all three. |
| Disk | ~1 GiB free | More for model downloads; see storage below. |

There is **no** `requirements.txt`, `pyproject.toml` or package install step:
the platform deliberately has no third-party runtime dependency. PyYAML is
optional (only needed if you choose a YAML config over the default JSON) and is
imported defensively. See [`dependencies.md`](dependencies.md) and
[`../decisions/ADR-0004-dependency-independence.md`](../decisions/ADR-0004-dependency-independence.md).

## Get the code

```text
git clone <upstream-url> engineering-development-engine
```

## Verify the installation

Run the test suite and a smoke command from the repository root:

```text
python -m pytest tests/ -q
python -m src version
python -m src env --json
```

Expected: the suite passes (skipped tests are explained in
[`testing.md`](testing.md)); the version prints; the environment report is
valid JSON.

## Storage isolation (recommended on Windows)

To avoid growing the system drive, development caches and temporary files are
redirected to a dedicated workspace (`D:\EngineeringWorkspace\` by default):

```text
pwsh -File scripts\windows\dev-env.ps1     # sets session TEMP/TMP etc. to D:
```

Configured redirections (see [`storage.md`](storage.md)):

- pip cache → `D:\EngineeringWorkspace\caches\pip`
- npm cache → `D:\EngineeringWorkspace\caches\npm`
- HuggingFace home → `D:\EngineeringWorkspace\models\huggingface`

Guard any expensive operation with a preflight check before running it:

```text
python -m src storage preflight dependency_install
python -m src storage preflight model_download
```

Exit code `3` means the destination drive lacks the required free space.

## Platform scripts

Thin wrappers exist per platform (they call the shared Python module; no
business logic is duplicated):

| Platform | Healthcheck | Install (plan) | Install (execute) |
|---|---|---|---|
| Windows | `scripts\windows\healthcheck.ps1` | `scripts\windows\install.ps1` | add `--execute` |
| Linux | `scripts/linux/healthcheck.sh` | `scripts/linux/install.sh` | add `--execute` |
| macOS | `scripts/macos/healthcheck.sh` | `scripts/macos/install.sh` | add `--execute` |

`install` without `--execute` prints a plan only. `--execute` performs real
installs and is refused when storage is insufficient — it requires owner
approval for network/privileged operations (install gate B-2).

## Troubleshooting

| Symptom | Cause | Action |
|---|---|---|
| Tools show `NOT_FOUND` | Specialist tools are not installed | Expected; install them only with approval, or rely on the offline scope. |
| `install --execute` exits `3` | Destination drive below the threshold | Free space or relocate `development_root` in `config/storage.json`. |
| Workflow `ACQUIRE`/`ANALYZE` `BLOCKED` | Scrapling not installed (B-2) / no live Taiga-S1 provider | Expected; see [`mvp.md`](mvp.md). |
| `config error` on a YAML file | PyYAML not installed | Use JSON config (default) or install PyYAML. |
| `pytest` reports a `tmp` `PermissionError` on Windows | Pytest temp dir on a locked drive | Set `TMP`/`TEMP` to a writable drive (see storage isolation). |

## Uninstall / clean state

The platform stores no state outside the repository except:
- development caches under the configured `development_root`;
- generated `environment.json` / `environment-report.md` (gitignored);
- project outputs you explicitly wrote (`projects/`, `simulations/`, …).

Removing those directories returns the machine to a clean state; the
repository itself is the long-term memory.
