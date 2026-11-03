#!/usr/bin/env python3
"""Find selected high-confidence credential patterns without printing values.

This dependency-free check is a guardrail, not a general secret scanner. It
reads non-ignored Git files that are small UTF-8 text, skips generated and
binary content, and reports only path, line, and pattern category.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 5 * 1024 * 1024
SKIP_PARTS = {
    ".git",
    ".venv",
    "venv",
    ".tox",
    "node_modules",
    "__pycache__",
}
SKIP_PREFIXES = {Path("evals/runs"), Path("evals/reports")}

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key-block", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----")),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    (
        "aws-secret-access-key",
        re.compile(
            r"(?i)\baws_secret_access_key\s*[:=]\s*['\"]?"
            r"[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"
        ),
    ),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("stripe-secret-key", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    (
        "url-embedded-credential",
        re.compile(r"(?i)\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]{6,}@"),
    ),
)


@dataclass(frozen=True)
class Finding:
    line: int
    category: str


def scan_text(text: str) -> list[Finding]:
    """Return line/category pairs only; never return matched credential text."""
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for category, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(Finding(line_number, category))
    return findings


def list_repository_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or "git ls-files failed")
    paths = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative = Path(os.fsdecode(raw_path))
        if relative.is_absolute() or ".." in relative.parts:
            continue
        if any(part in SKIP_PARTS for part in relative.parts):
            continue
        if any(relative == prefix or prefix in relative.parents for prefix in SKIP_PREFIXES):
            continue
        paths.append(root / relative)
    return paths


def scan_file(path: Path) -> list[Finding]:
    try:
        if path.is_symlink() or path.stat().st_size > MAX_FILE_BYTES:
            return []
        content = path.read_bytes()
    except OSError:
        return []
    if b"\0" in content:
        return []
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return []
    return scan_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    args = parser.parse_args()
    root = args.root.resolve()

    try:
        files = list_repository_files(root)
    except RuntimeError as exc:
        print(f"ERROR: cannot enumerate Git files under {root}: {exc}")
        return 2

    count = 0
    for path in sorted(files):
        findings = scan_file(path)
        for finding in findings:
            relative = path.relative_to(root).as_posix()
            print(f"{relative}:{finding.line}: {finding.category}")
            count += 1
    if count:
        print(f"Found {count} potential credential pattern(s); matched values were not printed.")
        return 1
    print("OK   no selected high-confidence credential patterns found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
