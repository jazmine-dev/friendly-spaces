@echo off
REM Rebuilds index.html and sponsoring.html from src\templates. Double-click after editing a template.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1
pause
