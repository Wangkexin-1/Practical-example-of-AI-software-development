@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py "samples\valid\all_modalities.csv" %*
    goto finished
)
where python >nul 2>nul
if not errorlevel 1 (
    python main.py "samples\valid\all_modalities.csv" %*
    goto finished
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 main.py "samples\valid\all_modalities.csv" %*
    goto finished
)
echo Python was not found. Please follow docs/run.md to prepare Python with Tkinter.
pause
exit /b 1
:finished
if errorlevel 1 (
    echo Application failed. Check logs/application.log.
    pause
    exit /b 1
)
exit /b 0
