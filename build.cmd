@echo off
REM Rebuilds every page from src\ into the site root. Double-click after editing.
cd /d "%~dp0"
python build.py
pause
