@echo off
cd /d "%~dp0.."

:: 1. Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in %CD%\venv
    echo         Please run "python -m venv venv" and install dependencies.
    exit /b 1
)

:: 2. Activate Environment
call venv\Scripts\activate.bat

:: 3. Run the Python Module (Updated path to src)
echo [INFO] Running wallpaper generator...
python -m src.life_wallpaper.main

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python script failed with error code %ERRORLEVEL%
    call venv\Scripts\deactivate.bat
    exit /b %ERRORLEVEL%
)

:: 4. Cleanup
call venv\Scripts\deactivate.bat
echo [SUCCESS] Wallpaper updated.
