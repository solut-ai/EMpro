from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def resolve_root() -> Path:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return Path(sys.argv[1]).resolve()
    return Path(__file__).resolve().parents[2]


def main() -> int:
    root = resolve_root()
    app_file = root / "app.py"
    if not app_file.exists():
        print(f"[ERROR] app.py not found at: {app_file}")
        return 11

    host = os.environ.get("OTFZ_HOST", "127.0.0.1")
    port = os.environ.get("OTFZ_PORT", "8000")

    env = os.environ.copy()
    env["OTFZ_IGNORE_PRINTER_INIT"] = "1"
    env["OTFZ_PRINTER_OPTIONAL"] = "1"
    env["OTFZ_FAKE_PRINTER_NAME"] = "OTFZ_NULL_PRINTER"
    env["PRINTER"] = "OTFZ_NULL_PRINTER"
    env["PYTHONPATH"] = str(root) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    bootstrap = textwrap.dedent(
        r'''
        import importlib
        import os
        import sys
        import traceback
        import types
        from pathlib import Path

        root = Path(sys.argv[1]).resolve()
        host = sys.argv[2]
        port = int(sys.argv[3])

        def dummy_printer_handle():
            return {"name": os.environ.get("OTFZ_FAKE_PRINTER_NAME", "OTFZ_NULL_PRINTER"), "status": "ignored"}

        class DummyDC:
            def CreatePrinterDC(self, *args, **kwargs): return None
            def StartDoc(self, *args, **kwargs): return 1
            def StartPage(self, *args, **kwargs): return 1
            def EndPage(self, *args, **kwargs): return 1
            def EndDoc(self, *args, **kwargs): return 1
            def DeleteDC(self, *args, **kwargs): return None
            def AbortDoc(self, *args, **kwargs): return None

        class DummyEscposPrinter:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs
            def text(self, *args, **kwargs): return None
            def image(self, *args, **kwargs): return None
            def barcode(self, *args, **kwargs): return None
            def qr(self, *args, **kwargs): return None
            def cut(self, *args, **kwargs): return None
            def close(self, *args, **kwargs): return None
            def open(self, *args, **kwargs): return None
            def open_cashdraw(self, *args, **kwargs): return None

        try:
            import win32print  # type: ignore
        except Exception:
            win32print = types.ModuleType("win32print")
            sys.modules["win32print"] = win32print

        win32print.GetDefaultPrinter = lambda *a, **k: os.environ.get("OTFZ_FAKE_PRINTER_NAME", "OTFZ_NULL_PRINTER")
        win32print.EnumPrinters = lambda *a, **k: []
        win32print.OpenPrinter = lambda *a, **k: dummy_printer_handle()
        win32print.ClosePrinter = lambda *a, **k: None
        win32print.GetPrinter = lambda *a, **k: {"pPrinterName": os.environ.get("OTFZ_FAKE_PRINTER_NAME", "OTFZ_NULL_PRINTER")}
        win32print.StartDocPrinter = lambda *a, **k: 1
        win32print.EndDocPrinter = lambda *a, **k: None
        win32print.StartPagePrinter = lambda *a, **k: 1
        win32print.EndPagePrinter = lambda *a, **k: None
        win32print.WritePrinter = lambda *a, **k: 0
        win32print.SetDefaultPrinter = lambda *a, **k: None

        try:
            import win32ui  # type: ignore
        except Exception:
            win32ui = types.ModuleType("win32ui")
            sys.modules["win32ui"] = win32ui
        win32ui.CreateDC = lambda *a, **k: DummyDC()

        escpos_module = sys.modules.get("escpos")
        if escpos_module is None:
            escpos_module = types.ModuleType("escpos")
            sys.modules["escpos"] = escpos_module

        try:
            import escpos.printer as escpos_printer  # type: ignore
        except Exception:
            escpos_printer = types.ModuleType("escpos.printer")
            sys.modules["escpos.printer"] = escpos_printer
        for name in ["Win32Raw", "Usb", "Network", "File", "Serial", "Dummy"]:
            setattr(escpos_printer, name, DummyEscposPrinter)

        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

        try:
            module = importlib.import_module("app")
        except Exception:
            print("[ERROR] Failed to import app.py after printer bypass patch.")
            traceback.print_exc()
            raise SystemExit(20)

        fastapi_app = getattr(module, "app", None)
        if fastapi_app is None:
            print("[ERROR] Imported app.py but did not find variable named 'app'.")
            raise SystemExit(21)

        try:
            import uvicorn
        except Exception:
            print("[ERROR] uvicorn is not installed in the active Python environment.")
            traceback.print_exc()
            raise SystemExit(22)

        print("[INFO] Printer initialization bypass is active.")
        print(f"[INFO] Root: {root}")
        print(f"[INFO] Host/Port: {host}:{port}")
        print("[INFO] Reload is disabled for the printer-bypass launcher.")
        uvicorn.run(fastapi_app, host=host, port=port, reload=False)
        '''
    )

    with tempfile.NamedTemporaryFile("w", suffix="_otfz_printer_bootstrap.py", delete=False, encoding="utf-8") as tmp:
        tmp.write(bootstrap)
        bootstrap_path = tmp.name

    cmd = [sys.executable, bootstrap_path, str(root), host, port]
    print("[INFO] Running printer-bypass startup command:")
    print(" ".join([cmd[0]] + [f'"{part}"' if " " in part else part for part in cmd[1:]]))

    try:
        completed = subprocess.run(cmd, cwd=str(root), env=env)
        return completed.returncode
    finally:
        try:
            os.remove(bootstrap_path)
        except OSError:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
