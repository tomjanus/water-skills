"""Subprocess-based capture adapter for deterministic CLI tasks."""

from __future__ import annotations

import shlex
import subprocess
import time
from pathlib import Path
from typing import Any, Sequence

from .base import CaptureAdapter


class CLICaptureAdapter(CaptureAdapter):
    """Run a command without a shell and save its outputs as trial artifacts.

    Commands must be passed as an argument sequence. Shell expansion and
    shell-interpreted command strings are deliberately unsupported.
    """

    def __init__(
        self,
        command: Sequence[str],
        skill: str,
        model: str,
        *,
        cwd: Path | str | None = None,
        input_text: str | None = None,
        timeout: float = 120.0,
        runs_root: Path | str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(skill, model, runs_root=runs_root, metadata=metadata)
        self.command = tuple(command)
        self.cwd = Path(cwd) if cwd is not None else None
        self.input_text = input_text
        self.timeout = timeout

    def validate_prerequisites(self) -> list[str]:
        errors = super().validate_prerequisites()
        if not self.command or any(not isinstance(arg, str) for arg in self.command):
            errors.append("command must be a non-empty sequence of strings")
        if self.cwd is not None and not self.cwd.is_dir():
            errors.append(f"working directory does not exist: {self.cwd}")
        if self.timeout <= 0:
            errors.append("timeout must be positive")
        return errors

    def capture(self, task_id: str, condition: str, trial: int) -> dict[str, Any]:
        run_dir = self._run_directory(task_id, condition, trial)
        started = time.monotonic()
        timed_out = False
        return_code: int | None
        try:
            completed = subprocess.run(
                self.command,
                cwd=self.cwd,
                input=self.input_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
                check=False,
                shell=False,
            )
            stdout = completed.stdout
            stderr = completed.stderr
            return_code = completed.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = self._as_text(exc.stdout)
            stderr = self._as_text(exc.stderr)
            return_code = None
        elapsed = time.monotonic() - started

        (run_dir / "outputs" / "stdout.txt").write_text(stdout, encoding="utf-8")
        (run_dir / "outputs" / "stderr.txt").write_text(stderr, encoding="utf-8")
        transcript = [
            "# Captured CLI trial",
            "",
            f"- Command: `{shlex.join(self.command)}`",
            f"- Exit code: `{return_code if return_code is not None else 'timeout'}`",
            "",
            "## Standard output",
            "",
            "```text",
            stdout.rstrip(),
            "```",
            "",
            "## Standard error",
            "",
            "```text",
            stderr.rstrip(),
            "```",
            "",
        ]
        (run_dir / "transcript.md").write_text("\n".join(transcript), encoding="utf-8")
        return self._write_metadata(
            run_dir,
            task_id,
            condition,
            trial,
            time_seconds=elapsed,
            extra={"command_exit_code": return_code, "timed_out": timed_out},
        )

    @staticmethod
    def _as_text(value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value
