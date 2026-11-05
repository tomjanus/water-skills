#!/usr/bin/env python3
"""water-skills authoring runway CLI.

Stage 2c: water-skills new --from-issue <identifier> [--dry-run]

--dry-run prints the planned files and unresolved questions without
changing the tree. Without --dry-run, the command creates a feature
branch, writes the skill directory (SKILL.md, provenance.yaml,
evals/evals.json), stages and commits the files, and prints
instructions for opening a draft pull request on GitHub.

Issue content is treated as untrusted data: it is read from a file,
never interpolated into shell commands, and never executed.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
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

METHOD_STATUSES = {"established", "adapted", "heuristic", "hypothesis"}
REVIEW_STATUSES = {"not_reviewed", "under_review", "reviewed"}


def slugify(text: str) -> str:
    """Derive a slug from text against a strict allowlist (lowercase, digits, hyphens)."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "proposal"


def parse_issue_md(content: str) -> dict[str, str | None]:
    """Parse free-text issue content (propose-skill.md variant) into fields.

    Section headers are matched case-insensitively. HTML comments and
    checklist markers are skipped. Fields not present remain None.
    """
    fields: dict[str, str | None] = {
        "domain": None,
        "problem": None,
        "prompt": None,
        "expected": None,
        "inputs": None,
        "software": None,
        "references": None,
        "transcript": None,
    }
    current: str | None = None
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("<!--") or stripped.startswith("-->"):
            continue
        if stripped.startswith("## "):
            header = stripped[2:].strip().lower()
            if "domain" in header:
                current = "domain"
            elif "problem" in header:
                current = "problem"
            elif "produced" in header:
                current = "expected"
            elif "agent" in header:
                current = "prompt"
            elif "inputs" in header:
                current = "inputs"
            elif "software" in header:
                current = "software"
            elif "references" in header:
                current = "references"
            elif "transcript" in header:
                current = "transcript"
            else:
                current = None
        elif current and stripped and not stripped.startswith("- ["):
            if fields[current] is None:
                fields[current] = stripped
            else:
                fields[current] = f"{fields[current]} {stripped}"
    return fields


def derive_plan(fields: dict[str, str | None], issue_id: str) -> dict:
    """Derive planned files and unresolved questions from parsed issue fields."""
    problem = fields.get("problem") or ""
    skill_name = slugify(problem[:60]) if problem else f"issue-{issue_id}"

    planned: dict = {
        "issue_id": issue_id,
        "branch": f"skill/{issue_id}-{skill_name}",
        "directory": f"skills/{skill_name}/",
        "files": [
            f"skills/{skill_name}/SKILL.md",
            f"skills/{skill_name}/provenance.yaml",
            f"skills/{skill_name}/evals/evals.json",
        ],
        "optional_folders": [],
        "questions": [],
    }

    if not fields.get("problem"):
        planned["questions"].append("No problem described — cannot derive skill purpose.")
    if not fields.get("prompt"):
        planned["questions"].append("No agent prompt recorded — cannot derive eval case.")
    if not fields.get("expected"):
        planned["questions"].append("No expected result described — cannot define checkable condition.")
    if not fields.get("software"):
        planned["questions"].append("No software and version provided.")
    if not fields.get("references"):
        planned["questions"].append("No references supplied — method status unverifiable.")

    return planned


def render_plan(plan: dict) -> str:
    """Render the dry-run plan as plain text."""
    lines: list[str] = []
    lines.append(f"water-skills new --from-issue {plan['issue_id']} --dry-run")
    lines.append(f"Branch: {plan['branch']}")
    lines.append(f"Directory: {plan['directory']}")
    lines.append("Planned files:")
    for path in plan["files"]:
        lines.append(f"  {path}")
    if plan["optional_folders"]:
        lines.append("Optional folders:")
        for path in plan["optional_folders"]:
            lines.append(f"  {path}")
    if plan["questions"]:
        lines.append("Unresolved questions:")
        for question in plan["questions"]:
            lines.append(f"  - {question}")
    else:
        lines.append("Unresolved questions: none")
    return "\n".join(lines)


def read_issue_content(identifier: str, issue_file: Path | None) -> str | None:
    """Read issue content from a local file.

    GitHub API integration is not available in Stage 2c (no token, no
    network calls to untrusted content sources). The identifier is treated
    as a file path if it exists on disk; otherwise it is assumed to be an
    issue number and an error is returned.
    """
    if issue_file is not None:
        if not issue_file.is_file():
            print(f"ERROR: issue file not found: {issue_file}", file=sys.stderr)
            return None
        return issue_file.read_text(encoding="utf-8")

    path = Path(identifier)
    if path.is_file():
        return path.read_text(encoding="utf-8")

    print(
        "ERROR: GitHub API integration is not available in Stage 2c.",
        file=sys.stderr,
    )
    print(
        f"       Provide issue content with --issue-file <path> or pass a file path "
        f"(got: {identifier}).",
        file=sys.stderr,
    )
    return None


def render_skill_md(skill_name: str, fields: dict[str, str | None]) -> str:
    """Render the scaffold SKILL.md body from parsed issue fields."""
    title = (fields.get("problem") or f"Skill from issue").strip()
    description = (fields.get("problem") or "").strip()
    procedure_steps = []
    if fields.get("prompt"):
        procedure_steps.append(f"1. {fields['prompt']}")
    if fields.get("expected"):
        procedure_steps.append(f"2. Compare the agent output against: {fields['expected']}")
    if fields.get("inputs"):
        procedure_steps.append(f"3. Confirm inputs match: {fields['inputs']}")
    if fields.get("software"):
        procedure_steps.append(f"4. Record the software used: {fields['software']}")
    if not procedure_steps:
        procedure_steps.append("1. <Step grounded in the contributor's workflow.>")

    checks = []
    if fields.get("software"):
        checks.append(f"- Confirm the software version matches: {fields['software']}")
    checks.append("- Confirm units, assumptions, and physical plausibility.")
    checks.append("- Report what to do when a check fails.")

    references = []
    if fields.get("references"):
        references.append(f"- {fields['references']}")
    if not references:
        references.append("- <Only references supplied or verified by the contributor.>")

    lines: list[str] = []
    lines.append("---")
    lines.append(f"name: {skill_name}")
    lines.append(f"description: {description or '<what it does and when to use it>'}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title}")
    lines.append("")
    lines.append("<One paragraph: the task this skill enables.>")
    lines.append("")
    lines.append("## When to use this skill")
    lines.append("")
    lines.append("<The specific triggers and the boundary.>")
    lines.append("")
    lines.append("## Procedure")
    lines.append("")
    for step in procedure_steps:
        lines.append(step)
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for check in checks:
        lines.append(check)
    lines.append("")
    lines.append("## References")
    lines.append("")
    for ref in references:
        lines.append(ref)
    return "\n".join(lines) + "\n"


def render_provenance_yaml(skill_name: str, fields: dict[str, str | None]) -> str:
    """Render provenance.yaml using only fields valid per provenance.schema.json.

    Uses method_status: hypothesis (new skill, unverified) and
    review_status: not_reviewed so an incomplete record is visible
    rather than silently defaulted. Catalog fields are explicit nulls or
    empty lists so a missing value is visible rather than inferred.
    """
    author = fields.get("author") or "<contributor>"
    software = fields.get("software") or ""
    title = (fields.get("problem") or "<Title>").strip()
    summary = (fields.get("problem") or "<One sentence for the catalog>").strip()

    lines: list[str] = []
    lines.append(f'authors: ["{author}"]')
    lines.append("method_status: hypothesis   # new skill, unverified until domain review")
    lines.append(f'title: "{escape_json(title)}"')
    lines.append(f'summary: "{escape_json(summary)}"')
    lines.append("status: unknown")
    lines.append("references: []")
    if software:
        lines.append(f'software_tested: ["{software}"]')
    else:
        lines.append("software_tested: []")
    lines.append("reviewers: []")
    lines.append("evidence: []")
    lines.append("review_status: not_reviewed")
    lines.append("aliases: []")
    lines.append("supersedes: []")
    lines.append("superseded_by: null")
    lines.append("last_reviewed: null")
    lines.append("review_interval_days: 180")
    return "\n".join(lines) + "\n"


def render_evals_json(skill_name: str, fields: dict[str, str | None]) -> str:
    """Render evals/evals.json scaffold stub.

    Uses the runner's required schema: skill_name, evals array, each case
    with id, prompt, expected_output. Assertions are strings; an empty
    assertions list means the case is a placeholder awaiting a
    discriminating deterministic check.
    """
    prompt = fields.get("prompt") or "<contributor prompt>"
    expected = fields.get("expected") or "<what a correct result must contain>"
    case_slug = slugify(prompt[:40]) if prompt else "placeholder-case"

    lines: list[str] = []
    lines.append("{")
    lines.append(f'  "skill_name": "{skill_name}",')
    lines.append('  "evals": [')
    lines.append("    {")
    lines.append(f'      "id": "0001-{case_slug}",')
    lines.append(f'      "prompt": "{escape_json(prompt)}",')
    lines.append(f'      "expected_output": "{escape_json(expected)}",')
    lines.append('      "assertions": []')
    lines.append("    }")
    lines.append("  ]")
    lines.append("}")
    return "\n".join(lines) + "\n"


def escape_json(text: str) -> str:
    """Escape a string for safe embedding in a JSON string literal."""
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def run_git(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess:
    """Run a git command safely (no shell interpolation of issue content)."""
    return subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def write_skill(skill_name: str, fields: dict[str, str | None]) -> list[str]:
    """Write the skill directory files. Returns list of written file paths."""
    skill_dir = SKILLS_DIR / skill_name
    evals_dir = skill_dir / "evals"
    skill_dir.mkdir(parents=True, exist_ok=True)
    evals_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for path, content in [
        (skill_dir / "SKILL.md", render_skill_md(skill_name, fields)),
        (skill_dir / "provenance.yaml", render_provenance_yaml(skill_name, fields)),
        (evals_dir / "evals.json", render_evals_json(skill_name, fields)),
    ]:
        path.write_text(content, encoding="utf-8")
        written.append(str(path.relative_to(ROOT)))

    return written


def git_branch_exists(branch: str) -> bool:
    """Return True if the branch already exists."""
    result = run_git(["rev-parse", "--verify", branch])
    return result.returncode == 0


def create_branch(branch: str) -> tuple[bool, str]:
    """Create a new branch. Returns (success, message)."""
    if git_branch_exists(branch):
        return False, f"branch {branch!r} already exists"
    result = run_git(["checkout", "-b", branch])
    if result.returncode != 0:
        return False, result.stderr.strip() or f"failed to create branch {branch!r}"
    return True, f"created branch {branch!r}"


def stage_and_commit(files: list[str], branch: str, issue_id: str) -> tuple[bool, str]:
    """Stage files and commit them on the current branch."""
    add_result = run_git(["add"] + files)
    if add_result.returncode != 0:
        return False, add_result.stderr.strip() or "git add failed"

    commit_msg = f"scaffold(skill): add {skill_name_from_files(files)} from issue #{issue_id}"
    commit_result = run_git(["commit", "-m", commit_msg])
    if commit_result.returncode != 0:
        return False, commit_result.stderr.strip() or "git commit failed"
    return True, "committed"


def skill_name_from_files(files: list[str]) -> str:
    """Extract skill name from a list of repository-relative file paths."""
    for path in files:
        parts = Path(path).parts
        if len(parts) >= 2 and parts[0] == "skills":
            return parts[1]
    return "skill"


def draft_pr_instructions(branch: str, issue_id: str, skill_name: str) -> str:
    """Return plain-language instructions for opening the draft PR."""
    lines: list[str] = []
    lines.append("")
    lines.append("=== Draft pull request ===")
    lines.append("")
    lines.append("The skill directory has been committed on branch:")
    lines.append(f"  {branch}")
    lines.append("")
    lines.append("To open a draft pull request:")
    lines.append(f"  1. Go to https://github.com/<owner>/water-skills/compare/dev...{branch}")
    lines.append(f"  2. Create a pull request targeting the `dev` branch.")
    lines.append("  3. Mark it as a draft (do not mark ready for review).")
    lines.append(f"  4. In the PR body, reference issue #{issue_id}.")
    lines.append("")
    lines.append("The contributor reviews the draft in the GitHub web editor and")
    lines.append("answers the unresolved questions listed above. A domain reviewer")
    lines.append("then reviews units, assumptions, method, citations, and eval.")
    lines.append("")
    return "\n".join(lines)


def validate_acceptance(fields: dict[str, str | None]) -> list[str]:
    """Check the acceptance criteria the script can verify from issue content.

    Returns a list of unmet criteria (empty if all pass). Criteria that
    require human judgement (named reviewer, duplicate search) are not
    checked here and must be verified by the maintainer before running
    write mode.
    """
    unmet: list[str] = []
    if not fields.get("problem"):
        unmet.append("The problem is real and specific (missing from issue).")
    if not fields.get("prompt"):
        unmet.append("The agent prompt is recorded (missing from issue).")
    if not fields.get("expected"):
        unmet.append("The expected result is checkable (missing from issue).")
    return unmet


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="water-skills",
        description="water-skills authoring runway CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    new_cmd = sub.add_parser("new", help="Create a skill from an issue")
    new_cmd.add_argument(
        "--from-issue",
        required=True,
        help="Issue number or path to a local issue content file",
    )
    new_cmd.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned files and questions without changing the tree",
    )
    new_cmd.add_argument(
        "--issue-file",
        type=Path,
        help="Path to a local file containing the issue content",
    )

    args = parser.parse_args()

    if args.command == "new":
        content = read_issue_content(args.from_issue, args.issue_file)
        if content is None:
            return 1

        fields = parse_issue_md(content)
        plan = derive_plan(fields, args.from_issue)

        if args.dry_run:
            print(render_plan(plan))
            return 0

        # Write-enabled mode: validate acceptance criteria the script can check.
        unmet = validate_acceptance(fields)
        if unmet:
            print("ERROR: acceptance criteria not met:", file=sys.stderr)
            for criterion in unmet:
                print(f"  - {criterion}", file=sys.stderr)
            print(
                "       Complete the issue form and re-run. Use --dry-run to see "
                "all unresolved questions.",
                file=sys.stderr,
            )
            return 1

        skill_name = plan["directory"].strip("/").removeprefix("skills/")
        branch = plan["branch"]

        # Create the feature branch.
        ok, message = create_branch(branch)
        if not ok:
            print(f"ERROR: {message}", file=sys.stderr)
            return 1

        # Write the skill directory files.
        written = write_skill(skill_name, fields)

        # Stage and commit.
        ok, message = stage_and_commit(written, branch, args.from_issue)
        if not ok:
            print(f"ERROR: {message}", file=sys.stderr)
            return 1

        print(f"OK   created skill directory: skills/{skill_name}/")
        print(f"OK   committed on branch: {branch}")
        print(draft_pr_instructions(branch, args.from_issue, skill_name))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
