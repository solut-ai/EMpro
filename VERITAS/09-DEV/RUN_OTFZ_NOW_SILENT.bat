@echo off
cd /d "%~dp0\..\.."
set "OTFZ_IGNORE_PRINTER_INIT=1"
set "OTFZ_PRINTER_OPTIONAL=1"
set "OTFZ_FAKE_PRINTER_NAME=OTFZ_NULL_PRINTER"
set "PRINTER=OTFZ_NULL_PRINTER"
start "" /min cmd /c "py -3.10 VERITAS\09-DEV\start_otfz_ignore_printer.py \"%cd%\" >nul 2>&1"
exit /b 0
