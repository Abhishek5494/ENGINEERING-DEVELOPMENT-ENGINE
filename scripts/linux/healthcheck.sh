#!/usr/bin/env sh
# healthcheck.sh - thin wrapper over shared PEM code (MASTER section 23).
# All business logic lives in src/pem/ops.py; this file only resolves the
# repository root, invokes the shared module, and propagates its exit code.
# Exits nonzero when the shared health check reports an unhealthy host.

script_dir=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
repo_root=$(CDPATH= cd -P "$script_dir/../.." && pwd)

if command -v python3 >/dev/null 2>&1; then
    python_cmd=python3
elif command -v python >/dev/null 2>&1; then
    python_cmd=python
else
    echo "python interpreter not found on PATH (execution error, exit 2)" >&2
    exit 2
fi

cd "$repo_root" || exit 2
exec "$python_cmd" -m src.pem.ops healthcheck "$@"