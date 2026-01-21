$ErrorActionPreference = "Stop"
$TaskName = "LifeWallpaperUpdate"

Write-Host "Uninstalling Life Wallpaper Automation..." -ForegroundColor Cyan

# 1. Remove Scheduled Task
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
        Write-Host "[OK] Removed Scheduled Task: $TaskName" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to remove scheduled task. Please run as Administrator."
        exit 1
    }
}
else {
    Write-Host "[INFO] Scheduled Task '$TaskName' not found." -ForegroundColor Yellow
}

# 2. Cleanup Runtime Files (Logs and State)
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$FilesToRemove = @(
    "$ProjectRoot\wallpaper_state.json",
    "$ProjectRoot\wallpaper_activity.log"
)

foreach ($File in $FilesToRemove) {
    if (Test-Path $File) {
        Remove-Item -Path $File -Force
        Write-Host "[OK] Removed file: $(Split-Path $File -Leaf)" -ForegroundColor Green
    }
}

Write-Host "`nUninstallation Complete." -ForegroundColor Green
Write-Host "To completely remove the program, you can now safely delete this folder." -ForegroundColor Gray

Read-Host "Press any key to continue..."
