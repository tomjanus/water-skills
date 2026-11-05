#!/usr/bin/env python3
"""Check local Markdown link targets in contributor-facing repository files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ROOT_MARKDOWN = (
    "README.md",
    "CONTRIBUTING.md",
    "RELEASING.md",
    "CHANGELOG.md",
    "EVALS.md",
    "REPOSITORY_STRUCTURE.md",
    "GLOSSARY.md",
)
MARKDOWN_DIRECTORIES = ("skills", "contributing", ".github", "agents")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)")
INLINE_CODE = re.compile(r"`+[^`]*`+")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
MARKDOWN_ESCAPABLE = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")


@dataclass(frozen=True)
class Link:
    line: int
    target: str


@dataclass(frozen=True)
class LinkError:
    source: Path
    line: int
    target: str
    problem: str = "missing target"


def markdown_files(root: Path = ROOT) -> list[Path]:
    files = {root / name for name in ROOT_MARKDOWN if (root / name).is_file()}
    for directory in MARKDOWN_DIRECTORIES:
        base = root / directory
        if base.is_dir():
            files.update(path for path in base.rglob("*.md") if path.is_file())
    return sorted(files)


def extract_links(text: str) -> list[Link]:
    links: list[Link] = []
    fence_marker: str | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        fence_match = FENCE.match(raw_line)
        if fence_match:
            marker = fence_match.group(1)[0]
            if fence_marker is None:
                fence_marker = marker
            elif marker == fence_marker:
                fence_marker = None
            continue
        if fence_marker is not None:
            continue
        line = INLINE_CODE.sub("", raw_line)
        links.extend(_inline_links(line_number, line))
        definition = REFERENCE_LINK.match(line)
        if definition:
            links.append(Link(line_number, definition.group(1).strip("<>")))
    return links


def _inline_links(line_number: int, line: str) -> list[Link]:
    links: list[Link] = []
    cursor = 0
    while True:
        label_end = line.find("](", cursor)
        if label_end < 0:
            return links
        position = label_end + 2
        while position < len(line) and line[position].isspace():
            position += 1
        if position >= len(line):
            return links

        if line[position] == "<":
            target_end = line.find(">", position + 1)
            if target_end < 0:
                cursor = position + 1
                continue
            target = line[position + 1 : target_end]
            position = target_end + 1
        else:
            target_start = position
            depth = 0
            escaped = False
            while position < len(line):
                character = line[position]
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == "(":
                    depth += 1
                elif character == ")":
                    if depth == 0:
                        break
                    depth -= 1
                elif character.isspace() and depth == 0:
                    break
                position += 1
            target = line[target_start:position]
        if target:
            links.append(Link(line_number, target))

        # Skip an optional title and the enclosing ')' before finding another link.
        depth = 0
        quote: str | None = None
        escaped = False
        while position < len(line):
            character = line[position]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif quote is not None:
                if character == quote:
                    quote = None
            elif character in {'"', "'"}:
                quote = character
            elif character == "(":
                depth += 1
            elif character == ")":
                if depth == 0:
                    position += 1
                    break
                depth -= 1
            position += 1
        cursor = position


def resolve_local_target(source: Path, target: str, root: Path = ROOT) -> Path | None:
    target = _unescape_destination(target)
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path_text = unquote(parsed.path)
    if path_text.startswith("/"):
        destination = (root / path_text.lstrip("/")).resolve()
    else:
        destination = (source.parent / path_text).resolve()
    try:
        destination.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("local link escapes the repository root") from exc
    return destination


def _unescape_destination(target: str) -> str:
    """Remove Markdown backslash escapes for ASCII punctuation in link paths."""
    result: list[str] = []
    index = 0
    while index < len(target):
        if (
            target[index] == "\\"
            and index + 1 < len(target)
            and target[index + 1] in MARKDOWN_ESCAPABLE
        ):
            index += 1
        result.append(target[index])
        index += 1
    return "".join(result)


def check_file(source: Path, root: Path = ROOT) -> list[LinkError]:
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return [LinkError(source, 1, "<unreadable Markdown file>")]
    errors: list[LinkError] = []
    for link in extract_links(text):
        try:
            destination = resolve_local_target(source, link.target, root)
        except ValueError:
            errors.append(LinkError(source, link.line, link.target, "escapes repository root"))
            continue
        if destination is not None and not destination.exists():
            errors.append(LinkError(source, link.line, link.target))
    return errors


def main() -> int:
    files = markdown_files()
    errors: list[LinkError] = []
    link_count = 0
    for source in files:
        try:
            link_count += len(extract_links(source.read_text(encoding="utf-8")))
        except (OSError, UnicodeError):
            pass
        errors.extend(check_file(source))

    if errors:
        for error in errors:
            relative = error.source.relative_to(ROOT).as_posix()
            print(f"{relative}:{error.line}: {error.problem}: {error.target!r}")
        return 1
    print(f"OK   checked {len(files)} Markdown files ({link_count} links)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
