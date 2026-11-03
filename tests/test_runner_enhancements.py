from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from evals import runner
from evals.capture import CLICaptureAdapter


def _case_result(
    case_id: str,
    passed: bool,
    metadata: dict[str, Any] | None = None,
) -> runner.CaseResult:
    result = runner.CaseResult(
        case_id=case_id,
        label=case_id,
        condition="with_skill",
        trial="trial-1",
        metadata=metadata or {},
    )
    result.results.append(
        runner.AssertionResult("regex:pass", "regex", passed, "synthetic assertion")
    )
    return result


class SummaryEnhancementTests(unittest.TestCase):
    def test_summary_adds_variance_cost_time_and_environment(self) -> None:
        results = [
            _case_result(
                "case-a",
                True,
                {
                    "cost": 0.5,
                    "time_seconds": 2.0,
                    "model": "model-a",
                    "agent_harness": "harness-a",
                    "software_versions": {"epanetparser": "1.2"},
                    "os_info": "Linux",
                    "licence_mode": "not_applicable",
                },
            ),
            _case_result(
                "case-a",
                False,
                {
                    "cost": 1.0,
                    "time_seconds": 3.0,
                    "model": "model-a",
                    "agent_harness": "harness-a",
                    "software_versions": {"epanetparser": "1.2"},
                    "os_info": "Linux",
                    "licence_mode": "not_applicable",
                },
            ),
        ]

        summary = runner.summarize(results)
        stats = summary["conditions"]["with_skill"]

        self.assertEqual(stats["trials"], 2)
        self.assertEqual(stats["passed"], 1)
        self.assertAlmostEqual(stats["trial_pass_variance"], 0.25)
        self.assertAlmostEqual(stats["cost"], 1.5)
        self.assertAlmostEqual(stats["time_seconds"], 5.0)
        self.assertEqual(stats["environment"]["os_info"], ["Linux"])
        self.assertEqual(stats["environment"]["software_versions"], [{"epanetparser": "1.2"}])
        self.assertEqual(stats["run_metadata"]["model"], ["model-a"])
        self.assertAlmostEqual(
            summary["cases"][0]["with_skill"]["trial_pass_variance"], 0.25
        )

    def test_summary_preserves_existing_fields_and_handles_absent_metadata(self) -> None:
        summary = runner.summarize([_case_result("case-a", True)])
        stats = summary["conditions"]["with_skill"]

        self.assertEqual(stats["trials"], 1)
        self.assertEqual(stats["passed"], 1)
        self.assertEqual(stats["trial_pass_rate"], 1.0)
        self.assertEqual(stats["checks_passed"], 1)
        self.assertEqual(stats["checks_total"], 1)
        self.assertEqual(stats["cost"], None)
        self.assertEqual(stats["time_seconds"], None)

    def test_markdown_report_includes_added_metrics(self) -> None:
        summary = runner.summarize(
            [
                _case_result("case-a", True, {"cost": 0.25, "time_seconds": 4.0}),
                _case_result("case-a", False, {"cost": 0.25, "time_seconds": 5.0}),
            ]
        )

        report = runner.render_markdown("demo", summary)
        self.assertIn("pooled trial pass variance", report)
        self.assertIn("total cost", report)
        self.assertIn("total time", report)
        self.assertIn("0.25", report)


class RunMetadataEnrichmentTests(unittest.TestCase):
    def test_run_suite_enriches_summary_from_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "skills" / "demo"
            evals_dir = skill_dir / "evals"
            evals_dir.mkdir(parents=True)
            (evals_dir / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "demo",
                        "evals": [
                            {
                                "id": "case-a",
                                "prompt": "do the task",
                                "expected_output": "done",
                                "assertions": ["regex:done"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            trial_dir = root / "runs" / "demo" / "case-a" / "with_skill" / "trial-1"
            trial_dir.mkdir(parents=True)
            (trial_dir / "transcript.md").write_text("done", encoding="utf-8")
            (trial_dir / "metadata.json").write_text(
                json.dumps(
                    {
                        "task_id": "case-a",
                        "condition": "with_skill",
                        "trial": 1,
                        "model": "test-model",
                        "timestamp": "2026-11-03T10:00:00Z",
                        "agent_harness": "test-agent",
                        "eval_harness": "water-skills",
                        "skill_revision": "abc123",
                        "software_versions": {"tool": "2.0"},
                        "os_info": "Linux",
                        "licence_mode": "not_applicable",
                        "cost": 0.12,
                        "time_seconds": 7.5,
                    }
                ),
                encoding="utf-8",
            )
            old_skills_dir, old_runs_dir = runner.SKILLS_DIR, runner.RUNS_DIR
            try:
                runner.SKILLS_DIR = root / "skills"
                runner.RUNS_DIR = root / "runs"
                results = runner.run_suite(
                    "demo",
                    [("with_skill", str(runner.RUNS_DIR / "demo" / "{case}" / "with_skill"))],
                    None,
                )
                summary = runner.summarize(results)
            finally:
                runner.SKILLS_DIR, runner.RUNS_DIR = old_skills_dir, old_runs_dir

        stats = summary["conditions"]["with_skill"]
        self.assertEqual(stats["run_metadata"]["model"], ["test-model"])
        self.assertEqual(stats["run_metadata"]["agent_harness"], ["test-agent"])
        self.assertEqual(stats["run_metadata"]["skill_revision"], ["abc123"])
        self.assertEqual(stats["environment"]["os_info"], ["Linux"])
        self.assertAlmostEqual(stats["cost"], 0.12)
        self.assertAlmostEqual(stats["time_seconds"], 7.5)

    def test_missing_or_invalid_metadata_does_not_fail_grading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "skills" / "demo"
            evals_dir = skill_dir / "evals"
            evals_dir.mkdir(parents=True)
            (evals_dir / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "demo",
                        "evals": [
                            {
                                "id": "case-a",
                                "prompt": "do the task",
                                "expected_output": "done",
                                "assertions": ["regex:done"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            run_root = root / "runs" / "demo" / "case-a" / "with_skill"
            missing_dir = run_root / "trial-1"
            missing_dir.mkdir(parents=True)
            (missing_dir / "transcript.md").write_text("done", encoding="utf-8")
            invalid_dir = run_root / "trial-2"
            invalid_dir.mkdir()
            (invalid_dir / "transcript.md").write_text("done", encoding="utf-8")
            (invalid_dir / "metadata.json").write_text("not json", encoding="utf-8")
            old_skills_dir, old_runs_dir = runner.SKILLS_DIR, runner.RUNS_DIR
            try:
                runner.SKILLS_DIR = root / "skills"
                runner.RUNS_DIR = root / "runs"
                results = runner.run_suite(
                    "demo",
                    [("with_skill", str(runner.RUNS_DIR / "demo" / "{case}" / "with_skill"))],
                    None,
                )
            finally:
                runner.SKILLS_DIR, runner.RUNS_DIR = old_skills_dir, old_runs_dir

        self.assertEqual(len(results), 2)
        self.assertTrue(all(result.passed for result in results))
        summary = runner.summarize(results)
        self.assertEqual(summary["conditions"]["with_skill"]["trials"], 2)


class RegressionDetectionTests(unittest.TestCase):
    def test_regression_in_synthetic_artifact_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = Path(temp_dir)
            (artifacts / "transcript.md").write_text("node count: 4", encoding="utf-8")
            passing_case = {
                "id": "synthetic-regression",
                "expected_output": "node count reported",
                "assertions": ["regex:node count: 4"],
            }
            baseline = runner.grade_case(
                passing_case, artifacts, "with_skill", "trial-1", artifacts, None
            )
            self.assertTrue(baseline.passed)

            failing_case = {**passing_case, "assertions": ["regex:node count: 5"]}
            regressed = runner.grade_case(
                failing_case, artifacts, "with_skill", "trial-1", artifacts, None
            )
            self.assertFalse(regressed.passed)


class PairedCaptureIntegrationTests(unittest.TestCase):
    def test_same_task_multiple_trials_grade_baseline_and_with_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "skills" / "skill-writing"
            evals_dir = skill_dir / "evals"
            evals_dir.mkdir(parents=True)
            (evals_dir / "evals.json").write_text(
                json.dumps(
                    {
                        "skill_name": "skill-writing",
                        "evals": [
                            {
                                "id": "write-epanet-parser",
                                "prompt": "Create a focused EPANET parser skill.",
                                "expected_output": "A focused skill-writing procedure.",
                                "routing": {"expect": ["skill-writing"]},
                                "assertions": ["regex:specific procedure"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            runs_root = root / "runs"
            for condition, output in (
                ("without_skill", "generic draft"),
                ("with_skill", "skill-writing: specific procedure"),
            ):
                for trial in (1, 2):
                    adapter = CLICaptureAdapter(
                        [sys.executable, "-c", "print(__import__('sys').argv[1])", output],
                        "skill-writing",
                        "synthetic-test-only",
                        runs_root=runs_root,
                    )
                    adapter.capture("write-epanet-parser", condition, trial)

            old_skills_dir, old_runs_dir = runner.SKILLS_DIR, runner.RUNS_DIR
            try:
                runner.SKILLS_DIR = root / "skills"
                runner.RUNS_DIR = runs_root
                results = runner.run_suite(
                    "skill-writing",
                    [
                        ("without_skill", str(runs_root / "skill-writing" / "{case}" / "without_skill")),
                        ("with_skill", str(runs_root / "skill-writing" / "{case}" / "with_skill")),
                    ],
                    None,
                )
                summary = runner.summarize(results)
            finally:
                runner.SKILLS_DIR, runner.RUNS_DIR = old_skills_dir, old_runs_dir

        self.assertEqual(summary["conditions"]["without_skill"]["trials"], 2)
        self.assertEqual(summary["conditions"]["without_skill"]["passed"], 0)
        self.assertEqual(summary["conditions"]["with_skill"]["trials"], 2)
        self.assertEqual(summary["conditions"]["with_skill"]["passed"], 2)
        self.assertEqual(len(results), 4)


if __name__ == "__main__":
    unittest.main()
