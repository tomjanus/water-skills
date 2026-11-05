from __future__ import annotations

import contextlib
import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_provenance import parse_provenance, validate_record
from check_staleness import evaluate
from generate_catalog import (
    CatalogError,
    build_catalog,
    check_outputs,
    render_catalog_json,
    render_docs,
    render_readme_block,
    render_staleness_json,
    replace_readme_block,
    write_outputs,
)


def write_skill(
    root: Path,
    name: str,
    description: str | None = None,
    provenance: str | None = None,
    eval_cases: int | None = 1,
) -> None:
    skill_dir = root / "skills" / name
    skill_dir.mkdir(parents=True)
    text = description or f"Does {name}."
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {text}\n---\n\n# {name.title()}\n",
        encoding="utf-8",
    )
    if eval_cases is not None:
        evals_dir = skill_dir / "evals"
        evals_dir.mkdir()
        cases = [
            {"id": f"case-{index}", "prompt": "p", "expected_output": "e", "assertions": []}
            for index in range(eval_cases)
        ]
        (evals_dir / "evals.json").write_text(
            json.dumps({"skill_name": name, "evals": cases}),
            encoding="utf-8",
        )
    if provenance is not None:
        (skill_dir / "provenance.yaml").write_text(provenance, encoding="utf-8")


def write_readme(root: Path) -> None:
    (root / "README.md").write_text(
        "# Test\n\n<!-- catalog:start -->\n<!-- catalog:end -->\n",
        encoding="utf-8",
    )


class CatalogBuildTests(unittest.TestCase):
    def test_missing_provenance_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo")
            catalog = build_catalog(root)
            entry = catalog["skills"][0]
            self.assertEqual(entry["name"], "foo")
            self.assertEqual(entry["provenance_status"], "not_recorded")
            self.assertEqual(entry["status"], "unknown")
            self.assertEqual(entry["review_status"], "not_recorded")
            self.assertEqual(entry["authors"], [])
            self.assertEqual(entry["summary"], "Does foo.")
            self.assertEqual(entry["eval"]["cases"], 1)

    def test_recorded_provenance_drives_catalog_fields(self) -> None:
        provenance = """\
authors: ["A"]
method_status: adapted
title: "Foo title"
summary: "Foo summary"
status: finish
review_status: reviewed
reviewers: ["R"]
last_reviewed: 2026-01-01
review_interval_days: 30
aliases: ["foo-old"]
supersedes: []
superseded_by: null
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", provenance=provenance)
            entry = build_catalog(root)["skills"][0]
            self.assertEqual(entry["provenance_status"], "recorded")
            self.assertEqual(entry["title"], "Foo title")
            self.assertEqual(entry["summary"], "Foo summary")
            self.assertEqual(entry["status"], "finish")
            self.assertEqual(entry["review_status"], "reviewed")
            self.assertEqual(entry["method_status"], "adapted")
            self.assertEqual(entry["reviewers"], ["R"])
            self.assertEqual(entry["aliases"], ["foo-old"])
            self.assertEqual(entry["review_due"], "2026-01-31")

    def test_missing_eval_suite_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", eval_cases=None)
            self.assertIsNone(build_catalog(root)["skills"][0]["eval"])

    def test_frontmatter_name_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill_dir = root / "skills" / "foo"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: bar\ndescription: Does foo.\n---\n\n# Foo\n",
                encoding="utf-8",
            )
            with self.assertRaises(CatalogError):
                build_catalog(root)

    def test_duplicate_description_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", description="Same text.")
            write_skill(root, "bar", description="Same text.")
            with self.assertRaises(CatalogError):
                build_catalog(root)

    def test_alias_cannot_conflict_with_a_skill_name(self) -> None:
        provenance = 'authors: ["A"]\nmethod_status: hypothesis\naliases: ["bar"]\n'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", provenance=provenance)
            write_skill(root, "bar")
            with self.assertRaises(CatalogError):
                build_catalog(root)

    def test_alias_must_be_unique(self) -> None:
        first = 'authors: ["A"]\nmethod_status: hypothesis\naliases: ["old"]\n'
        second = 'authors: ["B"]\nmethod_status: hypothesis\naliases: ["old"]\n'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", provenance=first)
            write_skill(root, "bar", provenance=second)
            with self.assertRaises(CatalogError):
                build_catalog(root)

    def test_supersedes_requires_symmetry(self) -> None:
        foo = 'authors: ["A"]\nmethod_status: hypothesis\nsuperseded_by: bar\n'
        bar = 'authors: ["B"]\nmethod_status: hypothesis\nsupersedes: []\n'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", provenance=foo)
            write_skill(root, "bar", provenance=bar)
            with self.assertRaises(CatalogError):
                build_catalog(root)

            (root / "skills" / "bar" / "provenance.yaml").write_text(
                'authors: ["B"]\nmethod_status: hypothesis\nsupersedes: ["foo"]\n',
                encoding="utf-8",
            )
            build_catalog(root)

    def test_superseded_by_target_must_exist(self) -> None:
        provenance = 'authors: ["A"]\nmethod_status: hypothesis\nsuperseded_by: missing\n'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", provenance=provenance)
            with self.assertRaises(CatalogError):
                build_catalog(root)


class CatalogRenderTests(unittest.TestCase):
    def test_output_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo")
            write_skill(root, "bar")
            first = build_catalog(root)
            second = build_catalog(root)
            self.assertEqual(render_catalog_json(first), render_catalog_json(second))
            self.assertEqual(render_docs(first), render_docs(second))

    def test_docs_links_target_the_released_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo")
            docs = render_docs(build_catalog(root))
            self.assertIn(
                "https://github.com/tomjanus/water-skills/tree/main/skills/foo", docs
            )
            self.assertNotIn("/tree/dev/", docs)

    def test_docs_show_alias_mapping(self) -> None:
        provenance = 'authors: ["A"]\nmethod_status: hypothesis\naliases: ["foo-old"]\n'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", provenance=provenance)
            docs = render_docs(build_catalog(root))
            self.assertIn("| `foo-old` | `foo` |", docs)

    def test_docs_state_when_no_aliases_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo")
            self.assertIn("No aliases are recorded.", render_docs(build_catalog(root)))

    def test_readme_block_contains_markers_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo")
            block = render_readme_block(build_catalog(root))
            self.assertIn("<!-- catalog:start -->", block)
            self.assertIn("<!-- catalog:end -->", block)
            self.assertIn("[`foo`](skills/foo/)", block)

    def test_replace_readme_block_requires_markers(self) -> None:
        with self.assertRaises(CatalogError):
            replace_readme_block("# Test\n", "block")

    def test_write_and_check_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo")
            write_readme(root)
            catalog = build_catalog(root)
            with contextlib.redirect_stdout(io.StringIO()):
                write_outputs(root, catalog)
            self.assertEqual(check_outputs(root, catalog), [])

            (root / "catalog" / "catalog.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(
                check_outputs(root, catalog),
                ["catalog/catalog.json: out of date"],
            )

    def test_staleness_report_states(self) -> None:
        provenance = """\
authors: ["A"]
method_status: hypothesis
last_reviewed: 2026-01-01
review_interval_days: 30
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "foo", provenance=provenance)
            write_skill(root, "bar")
            report = json.loads(render_staleness_json(build_catalog(root)))
            states = {entry["name"]: entry["review_state"] for entry in report["skills"]}
            self.assertEqual(states, {"foo": "scheduled", "bar": "unknown"})
            due = {entry["name"]: entry["review_due"] for entry in report["skills"]}
            self.assertEqual(due, {"foo": "2026-01-31", "bar": None})


class StalenessEvaluationTests(unittest.TestCase):
    def test_due_and_unknown_items_are_separated(self) -> None:
        report = {
            "skills": [
                {"name": "past", "review_due": "2026-01-01"},
                {"name": "future", "review_due": "2026-12-31"},
                {"name": "missing", "review_due": None},
            ]
        }
        due, unknown = evaluate(report, today=dt.date(2026, 6, 1))
        self.assertEqual(due, [("past", "2026-01-01")])
        self.assertEqual(unknown, ["missing"])


class ProvenanceCatalogFieldTests(unittest.TestCase):
    def test_catalog_fields_pass_the_validator(self) -> None:
        record = parse_provenance(
            """\
authors: ["A"]
method_status: established
title: "Title"
summary: "Summary"
status: publish
review_status: reviewed
reviewers: ["R"]
aliases: ["old-name"]
supersedes: ["older-name"]
superseded_by: null
last_reviewed: 2026-01-01
review_interval_days: 180
"""
        )
        self.assertEqual(validate_record(record), [])

    def test_invalid_catalog_fields_are_rejected(self) -> None:
        record = parse_provenance(
            """\
authors: ["A"]
method_status: established
status: published
last_reviewed: 2026-1-1
review_interval_days: 0
superseded_by: ""
"""
        )
        errors = validate_record(record)
        self.assertTrue(any("status" in error for error in errors))
        self.assertTrue(any("last_reviewed" in error for error in errors))
        self.assertTrue(any("review_interval_days" in error for error in errors))
        self.assertTrue(any("superseded_by" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
