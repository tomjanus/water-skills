#!/usr/bin/env python3
"""Report skills whose review is due or whose review date is not recorded."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STALENESS_PATH = ROOT / "catalog" / "staleness.json"


def load_report(path: Path = STALENESS_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    report: dict[str, Any], today: dt.date | None = None
) -> tuple[list[tuple[str, str]], list[str]]:
    """Return (due, unknown) review items relative to today's date."""
    today = today or dt.date.today()
    due: list[tuple[str, str]] = []
    unknown: list[str] = []
    for entry in report.get("skills", []):
        name = entry.get("name", "<unnamed>")
        review_due = entry.get("review_due")
        if review_due is None:
            unknown.append(name)
            continue
        try:
            due_date = dt.date.fromisoformat(review_due)
        except (TypeError, ValueError):
            unknown.append(name)
            continue
        if due_date <= today:
            due.append((name, review_due))
    return due, unknown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail",
        action="store_true",
        help="exit non-zero when any review is due or unknown",
    )
    parser.add_argument(
        "--today",
        type=dt.date.fromisoformat,
        help="compare against this date (YYYY-MM-DD) instead of today",
    )
    parser.add_argument("--path", type=Path, default=STALENESS_PATH, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        report = load_report(args.path)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {args.path}: {exc}", file=sys.stderr)
        return 1

    due, unknown = evaluate(report, args.today)
    for name, review_due in due:
        print(f"WARNING: {name}: review due {review_due}")
    for name in unknown:
        print(f"WARNING: {name}: last_reviewed not recorded")

    if not due and not unknown:
        print("OK   no reviews due")
        return 0
    if args.fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
