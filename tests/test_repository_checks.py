from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from check_links import extract_links, resolve_local_target
from check_provenance import ProvenanceError, parse_provenance, validate_record
from check_secrets import scan_text
from check_skill_layout import inspect_skill_directory
from evals.runner import json_path_value


class SecretScannerTests(unittest.TestCase):
    def test_detects_selected_patterns_without_returning_values(self) -> None:
        lines = [
            "-----BEGIN " + "PRIVATE KEY-----",
            "AKIA" + "A" * 16,
            "aws_secret_access_key=" + "A" * 40,
            "aws_secret_access_key=" + "A" * 39 + "/",
            "aws_secret_access_key=" + "A" * 39 + "+",
            "aws_secret_access_key=" + "A" * 39 + "=",
            "ghp_" + "A" * 30,
            "github_pat_" + "A" * 30,
            "xoxb-" + "A" * 20,
            "sk_live_" + "A" * 20,
            "AIza" + "A" * 35,
            "https://user:" + "synthetic-secret" + "@example.test",
        ]
        findings = scan_text("\n".join(lines))
        self.assertEqual(
            [finding.category for finding in findings],
            [
                "private-key-block",
                "aws-access-key-id",
                "aws-secret-access-key",
                "aws-secret-access-key",
                "aws-secret-access-key",
                "aws-secret-access-key",
                "github-token",
                "github-token",
                "slack-token",
                "stripe-secret-key",
                "google-api-key",
                "url-embedded-credential",
            ],
        )
        self.assertEqual([finding.line for finding in findings], list(range(1, 13)))
        self.assertTrue(all(not hasattr(finding, "value") for finding in findings))

    def test_ignores_generic_words_and_short_values(self) -> None:
        self.assertEqual(scan_text("password=not-a-real-token\napi_key=example"), [])


class ProvenanceTests(unittest.TestCase):
    def test_parses_supported_yaml_subset(self) -> None:
        record = parse_provenance(
            "authors:\n"
            "  - Example Author\n"
            "method_status: adapted\n"
            "references:\n"
            "  - https://example.test/source#method\n"
            "software_tested: []\n"
            "reviewers: []\n"
            "evidence: []\n"
            "review_status: not_reviewed\n"
        )
        self.assertEqual(validate_record(record), [])

    def test_requires_author_and_known_method_status(self) -> None:
        record = {"authors": [], "method_status": "unsupported-label"}
        errors = validate_record(record)
        self.assertTrue(any("authors" in error for error in errors))
        self.assertTrue(any("method_status" in error for error in errors))

    def test_reviewed_record_requires_reviewer(self) -> None:
        record = {"authors": ["Example Author"], "method_status": "hypothesis", "review_status": "reviewed"}
        self.assertIn("'reviewers' is required when review_status is 'reviewed'", validate_record(record))

    def test_rejects_explicit_null_review_status(self) -> None:
        record = parse_provenance(
            "authors:\n  - Example Author\nmethod_status: established\nreview_status: null\n"
        )
        self.assertTrue(any("review_status" in error for error in validate_record(record)))

    def test_rejects_duplicate_and_unknown_fields(self) -> None:
        with self.assertRaises(ProvenanceError):
            parse_provenance("authors: []\nauthors: []\n")
        with self.assertRaises(ProvenanceError):
            parse_provenance("authors: []\nlicense: MIT\n")


class SkillLayoutTests(unittest.TestCase):
    def test_accepts_known_optional_folders_and_warns_when_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = Path(temporary) / "example-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nname: example-skill\n---\n", encoding="utf-8")
            (skill_dir / "references").mkdir()
            errors, warnings = inspect_skill_directory(skill_dir)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)

    def test_rejects_unknown_top_level_folders(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = Path(temporary) / "example-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("content", encoding="utf-8")
            (skill_dir / "models-ml").mkdir()
            errors, _ = inspect_skill_directory(skill_dir)
        self.assertTrue(any("unrecognized" in error for error in errors))


class MarkdownLinkTests(unittest.TestCase):
    def test_extracts_inline_and_reference_links_but_skips_code(self) -> None:
        text = (
            "[local](../guide.md#intro) and [web](https://example.test)\n"
            "[ref]: images/plot.png\n"
            "```md\n[ignored](missing.md)\n```\n"
        )
        links = extract_links(text)
        self.assertEqual(
            [link.target for link in links],
            ["../guide.md#intro", "https://example.test", "images/plot.png"],
        )
        self.assertEqual([link.line for link in links], [1, 1, 2])

    def test_extracts_destinations_with_balanced_parentheses(self) -> None:
        links = extract_links('[plot](plots/curve_(1).png "plot title")')
        self.assertEqual([link.target for link in links], ["plots/curve_(1).png"])

    def test_unescapes_parentheses_in_local_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "docs" / "page.md"
            asset = root / "docs" / "plots" / "curve_(1).png"
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b"image")
            link = extract_links(r"[plot](plots/curve_\(1\).png)")[0]
            self.assertEqual(resolve_local_target(source, link.target, root), asset.resolve())

    def test_resolves_relative_and_root_relative_local_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "docs" / "page.md"
            self.assertEqual(
                resolve_local_target(source, "../guide.md", root),
                (root / "guide.md").resolve(),
            )
            self.assertEqual(resolve_local_target(source, "/LICENSE", root), root / "LICENSE")
            self.assertIsNone(resolve_local_target(source, "https://example.test", root))
            with self.assertRaises(ValueError):
                resolve_local_target(source, "../../outside.md", root)


class JsonAssertionPathTests(unittest.TestCase):
    def test_resolves_dictionary_keys_and_array_indexes(self) -> None:
        data = {"nodes": [{"id": "junction-1"}]}
        self.assertEqual(json_path_value(data, "nodes.0.id"), (True, "junction-1"))

    def test_rejects_missing_or_invalid_array_indexes(self) -> None:
        data = {"nodes": [{"id": "junction-1"}]}
        self.assertEqual(json_path_value(data, "nodes.1.id"), (False, None))
        self.assertEqual(json_path_value(data, "nodes.-1.id"), (False, None))
        self.assertEqual(json_path_value(data, f"nodes.{'9' * 5000}.id"), (False, None))


if __name__ == "__main__":
    unittest.main()
