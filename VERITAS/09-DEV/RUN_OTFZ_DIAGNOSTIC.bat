@echo off
setlocal ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "OTFZ_ROOT=%%~fI"
set "PRECHECK=%SCRIPT_DIR%otfz_fastapi_build_check.py"
set "PY_LAUNCHER=%SCRIPT_DIR%start_otfz_ignore_printer.py"
set "LOG_DIR=%OTFZ_ROOT%\logs"
set "LOG_FILE=%LOG_DIR%\otfz_diagnostic_latest.log"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>&1

echo ================================================================ > "%LOG_FILE%"
echo OTFZ Diagnostic Launcher >> "%LOG_FILE%"
echo ================================================================ >> "%LOG_FILE%"
echo DATE: %DATE% %TIME% >> "%LOG_FILE%"
echo ROOT: %OTFZ_ROOT% >> "%LOG_FILE%"
echo PRECHECK: %PRECHECK% >> "%LOG_FILE%"
echo PY_LAUNCHER: %PY_LAUNCHER% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

echo OTFZ diagnostic log:
echo %LOG_FILE%
echo.

if not exist "%OTFZ_ROOT%\app.py" (
  echo [ERROR] app.py not found at %OTFZ_ROOT%\app.py >> "%LOG_FILE%"
  echo [ERROR] app.py not found.
  echo See log: %LOG_FILE%
  pause
  exit /b 11
)

where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python launcher 'py' not found in PATH. >> "%LOG_FILE%"
  echo [ERROR] Python launcher 'py' not found.
  echo See log: %LOG_FILE%
  pause
  exit /b 12
)

if not exist "%PY_LAUNCHER%" (
  echo [ERROR] Printer-bypass launcher not found at %PY_LAUNCHER% >> "%LOG_FILE%"
  echo [ERROR] Printer-bypass launcher not found.
  echo See log: %LOG_FILE%
  pause
  exit /b 13
)

set "OTFZ_IGNORE_PRINTER_INIT=1"
set "OTFZ_PRINTER_OPTIONAL=1"
set "OTFZ_FAKE_PRINTER_NAME=OTFZ_NULL_PRINTER"
set "PRINTER=OTFZ_NULL_PRINTER"
set "OTFZ_HOST=127.0.0.1"
set "OTFZ_PORT=8000"

echo ENV: OTFZ_IGNORE_PRINTER_INIT=%OTFZ_IGNORE_PRINTER_INIT% >> "%LOG_FILE%"
echo ENV: OTFZ_PRINTER_OPTIONAL=%OTFZ_PRINTER_OPTIONAL% >> "%LOG_FILE%"
echo ENV: OTFZ_FAKE_PRINTER_NAME=%OTFZ_FAKE_PRINTER_NAME% >> "%LOG_FILE%"
echo ENV: PRINTER=%PRINTER% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

if exist "%PRECHECK%" (
  echo [PRECHECK] Running static scan... >> "%LOG_FILE%"
  echo [PRECHECK] Command: py -3.10 "%PRECHECK%" "%OTFZ_ROOT%" --verbose --json "%OTFZ_ROOT%\build_check_report.json" >> "%LOG_FILE%"
  py -3.10 "%PRECHECK%" "%OTFZ_ROOT%" --verbose --json "%OTFZ_ROOT%\build_check_report.json" >> "%LOG_FILE%" 2>&1
  set "PRECHECK_EXIT=!ERRORLEVEL!"
  echo [PRECHECK] Exit code: !PRECHECK_EXIT! >> "%LOG_FILE%"
  if not "!PRECHECK_EXIT!"=="0" (
    echo [PRECHECK] Continuing anyway. Precheck failure will not block startup. >> "%LOG_FILE%"
  )
  echo. >> "%LOG_FILE%"
) else (
  echo [PRECHECK] Script not found. Skipping and continuing. >> "%LOG_FILE%"
  echo. >> "%LOG_FILE%"
)

echo [START] Launching FastAPI through printer bypass... >> "%LOG_FILE%"
cd /d "%OTFZ_ROOT%"
echo [START] Command: py -3.10 "%PY_LAUNCHER%" "%OTFZ_ROOT%" >> "%LOG_FILE%"
py -3.10 "%PY_LAUNCHER%" "%OTFZ_ROOT%" >> "%LOG_FILE%" 2>&1
set "APP_EXIT=%ERRORLEVEL%"
echo. >> "%LOG_FILE%"
echo [EXIT] FastAPI exited with code !APP_EXIT! >> "%LOG_FILE%"
echo [DONE] Review log file at: %LOG_FILE% >> "%LOG_FILE%"

echo.
echo FastAPI exited with code %APP_EXIT%
echo Review log:
echo %LOG_FILE%
pause
exit /b %APP_EXIT%
