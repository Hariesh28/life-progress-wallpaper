$ErrorActionPreference = "Stop"

# Configuration
$StateFile = "$PSScriptRoot\wallpaper_state.json"
$LogFile = "$PSScriptRoot\wallpaper_activity.log"
$WallpaperScript = "$PSScriptRoot\run_wallpaper.bat"

# Function to write to log
function Write-Log {
    param ([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Add-Content -Path $LogFile -Value $LogEntry
    Write-Host $LogEntry
}

try {
    # 1. Check if we already ran today
    $Today = (Get-Date).ToString("yyyy-MM-dd")

    if (Test-Path $StateFile) {
        $State = Get-Content $StateFile | ConvertFrom-Json
        if ($State.LastRunDate -eq $Today) {
            Write-Log "Skipping update: Already executed for today ($Today)."
            exit 0
        }
    }

    # 2. Run the actual wallpaper update
    Write-Log "Starting wallpaper update..."

    $Process = Start-Process -FilePath $WallpaperScript -Wait -NoNewWindow -PassThru

    if ($Process.ExitCode -eq 0) {
        Write-Log "Wallpaper update completed successfully."

        # 3. Update state file
        $NewState = @{
            LastRunDate = $Today
            LastRunTime = (Get-Date).ToString("HH:mm:ss")
        }
        $NewState | ConvertTo-Json | Set-Content $StateFile
    }
    else {
        Write-Log "ERROR: Wallpaper script failed with exit code $($Process.ExitCode)."
        exit 1
    }

}
catch {
    Write-Log "CRITICAL ERROR: $_"
    exit 1
}
