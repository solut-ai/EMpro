@echo off
setlocal
cd /d "%~dp0"
set "APP_ROOT=%cd%"
set "OTFZ_IGNORE_PRINTER_INIT=1"
set "OTFZ_PRINTER_OPTIONAL=1"
set "OTFZ_FAKE_PRINTER_NAME=OTFZ_NULL_PRINTER"
set "PRINTER=OTFZ_NULL_PRINTER"

if not exist "%APP_ROOT%\app.py" (
  echo [ERROR] app.py not found at "%APP_ROOT%\app.py"
  exit /b 1
)

where py >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python launcher 'py' not found in PATH.
  exit /b 1
)

if not exist "%APP_ROOT%\start_otfz_ignore_printer.py" (
  echo [ERROR] start_otfz_ignore_printer.py not found at "%APP_ROOT%\start_otfz_ignore_printer.py"
  exit /b 1
)

echo Starting OTFZ from 09-DEV app root: "%APP_ROOT%"
py -3.10 "%APP_ROOT%\start_otfz_ignore_printer.py" "%APP_ROOT%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo [ERROR] Launcher exited with code %EXIT_CODE%.
)

exit /b %EXIT_CODE%
