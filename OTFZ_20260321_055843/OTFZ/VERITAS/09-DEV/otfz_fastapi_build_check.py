from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

DEFAULT_ROOT = Path(r"C:\Users\middl\Documents\OTFZ")
MAX_FILE_SIZE = 2_500_000  # bytes
TEXT_EXTENSIONS = {".py", ".txt", ".md", ".json", ".toml", ".ini", ".cfg", ".yml", ".yaml"}
CODE_EXTENSIONS = {".py"}

SEVERITY_ORDER = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

PATTERN_RULES = [
    ("CRITICAL", r"\bexec\s*\(", "Dynamic exec() usage can run arbitrary code."),
    ("CRITICAL", r"\beval\s*\(", "Dynamic eval() usage can execute attacker-controlled expressions."),
    ("HIGH", r"\bos\.system\s*\(", "os.system() executes shell commands directly."),
    ("HIGH", r"subprocess\.(run|Popen|call|check_output|check_call)\s*\(", "Subprocess execution detected; verify command safety."),
    ("HIGH", r"shell\s*=\s*True", "shell=True increases command injection risk."),
    ("HIGH", r"pickle\.loads\s*\(", "pickle.loads() on untrusted data can be unsafe."),
    ("HIGH", r"marshal\.loads\s*\(", "marshal.loads() may be used to unpack opaque payloads."),
    ("HIGH", r"ctypes\.", "ctypes usage can load native code or alter process memory."),
    ("HIGH", r"winreg\.", "Windows registry modification capability detected."),
    ("HIGH", r"schtasks|powershell|reg add|curl\s+http|wget\s+http", "System-level command or remote fetch pattern detected."),
    ("MEDIUM", r"requests\.(post|put|get)\s*\(", "Network requests detected; review destinations and payloads."),
    ("MEDIUM", r"urllib\.(request|parse)|httpx\.", "HTTP client usage detected; verify outbound network intent."),
    ("MEDIUM", r"base64\.b64decode\s*\(", "Encoded payload decoding detected; review for obfuscation."),
    ("MEDIUM", r"os\.environ|getenv\s*\(", "Environment-variable access detected; verify secret handling."),
    ("MEDIUM", r"open\s*\(.+,\s*['\"]w", "File write operation detected."),
    ("MEDIUM", r"socket\.", "Socket usage detected; review network behavior."),
    ("LOW", r"FastAPI\s*\(", "FastAPI app construction detected."),
    ("LOW", r"uvicorn", "Uvicorn reference detected."),
]

SUSPICIOUS_HOST_RULES = [
    ("HIGH", r"https?://(?:\d{1,3}\.){3}\d{1,3}", "Direct IP HTTP endpoint found."),
    ("HIGH", r"pastebin|gist\.githubusercontent|raw\.githubusercontent", "Raw code hosting endpoint found; verify if intentional."),
    ("MEDIUM", r"ngrok|trycloudflare|serveo", "Tunnel endpoint found; review exposure risk."),
]


@dataclass
class Finding:
    severity: str
    file: str
    line: int
    category: str
    message: str
    snippet: str = ""


class ThreatVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.findings: list[Finding] = []

    def add(self, severity: str, node: ast.AST, category: str, message: str, snippet: str = "") -> None:
        self.findings.append(
            Finding(
                severity=severity,
                file=self.file_path.as_posix(),
                line=getattr(node, "lineno", 0) or 0,
                category=category,
                message=message,
                snippet=snippet.strip(),
            )
        )

    def visit_Call(self, node: ast.Call) -> None:
        name = self._call_name(node)
        if name in {"eval", "exec"}:
            self.add("CRITICAL", node, "dynamic-execution", f"{name}() call found.")
        elif name == "os.system":
            self.add("HIGH", node, "shell-execution", "os.system() call found.")
        elif name in {"subprocess.run", "subprocess.Popen", "subprocess.call", "subprocess.check_output", "subprocess.check_call"}:
            shell_true = any(kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True for kw in node.keywords)
            if shell_true:
                self.add("CRITICAL", node, "shell-execution", f"{name}(..., shell=True) found.")
            else:
                self.add("HIGH", node, "process-execution", f"{name}() call found.")
        elif name in {"pickle.loads", "marshal.loads"}:
            self.add("HIGH", node, "unsafe-deserialization", f"{name}() call found.")
        elif name.startswith("requests.") or name.startswith("httpx."):
            self.add("MEDIUM", node, "network", f"Outbound HTTP call via {name}().")
        elif name in {"base64.b64decode", "b64decode"}:
            self.add("MEDIUM", node, "obfuscation", "Base64 decode call found.")
        elif name == "compile":
            self.add("HIGH", node, "dynamic-execution", "compile() call found; verify downstream execution path.")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.name.split(".")[0]
            if name in {"subprocess", "ctypes", "socket", "pickle", "marshal", "winreg"}:
                self.add("MEDIUM", node, "import", f"Sensitive module import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = (node.module or "").split(".")[0]
        if module in {"subprocess", "ctypes", "socket", "pickle", "marshal", "winreg"}:
            self.add("MEDIUM", node, "import", f"Sensitive module import from: {node.module}")
        self.generic_visit(node)

    @staticmethod
    def _call_name(node: ast.Call) -> str:
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            parts = []
            while isinstance(func, ast.Attribute):
                parts.append(func.attr)
                func = func.value
            if isinstance(func, ast.Name):
                parts.append(func.id)
            return ".".join(reversed(parts))
        return ""


class BuildCheck:
    def __init__(self, root: Path, output: Path | None = None, verbose: bool = False):
        self.root = root
        self.output = output
        self.verbose = verbose
        self.findings: list[Finding] = []
        self.build_notes: list[str] = []
        self.checked_files = 0
        self.syntax_ok = 0
        self.syntax_failed = 0

    def run(self) -> int:
        if not self.root.exists():
            self.findings.append(Finding("CRITICAL", self.root.as_posix(), 0, "path", "Target root does not exist."))
            return self.finish()

        self.check_structure()
        for path in self.iter_files(self.root):
            self.checked_files += 1
            self.scan_file(path)
        self.check_fastapi_expectations()
        return self.finish()

    def iter_files(self, root: Path) -> Iterable[Path]:
        skip_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}
        script_name = Path(__file__).name
        for path in root.rglob("*"):
            if any(part in skip_dirs for part in path.parts):
                continue
            if path.is_file() and path.name == script_name:
                continue
            if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
                yield path

    def check_structure(self) -> None:
        app_py = self.root / "app.py"
        if app_py.exists():
            self.build_notes.append(f"Found app entry: {app_py}")
        else:
            self.findings.append(Finding("HIGH", self.root.as_posix(), 0, "build", "app.py not found at root; FastAPI startup may fail."))

        req = self.root / "requirements.txt"
        pyproject = self.root / "pyproject.toml"
        if req.exists() or pyproject.exists():
            self.build_notes.append("Dependency manifest found.")
        else:
            self.findings.append(Finding("MEDIUM", self.root.as_posix(), 0, "build", "No requirements.txt or pyproject.toml found."))

    def scan_file(self, path: Path) -> None:
        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                self.findings.append(Finding("MEDIUM", path.as_posix(), 0, "size", f"Skipping very large file over {MAX_FILE_SIZE} bytes."))
                return
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            self.findings.append(Finding("MEDIUM", path.as_posix(), 0, "read", f"Could not read file: {exc}"))
            return

        self.regex_scan(path, text)
        if path.suffix.lower() in CODE_EXTENSIONS:
            self.ast_scan(path, text)

    def regex_scan(self, path: Path, text: str) -> None:
        lines = text.splitlines()
        for idx, line in enumerate(lines, start=1):
            for severity, pattern, message in PATTERN_RULES:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    self.findings.append(Finding(severity, path.as_posix(), idx, "pattern", message, line[:180]))
            for severity, pattern, message in SUSPICIOUS_HOST_RULES:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    self.findings.append(Finding(severity, path.as_posix(), idx, "endpoint", message, line[:180]))
            if self.looks_obfuscated(line):
                self.findings.append(Finding("HIGH", path.as_posix(), idx, "obfuscation", "Long high-entropy or encoded-looking line found.", line[:180]))

    def ast_scan(self, path: Path, text: str) -> None:
        try:
            tree = ast.parse(text, filename=str(path))
            self.syntax_ok += 1
        except SyntaxError as exc:
            self.syntax_failed += 1
            self.findings.append(Finding("HIGH", path.as_posix(), exc.lineno or 0, "syntax", f"Syntax error: {exc.msg}"))
            return
        visitor = ThreatVisitor(path)
        visitor.visit(tree)
        self.findings.extend(visitor.findings)

    def check_fastapi_expectations(self) -> None:
        app_py = self.root / "app.py"
        if not app_py.exists():
            return
        text = app_py.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"from\s+fastapi\s+import\s+FastAPI|import\s+fastapi", text):
            self.build_notes.append("FastAPI import detected in app.py.")
        else:
            self.findings.append(Finding("MEDIUM", app_py.as_posix(), 0, "build", "app.py does not appear to import FastAPI."))

        if re.search(r"\bapp\s*=\s*FastAPI\s*\(", text):
            self.build_notes.append("Detected likely FastAPI app object: app = FastAPI(...)")
        else:
            self.findings.append(Finding("MEDIUM", app_py.as_posix(), 0, "build", "Could not find 'app = FastAPI(...)' pattern in app.py."))

        req = self.root / "requirements.txt"
        if req.exists():
            req_text = req.read_text(encoding="utf-8", errors="ignore").lower()
            if "fastapi" not in req_text:
                self.findings.append(Finding("MEDIUM", req.as_posix(), 0, "dependency", "requirements.txt does not mention fastapi."))
            if "uvicorn" not in req_text:
                self.findings.append(Finding("LOW", req.as_posix(), 0, "dependency", "requirements.txt does not mention uvicorn."))

    @staticmethod
    def looks_obfuscated(line: str) -> bool:
        stripped = line.strip()
        if len(stripped) < 180:
            return False
        if re.fullmatch(r"[A-Za-z0-9+/=]{180,}", stripped):
            return True
        if re.fullmatch(r"[A-Fa-f0-9]{220,}", stripped):
            return True
        return False

    def finish(self) -> int:
        self.findings.sort(key=lambda f: (-SEVERITY_ORDER.get(f.severity, 0), f.file, f.line))
        summary = {
            "root": str(self.root),
            "checked_files": self.checked_files,
            "syntax_ok": self.syntax_ok,
            "syntax_failed": self.syntax_failed,
            "build_notes": self.build_notes,
            "counts": self.counts(),
            "findings": [asdict(f) for f in self.findings],
        }

        self.print_report(summary)
        if self.output:
            self.output.parent.mkdir(parents=True, exist_ok=True)
            self.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            print(f"\nSaved JSON report to: {self.output}")

        if summary["counts"].get("CRITICAL", 0) > 0:
            return 2
        if summary["counts"].get("HIGH", 0) > 0:
            return 1
        return 0

    def counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for finding in self.findings:
            counts[finding.severity] = counts.get(finding.severity, 0) + 1
        return counts

    def print_report(self, summary: dict) -> None:
        print("=" * 72)
        print("OTFZ FastAPI Build Check + Threatening Code Detection")
        print("=" * 72)
        print(f"Root: {summary['root']}")
        print(f"Checked files: {summary['checked_files']}")
        print(f"Syntax OK: {summary['syntax_ok']} | Syntax failed: {summary['syntax_failed']}")
        print("Build notes:")
        if summary["build_notes"]:
            for note in summary["build_notes"]:
                print(f"  - {note}")
        else:
            print("  - None")

        print("Severity counts:")
        if summary["counts"]:
            for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
                if sev in summary["counts"]:
                    print(f"  - {sev}: {summary['counts'][sev]}")
        else:
            print("  - No findings")

        print("\nTop findings:")
        if not self.findings:
            print("  - No suspicious patterns found by heuristics.")
        else:
            for finding in self.findings[:40]:
                line = f"  - [{finding.severity}] {finding.file}:{finding.line} | {finding.category} | {finding.message}"
                print(line)
                if self.verbose and finding.snippet:
                    print(f"      {finding.snippet}")

        print("\nExit codes: 0=no HIGH/CRITICAL findings, 1=HIGH findings, 2=CRITICAL findings")
        print("Note: This is a heuristic static scan, not a guarantee of safety.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OTFZ FastAPI build-check with threatening code detection")
    parser.add_argument("root", nargs="?", default=str(DEFAULT_ROOT), help="Path to scan. Defaults to C:\\Users\\middl\\Documents\\OTFZ")
    parser.add_argument("--json", dest="json_path", default="build_check_report.json", help="Path for JSON report output")
    parser.add_argument("--no-json", action="store_true", help="Disable JSON report output")
    parser.add_argument("--verbose", action="store_true", help="Print matching snippets")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser()
    output = None if args.no_json else Path(args.json_path)
    if output and not output.is_absolute():
        output = root / output
    checker = BuildCheck(root=root, output=output, verbose=args.verbose)
    return checker.run()


if __name__ == "__main__":
    raise SystemExit(main())
