# dev-env.ps1 - configure the current PowerShell session for D:-drive
# development isolation (T-1800). This sets PROCESS-scoped environment
# variables only: it never changes machine or user settings, and it never
# deletes anything. Dot-source it to affect your shell:
#
#     . .\scripts\windows\dev-env.ps1
#
# Persistent (machine) redirections that were applied once are recorded in
# docs/storage.md (pip cache-dir, npm cache, HF_HOME/HF_HUB_CACHE).
#
# Standard: no tool lists or business logic here (MASTER section 23); this is
# pure environment configuration.

$ErrorActionPreference = "Stop"

$devRoot = if ($env:EDE_DEV_ROOT) { $env:EDE_DEV_ROOT } else { "D:\EngineeringWorkspace" }

$paths = @{
    "EDE_DEV_ROOT"  = $devRoot
    "TEMP"          = Join-Path $devRoot "temp"
    "TMP"           = Join-Path $devRoot "temp"
    "PIP_CACHE_DIR" = Join-Path $devRoot "caches\pip"
    "HF_HOME"       = Join-Path $devRoot "models\huggingface"
    "HF_HUB_CACHE"  = Join-Path $devRoot "models\huggingface\hub"
}

foreach ($entry in $paths.GetEnumerator()) {
    if ($entry.Key -ne "EDE_DEV_ROOT" -and -not (Test-Path -LiteralPath $entry.Value)) {
        New-Item -ItemType Directory -Path $entry.Value -Force | Out-Null
    }
    Set-Item -Path ("Env:" + $entry.Key) -Value $entry.Value
}

Write-Host "Development storage configured for this session:"
foreach ($entry in $paths.GetEnumerator()) {
    Write-Host ("  {0,-14} = {1}" -f $entry.Key, $entry.Value)
}
Write-Host "Persistent redirections: see docs/storage.md"
