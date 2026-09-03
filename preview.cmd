@echo off
REM Local preview for the Friendly Spaces site. No build step, no dependencies.
REM Double-click this file, then open http://localhost:8081
cd /d "%~dp0"
echo.
echo   Friendly Spaces - local preview
echo   ---------------------------------------
echo   http://localhost:8081
echo.
echo   Press Ctrl+C to stop.
echo.
start "" http://localhost:8081
python -m http.server 8081
