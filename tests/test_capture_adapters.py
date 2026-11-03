from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from evals.capture import CLICaptureAdapter, CaptureAdapter, ManualCaptureAdapter
from evals.schema import validate_metadata


class CaptureAdapterBaseTests(unittest.TestCase):
    def test_base_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            CaptureAdapter("skill", "model")  # type: ignore[abstract]

    def test_layout_documents_standard_artifact_paths(self) -> None:
        adapter = ManualCaptureAdapter("skill", "model", runs_root="unused")
        self.assertEqual(adapter.artifact_layout()["outputs"], "outputs/")
        self.assertEqual(adapter.artifact_layout()["state"], "state/")
        self.assertEqual(adapter.artifact_layout()["metadata"], "metadata.json")

    def test_rejects_path_traversal_in_task_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adapter = ManualCaptureAdapter(
                "skill", "model", runs_root=temp_dir, input_fn=lambda _: ""
            )
            with self.assertRaisesRegex(ValueError, "safe single path component"):
                adapter.capture("../escape", "with_skill", 1)


class CLICaptureAdapterTests(unittest.TestCase):
    def test_capture_writes_outputs_transcript_and_valid_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adapter = CLICaptureAdapter(
                [sys.executable, "-c", "print('node count: 4'); print('warning', file=__import__('sys').stderr)"],
                "skill-writing",
                "test-model",
                runs_root=temp_dir,
            )
            metadata = adapter.capture("inspect-network", "with_skill", 2)
            trial_dir = Path(temp_dir) / "skill-writing" / "inspect-network" / "with_skill" / "trial-2"

            self.assertEqual(validate_metadata(metadata), [])
            self.assertEqual(metadata["schema_version"], "1.0")
            self.assertEqual(metadata["command_exit_code"], 0)
            self.assertEqual((trial_dir / "outputs" / "stdout.txt").read_text(), "node count: 4\n")
            self.assertIn("warning", (trial_dir / "outputs" / "stderr.txt").read_text())
            self.assertTrue((trial_dir / "transcript.md").is_file())
            self.assertTrue((trial_dir / "state").is_dir())
            saved_metadata = json.loads((trial_dir / "metadata.json").read_text())
            self.assertEqual(saved_metadata, metadata)

    def test_nonzero_command_is_captured_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adapter = CLICaptureAdapter(
                [sys.executable, "-c", "raise SystemExit(7)"],
                "skill-writing",
                "test-model",
                runs_root=temp_dir,
            )
            metadata = adapter.capture("failure-case", "without_skill", 1)
            self.assertEqual(metadata["command_exit_code"], 7)
            self.assertFalse(metadata["timed_out"])

    def test_command_is_not_shell_interpreted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adapter = CLICaptureAdapter(
                [sys.executable, "-c", "import sys; print(sys.argv[1])", "$(touch SHOULD_NOT_EXIST)"],
                "skill-writing",
                "test-model",
                runs_root=temp_dir,
            )
            adapter.capture("literal-argument", "with_skill", 1)
            self.assertFalse((Path(temp_dir) / "SHOULD_NOT_EXIST").exists())

    def test_existing_trial_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            adapter = CLICaptureAdapter(
                [sys.executable, "-c", "pass"],
                "skill-writing",
                "test-model",
                runs_root=temp_dir,
            )
            adapter.capture("same-task", "with_skill", 1)
            with self.assertRaises(FileExistsError):
                adapter.capture("same-task", "with_skill", 1)


class ManualCaptureAdapterTests(unittest.TestCase):
    def test_manual_capture_writes_guide_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts: list[str] = []
            displayed: list[str] = []
            adapter = ManualCaptureAdapter(
                "epanet-validation",
                "manual-model",
                runs_root=temp_dir,
                metadata={"agent_harness": "manual session"},
                input_fn=lambda prompt: prompts.append(prompt) or "",
                output_fn=displayed.append,
            )
            metadata = adapter.capture("inspect-inp", "without_skill", 1)
            trial_dir = Path(temp_dir) / "epanet-validation" / "inspect-inp" / "without_skill" / "trial-1"

            self.assertEqual(validate_metadata(metadata), [])
            self.assertEqual(metadata["capture_mode"], "manual")
            self.assertEqual(metadata["agent_harness"], "manual session")
            self.assertTrue((trial_dir / "capture-guide.md").is_file())
            self.assertEqual(len(prompts), 1)
            self.assertIn(str(trial_dir), displayed[0])

    def test_prerequisite_reports_missing_model(self) -> None:
        adapter = ManualCaptureAdapter("skill", "", runs_root="unused")
        self.assertIn("model must be provided", adapter.validate_prerequisites())


if __name__ == "__main__":
    unittest.main()
