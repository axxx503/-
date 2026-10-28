param(
    [string]$GameDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PayloadDir = Join-Path $ScriptDir "payload"
$ManifestPath = Join-Path $PayloadDir "manifest.json"
$Manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

$DefaultCandidates = @(
    "C:\Program Files (x86)\Steam\steamapps\common\over the hill",
    "C:\Program Files\Steam\steamapps\common\over the hill",
    "D:\SteamLibrary\steamapps\common\over the hill",
    "E:\SteamLibrary\steamapps\common\over the hill"
)

if ([string]::IsNullOrWhiteSpace($GameDir)) {
    foreach ($cand in $DefaultCandidates) {
        if (Test-Path (Join-Path $cand "over the hill.exe")) {
            $GameDir = $cand
            break
        }
    }
}

if ([string]::IsNullOrWhiteSpace($GameDir) -or -not (Test-Path (Join-Path $GameDir "over the hill.exe"))) {
    Write-Host "[ERROR] Could not locate 'over the hill.exe'." -ForegroundColor Red
    exit 1
}

$LogFile = Join-Path $GameDir "arabic_patch.log"
function Write-PatchLog([string]$msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

Write-PatchLog "=== Starting over the hill Arabic Localization Uninstaller ==="
$BackupDir = Join-Path $GameDir "_ArabicPatchBackup"
if (-not (Test-Path $BackupDir)) {
    Write-PatchLog "[ERROR] Backup directory not found at: $BackupDir"
    exit 1
}

$FileKeys = @("resources.assets", "ui_assets_all", "loc_strings", "loc_assets")
foreach ($key in $FileKeys) {
    $entry = $Manifest.files.$key
    $targetFile = Join-Path $GameDir $entry.rel_path
    $leafName = Split-Path -Leaf $targetFile
    $backupFile = Join-Path $BackupDir $leafName
    $origHash = $entry.orig_sha256.ToUpper()

    if (-not (Test-Path $backupFile)) {
        Write-PatchLog "[ERROR] Backup file missing: $backupFile"
        exit 1
    }

    Copy-Item -Path $backupFile -Destination $targetFile -Force
    $restoredHash = (Get-FileHash -Path $targetFile -Algorithm SHA256).Hash.ToUpper()
    if ($restoredHash -ne $origHash) {
        Write-PatchLog "[ERROR] SHA-256 mismatch after restoring $leafName! Expected $origHash, got $restoredHash"
        exit 1
    }
    Write-PatchLog "[RESTORED] $leafName restored and verified (SHA256: $restoredHash)"
}

Remove-Item -Path $BackupDir -Recurse -Force
Write-PatchLog "Removed backup directory _ArabicPatchBackup. Original game state 100% restored."
Write-PatchLog "=== Uninstallation Complete ==="
exit 0

