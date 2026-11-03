#!/usr/bin/env python3
"""Validate the repository's deliberately small provenance YAML schema."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
SCHEMA_PATH = ROOT / "provenance.schema.json"

LIST_FIELDS = {"authors", "references", "software_tested", "reviewers", "evidence"}
SCALAR_FIELDS = {"method_status", "review_status"}
ALLOWED_FIELDS = LIST_FIELDS | SCALAR_FIELDS
METHOD_STATUSES = {"established", "adapted", "heuristic", "hypothesis"}
REVIEW_STATUSES = {"not_reviewed", "under_review", "reviewed"}


class ProvenanceError(ValueError):
    """Raised when a provenance file is outside the supported YAML subset."""


def _strip_comment(line: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(line):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in {'"', "'"}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
            continue
        if character == "#" and quote is None and (index == 0 or line[index - 1].isspace()):
            return line[:index].rstrip()
    return line.rstrip()


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith("["):
        try:
            return json.loads(value)
        except json.JSONDecodeError as exc:
            raise ProvenanceError(f"inline lists must use JSON-compatible YAML: {exc}") from exc
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ProvenanceError(f"invalid quoted string: {exc}") from exc
        if not isinstance(parsed, str):
            raise ProvenanceError("quoted scalar must be a string")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise ProvenanceError("unterminated single-quoted string")
        return value[1:-1].replace("''", "'")
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"[-+]?(?:0|[1-9][0-9]*)", value):
        return int(value)
    if re.fullmatch(r"[-+]?(?:[0-9]+\.[0-9]*|\.[0-9]+)", value):
        return float(value)
    return value


def parse_provenance(text: str) -> dict[str, Any]:
    """Parse top-level scalars and string lists in the provenance contract."""
    record: dict[str, Any] = {}
    current_list: str | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line)
        if not line.strip():
            continue
        if "\t" in line[: len(line) - len(line.lstrip())]:
            raise ProvenanceError(f"line {line_number}: tabs are not supported for indentation")

        if line.startswith("  - "):
            if current_list not in LIST_FIELDS:
                raise ProvenanceError(f"line {line_number}: list item without a list field")
            try:
                item = _parse_scalar(line[4:])
            except ProvenanceError as exc:
                raise ProvenanceError(f"line {line_number}: {exc}") from exc
            record[current_list].append(item)
            continue

        if line[0].isspace():
            raise ProvenanceError(f"line {line_number}: only two-space list indentation is supported")

        key, separator, raw_value = line.partition(":")
        if not separator or not re.fullmatch(r"[a-z_]+", key):
            raise ProvenanceError(f"line {line_number}: expected a top-level field")
        if key not in ALLOWED_FIELDS:
            raise ProvenanceError(f"line {line_number}: unknown field {key!r}")
        if key in record:
            raise ProvenanceError(f"line {line_number}: duplicate field {key!r}")

        value = raw_value.strip()
        if not value:
            if key not in LIST_FIELDS:
                raise ProvenanceError(f"line {line_number}: {key!r} requires a scalar value")
            record[key] = []
            current_list = key
            continue

        try:
            record[key] = _parse_scalar(value)
        except ProvenanceError as exc:
            raise ProvenanceError(f"line {line_number}: {exc}") from exc
        current_list = key if key in LIST_FIELDS and isinstance(record[key], list) else None

    return record


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for required in ("authors", "method_status"):
        if required not in record:
            errors.append(f"missing required field {required!r}")

    authors = record.get("authors")
    if not isinstance(authors, list) or not authors:
        errors.append("'authors' must be a non-empty list of names")
    elif any(not isinstance(author, str) or not author.strip() for author in authors):
        errors.append("'authors' entries must be non-empty strings")

    method_status = record.get("method_status")
    if not isinstance(method_status, str) or method_status not in METHOD_STATUSES:
        errors.append(f"'method_status' must be one of {', '.join(sorted(METHOD_STATUSES))}")

    for field in LIST_FIELDS - {"authors"}:
        if field not in record:
            continue
        value = record[field]
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f"'{field}' must be a list of non-empty strings")

    review_status = record.get("review_status")
    if "review_status" in record and (
        not isinstance(review_status, str) or review_status not in REVIEW_STATUSES
    ):
        errors.append(f"'review_status' must be one of {', '.join(sorted(REVIEW_STATUSES))}")
    if review_status == "reviewed" and not record.get("reviewers"):
        errors.append("'reviewers' is required when review_status is 'reviewed'")
    return errors


def validate_schema_file(path: Path = SCHEMA_PATH) -> list[str]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(ROOT)}: cannot read valid JSON Schema ({exc})"]
    if not isinstance(schema, dict):
        return ["provenance.schema.json must contain a JSON object"]
    expected_required = {"authors", "method_status"}
    required = set(schema.get("required", []))
    method_values = set(schema.get("properties", {}).get("method_status", {}).get("enum", []))
    errors: list[str] = []
    if required != expected_required:
        errors.append("provenance.schema.json must require exactly authors and method_status")
    if method_values != METHOD_STATUSES:
        errors.append("provenance.schema.json method_status enum does not match the validator")
    return errors


def main() -> int:
    errors = validate_schema_file()
    records = sorted(SKILLS_DIR.glob("*/provenance.yaml")) if SKILLS_DIR.is_dir() else []
    for path in records:
        try:
            record = parse_provenance(path.read_text(encoding="utf-8"))
            errors.extend(f"{path.relative_to(ROOT)}: {message}" for message in validate_record(record))
        except (OSError, UnicodeError, ProvenanceError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if records:
        for path in records:
            print(f"OK   {path.relative_to(ROOT)}")
    else:
        print("OK   provenance.schema.json (no per-skill provenance records present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
