<#
.SYNOPSIS
    Installer script for SignalRGB AI Token Tracker.
.DESCRIPTION
    Installs AITokenTracker executable to LocalAppData, copies the SignalRGB effect
    files to WhirlwindFX Effects directory, creates Startup and Desktop shortcuts,
    and launches the tracker in background mode.
#>

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       SignalRGB AI Token Tracker - Installation          " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Paths configuration
$sourceDir = $PSScriptRoot
$sourceExe = Join-Path $sourceDir "AITokenTracker.exe"
$sourceEffectsDir = Join-Path $sourceDir "effects\AI Token Tracker"
$sourceConfig = Join-Path $sourceDir "config.json"

$installDir = Join-Path $env:LOCALAPPDATA "AITokenTracker"
$targetExe = Join-Path $installDir "AITokenTracker.exe"
$targetConfig = Join-Path $installDir "config.json"

$userProfile = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
$effectsBaseDir = Join-Path $userProfile "Documents\WhirlwindFX\Effects"
$targetEffectDir = Join-Path $effectsBaseDir "AI Token Tracker"

$startupDir = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Startup)
$desktopDir = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)

# 2. Stop running instance if active
$runningProcesses = Get-Process -Name "AITokenTracker" -ErrorAction SilentlyContinue
if ($runningProcesses) {
    Write-Host "[*] Stopping existing AI Token Tracker process..." -ForegroundColor Yellow
    Stop-Process -Name "AITokenTracker" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# 3. Create install directory
Write-Host "[1/5] Setting up installation folder..." -ForegroundColor Cyan
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}
Write-Host "  [+] Install directory: $installDir" -ForegroundColor Green

# 4. Copy executable and configuration
Write-Host "[2/5] Copying application files..." -ForegroundColor Cyan
if (Test-Path $sourceExe) {
    Copy-Item -Path $sourceExe -Destination $targetExe -Force
    Write-Host "  [+] Copied AITokenTracker.exe" -ForegroundColor Green
} else {
    Write-Host "  [!] Notice: AITokenTracker.exe not found in source directory." -ForegroundColor Yellow
    Write-Host "      If building from source or testing, ensure AITokenTracker.exe is in the root folder." -ForegroundColor Yellow
}

if (Test-Path $sourceConfig) {
    if (-not (Test-Path $targetConfig)) {
        Copy-Item -Path $sourceConfig -Destination $targetConfig -Force
        Write-Host "  [+] Copied default config.json" -ForegroundColor Green
    } else {
        Write-Host "  [i] Preserving existing config.json" -ForegroundColor DarkGray
    }
}

# 5. Install SignalRGB Effect
Write-Host "[3/5] Installing SignalRGB effect files..." -ForegroundColor Cyan
if (-not (Test-Path $targetEffectDir)) {
    New-Item -ItemType Directory -Path $targetEffectDir -Force | Out-Null
}

if (Test-Path $sourceEffectsDir) {
    Copy-Item -Path (Join-Path $sourceEffectsDir "*") -Destination $targetEffectDir -Recurse -Force
    Write-Host "  [+] Effect installed to: $targetEffectDir" -ForegroundColor Green
} else {
    Write-Host "  [!] Warning: Source effect directory not found at $sourceEffectsDir" -ForegroundColor Yellow
}

# 6. Create Shortcuts (Startup and Desktop)
Write-Host "[4/5] Creating shortcuts..." -ForegroundColor Cyan
try {
    $wscript = New-Object -ComObject WScript.Shell

    # Windows Startup Shortcut (launches with --background)
    $startupShortcutPath = Join-Path $startupDir "AI Token Tracker.lnk"
    $startupShortcut = $wscript.CreateShortcut($startupShortcutPath)
    $startupShortcut.TargetPath = $targetExe
    $startupShortcut.Arguments = "--background"
    $startupShortcut.WorkingDirectory = $installDir
    $startupShortcut.Description = "SignalRGB AI Token Tracker (Startup Background Service)"
    $startupShortcut.Save()
    Write-Host "  [+] Windows Startup shortcut created" -ForegroundColor Green

    # Desktop Shortcut
    $desktopShortcutPath = Join-Path $desktopDir "AI Token Tracker.lnk"
    $desktopShortcut = $wscript.CreateShortcut($desktopShortcutPath)
    $desktopShortcut.TargetPath = $targetExe
    $desktopShortcut.WorkingDirectory = $installDir
    $desktopShortcut.Description = "SignalRGB AI Token Tracker"
    $desktopShortcut.Save()
    Write-Host "  [+] Desktop shortcut created" -ForegroundColor Green

    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($wscript) | Out-Null
} catch {
    Write-Host "  [!] Warning: Failed to create shortcuts: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 7. Start application in background mode
Write-Host "[5/5] Launching application..." -ForegroundColor Cyan
if (Test-Path $targetExe) {
    try {
        Start-Process -FilePath $targetExe -ArgumentList "--background" -WorkingDirectory $installDir
        Write-Host "  [+] AI Token Tracker started in background mode." -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not start process: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [i] Skipping startup because AITokenTracker.exe was not present." -ForegroundColor DarkGray
}

# 8. Finished summary
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   [SUCCESS] AI Token Tracker Setup Completed!            " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " - App Directory     : $installDir" -ForegroundColor White
Write-Host " - SignalRGB Effect  : $targetEffectDir" -ForegroundColor White
Write-Host " - Auto-start        : Enabled (Windows Startup)" -ForegroundColor White
Write-Host " - Desktop Shortcut  : Created" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host " 1. Open SignalRGB." -ForegroundColor White
Write-Host " 2. Go to the 'Customize' or 'Effects' tab." -ForegroundColor White
Write-Host " 3. Select 'AI Token Tracker' to view live RGB metrics." -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
