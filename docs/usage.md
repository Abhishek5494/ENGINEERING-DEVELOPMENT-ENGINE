# Usage Guide

How to operate the Engineering Development Engine. All commands are
offline-first and require only Python 3.11+ (see
[`installation.md`](installation.md)). For the product scope see
[`mvp.md`](mvp.md).

## Unified CLI

The platform exposes one entry point:

```text
python -m src <command> [options]
```

| Command | Purpose |
|---|---|
| `python -m src version` | Print the platform version. |
| `python -m src env [--json] [--write]` | Detect system/hardware/tools and build the environment report. `--write` writes `environment.json` + `environment-report.md`. |
| `python -m src tools [--json]` | List detected tools and capability states. |
| `python -m src storage preflight OPERATION [--path P] [--margin-bytes N]` | Check free space for an operation from `config/storage.json`. Exit `3` when blocked. |
| `python -m src upstream [--json]` | Validate and list the canonical upstream-source registry. |
| `python -m src cie identify --url URL [--html FILE]` | Identify an exact product from locally supplied HTML (default: stdin). |
| `python -m src rea inspect PATH` | Fingerprint a local file (type, hashes, strings, tooling). |
| `python -m src workflow run --name NAME [--code FILE] [--json] [--write] [--overwrite]` | Run the unified engineering workflow and print honest per-stage status. |

Each subsystem also keeps its own module entry point
(`python -m src.<module>`); the CLI above is a thin dispatcher over the same
functions. Run `python -m src --help` for the full option list.

## Examples

Environment report (human-readable):

```text
python -m src env
```

Environment report (machine-readable):

```text
python -m src env --json
```

Storage preflight before an expensive operation:

```text
python -m src storage preflight model_download
```

Identify a component from a saved product page:

```text
python -m src cie identify --url https://example.com/p/1 --html page.html
```

Inspect a downloaded file (authorized investigation only):

```text
python -m src rea inspect firmware.bin
```

Run the partial workflow and persist its report:

```text
python -m src workflow run --name demo --code model.py --write
```

## Reading workflow output

`workflow run` prints every stage of the MASTER §50 pipeline with an honest
status:

- `COMPLETE` — executed against a real subsystem.
- `READY` — the external tool is present but was not driven in this run.
- `UNAVAILABLE` — the external tool is absent on this host.
- `BLOCKED` — a capability that requires authorisation (install gate B-2) or a
  live Taiga-S1 provider.

A run that has any `BLOCKED`/`UNAVAILABLE` stage is reported as
`PARTIALLY-VALIDATED`. The platform never reports a stage `COMPLETE` unless it
actually performed the work (MASTER §46).

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success. |
| `2` | Usage or input error (e.g. unknown operation, missing file). |
| `3` | Storage preflight blocked an operation (insufficient space). |

## Python API

Every command is a thin wrapper over a typed Python function, e.g.:

```python
from src.orchestration import run_workflow, write_project
from src.cie import identify_page
from src.rea import inspect_target
from src.core.storage import preflight

report = run_workflow("demo")
print(report.validation_level)          # PARTIALLY-VALIDATED
print([s.value for s in report.blocked])  # ['ACQUIRE', 'ANALYZE']
```

APIs return structured dataclasses/dicts and hold no hidden global state
(`architecture.md` §6).
