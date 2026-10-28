param(
    [string]$GameDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PayloadDir = Join-Path $ScriptDir "payload"
$ManifestPath = Join-Path $PayloadDir "manifest.json"

if (-not (Test-Path $ManifestPath)) {
    Write-Host "[ERROR] Manifest file missing: $ManifestPath" -ForegroundColor Red
    exit 1
}

$Manifest = Get-Content $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json

# 1. Detect game path
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
    Write-Host "[ERROR] Could not automatically locate 'over the hill.exe'." -ForegroundColor Red
    Write-Host "Please pass -GameDir <path_to_game_folder>." -ForegroundColor Yellow
    exit 1
}

$LogFile = Join-Path $GameDir "arabic_patch.log"
function Write-PatchLog([string]$msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

Write-PatchLog "=== Starting over the hill Arabic Localization Installer v1.0 ==="
Write-PatchLog "Target game directory: $GameDir"

# Verify user saves are never touched
$SavesDir = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "My Games\over the hill"
Write-PatchLog "User save directory ($SavesDir) will NOT be modified."

$BackupDir = Join-Path $GameDir "_ArabicPatchBackup"
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

# 2. Verify SHA-256 of target files & create clean backups
$FileKeys = @("resources.assets", "ui_assets_all", "loc_strings", "loc_assets")
foreach ($key in $FileKeys) {
    $entry = $Manifest.files.$key
    $relPath = $entry.rel_path
    $origHash = $entry.orig_sha256.ToUpper()
    $patchedHash = $entry.patched_sha256.ToUpper()

    $targetFile = Join-Path $GameDir $relPath
    if (-not (Test-Path $targetFile)) {
        Write-PatchLog "[ERROR] Required game file missing: $targetFile"
        exit 1
    }

    $leafName = Split-Path -Leaf $targetFile
    $backupFile = Join-Path $BackupDir $leafName
    $currentHash = (Get-FileHash -Path $targetFile -Algorithm SHA256).Hash.ToUpper()

    if (Test-Path $backupFile) {
        $backupHash = (Get-FileHash -Path $backupFile -Algorithm SHA256).Hash.ToUpper()
        if ($backupHash -eq $origHash) {
            Write-PatchLog "[OK] Existing verified backup found for $leafName (SHA256: $backupHash)"
            continue
        }
    }

    if ($currentHash -eq $origHash) {
        Copy-Item -Path $targetFile -Destination $backupFile -Force
        Write-PatchLog "[BACKUP] Backed up original $leafName (SHA256: $currentHash)"
    }
    elseif ($currentHash -eq $patchedHash) {
        Write-PatchLog "[WARN] $leafName is already patched ($currentHash), but no local backup existed."
        exit 1
    }
    else {
        Write-PatchLog "[ERROR] $leafName has an unrecognized SHA-256 ($currentHash). Expected $origHash. Aborting to protect game files."
        exit 1
    }
}

# 3. Locate Python runtime to apply object-level patch
$VenvPy = Join-Path (Split-Path -Parent $ScriptDir) ".venv\Scripts\python.exe"
$PyExe = $null
if (Test-Path $VenvPy) {
    $PyExe = $VenvPy
} else {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { $PyExe = $cmd.Source }
}

if (-not $PyExe) {
    Write-PatchLog "[ERROR] Python environment not found to run tools\apply_patch.py."
    exit 1
}

$PatcherScript = Join-Path $ScriptDir "tools\apply_patch.py"
Write-PatchLog "Running object-level asset patcher ($PyExe)..."
& $PyExe $PatcherScript $GameDir $PayloadDir 2>&1 | ForEach-Object { Write-PatchLog $_ }
if ($LASTEXITCODE -ne 0) {
    Write-PatchLog "[ERROR] Patcher failed with exit code $LASTEXITCODE. Restoring backups..."
    powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ScriptDir "Uninstall-Arabic.ps1") -GameDir $GameDir
    exit 1
}

# 4. Verify patched files
foreach ($key in $FileKeys) {
    $entry = $Manifest.files.$key
    $targetFile = Join-Path $GameDir $entry.rel_path
    $newHash = (Get-FileHash -Path $targetFile -Algorithm SHA256).Hash.ToUpper()
    $leafName = Split-Path -Leaf $targetFile
    Write-PatchLog "[VERIFIED] Patched $leafName (SHA256: $newHash)"
}

Write-PatchLog "=== Arabic Localization Installed Successfully! ==="
exit 0
