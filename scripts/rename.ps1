# raw/ images -> named/ via rename_map.json
param(
    [string]$Map = "",
    [switch]$DryRun,
    [switch]$Move,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Remaining
)

$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $Map) {
    $Map = Join-Path $ScriptDir "..\rename_map.json"
}

for ($i = 0; $i -lt $Remaining.Count; $i++) {
    switch ($Remaining[$i]) {
        "--dry-run" { $DryRun = $true }
        "--move" { $Move = $true }
        "--map" {
            $i++
            if ($i -lt $Remaining.Count) { $Map = $Remaining[$i] }
        }
    }
}

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $ScriptDir "..")
$RawDir = Join-Path $Root "raw"
$NamedDir = Join-Path $Root "named"

if (-not (Test-Path $Map)) {
    Write-Error "Map not found: $Map"
    exit 1
}

$json = Get-Content $Map -Raw -Encoding UTF8 | ConvertFrom-Json
$items = if ($json.items) { $json.items } else { $json }

New-Item -ItemType Directory -Force -Path $RawDir | Out-Null
New-Item -ItemType Directory -Force -Path $NamedDir | Out-Null

$ok = 0
$skipped = 0
$failed = 0
$index = 0

foreach ($item in $items) {
    $index++
    $srcName = [string]$item.from
    $dstName = [string]$item.to

    if ([string]::IsNullOrWhiteSpace($srcName) -or [string]::IsNullOrWhiteSpace($dstName)) {
        Write-Host "[skip] #$index : empty from/to"
        $skipped++
        continue
    }

    if ($srcName.StartsWith("REPLACE_ME")) {
        Write-Host "[skip] #$index : placeholder $srcName"
        $skipped++
        continue
    }

    $src = Join-Path $RawDir $srcName
    if (-not (Test-Path $src)) {
        $matches = Get-ChildItem -Path $RawDir -File -Filter $srcName -ErrorAction SilentlyContinue
        if ($matches.Count -eq 1) {
            $src = $matches[0].FullName
        }
        elseif ($matches.Count -gt 1) {
            Write-Host "[skip] #$index : multiple matches for $srcName"
            $skipped++
            continue
        }
        else {
            Write-Host "[miss] #$index : not in raw/ -> $srcName"
            $failed++
            continue
        }
    }

    $dst = Join-Path $NamedDir $dstName
    $action = if ($Move) { "move" } else { "copy" }

    if ($DryRun) {
        Write-Host "[dry] ${action}: $(Split-Path $src -Leaf) -> named/$dstName"
        $ok++
        continue
    }

    if (Test-Path $dst) {
        Write-Host "[skip] #$index : already exists named/$dstName"
        $skipped++
        continue
    }

    if ($Move) {
        Move-Item -Path $src -Destination $dst
    }
    else {
        Copy-Item -Path $src -Destination $dst
    }

    $starTxt = ""
    if ($item.stars) {
        $count = [int]$item.stars
        $starTxt = " (" + ("*" * $count) + ")"
    }
    Write-Host "[ok] $(Split-Path $src -Leaf) -> $dstName$starTxt"
    $ok++
}

Write-Host ""
Write-Host "done: ok=$ok, skip=$skipped, miss=$failed"
if ($failed -gt 0) { exit 1 }
