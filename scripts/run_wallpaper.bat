@echo off
setlocal
cd /d "%~dp0"

set "LOGFILE=manual_run.log"
echo [INFO] Starting manual wallpaper run at %DATE% %TIME% > "%LOGFILE%"

:: 1. Check Python/Venv
set "VENV_DIR=..\venv"
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at %VENV_DIR%.
    echo [ERROR] Virtual environment not found. >> "%LOGFILE%"
    echo         Please run "setup.bat" first to initialize the project.
    goto :Error
)

:: 2. Activate Environment
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorLevel% neq 0 (
    echo [ERROR] Failed to activate venv.
    echo [ERROR] Failed to activate venv. >> "%LOGFILE%"
    goto :Error
)

:: 3. Run the Python Module
echo [INFO] Running wallpaper generator...
echo [INFO] Running wallpaper generator... >> "%LOGFILE%"
python -m life_wallpaper.main >> "%LOGFILE%" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Wallpaper script failed. Check %LOGFILE% for details.
    echo [ERROR] Wallpaper script failed. >> "%LOGFILE%"
    goto :Error
)

:: 4. Success
echo [SUCCESS] Wallpaper updated successfully! >> "%LOGFILE%"
echo.
echo [SUCCESS] Wallpaper updated.
echo.
call "%VENV_DIR%\Scripts\deactivate.bat"
echo Done.
:: Pause only if explicitly double-clicked (optional, but good for manual runs)
pause
exit /b 0

:Error
echo.
echo [FAILED] Execution failed.
echo Check %~dp0%LOGFILE% for details.
echo [FAILED] Execution failed at %DATE% %TIME% >> "%LOGFILE%"
if exist "%VENV_DIR%\Scripts\deactivate.bat" call "%VENV_DIR%\Scripts\deactivate.bat"
pause
exit /b 1
