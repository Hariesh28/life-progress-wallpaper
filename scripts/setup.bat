@echo off
setlocal
cd /d "%~dp0"

set "LOGFILE=setup.log"
echo [INFO] Starting setup at %DATE% %TIME% > "%LOGFILE%"

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
echo      Life Wallpaper - One-Click Setup
echo ==========================================
echo.

:: 1. Check Python
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.8+ and add it to PATH.
    echo [ERROR] Python is not found in PATH. >> "%LOGFILE%"
    goto :Error
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [INFO] Found %%i >> "%LOGFILE%"

:: 2. Setup Virtual Environment
set "VENV_DIR=..\venv"
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo [INFO] Virtual environment already exists.
    echo [INFO] Virtual environment already exists at %VENV_DIR%. >> "%LOGFILE%"
) else (
    echo [INFO] Creating virtual environment...
    echo [INFO] Creating virtual environment... >> "%LOGFILE%"
    python -m venv "%VENV_DIR%"
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        echo [ERROR] Failed to create virtual environment. >> "%LOGFILE%"
        goto :Error
    )
    echo [SUCCESS] Virtual environment created. >> "%LOGFILE%"
)

:: 3. Install Dependencies
echo [INFO] Installing/Updating dependencies...
echo [INFO] Installing/Updating dependencies... >> "%LOGFILE%"
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip >> "%LOGFILE%" 2>&1
"%VENV_DIR%\Scripts\pip.exe" install -r "..\requirements.txt" >> "%LOGFILE%" 2>&1
"%VENV_DIR%\Scripts\pip.exe" install -e ".." >> "%LOGFILE%" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Check setup.log for details.
    echo [ERROR] Failed to install dependencies. >> "%LOGFILE%"
    goto :Error
)
echo [SUCCESS] Dependencies installed. >> "%LOGFILE%"

:: 4. Install Task
echo [INFO] Registering scheduled task...
echo [INFO] Registering scheduled task... >> "%LOGFILE%"
powershell -NoProfile -ExecutionPolicy Bypass -File "install_task.ps1" >> "%LOGFILE%" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Failed to register scheduled task.
    echo [ERROR] Failed to register scheduled task. >> "%LOGFILE%"
    goto :Error
)

echo.
echo ==========================================
echo [SUCCESS] Setup completed successfully!
echo ==========================================
echo [SUCCESS] Setup completed successfully at %DATE% %TIME% >> "%LOGFILE%"
echo.
echo You can close this window.
pause
exit /b 0

:Error
echo.
echo ==========================================
echo [FAILED] Setup failed.
echo check %~dp0%LOGFILE% for details.
echo ==========================================
echo [FAILED] Setup failed at %DATE% %TIME% >> "%LOGFILE%"
pause
exit /b 1
