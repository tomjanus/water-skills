from __future__ import annotations

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))

from schema import validate_metadata, SCHEMA_VERSION, REQUIRED_FIELDS  # noqa: E402


class SchemaVersionTests(unittest.TestCase):
    def test_schema_version_is_string(self) -> None:
        self.assertIsInstance(SCHEMA_VERSION, str)
        self.assertFalse(SCHEMA_VERSION == "")


class RequiredFieldsTests(unittest.TestCase):
    def test_required_fields_are_non_empty(self) -> None:
        for field in REQUIRED_FIELDS:
            self.assertIsInstance(field, str)
            self.assertFalse(field == "")

    def test_valid_metadata_returns_no_errors(self) -> None:
        metadata = {
            "task_id": "write-epanet-parser",
            "condition": "without_skill",
            "trial": 1,
            "model": "claude-3-5-sonnet",
            "timestamp": "2026-11-03T10:00:00Z",
        }
        self.assertEqual(validate_metadata(metadata), [])

    def test_missing_required_field_reports_error(self) -> None:
        metadata = {
            "condition": "without_skill",
            "trial": 1,
            "model": "claude-3-5-sonnet",
            "timestamp": "2026-11-03T10:00:00Z",
        }
        errors = validate_metadata(metadata)
        self.assertIn("missing required field: task_id", errors)

    def test_empty_required_field_reports_error(self) -> None:
        metadata = {
            "task_id": "",
            "condition": "without_skill",
            "trial": 1,
            "model": "claude-3-5-sonnet",
            "timestamp": "2026-11-03T10:00:00Z",
        }
        errors = validate_metadata(metadata)
        self.assertIn("required field 'task_id' must not be empty", errors)

    def test_non_dict_metadata_reports_error(self) -> None:
        self.assertEqual(
            validate_metadata("not a dict"),
            ["metadata must be a JSON object"],
        )
        self.assertEqual(validate_metadata(None), ["metadata must be a JSON object"])
        self.assertEqual(validate_metadata([1, 2]), ["metadata must be a JSON object"])


class ConditionTests(unittest.TestCase):
    def test_valid_conditions_pass(self) -> None:
        for condition in ("without_skill", "with_skill", "compare:eval-writing"):
            metadata = {
                "task_id": "t1",
                "condition": condition,
                "trial": 1,
                "model": "m",
                "timestamp": "2026-11-03T10:00:00Z",
            }
            self.assertEqual(validate_metadata(metadata), [])

    def test_invalid_condition_reports_error(self) -> None:
        metadata = {
            "task_id": "t1",
            "condition": "bogus",
            "trial": 1,
            "model": "m",
            "timestamp": "2026-11-03T10:00:00Z",
        }
        errors = validate_metadata(metadata)
        self.assertTrue(any("invalid condition" in e for e in errors))


class TrialTests(unittest.TestCase):
    def test_trial_must_be_positive_integer(self) -> None:
        base = {
            "task_id": "t1",
            "condition": "without_skill",
            "model": "m",
            "timestamp": "2026-11-03T10:00:00Z",
        }
        errors = validate_metadata({**base, "trial": 0})
        self.assertTrue(any("trial must be a positive integer" in e for e in errors))

        errors = validate_metadata({**base, "trial": -1})
        self.assertTrue(any("trial must be a positive integer" in e for e in errors))

        errors = validate_metadata({**base, "trial": "not-an-int"})
        self.assertTrue(any("trial must be a positive integer" in e for e in errors))

        errors = validate_metadata({**base, "trial": 1})
        self.assertEqual(errors, [])


class OptionalFieldTests(unittest.TestCase):
    def test_unknown_fields_are_ignored(self) -> None:
        metadata = {
            "task_id": "t1",
            "condition": "without_skill",
            "trial": 1,
            "model": "m",
            "timestamp": "2026-11-03T10:00:00Z",
            "custom_extra_field": "ignored",
        }
        self.assertEqual(validate_metadata(metadata), [])

    def test_negative_cost_reports_error(self) -> None:
        metadata = {
            "task_id": "t1",
            "condition": "without_skill",
            "trial": 1,
            "model": "m",
            "timestamp": "2026-11-03T10:00:00Z",
            "cost": -1.0,
        }
        errors = validate_metadata(metadata)
        self.assertTrue(any("cost must be non-negative" in e for e in errors))

    def test_negative_time_seconds_reports_error(self) -> None:
        metadata = {
            "task_id": "t1",
            "condition": "without_skill",
            "trial": 1,
            "model": "m",
            "timestamp": "2026-11-03T10:00:00Z",
            "time_seconds": -5,
        }
        errors = validate_metadata(metadata)
        self.assertTrue(any("time_seconds must be non-negative" in e for e in errors))

    def test_non_dict_software_versions_reports_error(self) -> None:
        metadata = {
            "task_id": "t1",
            "condition": "without_skill",
            "trial": 1,
            "model": "m",
            "timestamp": "2026-11-03T10:00:00Z",
            "software_versions": "not-a-dict",
        }
        errors = validate_metadata(metadata)
        self.assertTrue(any("software_versions must be an object" in e for e in errors))

    def test_all_optional_fields_valid(self) -> None:
        metadata = {
            "task_id": "t1",
            "condition": "without_skill",
            "trial": 3,
            "model": "claude-3-5-sonnet",
            "timestamp": "2026-11-03T10:00:00Z",
            "agent_harness": "Claude Code",
            "agent_harness_version": "1.0.0",
            "eval_harness": "water-skills",
            "eval_harness_version": "1.0",
            "skill_revision": "abc123",
            "software_versions": {"epanet": "2.2"},
            "os_info": "Linux",
            "licence_mode": "commercial",
            "cost": 0.05,
            "time_seconds": 42.5,
        }
        self.assertEqual(validate_metadata(metadata), [])
