@echo off
REM ResumeChap launcher for Windows (double-clickable).
cd /d "%~dp0app"

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  set PY=python
) else (
  where py >nul 2>nul
  if %ERRORLEVEL%==0 (
    set PY=py
  ) else (
    echo Python 3 is required but was not found.
    echo Install it from https://www.python.org/downloads/ and check "Add Python to PATH".
    pause
    exit /b 1
  )
)

%PY% run.py %*
pause
