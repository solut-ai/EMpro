@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "OTFZ_ROOT=%%~fI"
set "VERITAS_DEV=%SCRIPT_DIR%"
set "PRECHECK=%VERITAS_DEV%otfz_fastapi_build_check.py"
set "REPORT=%OTFZ_ROOT%\build_check_report.json"
set "HOST=127.0.0.1"
set "PORT=8000"

echo ================================================================
echo OTFZ Install Requirements + FastAPI Launcher
echo ================================================================
echo Root      : %OTFZ_ROOT%
echo Precheck  : %PRECHECK%
echo Report    : %REPORT%
echo Host/Port : %HOST%:%PORT%
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python launcher 'py' was not found in PATH.
  pause
  exit /b 12
)

if not exist "%PRECHECK%" (
  echo [ERROR] Precheck script not found.
  echo Expected: %PRECHECK%
  pause
  exit /b 10
)

if not exist "%OTFZ_ROOT%\app.py" (
  echo [ERROR] app.py not found at OTFZ root.
  echo Expected: %OTFZ_ROOT%\app.py
  pause
  exit /b 11
)

cd /d "%OTFZ_ROOT%"

echo [1/4] Installing or refreshing dependencies...
if exist "%OTFZ_ROOT%\requirements.txt" (
  py -3.10 -m pip install -r "%OTFZ_ROOT%\requirements.txt"
  set "PIP_EXIT=%ERRORLEVEL%"
  if not "%PIP_EXIT%"=="0" (
    echo [ERROR] requirements install failed with code %PIP_EXIT%.
    pause
    exit /b %PIP_EXIT%
  )
) else (
  echo [INFO] requirements.txt not found at root. Skipping dependency install.
)
echo.

echo [2/4] Running static precheck...
py -3.10 "%PRECHECK%" "%OTFZ_ROOT%" --verbose --json "%REPORT%"
set "SCAN_EXIT=%ERRORLEVEL%"
echo.

if %SCAN_EXIT% GEQ 2 (
  echo [BLOCKED] Critical findings detected. FastAPI startup aborted.
  echo Review: %REPORT%
  pause
  exit /b %SCAN_EXIT%
)

if %SCAN_EXIT% EQU 1 (
  echo [WARNING] High-severity findings detected.
  echo Review the report before continuing:
  echo %REPORT%
  choice /C YN /N /M "Continue starting FastAPI anyway? [Y/N]: "
  if errorlevel 2 (
    echo Startup canceled by user.
    exit /b 1
  )
)

echo [3/4] Starting FastAPI with uvicorn...
py -3.10 -m uvicorn app:app --reload --host %HOST% --port %PORT%
set "UVICORN_EXIT=%ERRORLEVEL%"
echo.

echo [4/4] FastAPI process exited with code %UVICORN_EXIT%.
pause
exit /b %UVICORN_EXIT%
