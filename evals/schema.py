"""Versioned run metadata schema for eval captures.

Defines the V1 contract for metadata.json recorded alongside captured eval
artifacts. Validation is additive: known fields are checked when present,
unknown fields are ignored. Existing free-form metadata remains valid.
"""

from __future__ import annotations

import re
from typing import Any

SCHEMA_VERSION = "1.0"

REQUIRED_FIELDS = ("task_id", "condition", "trial", "model", "timestamp")

OPTIONAL_FIELDS = (
    "agent_harness",
    "agent_harness_version",
    "eval_harness",
    "eval_harness_version",
    "skill_revision",
    "software_versions",
    "os_info",
    "licence_mode",
    "cost",
    "time_seconds",
)

CONDITION_RE = re.compile(r"^(without_skill|with_skill|compare:.+)$")


def validate_metadata(metadata: dict[str, Any]) -> list[str]:
    """Validate a captured-run metadata dict against the V1 schema.

    Returns a list of human-readable error messages. An empty list means the
    metadata is valid. Unknown fields are ignored (additive validation).
    """
    errors: list[str] = []

    if not isinstance(metadata, dict):
        return ["metadata must be a JSON object"]

    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"missing required field: {field}")
        elif metadata[field] is None or metadata[field] == "":
            errors.append(f"required field {field!r} must not be empty")

    condition = metadata.get("condition")
    if condition is not None and not CONDITION_RE.match(str(condition)):
        errors.append(
            f"invalid condition {condition!r}; "
            "use 'without_skill', 'with_skill', or 'compare:<skill>'"
        )

    trial = metadata.get("trial")
    if trial is not None:
        try:
            trial_int = int(trial)
            if trial_int < 1:
                errors.append("trial must be a positive integer")
        except (ValueError, TypeError):
            errors.append("trial must be a positive integer")

    cost = metadata.get("cost")
    if cost is not None:
        try:
            cost_float = float(cost)
            if cost_float < 0:
                errors.append("cost must be non-negative")
        except (ValueError, TypeError):
            errors.append("cost must be a number")

    time_seconds = metadata.get("time_seconds")
    if time_seconds is not None:
        try:
            time_float = float(time_seconds)
            if time_float < 0:
                errors.append("time_seconds must be non-negative")
        except (ValueError, TypeError):
            errors.append("time_seconds must be a number")

    software_versions = metadata.get("software_versions")
    if software_versions is not None and not isinstance(software_versions, dict):
        errors.append("software_versions must be an object")

    return errors
