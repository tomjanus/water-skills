from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from water_skills import (
    derive_plan,
    escape_json,
    parse_issue_md,
    render_evals_json,
    render_plan,
    render_provenance_yaml,
    render_skill_md,
    slugify,
    validate_acceptance,
)

# Import the provenance checker for cross-validation tests.
from check_provenance import parse_provenance, validate_record


class SlugifyTests(unittest.TestCase):
    def test_slugifies_problem_text(self) -> None:
        self.assertEqual(
            slugify("Check EPANET pressure results"),
            "check-epanet-pressure-results",
        )

    def test_handles_empty_text(self) -> None:
        self.assertEqual(slugify(""), "proposal")

    def test_strips_non_allowlist_characters(self) -> None:
        self.assertEqual(slugify("Hello, World! 2026"), "hello-world-2026")

    def test_collapses_runs_of_non_allowlist(self) -> None:
        self.assertEqual(slugify("A   B!!!C"), "a-b-c")


class ParseIssueMdTests(unittest.TestCase):
    def test_parses_all_sections(self) -> None:
        content = """## Domain
hydraulics

## What problem did you encounter?
I need to check pressure results.

## What did you ask the agent?
Check these pressures.

## What should the agent have produced?
A validation report.

## Inputs and data
EPANET .inp file.

## Software and version
EPANET 2.2

## References
EPANET manual.

## Transcript (optional)
session log.
"""
        fields = parse_issue_md(content)
        self.assertEqual(fields["domain"], "hydraulics")
        self.assertEqual(fields["problem"], "I need to check pressure results.")
        self.assertEqual(fields["prompt"], "Check these pressures.")
        self.assertEqual(fields["expected"], "A validation report.")
        self.assertEqual(fields["inputs"], "EPANET .inp file.")
        self.assertEqual(fields["software"], "EPANET 2.2")
        self.assertEqual(fields["references"], "EPANET manual.")
        self.assertEqual(fields["transcript"], "session log.")

    def test_missing_sections_remain_none(self) -> None:
        content = """## Domain
hydraulics

## What problem did you encounter?
A real problem.
"""
        fields = parse_issue_md(content)
        self.assertEqual(fields["domain"], "hydraulics")
        self.assertEqual(fields["problem"], "A real problem.")
        self.assertIsNone(fields["prompt"])
        self.assertIsNone(fields["expected"])

    def test_skips_html_comments_and_checklist_markers(self) -> None:
        content = """## What problem did you encounter?
<!-- comment -->
A real problem.
- [ ] I confirm this is real.
"""
        fields = parse_issue_md(content)
        self.assertEqual(fields["problem"], "A real problem.")


class DerivePlanTests(unittest.TestCase):
    def test_derives_complete_plan(self) -> None:
        fields = {
            "domain": "hydraulics",
            "problem": "Check EPANET pressure results",
            "prompt": "Check these pressures.",
            "expected": "A validation report.",
            "inputs": "EPANET .inp file.",
            "software": "EPANET 2.2",
            "references": "EPANET manual.",
            "transcript": None,
        }
        plan = derive_plan(fields, "123")
        self.assertEqual(plan["issue_id"], "123")
        self.assertEqual(plan["branch"], "skill/123-check-epanet-pressure-results")
        self.assertEqual(
            plan["directory"], "skills/check-epanet-pressure-results/"
        )
        self.assertIn(
            "skills/check-epanet-pressure-results/SKILL.md", plan["files"]
        )
        self.assertIn(
            "skills/check-epanet-pressure-results/provenance.yaml", plan["files"]
        )
        self.assertIn(
            "skills/check-epanet-pressure-results/evals/evals.json", plan["files"]
        )
        self.assertEqual(plan["questions"], [])

    def test_reports_unresolved_questions(self) -> None:
        fields = {
            "domain": None,
            "problem": None,
            "prompt": None,
            "expected": None,
            "inputs": None,
            "software": None,
            "references": None,
            "transcript": None,
        }
        plan = derive_plan(fields, "999")
        self.assertEqual(plan["branch"], "skill/999-issue-999")
        self.assertGreater(len(plan["questions"]), 0)
        self.assertTrue(
            any("No problem described" in q for q in plan["questions"])
        )
        self.assertTrue(
            any("No agent prompt recorded" in q for q in plan["questions"])
        )

    def test_falls_back_to_issue_id_when_no_problem(self) -> None:
        fields = {
            "domain": "hydraulics",
            "problem": "",
            "prompt": "Check pressures.",
            "expected": "A report.",
            "inputs": None,
            "software": None,
            "references": None,
            "transcript": None,
        }
        plan = derive_plan(fields, "42")
        self.assertEqual(plan["directory"], "skills/issue-42/")
        self.assertTrue(any("No problem described" in q for q in plan["questions"]))


class RenderPlanTests(unittest.TestCase):
    def test_render_includes_branch_directory_files_and_questions(self) -> None:
        plan = {
            "issue_id": "7",
            "branch": "skill/7-check-pressures",
            "directory": "skills/check-pressures/",
            "files": [
                "skills/check-pressures/SKILL.md",
                "skills/check-pressures/provenance.yaml",
                "skills/check-pressures/evals/evals.json",
            ],
            "optional_folders": [],
            "questions": ["No software and version provided."],
        }
        output = render_plan(plan)
        self.assertIn("water-skills new --from-issue 7 --dry-run", output)
        self.assertIn("Branch: skill/7-check-pressures", output)
        self.assertIn("Directory: skills/check-pressures/", output)
        self.assertIn("  skills/check-pressures/SKILL.md", output)
        self.assertIn("Unresolved questions:", output)
        self.assertIn("- No software and version provided.", output)


class RenderSkillMdTests(unittest.TestCase):
    def test_renders_skill_md_without_license_field(self) -> None:
        fields = {
            "problem": "Check EPANET pressure results for negative pressures.",
            "prompt": "Check these pressures.",
            "expected": "A validation report.",
            "inputs": "EPANET .inp file.",
            "software": "EPANET 2.2",
            "references": "EPANET manual.",
        }
        output = render_skill_md("check-epanet-pressure", fields)
        self.assertIn("name: check-epanet-pressure", output)
        self.assertIn("Check EPANET pressure results for negative pressures.", output)
        # No per-skill license field (repo-wide MIT per Stage 1).
        self.assertNotIn("license:", output)
        self.assertIn("## Procedure", output)
        self.assertIn("## Checks", output)
        self.assertIn("## References", output)

    def test_renders_minimal_skill_md_when_fields_missing(self) -> None:
        fields = {
            "problem": None,
            "prompt": None,
            "expected": None,
            "inputs": None,
            "software": None,
            "references": None,
        }
        output = render_skill_md("issue-42", fields)
        self.assertIn("name: issue-42", output)
        self.assertIn("description: <what it does and when to use it>", output)
        self.assertIn("1. <Step grounded in the contributor's workflow.>", output)


class RenderProvenanceYamlTests(unittest.TestCase):
    def test_renders_valid_provenance_schema(self) -> None:
        fields = {
            "problem": "Check EPANET pressure results.",
            "domain": "hydraulics",
            "software": "EPANET 2.2",
        }
        output = render_provenance_yaml("check-epanet-pressure", fields)
        self.assertIn('authors: ["<contributor>"]', output)
        self.assertIn("method_status: hypothesis", output)
        self.assertIn("review_status: not_reviewed", output)
        self.assertIn("references: []", output)
        self.assertIn('software_tested: ["EPANET 2.2"]', output)
        self.assertNotIn("license:", output)
        # Only schema-valid top-level fields are present.
        valid_fields = {
            "authors", "method_status", "references", "software_tested",
            "reviewers", "evidence", "review_status",
        }
        for line in output.splitlines():
            stripped = line.strip()
            if not stripped or line.startswith(" "):
                continue
            key = stripped.split(":")[0].strip()
            if key:
                self.assertIn(key, valid_fields)

    def test_provenance_passes_check_provenance_validator(self) -> None:
        """Verify the rendered provenance passes the repo's provenance checker."""
        fields = {
            "problem": "Check EPANET pressure results.",
            "domain": "hydraulics",
        }
        output = render_provenance_yaml("test-skill", fields)
        record = parse_provenance(output)
        errors = validate_record(record)
        self.assertEqual(errors, [])


class RenderEvalsJsonTests(unittest.TestCase):
    def test_renders_valid_evals_json(self) -> None:
        fields = {
            "prompt": "Check these pressures.",
            "expected": "A validation report listing negative pressures.",
        }
        output = render_evals_json("check-epanet-pressure", fields)
        suite = json.loads(output)
        self.assertEqual(suite["skill_name"], "check-epanet-pressure")
        self.assertIsInstance(suite["evals"], list)
        self.assertEqual(len(suite["evals"]), 1)
        case = suite["evals"][0]
        self.assertIn("id", case)
        self.assertIn("prompt", case)
        self.assertIn("expected_output", case)
        self.assertIsInstance(case["assertions"], list)

    def test_evals_json_passes_runner_validation(self) -> None:
        """Verify the rendered evals.json passes the runner's suite validation."""
        fields = {
            "prompt": "Check pressures.",
            "expected": "A report.",
        }
        output = render_evals_json("check-pressures", fields)
        suite = json.loads(output)
        # Simulate runner.validate_suite checks.
        self.assertEqual(suite["skill_name"], "check-pressures")
        cases = suite["evals"]
        self.assertIsInstance(cases, list)
        self.assertGreater(len(cases), 0)
        seen = set()
        for case in cases:
            for name in ("id", "prompt", "expected_output"):
                self.assertIn(name, case)
                self.assertTrue(case[name])
            self.assertNotIn(case["id"], seen)
            seen.add(case["id"])
            for assertion in case.get("assertions", []):
                self.assertIsInstance(assertion, str)


class EscapeJsonTests(unittest.TestCase):
    def test_escapes_quotes_and_backslashes(self) -> None:
        self.assertEqual(escape_json('say "hi"'), 'say \\"hi\\"')
        self.assertEqual(escape_json("a\\b"), "a\\\\b")

    def test_escapes_newlines(self) -> None:
        self.assertEqual(escape_json("line1\nline2"), "line1\\nline2")


class ValidateAcceptanceTests(unittest.TestCase):
    def test_passes_when_all_required_fields_present(self) -> None:
        fields = {
            "problem": "A real problem.",
            "prompt": "The agent prompt.",
            "expected": "The expected output.",
        }
        self.assertEqual(validate_acceptance(fields), [])

    def test_reports_missing_fields(self) -> None:
        fields = {"problem": None, "prompt": None, "expected": None}
        unmet = validate_acceptance(fields)
        self.assertEqual(len(unmet), 3)
        self.assertTrue(any("problem" in c.lower() for c in unmet))
        self.assertTrue(any("prompt" in c.lower() for c in unmet))
        self.assertTrue(any("expected" in c.lower() for c in unmet))


class WriteModeIntegrationTests(unittest.TestCase):
    """End-to-end tests using a temporary git repository."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="water-skills-test-"))
        self.repo_root = self.tmp / "repo"
        self.repo_root.mkdir()
        # Init a minimal git repo.
        subprocess.run(
            ["git", "init"],
            cwd=str(self.repo_root),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.test"],
            cwd=str(self.repo_root),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=str(self.repo_root),
            capture_output=True,
            check=True,
        )
        # Create minimal repo structure expected by the script.
        (self.repo_root / "skills").mkdir()
        (self.repo_root / "scripts").mkdir()
        # Copy the script into the temp repo's scripts dir.
        script_src = Path(__file__).resolve().parents[1] / "scripts" / "water_skills.py"
        script_dst = self.repo_root / "scripts" / "water_skills.py"
        script_dst.write_text(script_src.read_text(encoding="utf-8"), encoding="utf-8")
        # Commit the initial structure so there's a HEAD to branch from.
        subprocess.run(
            ["git", "add", "."],
            cwd=str(self.repo_root),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial"],
            cwd=str(self.repo_root),
            capture_output=True,
            check=True,
        )
        self.initial_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run_water_skills(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "scripts/water_skills.py"] + args,
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
        )

    def _write_issue_file(self, name: str, content: str) -> Path:
        path = self.tmp / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_write_mode_creates_branch_files_and_commit(self) -> None:
        issue_file = self._write_issue_file(
            "issue.md",
            """## Domain
hydraulics

## What problem did you encounter?
Check EPANET pressure results for negative pressures before calibration.

## What did you ask the agent?
Check whether these pressure results are plausible.

## What should the agent have produced?
A validation report listing negative pressures and out-of-range values.

## Software and version
EPANET 2.2

## References
EPANET 2.2 User Manual.
""",
        )
        result = self._run_water_skills(
            [
                "new",
                "--from-issue",
                "123",
                "--issue-file",
                str(issue_file),
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("committed on branch:", result.stdout)

        # Verify branch exists.
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(self.repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertTrue(branch_result.stdout.strip().startswith("skill/123-"))

        # Verify files exist.
        skill_dirs = [
            p for p in (self.repo_root / "skills").iterdir() if p.is_dir()
        ]
        self.assertEqual(len(skill_dirs), 1)
        skill_dir = skill_dirs[0]
        self.assertTrue((skill_dir / "SKILL.md").is_file())
        self.assertTrue((skill_dir / "provenance.yaml").is_file())
        self.assertTrue((skill_dir / "evals" / "evals.json").is_file())

        # Verify no optional folders created by default.
        optional = {"references", "scripts", "assets", "evals", "examples", "models", "adapters"}
        present = {p.name for p in skill_dir.iterdir() if p.is_dir()}
        self.assertEqual(present, {"evals"})

    def test_write_mode_rejects_missing_acceptance_criteria(self) -> None:
        issue_file = self._write_issue_file(
            "issue.md",
            """## Domain
hydraulics

## What problem did you encounter?

## What did you ask the agent?

## What should the agent have produced?

""",
        )
        result = self._run_water_skills(
            [
                "new",
                "--from-issue",
                "999",
                "--issue-file",
                str(issue_file),
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance criteria not met", result.stderr)

    def test_write_mode_rejects_existing_branch(self) -> None:
        # Pre-create the exact branch that write mode would generate.
        # Problem: "An existing skill problem." -> slug: an-existing-skill-problem
        subprocess.run(
            ["git", "checkout", "-b", "skill/42-an-existing-skill-problem"],
            cwd=str(self.repo_root),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "checkout", self.initial_branch],
            cwd=str(self.repo_root),
            capture_output=True,
            check=True,
        )

        issue_file = self._write_issue_file(
            "issue.md",
            """## What problem did you encounter?
An existing skill problem.

## What did you ask the agent?
Check this.

## What should the agent have produced?
That.

## Software and version
EPANET 2.2

## References
Manual.
""",
        )
        result = self._run_water_skills(
            [
                "new",
                "--from-issue",
                "42",
                "--issue-file",
                str(issue_file),
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)


if __name__ == "__main__":
    unittest.main()

