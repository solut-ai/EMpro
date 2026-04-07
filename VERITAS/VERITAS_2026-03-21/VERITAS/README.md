# OTFZ VERITAS Completion Bundle

Date: 2026-03-21  
Launch date: 2026-03-21  
Target run date: 2026-06-21

This bundle contains the current VERITAS core pack for transfer, local extraction, hashing, ingest, investor support, and Spektraxa management / learning use.

## Folder map

- `00-INDEX/VERITAS_MASTER_INDEX.md`
- `00-INDEX/VERITAS_CHANGELOG.md`
- `00-INDEX/VERITAS_FILE_REGISTER.csv`
- `00-INDEX/VERITAS_TAGS.json`
- `00-INDEX/Public_Source_Links.md`
- `01-WHITEPAPER/EchoMind_Overview.md`
- `01-WHITEPAPER/Spektraxa_AIR_Identity.md`
- `01-WHITEPAPER/Homepage_Hero_Copy.md`
- `03-CONSENSUS/SLVR8_Veritas_Spec_v0_2.md`
- `05-EDUCATION/Digital_Assets_Explained.md`
- `05-EDUCATION/AIR_Onboarding_Script.md`
- `06-BUSINESS/Investor_One_Pager.md`
- `06-BUSINESS/Multi-Commerce_MCt_Unreleased_Token_Profile.md`
- `09-DEV/otfz_fastapi_build_check.py`
- `09-DEV/start_otfz_fastapi_with_precheck.bat`
- `09-DEV/install_requirements_and_start_otfz.bat`
- `09-DEV/start_otfz_ignore_printer.py`
- `09-DEV/start_otfz_ignore_printer_error.bat`
- `09-DEV/RUN_OTFZ_NOW.bat`
- `09-DEV/RUN_OTFZ_NOW_SILENT.bat`
- `09-DEV/RUN_OTFZ_DIAGNOSTIC.bat`
- `09-DEV/RUN_OTFZ_DIAGNOSTIC_NO_PRECHECK.bat`

## Recommended local search bin

`C:\Users\middl\Documents\OTFZ`

## Recommended extracted destination

`C:\Users\middl\Documents\OTFZ\VERITAS`

## Local build-check script

Run the static FastAPI build check from the local bin after transfer:

`py -3.10 C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\otfz_fastapi_build_check.py C:\Users\middl\Documents\OTFZ --verbose`

The script checks for FastAPI startup expectations and flags potentially threatening code patterns such as `exec`, `eval`, unsafe subprocess usage, suspicious outbound endpoints, unsafe deserialization, and obfuscation-like payload lines before you start the app.

Windows launchers are also included:

`C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\start_otfz_fastapi_with_precheck.bat`

That launcher runs the precheck first, blocks on critical findings, prompts on high-severity findings, and then starts `uvicorn app:app --reload --host 127.0.0.1 --port 8000`.

`C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\install_requirements_and_start_otfz.bat`

That launcher first installs or refreshes dependencies from `requirements.txt` when present, then runs the same precheck flow, and finally starts the FastAPI app.

A printer-bypass launcher set is also included for systems where startup fails on missing printer or printer-device initialization:

`C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\start_otfz_ignore_printer_error.bat`

That BAT file runs the precheck, sets printer-optional environment flags, and then starts:

`C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\start_otfz_ignore_printer.py`

The Python wrapper patches common Windows printer interfaces such as `win32print`, `win32ui`, and common ESC/POS printer classes so the app can start even when no printer is physically connected. To preserve the patch, this path intentionally starts FastAPI with reload disabled.

For the shortest possible startup path, use:

`C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\RUN_OTFZ_NOW.bat`

That file only changes into the OTFZ root, sets printer-ignore environment variables, and launches the printer-bypass Python starter with minimal commands.

For the quietest startup path, use:

`C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\RUN_OTFZ_NOW_SILENT.bat`

That file uses the same printer-ignore environment variables but launches the Python starter through a minimized `cmd /c` path with stdout and stderr redirected to `nul`.

For troubleshooting, use:

`C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\RUN_OTFZ_DIAGNOSTIC.bat`

That launcher writes a local diagnostic log to `C:\Users\middl\Documents\OTFZ\logs\otfz_diagnostic_latest.log`, including precheck output, environment flags, launcher output, and FastAPI stderr/stdout.

If the precheck path is the part that is failing, use:

`C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV\RUN_OTFZ_DIAGNOSTIC_NO_PRECHECK.bat`

That variant skips precheck entirely and logs only the printer-bypass launcher and FastAPI startup output to `C:\Users\middl\Documents\OTFZ\logs\otfz_diagnostic_no_precheck.log`.

## Public source anchors

- https://outthefreezer.shop/
- https://outthefreezer.square.site/whitepaper
- https://bitcoin.org/bitcoin.pdf
- https://docs.cometbft.com/main/spec/consensus/consensus
- https://www.ibm.com/history/system-360
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4111501/

OUTTHEFREEZER provides the ecosystem context, the whitepaper supplies the Veritas / SLVR8 story, Bitcoin anchors the digital-value narrative, and CometBFT anchors the round-based BFT reference flow used in the technical draft [Source](https://outthefreezer.shop/) [Source](https://outthefreezer.square.site/whitepaper) [Source](https://bitcoin.org/bitcoin.pdf) [Source](https://docs.cometbft.com/main/spec/consensus/consensus)
