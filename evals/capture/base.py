"""Shared interface and artifact layout for capture adapters."""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from evals.schema import SCHEMA_VERSION, validate_metadata

_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")


class CaptureAdapter(ABC):
    """Base class for adapters that capture one task trial.

    Args:
        skill: Skill suite name. Must be a single safe path component.
        model: Model identifier, or an explicit label such as ``manual``.
        runs_root: Root directory for captured artifacts. Defaults to
            ``evals/runs`` in this repository.
        metadata: Additional descriptive metadata to include in the run file.
    """

    def __init__(
        self,
        skill: str,
        model: str,
        runs_root: Path | str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.skill = skill
        self.model = model
        self.runs_root = (
            Path(runs_root)
            if runs_root is not None
            else Path(__file__).resolve().parents[1] / "runs"
        )
        self.extra_metadata = dict(metadata or {})

    def validate_prerequisites(self) -> list[str]:
        """Return unmet requirements before starting capture."""
        errors: list[str] = []
        if not self._is_safe_component(self.skill):
            errors.append("skill must be a safe single path component")
        if not self.model.strip():
            errors.append("model must be provided")
        return errors

    def artifact_layout(self) -> dict[str, str]:
        """Describe the conventional artifact paths relative to a trial."""
        return {
            "outputs": "outputs/",
            "state": "state/",
            "screenshots": "screenshots/",
            "actions": "actions.jsonl",
            "transcript": "transcript.md",
            "metadata": "metadata.json",
        }

    @abstractmethod
    def capture(self, task_id: str, condition: str, trial: int) -> dict[str, Any]:
        """Capture a single trial and return its metadata."""

    def _run_directory(self, task_id: str, condition: str, trial: int) -> Path:
        errors = self.validate_prerequisites()
        if errors:
            raise ValueError("capture prerequisites not met: " + "; ".join(errors))
        if not self._is_safe_component(task_id):
            raise ValueError("task_id must be a safe single path component")
        if not self._is_safe_component(condition):
            raise ValueError("condition must be a safe single path component")
        if isinstance(trial, bool) or not isinstance(trial, int) or trial < 1:
            raise ValueError("trial must be a positive integer")

        run_dir = self.runs_root / self.skill / task_id / condition / f"trial-{trial}"
        if run_dir.exists():
            raise FileExistsError(f"capture directory already exists: {run_dir}")
        run_dir.mkdir(parents=True)
        (run_dir / "outputs").mkdir()
        (run_dir / "state").mkdir()
        return run_dir

    def _write_metadata(
        self,
        run_dir: Path,
        task_id: str,
        condition: str,
        trial: int,
        *,
        time_seconds: float | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "eval_harness": "water-skills capture adapters",
            **self.extra_metadata,
            **(extra or {}),
            "task_id": task_id,
            "condition": condition,
            "trial": trial,
            "model": self.model,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        if time_seconds is not None:
            metadata["time_seconds"] = max(0.0, time_seconds)
        errors = validate_metadata(metadata)
        if errors:
            raise ValueError("invalid capture metadata: " + "; ".join(errors))
        (run_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return metadata

    @staticmethod
    def _is_safe_component(value: str) -> bool:
        return bool(value and value not in {".", ".."} and _SAFE_COMPONENT.fullmatch(value))
