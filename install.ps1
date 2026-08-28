$userProfile = [System.Environment]::GetFolderPath("UserProfile")
$effectsBaseDir = Join-Path $userProfile "Documents\WhirlwindFX\Effects"
$targetEffectDir = Join-Path $effectsBaseDir "AI Token Tracker"
$sourceDir = Join-Path $PSScriptRoot "effects\AI Token Tracker"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Installing AI Token Tracker Effect into SignalRGB..." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not (Test-Path $targetEffectDir)) {
    New-Item -ItemType Directory -Path $targetEffectDir -Force | Out-Null
    Write-Host "[+] Created directory: $targetEffectDir" -ForegroundColor Yellow
}

$sourceHtml = Join-Path $sourceDir "AI Token Tracker.html"
$targetHtml = Join-Path $targetEffectDir "AI Token Tracker.html"
Copy-Item -Path $sourceHtml -Destination $targetHtml -Force
Write-Host "[+] Installed: $targetHtml" -ForegroundColor Green

$sourcePng = Join-Path $sourceDir "AI Token Tracker.png"
if (Test-Path $sourcePng) {
    Copy-Item -Path $sourcePng -Destination $targetEffectDir -Force
    Write-Host "[+] Installed preview image." -ForegroundColor Green
}

Write-Host "`n[SUCCESS] AI Token Tracker is now installed in SignalRGB!" -ForegroundColor Green
Write-Host "Open SignalRGB -> 'Effects' or 'Customize' tab to select 'AI Token Tracker'." -ForegroundColor Cyan
