#!/usr/bin/env python3
"""Generate the deterministic skill catalog from canonical repository metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from check_provenance import (  # noqa: E402
    LIFECYCLE_STATUSES,
    REVIEW_STATUSES,
    parse_provenance,
    validate_record,
)

CATALOG_SCHEMA_VERSION = 1
DEFAULT_REVIEW_INTERVAL_DAYS = 180
REPOSITORY_URL = "https://github.com/tomjanus/water-skills"
README_START = "<!-- catalog:start -->"
README_END = "<!-- catalog:end -->"
DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
CATALOG_REVIEW_STATUSES = REVIEW_STATUSES | {"not_recorded"}


class CatalogError(ValueError):
    """Raised when catalog metadata is inconsistent or unsafe to publish."""


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Read the top-level string fields from a SKILL.md frontmatter block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise CatalogError(f"{path}: missing frontmatter")

    record: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line[0].isspace():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            continue
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        record[key] = value
    else:
        raise CatalogError(f"{path}: unterminated frontmatter")
    return record


def derive_title(path: Path) -> str | None:
    """Return the first level-one heading after the frontmatter, if present."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def load_provenance(skill_dir: Path) -> dict[str, Any] | None:
    path = skill_dir / "provenance.yaml"
    if not path.is_file():
        return None
    record = parse_provenance(path.read_text(encoding="utf-8"))
    errors = validate_record(record)
    if errors:
        raise CatalogError(f"{path}: " + "; ".join(errors))
    return record


def load_eval_summary(skill_dir: Path, root: Path) -> dict[str, Any] | None:
    path = skill_dir / "evals" / "evals.json"
    if not path.is_file():
        return None
    try:
        suite = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(f"{path}: invalid JSON ({exc})") from exc
    cases = suite.get("evals", [])
    trials = suite.get("trials", 1)
    if not isinstance(trials, int) or isinstance(trials, bool) or trials < 1:
        trials = 1
    return {
        "suite": path.relative_to(root).as_posix(),
        "cases": len(cases) if isinstance(cases, list) else 0,
        "trials": trials,
    }


def compute_review_due(last_reviewed: Any, interval_days: Any) -> str | None:
    if not isinstance(last_reviewed, str) or not DATE_PATTERN.fullmatch(last_reviewed):
        return None
    if (
        not isinstance(interval_days, int)
        or isinstance(interval_days, bool)
        or interval_days < 1
    ):
        return None
    try:
        start = dt.date.fromisoformat(last_reviewed)
    except ValueError:
        return None
    return (start + dt.timedelta(days=interval_days)).isoformat()


def build_entry(skill_dir: Path, root: Path = ROOT) -> dict[str, Any]:
    frontmatter = parse_frontmatter(skill_dir / "SKILL.md")
    name = frontmatter.get("name") or skill_dir.name
    if name != skill_dir.name:
        raise CatalogError(
            f"{skill_dir}: frontmatter name {name!r} does not match directory name {skill_dir.name!r}"
        )

    provenance = load_provenance(skill_dir)
    description = frontmatter.get("description", "").strip()
    title = (provenance or {}).get("title") or derive_title(skill_dir / "SKILL.md") or name
    summary = (provenance or {}).get("summary") or description
    interval = (provenance or {}).get(
        "review_interval_days", DEFAULT_REVIEW_INTERVAL_DAYS
    )
    if not isinstance(interval, int) or isinstance(interval, bool) or interval < 1:
        interval = DEFAULT_REVIEW_INTERVAL_DAYS
    last_reviewed = (provenance or {}).get("last_reviewed")

    return {
        "name": name,
        "path": skill_dir.relative_to(root).as_posix(),
        "title": title,
        "description": description,
        "summary": summary,
        "status": (provenance or {}).get("status") or "unknown",
        "review_status": (provenance or {}).get("review_status") or "not_recorded",
        "provenance_status": "recorded" if provenance is not None else "not_recorded",
        "method_status": (provenance or {}).get("method_status"),
        "authors": (provenance or {}).get("authors", []),
        "reviewers": (provenance or {}).get("reviewers", []),
        "references": (provenance or {}).get("references", []),
        "software_tested": (provenance or {}).get("software_tested", []),
        "evidence": (provenance or {}).get("evidence", []),
        "aliases": (provenance or {}).get("aliases", []),
        "supersedes": (provenance or {}).get("supersedes", []),
        "superseded_by": (provenance or {}).get("superseded_by"),
        "last_reviewed": last_reviewed,
        "review_interval_days": interval,
        "review_due": compute_review_due(last_reviewed, interval),
        "eval": load_eval_summary(skill_dir, root),
    }


def validate_catalog(entries: list[dict[str, Any]]) -> None:
    names: dict[str, dict[str, Any]] = {}
    aliases: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    summaries: dict[str, str] = {}

    for entry in entries:
        name = entry["name"]
        if name in names:
            raise CatalogError(f"duplicate skill name {name!r}")
        names[name] = entry

        if entry["status"] not in LIFECYCLE_STATUSES:
            raise CatalogError(f"{name}: unknown status {entry['status']!r}")
        if entry["review_status"] not in CATALOG_REVIEW_STATUSES:
            raise CatalogError(f"{name}: unknown review_status {entry['review_status']!r}")
        if entry["last_reviewed"] is not None and entry["review_due"] is None:
            raise CatalogError(f"{name}: last_reviewed has no computable review_due")

        normalized_description = " ".join(entry["description"].lower().split())
        if normalized_description:
            if normalized_description in descriptions:
                raise CatalogError(
                    f"{name}: duplicate description also used by {descriptions[normalized_description]!r}"
                )
            descriptions[normalized_description] = name

        normalized_summary = " ".join(entry["summary"].lower().split())
        if normalized_summary:
            if normalized_summary in summaries:
                raise CatalogError(
                    f"{name}: duplicate summary also used by {summaries[normalized_summary]!r}"
                )
            summaries[normalized_summary] = name

    for entry in entries:
        for alias in entry["aliases"]:
            if alias in names:
                raise CatalogError(
                    f"{entry['name']}: alias {alias!r} conflicts with a skill name"
                )
            if alias in aliases:
                raise CatalogError(f"{entry['name']}: alias {alias!r} is not unique")
            aliases[alias] = entry["name"]

    for entry in entries:
        name = entry["name"]
        target = entry["superseded_by"]
        if target is not None:
            if target not in names:
                raise CatalogError(f"{name}: superseded_by target {target!r} does not exist")
            if name not in names[target]["supersedes"]:
                raise CatalogError(
                    f"{name}: superseded_by {target!r} but {target!r} does not list {name!r} in supersedes"
                )
        for old in entry["supersedes"]:
            if old not in names:
                raise CatalogError(f"{name}: supersedes target {old!r} does not exist")
            if names[old]["superseded_by"] != name:
                raise CatalogError(
                    f"{name}: supersedes {old!r} but {old!r} does not set superseded_by to {name!r}"
                )


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        raise CatalogError(f"{skills_dir}: skills directory not found")
    entries = [
        build_entry(skill_dir, root)
        for skill_dir in sorted(skills_dir.iterdir())
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file()
    ]
    if not entries:
        raise CatalogError(f"{skills_dir}: no skills found")
    validate_catalog(entries)
    return {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "source": "SKILL.md frontmatter, provenance.yaml, evals/evals.json",
        "skills": entries,
    }


def render_catalog_json(catalog: dict[str, Any]) -> str:
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def render_staleness_json(catalog: dict[str, Any]) -> str:
    skills = []
    for entry in catalog["skills"]:
        skills.append(
            {
                "name": entry["name"],
                "last_reviewed": entry["last_reviewed"],
                "review_interval_days": entry["review_interval_days"],
                "review_due": entry["review_due"],
                "review_state": "unknown"
                if entry["last_reviewed"] is None
                else "scheduled",
            }
        )
    report = {
        "schema_version": CATALOG_SCHEMA_VERSION,
        "default_review_interval_days": DEFAULT_REVIEW_INTERVAL_DAYS,
        "skills": skills,
    }
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def _md_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return " ".join(text.split()).replace("|", "\\|")


def _short(text: str, limit: int = 120) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3].rstrip() + "..."


def _skill_url(name: str) -> str:
    return f"{REPOSITORY_URL}/tree/main/skills/{name}"


def render_docs(catalog: dict[str, Any]) -> str:
    lines = [
        "---",
        "title: Skill catalog",
        "description: Generated catalog of water-skills, review status, provenance gaps, and review dates.",
        "---",
        "",
        "# Skill catalog",
        "",
        "This page is generated by `scripts/generate_catalog.py` from `SKILL.md` frontmatter, "
        "`provenance.yaml`, and `evals/evals.json`. Do not edit it by hand.",
        "",
        "```bash",
        "python scripts/generate_catalog.py",
        "```",
        "",
        "| Skill | Summary | Status | Review | Provenance | Eval cases |",
        "|---|---|---|---|---|---|",
    ]
    for entry in catalog["skills"]:
        eval_cases = entry["eval"]["cases"] if entry["eval"] else "none"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"[`{entry['name']}`]({_skill_url(entry['name'])})",
                    _md_cell(_short(entry["summary"])),
                    _md_cell(entry["status"]),
                    _md_cell(entry["review_status"]),
                    _md_cell(entry["provenance_status"]),
                    _md_cell(eval_cases),
                ]
            )
            + " |"
        )

    aliases = [
        (alias, entry["name"])
        for entry in catalog["skills"]
        for alias in entry["aliases"]
    ]
    lines.extend(["", "## Aliases", ""])
    if aliases:
        lines.extend(["| Alias | Skill |", "|---|---|"])
        lines.extend(f"| `{alias}` | `{name}` |" for alias, name in aliases)
    else:
        lines.append("No aliases are recorded.")

    lines.extend(
        [
            "",
            "## Review schedule",
            "",
            "| Skill | Last reviewed | Interval (days) | Review due |",
            "|---|---|---|---|",
        ]
    )
    for entry in catalog["skills"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{entry['name']}`",
                    _md_cell(entry["last_reviewed"] or "not recorded"),
                    _md_cell(entry["review_interval_days"]),
                    _md_cell(entry["review_due"] or "not scheduled"),
                ]
            )
            + " |"
        )

    gaps = [entry["name"] for entry in catalog["skills"] if entry["provenance_status"] != "recorded"]
    lines.extend(["", "## Provenance gaps", ""])
    if gaps:
        lines.append(
            "The following skills have no `provenance.yaml` record. Their catalog entries show "
            "`not_recorded`; no authors, reviewers, or evidence are inferred."
        )
        lines.append("")
        lines.extend(f"- `{name}`" for name in gaps)
    else:
        lines.append("All skills have a provenance record.")

    lines.extend(
        [
            "",
            "## Review work",
            "",
            "Run `python scripts/check_staleness.py` to list skills whose review is due or whose "
            "`last_reviewed` date is not recorded. Staleness is a warning, not an automatic removal.",
            "",
        ]
    )
    return "\n".join(lines)


def render_readme_block(catalog: dict[str, Any]) -> str:
    lines = [
        README_START,
        "| Skill | Summary | Status | Review |",
        "|---|---|---|---|",
    ]
    for entry in catalog["skills"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"[`{entry['name']}`]({entry['path']}/)",
                    _md_cell(_short(entry["summary"])),
                    _md_cell(entry["status"]),
                    _md_cell(entry["review_status"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "See the [generated catalog](src/content/docs/catalog/index.md) for provenance gaps and review dates.",
            README_END,
        ]
    )
    return "\n".join(lines)


def replace_readme_block(text: str, block: str) -> str:
    if README_START not in text or README_END not in text:
        raise CatalogError(
            f"README.md must contain {README_START} and {README_END} markers"
        )
    start = text.index(README_START)
    end = text.index(README_END, start) + len(README_END)
    return text[:start] + block + text[end:]


def output_paths(root: Path) -> dict[str, Path]:
    return {
        "catalog": root / "catalog" / "catalog.json",
        "staleness": root / "catalog" / "staleness.json",
        "docs": root / "src" / "content" / "docs" / "catalog" / "index.md",
        "readme": root / "README.md",
    }


def generated_outputs(root: Path, catalog: dict[str, Any]) -> dict[str, str]:
    readme_path = output_paths(root)["readme"]
    readme = readme_path.read_text(encoding="utf-8")
    return {
        "catalog": render_catalog_json(catalog),
        "staleness": render_staleness_json(catalog),
        "docs": render_docs(catalog),
        "readme": replace_readme_block(readme, render_readme_block(catalog)),
    }


def write_outputs(root: Path, catalog: dict[str, Any]) -> None:
    outputs = generated_outputs(root, catalog)
    paths = output_paths(root)
    for key, content in outputs.items():
        path = paths[key]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"WROTE {path.relative_to(root).as_posix()}")


def check_outputs(root: Path, catalog: dict[str, Any]) -> list[str]:
    outputs = generated_outputs(root, catalog)
    paths = output_paths(root)
    differences: list[str] = []
    for key, content in outputs.items():
        path = paths[key]
        if not path.is_file():
            differences.append(f"{path.relative_to(root).as_posix()}: missing")
            continue
        if path.read_text(encoding="utf-8") != content:
            differences.append(f"{path.relative_to(root).as_posix()}: out of date")
    return differences


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the generated files are current without writing them",
    )
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        catalog = build_catalog(args.root)
        if args.check:
            differences = check_outputs(args.root, catalog)
            if differences:
                for difference in differences:
                    print(f"ERROR: {difference}", file=sys.stderr)
                print("Run: python scripts/generate_catalog.py", file=sys.stderr)
                return 1
            print("OK   generated catalog is current")
            return 0
        write_outputs(args.root, catalog)
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
