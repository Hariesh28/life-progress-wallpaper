param (
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# --- Configuration ---
# Calculate paths relative to this script (scripts/)
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$StateFile = "$ProjectRoot\wallpaper_state.json"
$LogFile = "$ProjectRoot\wallpaper_activity.log"
$WallpaperScript = "$PSScriptRoot\run_wallpaper.bat"

# --- Logging Helper ---
function Write-Log {
    param ([string]$Message)

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"

    # Console output
    Write-Host $LogEntry

    # File output with simple retry logic for locking
    $RetryCount = 3
    while ($RetryCount -gt 0) {
        try {
            Add-Content -Path $LogFile -Value $LogEntry -ErrorAction Stop
            break
        } catch {
            Start-Sleep -Milliseconds 100
            $RetryCount--
        }
    }
}

try {
    # 1. Check Previous Execution
    $Today = (Get-Date).ToString("yyyy-MM-dd")

    if (-not $Force -and (Test-Path $StateFile)) {
        try {
            $StateContent = Get-Content $StateFile -Raw
            if ($StateContent) {
                $State = $StateContent | ConvertFrom-Json
                if ($State.LastRunDate -eq $Today) {
                    Write-Log "Skipping update: Already executed for today ($Today)."
                    exit 0
                }
            }
        } catch {
            Write-Log "Warning: State file corrupted or unreadable. Proceeding with update."
        }
    } elseif ($Force) {
        Write-Log "Force flag detected. Bypassing date check."
    }

    # 2. Validation
    if (-not (Test-Path $WallpaperScript)) {
        throw "Wallpaper script missing at: $WallpaperScript"
    }

    # 3. Execution
    Write-Log "Starting wallpaper update..."
    Write-Log "Script: $WallpaperScript"

    # Run the batch file
    # We use Start-Process to ensure we capture output clearly and separate the process
    $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
    $ProcessInfo.FileName = $WallpaperScript
    $ProcessInfo.WorkingDirectory = $ProjectRoot
    $ProcessInfo.RedirectStandardOutput = $true
    $ProcessInfo.RedirectStandardError = $true
    $ProcessInfo.UseShellExecute = $false
    $ProcessInfo.CreateNoWindow = $true

    $Process = New-Object System.Diagnostics.Process
    $Process.StartInfo = $ProcessInfo
    $Process.Start() | Out-Null

    $StdOut = $Process.StandardOutput.ReadToEnd()
    $StdErr = $Process.StandardError.ReadToEnd()

    $Process.WaitForExit()

    # 4. Log Output
    if ($StdOut) { Write-Log "OUTPUT:`n$StdOut" }
    if ($StdErr) { Write-Log "ERROR:`n$StdErr" }

    if ($Process.ExitCode -eq 0) {
        Write-Log "SUCCESS: Wallpaper updated."

        # 5. Update State (Atomic-ish)
        $NewState = @{
            LastRunDate = $Today
            LastRunTime = (Get-Date).ToString("HH:mm:ss")
        }

        $TempStateFile = "$StateFile.tmp"
        $NewState | ConvertTo-Json | Set-Content $TempStateFile
        Move-Item -Path $TempStateFile -Destination $StateFile -Force

    } else {
        Write-Log "FAILURE: Script exited with code $($Process.ExitCode)"
        exit 1
    }

} catch {
    Write-Log "CRITICAL ERROR: $_"
    Write-Log "Stack Trace: $($_.ScriptStackTrace)"
    exit 1
}
