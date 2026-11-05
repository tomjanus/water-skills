#!/usr/bin/env python3
"""Check links in the Starlight documentation before publishing.

Markdown files under ``src/content/docs`` are published as directory-style
routes.  A relative link such as ``../02-use-a-skill/`` is therefore resolved
against the page URL, not against the source file.  Links to Markdown sources
are resolved against the source tree.  Links to repository files outside the
docs tree must use absolute GitHub URLs; they must not be relative docs routes.
"""

from __future__ import annotations

import posixpath
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from check_links import Link, extract_links  # noqa: E402

DOCS_ROOT = ROOT / "src" / "content" / "docs"
SITE_BASE = "/water-skills"
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data"}


@dataclass(frozen=True)
class DocsLinkError:
    source: Path
    line: int
    target: str
    problem: str


def docs_files(docs_root: Path = DOCS_ROOT) -> list[Path]:
    return sorted(path for path in docs_root.rglob("*.md") if path.is_file())


def route_for_source(source: Path, docs_root: Path = DOCS_ROOT) -> str | None:
    """Return the published route for a docs Markdown source."""
    try:
        relative = source.resolve().relative_to(docs_root.resolve())
    except ValueError:
        return None
    if relative.suffix != ".md":
        return None
    if relative.name == "index.md":
        parts = relative.parent.parts
    else:
        parts = (*relative.parent.parts, relative.stem)
    route = "/" + "/".join(part for part in parts if part)
    return route.rstrip("/") + "/"


def route_map(docs_root: Path = DOCS_ROOT) -> dict[str, Path]:
    routes: dict[str, Path] = {}
    for source in docs_files(docs_root):
        route = route_for_source(source, docs_root)
        if route is not None:
            routes[route] = source
    return routes


def _strip_site_base(path: str) -> str:
    if path == SITE_BASE or path == SITE_BASE + "/":
        return "/"
    prefix = SITE_BASE + "/"
    if path.startswith(prefix):
        return "/" + path[len(prefix) :]
    return path


def _normalise_route(path: str) -> str:
    decoded = unquote(path)
    normalised = posixpath.normpath(decoded)
    if not normalised.startswith("/"):
        normalised = "/" + normalised
    return normalised.rstrip("/") + "/"


def _resolve_source_markdown(
    source: Path, path: str, docs_root: Path
) -> Path:
    decoded = unquote(path)
    if decoded.startswith("/"):
        return (docs_root / decoded.lstrip("/")).resolve()
    return (source.parent / decoded).resolve()


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory.resolve())
    except ValueError:
        return False
    return True


def check_link(
    source: Path,
    link: Link,
    docs_root: Path = DOCS_ROOT,
    routes: dict[str, Path] | None = None,
) -> DocsLinkError | None:
    parsed = urlsplit(link.target)
    if parsed.scheme.lower() in EXTERNAL_SCHEMES or parsed.netloc:
        return None
    if not parsed.path:
        return None

    path = parsed.path
    if path.endswith(".md"):
        destination = _resolve_source_markdown(source, path, docs_root)
        if not _is_within(destination, docs_root):
            return DocsLinkError(
                source,
                link.line,
                link.target,
                "Markdown link leaves the docs tree; use a GitHub URL",
            )
        if not destination.is_file():
            return DocsLinkError(source, link.line, link.target, "missing docs source")
        route = route_for_source(destination, docs_root)
        if route is None:
            return DocsLinkError(source, link.line, link.target, "missing docs route")
    else:
        source_route = route_for_source(source, docs_root) or "/"
        if path.startswith("/"):
            route = _normalise_route(_strip_site_base(path))
        else:
            route = _normalise_route(posixpath.join(source_route, path))

    available = routes if routes is not None else route_map(docs_root)
    if route not in available:
        return DocsLinkError(source, link.line, link.target, "missing docs route")
    return None


def check_file(
    source: Path,
    docs_root: Path = DOCS_ROOT,
    routes: dict[str, Path] | None = None,
) -> list[DocsLinkError]:
    try:
        text = source.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return [DocsLinkError(source, 1, "<unreadable Markdown file>", "unreadable file")]
    available = routes if routes is not None else route_map(docs_root)
    errors: list[DocsLinkError] = []
    for link in extract_links(text):
        error = check_link(source, link, docs_root, available)
        if error is not None:
            errors.append(error)
    return errors


def check_docs(root: Path = ROOT) -> list[DocsLinkError]:
    docs_root = root / "src" / "content" / "docs"
    sources = docs_files(docs_root)
    available = route_map(docs_root)
    errors: list[DocsLinkError] = []
    for source in sources:
        errors.extend(check_file(source, docs_root, available))
    return errors


def main() -> int:
    docs_root = DOCS_ROOT
    sources = docs_files(docs_root)
    errors = check_docs(ROOT)
    if errors:
        for error in errors:
            try:
                relative = error.source.relative_to(ROOT).as_posix()
            except ValueError:
                relative = error.source.as_posix()
            print(f"{relative}:{error.line}: {error.problem}: {error.target!r}")
        return 1
    link_count = 0
    for source in sources:
        try:
            link_count += len(extract_links(source.read_text(encoding="utf-8")))
        except (OSError, UnicodeError):
            pass
    print(f"OK   checked {len(sources)} docs files ({link_count} links)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
