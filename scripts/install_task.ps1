$ErrorActionPreference = "Stop"

$TaskName = "LifeWallpaperUpdate"
$GuardScript = "$PSScriptRoot\guard_runner.ps1"

if (-not (Test-Path $GuardScript)) {
    Write-Error "Could not find guard_runner.ps1 at $GuardScript"
    exit 1
}

# Action updates: Run PowerShell hidden, executing the guard script
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File `"$GuardScript`"" -WorkingDirectory $PSScriptRoot

# Triggers:
# 1. Daily at 12:00 AM
$TriggerDaily = New-ScheduledTaskTrigger -Daily -At 12:00am
# 2. At Logon (Ensures it runs if machine was off and "StartWhenAvailable" misses)
$TriggerLogon = New-ScheduledTaskTrigger -AtLogon

# Combine triggers
$Triggers = @($TriggerDaily, $TriggerLogon)

# Settings:
# - Run on battery
# - Do not stop if battery kicks in
# - Start ASAP if the time was missed (sleeping/off)
# - Kill after 5 minutes if stuck (guard against hangs)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

try {
    # Get the current user (DOMAIN\Username) to ensure the task runs as the correct user
    $CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

    # Register the task
    Register-ScheduledTask -Action $Action -Trigger $Triggers -Settings $Settings -TaskName $TaskName -Description "Daily wallpaper update with guard against duplicate runs." -User $CurrentUser -Force

    Write-Host "Task '$TaskName' created successfully."
    Write-Host "Run As User: $CurrentUser"
    Write-Host "Trigger: Daily at 12:00 AM (or next available)."
    Write-Host "Command: $GuardScript"
}
catch {
    Write-Error "Failed to register task."
    Write-Error $_
}
