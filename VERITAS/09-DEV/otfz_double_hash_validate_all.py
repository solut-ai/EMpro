#!/usr/bin/env python3
r"""
Compute and validate double-SHA256 hashes for all files under a target root.

Double hash definition used here:
    sha256(sha256(file_bytes).digest()).hexdigest()

Features
- Recursively scans all files under a root directory
- Writes JSON and CSV manifests with file size + double hash
- Optionally validates against an existing JSON/CSV manifest
- Returns non-zero exit code on mismatches or missing files during validation

Examples
    py -3.10 otfz_double_hash_validate_all.py C:\Users\middl\Documents\OTFZ\VERITAS\09-DEV
    py -3.10 otfz_double_hash_validate_all.py C:\Users\middl\Documents\OTFZ --json-out hashes.json --csv-out hashes.csv
    py -3.10 otfz_double_hash_validate_all.py C:\Users\middl\Documents\OTFZ --verify-against hashes.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

DEFAULT_EXCLUDES = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
}

SKIP_SUFFIXES = {".pyc", ".pyo", ".log"}


@dataclass
class FileRecord:
    relative_path: str
    size_bytes: int
    double_sha256: str


@dataclass
class ValidationIssue:
    severity: str
    kind: str
    relative_path: str
    details: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def double_sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(hashlib.sha256(data).digest()).hexdigest()


def double_sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    first = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            first.update(chunk)
    return hashlib.sha256(first.digest()).hexdigest()


def should_skip(path: Path, root: Path, excludes: set[str]) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in excludes for part in rel_parts[:-1]):
        return True
    if path.name in {"build_check_report.json", "double_hash_report.json"}:
        return True
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    return False


def iter_files(root: Path, excludes: set[str]) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and not should_skip(path, root, excludes):
            yield path


def scan_root(root: Path, excludes: set[str]) -> List[FileRecord]:
    records: List[FileRecord] = []
    for file_path in iter_files(root, excludes):
        rel = file_path.relative_to(root).as_posix()
        records.append(
            FileRecord(
                relative_path=rel,
                size_bytes=file_path.stat().st_size,
                double_sha256=double_sha256_file(file_path),
            )
        )
    return records


def write_json_manifest(path: Path, root: Path, records: List[FileRecord]) -> None:
    payload = {
        "schema": "otfz.double_sha256_manifest.v1",
        "generated_at_utc": utc_now_iso(),
        "root": str(root),
        "file_count": len(records),
        "files": [asdict(r) for r in records],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_csv_manifest(path: Path, records: List[FileRecord]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["relative_path", "size_bytes", "double_sha256"])
        for r in records:
            writer.writerow([r.relative_path, r.size_bytes, r.double_sha256])


def load_manifest(path: Path) -> Dict[str, FileRecord]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        files = data.get("files", [])
        return {
            item["relative_path"]: FileRecord(
                relative_path=item["relative_path"],
                size_bytes=int(item["size_bytes"]),
                double_sha256=item["double_sha256"],
            )
            for item in files
        }
    if suffix == ".csv":
        output: Dict[str, FileRecord] = {}
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                output[row["relative_path"]] = FileRecord(
                    relative_path=row["relative_path"],
                    size_bytes=int(row["size_bytes"]),
                    double_sha256=row["double_sha256"],
                )
        return output
    raise ValueError(f"Unsupported manifest format: {path}")


def validate_records(current: List[FileRecord], expected: Dict[str, FileRecord]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    current_map = {r.relative_path: r for r in current}

    for rel_path, expected_record in expected.items():
        current_record = current_map.get(rel_path)
        if current_record is None:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    kind="missing_file",
                    relative_path=rel_path,
                    details="Expected file is missing from current scan.",
                )
            )
            continue
        if current_record.size_bytes != expected_record.size_bytes:
            issues.append(
                ValidationIssue(
                    severity="HIGH",
                    kind="size_mismatch",
                    relative_path=rel_path,
                    details=f"Expected size {expected_record.size_bytes}, got {current_record.size_bytes}.",
                )
            )
        if current_record.double_sha256.lower() != expected_record.double_sha256.lower():
            issues.append(
                ValidationIssue(
                    severity="CRITICAL",
                    kind="hash_mismatch",
                    relative_path=rel_path,
                    details=f"Expected {expected_record.double_sha256}, got {current_record.double_sha256}.",
                )
            )

    for rel_path in sorted(set(current_map) - set(expected)):
        issues.append(
            ValidationIssue(
                severity="MEDIUM",
                kind="unexpected_file",
                relative_path=rel_path,
                details="File exists in current scan but not in expected manifest.",
            )
        )

    return issues


def write_validation_report(path: Path, root: Path, current: List[FileRecord], issues: List[ValidationIssue], verify_against: str | None) -> None:
    payload = {
        "schema": "otfz.double_sha256_validation_report.v1",
        "generated_at_utc": utc_now_iso(),
        "root": str(root),
        "verified_against": verify_against,
        "file_count": len(current),
        "issue_count": len(issues),
        "issues": [asdict(i) for i in issues],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def print_summary(records: List[FileRecord], issues: List[ValidationIssue]) -> None:
    print(f"Scanned files: {len(records)}")
    if not issues:
        print("Validation: PASS")
        return
    counts: Dict[str, int] = {}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    print("Validation: FAIL")
    print("Issue counts:")
    for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if severity in counts:
            print(f"  - {severity}: {counts[severity]}")
    for issue in issues[:20]:
        print(f"[{issue.severity}] {issue.kind}: {issue.relative_path} :: {issue.details}")
    if len(issues) > 20:
        print(f"... {len(issues) - 20} more issues omitted")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Double-SHA256 validation for all files under a root.")
    parser.add_argument("root", nargs="?", default=".", help="Root directory to scan.")
    parser.add_argument("--json-out", default="double_hash_manifest.json", help="JSON manifest output path.")
    parser.add_argument("--csv-out", default="double_hash_manifest.csv", help="CSV manifest output path.")
    parser.add_argument("--report-out", default="double_hash_report.json", help="Validation report JSON output path.")
    parser.add_argument("--verify-against", default="", help="Optional existing JSON/CSV manifest to validate against.")
    parser.add_argument("--exclude", action="append", default=[], help="Additional directory names to exclude. Can be supplied multiple times.")
    return parser.parse_args(argv)


def resolve_output(root: Path, output_value: str) -> Path:
    out = Path(output_value)
    return out if out.is_absolute() else root / out


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"[ERROR] Root directory not found: {root}")
        return 2

    excludes = set(DEFAULT_EXCLUDES)
    excludes.update(args.exclude)

    records = scan_root(root, excludes)

    json_out = resolve_output(root, args.json_out)
    csv_out = resolve_output(root, args.csv_out)
    report_out = resolve_output(root, args.report_out)

    write_json_manifest(json_out, root, records)
    write_csv_manifest(csv_out, records)

    issues: List[ValidationIssue] = []
    verify_against = args.verify_against.strip()
    if verify_against:
        manifest_path = Path(verify_against).resolve()
        if not manifest_path.exists():
            print(f"[ERROR] Validation manifest not found: {manifest_path}")
            return 2
        expected = load_manifest(manifest_path)
        issues = validate_records(records, expected)

    write_validation_report(report_out, root, records, issues, str(Path(verify_against).resolve()) if verify_against else None)

    print_summary(records, issues)
    print(f"JSON manifest: {json_out}")
    print(f"CSV manifest:  {csv_out}")
    print(f"Report JSON:   {report_out}")

    if any(i.severity == "CRITICAL" for i in issues):
        return 2
    if any(i.severity == "HIGH" for i in issues):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
