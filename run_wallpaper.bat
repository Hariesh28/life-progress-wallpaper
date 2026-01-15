@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m life_wallpaper.main
call venv\Scripts\deactivate.bat
