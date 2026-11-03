"""Guided adapter for human-operated capture sessions."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .base import CaptureAdapter


class ManualCaptureAdapter(CaptureAdapter):
    """Prepare an artifact directory and guide a human through capture.

    ``input_fn`` and ``output_fn`` are injectable for non-interactive use and
    tests. The human copies reviewed artifacts into the displayed trial path.
    """

    def __init__(
        self,
        skill: str,
        model: str,
        *,
        runs_root: Path | str | None = None,
        metadata: dict[str, Any] | None = None,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print,
    ) -> None:
        super().__init__(skill, model, runs_root=runs_root, metadata=metadata)
        self.input_fn = input_fn
        self.output_fn = output_fn

    def capture(self, task_id: str, condition: str, trial: int) -> dict[str, Any]:
        run_dir = self._run_directory(task_id, condition, trial)
        guide = (
            "# Manual capture guide\n\n"
            "1. Run the task under the stated condition and trial.\n"
            "2. Save produced files under `outputs/` and exported application "
            "state under `state/`.\n"
            "3. Add a readable `transcript.md`; optionally record redacted "
            "screenshots and actions.\n"
            "4. Do not include credentials, licence keys, confidential models, "
            "or unredacted client data.\n\n"
            f"Trial directory: `{run_dir}`\n"
        )
        (run_dir / "capture-guide.md").write_text(guide, encoding="utf-8")
        self.output_fn(guide)
        self.input_fn("Press Enter after saving reviewed artifacts to this trial directory: ")
        return self._write_metadata(
            run_dir,
            task_id,
            condition,
            trial,
            extra={"capture_mode": "manual"},
        )
