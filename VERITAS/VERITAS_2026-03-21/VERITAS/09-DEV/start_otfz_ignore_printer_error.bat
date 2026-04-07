@echo off
setlocal ENABLEEXTENSIONS

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "OTFZ_ROOT=%%~fI"
set "PY_LAUNCHER=%SCRIPT_DIR%start_otfz_ignore_printer.py"

echo ================================================================
echo OTFZ FastAPI Launcher - Ignore Printer Initialization Error
echo ================================================================
echo Root     : %OTFZ_ROOT%
echo Launcher : %PY_LAUNCHER%
echo.

if not exist "%OTFZ_ROOT%\app.py" (
  echo [ERROR] app.py not found at:
  echo %OTFZ_ROOT%\app.py
  pause
  exit /b 11
)

if not exist "%PY_LAUNCHER%" (
  echo [ERROR] Launcher not found at:
  echo %PY_LAUNCHER%
  pause
  exit /b 13
)

set "OTFZ_IGNORE_PRINTER_INIT=1"
set "OTFZ_PRINTER_OPTIONAL=1"
set "OTFZ_FAKE_PRINTER_NAME=OTFZ_NULL_PRINTER"
set "PRINTER=OTFZ_NULL_PRINTER"
set "OTFZ_HOST=127.0.0.1"
set "OTFZ_PORT=8000"

cd /d "%OTFZ_ROOT%"
echo Starting with printer bypass...
py -3.10 "%PY_LAUNCHER%" "%OTFZ_ROOT%"
set "APP_EXIT=%ERRORLEVEL%"
echo.
echo FastAPI exited with code %APP_EXIT%.
pause
exit /b %APP_EXIT%
