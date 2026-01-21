@echo off
setlocal
cd /d "%~dp0"

set "LOGFILE=uninstall.log"
echo [INFO] Starting uninstallation at %DATE% %TIME% > "%LOGFILE%"

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Requesting Administrator privileges...
    echo [INFO] Requesting Administrator privileges... >> "%LOGFILE%"
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [INFO] Admin privileges confirmed. >> "%LOGFILE%"
echo ==========================================
echo      Life Wallpaper - Uninstall
echo ==========================================
echo.

:: Execute Uninstall Script
echo [INFO] Removing scheduled task and files...
echo [INFO] Removing scheduled task and files... >> "%LOGFILE%"
powershell -NoProfile -ExecutionPolicy Bypass -File "uninstall_task.ps1" >> "%LOGFILE%" 2>&1

if %errorLevel% neq 0 (
    echo [ERROR] Uninstallation failed. Check uninstall.log.
    echo [ERROR] Uninstallation failed. >> "%LOGFILE%"
    goto :Error
)

echo.
echo ==========================================
echo [SUCCESS] Uninstallation completed.
echo ==========================================
echo [SUCCESS] Uninstallation completed at %DATE% %TIME% >> "%LOGFILE%"
echo.
echo You can close this window.
pause
exit /b 0

:Error
echo.
echo ==========================================
echo [FAILED] Uninstallation failed.
echo check %~dp0%LOGFILE% for details.
echo ==========================================
echo [FAILED] Uninstallation failed at %DATE% %TIME% >> "%LOGFILE%"
pause
exit /b 1
