#!/usr/bin/env python3
"""Check skill files and recognized optional top-level folder names."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
OPTIONAL_DIRECTORIES = {
    "references",
    "scripts",
    "assets",
    "evals",
    "examples",
    "models",
    "adapters",
}


def inspect_skill_directory(skill_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        errors.append(f"{skill_dir.name}: missing required SKILL.md")

    try:
        children = sorted(skill_dir.iterdir())
    except OSError as exc:
        return [f"{skill_dir.name}: cannot inspect directory ({exc})"], warnings

    for child in children:
        if not child.is_dir():
            continue
        if child.name not in OPTIONAL_DIRECTORIES:
            errors.append(
                f"{skill_dir.name}: unrecognized top-level directory {child.name!r}; "
                f"use a documented optional directory or request review"
            )
        elif not any(child.iterdir()):
            warnings.append(
                f"{skill_dir.name}/{child.name}: optional directory is empty; "
                "populate it only if the skill uses it"
            )
    return errors, warnings


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print("ERROR: missing skills/ directory")
        return 1
    skill_dirs = sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())
    if not skill_dirs:
        print("ERROR: no skill directories found under skills/")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    for skill_dir in skill_dirs:
        directory_errors, directory_warnings = inspect_skill_directory(skill_dir)
        errors.extend(directory_errors)
        warnings.extend(directory_warnings)

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"OK   checked {len(skill_dirs)} skill directories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
