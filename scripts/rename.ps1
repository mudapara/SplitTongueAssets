# スプリットタン婆 素材リネームスクリプト
# raw/ → named/ に rename_map.json に従ってコピー
#
# 使い方:
#   .\scripts\rename.ps1              # 実行
#   .\scripts\rename.ps1 -DryRun      # 確認のみ（コピーしない）
#   .\scripts\rename.ps1 -ListUnmapped  # raw/ にあって map に無いファイル一覧

param(
    [switch]$DryRun,
    [switch]$ListUnmapped,
    [string]$MapFile = "rename_map.json",
    [string]$RawDir = "raw",
    [string]$NamedDir = "named"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

$mapPath = Join-Path $RepoRoot $MapFile
if (-not (Test-Path $mapPath)) {
    Write-Error "rename_map.json が見つかりません: $mapPath"
}

$map = Get-Content $mapPath -Raw -Encoding UTF8 | ConvertFrom-Json
$rawPath = Join-Path $RepoRoot $RawDir
$namedPath = Join-Path $RepoRoot $NamedDir

if (-not (Test-Path $rawPath)) {
    Write-Error "raw/ フォルダがありません: $rawPath"
}

if (-not $DryRun -and -not $ListUnmapped) {
    New-Item -ItemType Directory -Force -Path $namedPath | Out-Null
}

$imageExts = @(".png", ".jpg", ".jpeg", ".webp", ".PNG", ".JPG", ".JPEG", ".WEBP")
$rawFiles = Get-ChildItem $rawPath -File | Where-Object {
    $imageExts -contains $_.Extension
}

$mapKeys = $map.PSObject.Properties.Name

if ($ListUnmapped) {
    Write-Host "`n=== raw/ にあって rename_map.json に無いファイル ===" -ForegroundColor Yellow
    $unmapped = @()
    foreach ($f in $rawFiles) {
        if ($mapKeys -notcontains $f.Name) {
            $unmapped += $f.Name
            Write-Host "  ? $($f.Name)"
        }
    }
    if ($unmapped.Count -eq 0) {
        Write-Host "  （なし）" -ForegroundColor Green
    } else {
        Write-Host "`n→ Cursor で「未マップ ○枚、リネーム案追加して」と依頼してください。" -ForegroundColor Cyan
    }
    exit 0
}

$ok = 0
$skip = 0
$missing = 0
$duplicate = @{}

Write-Host "`n=== リネーム開始 ===" -ForegroundColor Cyan
if ($DryRun) { Write-Host "（DryRun: コピーしません）`n" -ForegroundColor Yellow }

foreach ($prop in $map.PSObject.Properties) {
    $oldName = $prop.Name
    $entry = $prop.Value
    $newName = $entry.name

    if ([string]::IsNullOrWhiteSpace($newName)) {
        Write-Host "SKIP (名前なし): $oldName" -ForegroundColor DarkGray
        $skip++
        continue
    }

    $src = Join-Path $rawPath $oldName
    if (-not (Test-Path $src)) {
        $found = $rawFiles | Where-Object { $_.Name -eq $oldName }
        if (-not $found) {
            Write-Host "MISSING: $oldName" -ForegroundColor Red
            $missing++
            continue
        }
        $src = $found.FullName
    }

    $dest = Join-Path $namedPath $newName

    if ($duplicate.ContainsKey($newName)) {
        Write-Host "WARN 重複先: $newName <= $oldName (既に $($duplicate[$newName]))" -ForegroundColor Yellow
    } else {
        $duplicate[$newName] = $oldName
    }

    $tier = if ($entry.tier) { $entry.tier } else { "" }
    $label = if ($tier) { "[$tier] " } else { "" }

    if ($DryRun) {
        Write-Host "OK  $label$oldName -> $newName"
    } else {
        Copy-Item -Path $src -Destination $dest -Force
        Write-Host "OK  $label$oldName -> $newName" -ForegroundColor Green
    }
    $ok++
}

Write-Host "`n=== 結果 ===" -ForegroundColor Cyan
Write-Host "  成功: $ok"
Write-Host "  欠落(rawに無い): $missing"
Write-Host "  スキップ: $skip"

if (-not $DryRun -and $ok -gt 0) {
    Write-Host "`nnamed/ に $ok 枚コピーしました。" -ForegroundColor Green
    Write-Host '次: git add named/ ; git commit -m "Rename assets" ; git push'
}

$unmappedCount = ($rawFiles | Where-Object { $mapKeys -notcontains $_.Name }).Count
if ($unmappedCount -gt 0) {
    Write-Host "`n※ raw/ に未マップが $unmappedCount 枚あります。" -ForegroundColor Yellow
    Write-Host "  .\scripts\rename.ps1 -ListUnmapped で一覧表示"
}