#!/usr/bin/env python3
"""Assert that a produced skill body is a concise procedure, not a spec restatement."""

from __future__ import annotations

import re
import sys
from pathlib import Path

MAX_BODY_LINES = 500
GENERIC_MARKERS = (
    "what is a skill",
    "skills are reusable capabilities",
    "directory structure",
)
FRONTMATTER_RE = re.compile(r"^---\r?\n.*?\r?\n---\r?\n", re.DOTALL)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: check_body.py <artifacts-dir>")
    artifacts = Path(sys.argv[1])
    candidates = sorted(artifacts.rglob("SKILL.md"))
    if len(candidates) != 1:
        fail(f"expected exactly one SKILL.md under {artifacts}, found {len(candidates)}")

    text = candidates[0].read_text(encoding="utf-8")
    body = FRONTMATTER_RE.sub("", text, count=1)
    lines = body.splitlines()

    if len(lines) >= MAX_BODY_LINES:
        fail(f"body is {len(lines)} lines (must be under {MAX_BODY_LINES})")

    if not re.search(r"(?im)^#{1,3}\s*.*checklist", body):
        fail("body has no checklist section")

    if not re.search(r"(?m)^\s*(?:[-*]|\d+[.)])\s+\S", body):
        fail("body contains no procedural steps")

    lowered = body.lower()
    found = [marker for marker in GENERIC_MARKERS if marker in lowered]
    if found:
        fail(f"body restates generic skill knowledge: {', '.join(found)}")

    print(f"PASS: body is a concise procedure ({len(lines)} lines) with a checklist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
