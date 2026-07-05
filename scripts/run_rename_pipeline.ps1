# rename_sheet.csv -> named_bust / named_transparent 一括リネーム + assets_index.md 生成
param(
    [switch]$DryRun,
    [switch]$SkipPropose
)

$ErrorActionPreference = "Stop"
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$Root = Resolve-Path (Join-Path $ScriptDir "..")
function Invoke-RenamePy {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$ScriptArgs)
    if ($PyCmd -eq "py") {
        & py -3 $RenameScript @ScriptArgs
    }
    else {
        & $PyCmd $RenameScript @ScriptArgs
    }
    return $LASTEXITCODE
}

$PyCmd = $null
foreach ($candidate in @("py", "python", "python3")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $PyCmd = $candidate
        break
    }
}

if (-not $PyCmd) {
    Write-Error "Python not found (py / python / python3)"
    exit 1
}

$RenameScript = Join-Path $ScriptDir "rename_from_sheet.py"
$Folders = "named_bust,named_transparent"

Push-Location $Root
try {
    if (-not $SkipPropose) {
        Write-Host "=== propose new names ==="
        $code = Invoke-RenamePy --propose
        if ($code -ne 0) { exit $code }
        Write-Host ""
    }

    Write-Host "=== dry-run rename ==="
    if ($DryRun) {
        $code = Invoke-RenamePy --folders $Folders --dry-run
        if ($code -ne 0) { exit $code }
        Write-Host ""
        Write-Host "DryRun mode: rename skipped"
        exit 0
    }

    $code = Invoke-RenamePy --folders $Folders --dry-run
    if ($code -ne 0) { exit $code }
    Write-Host ""

    Write-Host "=== rename ==="
    $code = Invoke-RenamePy --folders $Folders
    if ($code -ne 0) { exit $code }
    Write-Host ""

    Write-Host "=== write assets_index.md ==="
    $code = Invoke-RenamePy --write-index --folders $Folders
    if ($code -ne 0) { exit $code }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "pipeline done"
