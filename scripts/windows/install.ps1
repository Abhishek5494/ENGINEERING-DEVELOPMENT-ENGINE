# install.ps1 — thin wrapper over shared PEM code (MASTER section 23).
# All business logic lives in src/pem/ops.py; this file only resolves the
# repository root, invokes the shared module, and propagates its exit code.
# Plan-only by default; --execute (forwarded via @args) runs guarded,
# idempotent installation (T-0107, src/pem/installer.py).
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "python interpreter not found on PATH (execution error, exit 2)"
    exit 2
}
Push-Location $repoRoot
try {
    & $python.Source -m src.pem.ops install @args
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
