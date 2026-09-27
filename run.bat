@echo off
title SkillSwap Campus Server
echo ========================================================
echo   Starting SkillSwap Campus (Learn. Teach. Grow Together.)
echo ========================================================
echo.
cd /d "%~dp0"

if exist venv\Scripts\python.exe (
    echo [OK] Using virtual environment...
    venv\Scripts\python.exe app.py
) else (
    echo [OK] Using system Python...
    python app.py
)
pause
