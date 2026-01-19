@echo off
cd /d "%~dp0"
echo ==========================================
echo      Installing Wallpaper Task
echo ==========================================
echo.

:: Check for Admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges.
    echo         Please right-click and select "Run as Administrator".
    echo.
    pause
    exit /b
)

echo [INFO] Administrative privileges detected.
echo [INFO] Installing task...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "install_task.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Task installation command finished.
    echo           Verifying task existence...
    schtasks /query /TN "DailyWallpaperUpdate" /FO LIST
) else (
    echo.
    echo [ERROR] PowerShell script failed.
)

echo.
echo Done.
pause
