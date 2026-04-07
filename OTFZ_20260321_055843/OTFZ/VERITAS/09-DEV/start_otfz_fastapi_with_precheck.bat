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
echo OTFZ FastAPI Launcher with Precheck
echo ================================================================
echo Root      : %OTFZ_ROOT%
echo Precheck  : %PRECHECK%
echo Report    : %REPORT%
echo Host/Port : %HOST%:%PORT%
echo.

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

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python launcher 'py' was not found in PATH.
  pause
  exit /b 12
)

echo [1/3] Running static precheck...
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

echo [2/3] Checking dependency hints...
if exist "%OTFZ_ROOT%\requirements.txt" (
  echo requirements.txt found.
) else (
  echo [INFO] requirements.txt not found at root. Using current environment as-is.
)
echo.

echo [3/3] Starting FastAPI with uvicorn...
cd /d "%OTFZ_ROOT%"
py -3.10 -m uvicorn app:app --reload --host %HOST% --port %PORT%
set "UVICORN_EXIT=%ERRORLEVEL%"
echo.
echo FastAPI process exited with code %UVICORN_EXIT%.
pause
exit /b %UVICORN_EXIT%
