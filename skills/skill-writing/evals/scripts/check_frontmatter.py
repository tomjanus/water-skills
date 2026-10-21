#!/usr/bin/env python3
"""Assert that a produced skill has valid, routing-oriented frontmatter."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROUTING_PHRASES = re.compile(
    r"\b(use when|when the user|when asked|trigger|invoked when|use this skill)\b",
    re.IGNORECASE,
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def find_skill_file(artifacts: Path) -> Path:
    candidates = sorted(artifacts.rglob("SKILL.md"))
    if len(candidates) != 1:
        fail(f"expected exactly one SKILL.md under {artifacts}, found {len(candidates)}")
    return candidates[0]


def parse_frontmatter(text: str) -> str:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        fail("missing or malformed YAML frontmatter delimiters")
    return match.group(1)


def main() -> int:
    if len(sys.argv) != 2:
        fail("usage: check_frontmatter.py <artifacts-dir>")
    artifacts = Path(sys.argv[1])
    skill_file = find_skill_file(artifacts)
    text = skill_file.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)

    name = re.search(r"^name:\s*(\S+)\s*$", frontmatter, re.MULTILINE)
    if not name:
        fail("frontmatter has no 'name' field")
    description = re.search(r"^description:\s*(.+?)\s*$", frontmatter, re.MULTILINE)
    if not description:
        fail("frontmatter has no 'description' field")

    value = description.group(1)
    if len(value) > 1024:
        fail(f"description is {len(value)} characters (max 1024)")
    if not ROUTING_PHRASES.search(value):
        fail("description does not state when to use the skill (no routing phrase)")

    if name.group(1) != skill_file.parent.name:
        fail(f"name '{name.group(1)}' does not match directory '{skill_file.parent.name}'")

    print(f"PASS: frontmatter valid (name={name.group(1)}, description={len(value)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
