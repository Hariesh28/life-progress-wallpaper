$ErrorActionPreference = "Stop"

$TaskName = "DailyWallpaperUpdate"
$GuardScript = "$PSScriptRoot\GuardWallpaperUpdate.ps1"

if (-not (Test-Path $GuardScript)) {
    Write-Error "Could not find GuardWallpaperUpdate.ps1 at $GuardScript"
    exit 1
}

# Action updates: Run PowerShell hidden, executing the guard script
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$GuardScript`""

# Trigger: Check daily at 12:00 AM
$Trigger = New-ScheduledTaskTrigger -Daily -At 12:00am

# Settings:
# - Run on battery
# - Do not stop if battery kicks in
# - Start ASAP if the time was missed (sleeping/off)
# - Kill after 5 minutes if stuck (guard against hangs)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

try {
    # Register purely as the current user ("LogonUser" ensures it runs in the user's session to change wallpaper)
    Register-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings -TaskName $TaskName -Description "Daily wallpaper update with guard against duplicate runs." -User "LogonUser" -Force
    Write-Host "Task '$TaskName' created successfully."
    Write-Host "Trigger: Daily at 12:00 AM (or next available)."
    Write-Host "Command: $GuardScript"
}
catch {
    Write-Error "Failed to register task."
    Write-Error $_
}
