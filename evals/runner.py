#!/usr/bin/env python3
"""Harness-agnostic eval runner for water-skills.

Discovers co-located skill evals, grades captured run artifacts against
deterministic assertions (and an optional LLM judge), and reports pass rates
with deltas against a baseline or comparator skill.

Usage:
    python evals/runner.py --skill skill-writing --all-conditions
    python evals/runner.py --all
    python evals/runner.py --skill skill-writing --compare skill-eval-writing
    python evals/runner.py --validate
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALS_ROOT = REPO_ROOT / "evals"
RUNS_DIR = EVALS_ROOT / "runs"
REPORTS_DIR = EVALS_ROOT / "reports"
SKILLS_DIR = REPO_ROOT / "skills"

CONDITION_BASELINE = "without_skill"
CONDITION_WITH = "with_skill"
ALL_CONDITIONS = (CONDITION_BASELINE, CONDITION_WITH)
VALID_CONDITIONS = ALL_CONDITIONS

REQUIRED_CASE_FIELDS = ("id", "prompt", "expected_output")
TRIAL_DIR_RE = re.compile(r"^trial-\d+$")


@dataclass
class AssertionResult:
    assertion: str
    kind: str
    passed: bool | None
    detail: str


@dataclass
class CaseResult:
    case_id: str
    label: str
    condition: str
    trial: str
    results: list[AssertionResult] = field(default_factory=list)

    @property
    def evaluated(self) -> list[AssertionResult]:
        return [r for r in self.results if r.passed is not None]

    @property
    def passed(self) -> bool:
        return bool(self.evaluated) and all(r.passed for r in self.evaluated)

    @property
    def score(self) -> int:
        return sum(1 for r in self.evaluated if r.passed)

    @property
    def total(self) -> int:
        return len(self.evaluated)


def load_suite(skill_dir: Path) -> dict[str, Any]:
    path = skill_dir / "evals" / "evals.json"
    if not path.is_file():
        raise ValueError(f"missing eval suite: {path}")
    try:
        suite = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON ({exc})") from exc
    validate_suite(skill_dir, suite)
    return suite


def validate_suite(skill_dir: Path, suite: dict[str, Any]) -> None:
    if not isinstance(suite, dict):
        raise ValueError(f"{skill_dir}: suite must be a JSON object")
    if suite.get("skill_name") != skill_dir.name:
        raise ValueError(
            f"{skill_dir}: 'skill_name' {suite.get('skill_name')!r} "
            f"does not match directory name {skill_dir.name!r}"
        )
    cases = suite.get("evals")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{skill_dir}: 'evals' must be a non-empty array")
    seen: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"{skill_dir}: eval #{index} must be an object")
        for name in REQUIRED_CASE_FIELDS:
            if not case.get(name):
                raise ValueError(f"{skill_dir}: eval #{index} missing {name!r}")
        case_id = case["id"]
        if case_id in seen:
            raise ValueError(f"{skill_dir}: duplicate eval id {case_id!r}")
        seen.add(case_id)
        _validate_case_refs(skill_dir, case)


def _validate_case_refs(skill_dir: Path, case: dict[str, Any]) -> None:
    evals_dir = skill_dir / "evals"
    for assertion in case.get("assertions", []):
        if not isinstance(assertion, str):
            raise ValueError(f"{skill_dir}: assertion must be a string")
        if assertion.startswith("script:"):
            script = evals_dir / "scripts" / assertion.split(":", 1)[1]
            if not script.is_file():
                raise ValueError(f"{skill_dir}: missing script {script}")
    for fixture in case.get("files", []):
        path = evals_dir / "files" / fixture
        if not path.is_file():
            raise ValueError(f"{skill_dir}: missing fixture {path}")


def discover_suites() -> list[Path]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        skill_dir
        for skill_dir in SKILLS_DIR.iterdir()
        if skill_dir.is_dir() and (skill_dir / "evals" / "evals.json").is_file()
    )


def artifact_dir(skill: str, case_id: str, condition: str) -> Path:
    return RUNS_DIR / skill / case_id / condition


def trial_dirs(artifacts: Path) -> list[Path]:
    if not artifacts.is_dir():
        return []
    trials = sorted(
        (p for p in artifacts.iterdir() if p.is_dir() and TRIAL_DIR_RE.match(p.name)),
        key=lambda p: p.name,
    )
    return trials or [artifacts]


def text_files(artifacts: Path) -> dict[str, str]:
    texts: dict[str, str] = {}
    for path in sorted(artifacts.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".csv", ".ini", ".inp"}:
            continue
        try:
            texts[str(path.relative_to(artifacts))] = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
    return texts


def grade_assertion(
    case: dict[str, Any],
    assertion: str,
    artifacts: Path,
    evals_dir: Path,
    judge_cmd: str | None,
) -> AssertionResult:
    texts = text_files(artifacts)
    combined = "\n".join(texts.values())

    if assertion.startswith("file:"):
        rel = assertion.split(":", 1)[1]
        candidates = (artifacts / rel, artifacts / "outputs" / rel)
        found = next((c for c in candidates if c.exists()), None)
        if found is None:
            matches = [p for p in artifacts.rglob(Path(rel).name) if p.is_file()]
            found = matches[0] if matches else None
        if found is None:
            return AssertionResult(assertion, "file", False, f"{rel} missing")
        return AssertionResult(assertion, "file", True, f"{found.relative_to(artifacts)} found")

    if assertion.startswith("regex:"):
        pattern = assertion.split(":", 1)[1]
        try:
            matched = bool(re.search(pattern, combined, re.MULTILINE))
        except re.error as exc:
            return AssertionResult(assertion, "regex", False, f"invalid pattern: {exc}")
        return AssertionResult(assertion, "regex", matched, f"pattern {'matched' if matched else 'not found'}")

    if assertion.startswith("json:"):
        _, rel, field = assertion.split(":", 2)
        path = artifacts / rel
        if not path.is_file():
            return AssertionResult(assertion, "json", False, f"missing {rel}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return AssertionResult(assertion, "json", False, f"invalid JSON: {exc}")
        value: Any = data
        for part in field.split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return AssertionResult(assertion, "json", False, f"missing field {field}")
        return AssertionResult(assertion, "json", True, f"field {field} present")

    if assertion.startswith("script:"):
        script = assertion.split(":", 1)[1]
        path = evals_dir / "scripts" / script
        if path.suffix == ".py":
            cmd = [sys.executable, str(path), str(artifacts)]
        elif path.suffix == ".sh":
            cmd = ["bash", str(path), str(artifacts)]
        else:
            cmd = [str(path), str(artifacts)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return AssertionResult(assertion, "script", False, f"could not run: {exc}")
        detail = (proc.stdout or proc.stderr).strip().splitlines()
        return AssertionResult(
            assertion,
            "script",
            proc.returncode == 0,
            detail[-1] if detail else f"exit {proc.returncode}",
        )

    if assertion == "agentskills":
        return _grade_agentskills(artifacts)

    return _grade_judge(case, assertion, combined, judge_cmd)


def _grade_agentskills(artifacts: Path) -> AssertionResult:
    skill_files = list(artifacts.rglob("SKILL.md"))
    if len(skill_files) != 1:
        return AssertionResult(
            "agentskills", "agentskills", False, f"expected one SKILL.md, found {len(skill_files)}"
        )
    skill_dir = skill_files[0].parent
    try:
        proc = subprocess.run(
            ["agentskills", "validate", str(skill_dir)],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        return AssertionResult("agentskills", "agentskills", None, "agentskills CLI not installed")
    except subprocess.TimeoutExpired:
        return AssertionResult("agentskills", "agentskills", False, "timed out")
    return AssertionResult(
        "agentskills",
        "agentskills",
        proc.returncode == 0,
        (proc.stdout or proc.stderr).strip() or f"exit {proc.returncode}",
    )


def _grade_judge(
    case: dict[str, Any], assertion: str, transcript: str, judge_cmd: str | None
) -> AssertionResult:
    if not judge_cmd:
        return AssertionResult(assertion, "judge", None, "judge disabled (set EVAL_JUDGE_CMD)")
    payload = json.dumps(
        {
            "assertion": assertion,
            "case_id": case["id"],
            "expected_output": case.get("expected_output", ""),
            "transcript": transcript,
        }
    )
    try:
        proc = subprocess.run(
            judge_cmd,
            shell=True,
            input=payload,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return AssertionResult(assertion, "judge", None, f"judge failed: {exc}")
    for line in reversed(proc.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                verdict = json.loads(line)
            except json.JSONDecodeError:
                continue
            return AssertionResult(
                assertion,
                "judge",
                bool(verdict.get("pass")),
                str(verdict.get("reason", "")).strip(),
            )
    return AssertionResult(assertion, "judge", None, "judge returned no JSON verdict")


def grade_case(
    case: dict[str, Any],
    artifacts: Path,
    condition: str,
    trial: str,
    evals_dir: Path,
    judge_cmd: str | None,
) -> CaseResult:
    result = CaseResult(case["id"], case.get("label", case["id"]), condition, trial)
    routing = case.get("routing")
    if routing is None and case.get("expected_skill"):
        routing = {"expect": [case["expected_skill"]]}
    if routing:
        texts = text_files(artifacts)
        combined = "\n".join(texts.values())
        for expected in routing.get("expect", []):
            found = expected.lower() in combined.lower()
            result.results.append(
                AssertionResult(f"route:{expected}", "route", found, f"transcript {'mentions' if found else 'does not mention'} {expected}")
            )
        for forbidden in routing.get("forbid", []):
            found = forbidden.lower() in combined.lower()
            result.results.append(
                AssertionResult(f"route-not:{forbidden}", "route", not found, f"transcript {'mentions' if found else 'does not mention'} {forbidden}")
            )
    for assertion in case.get("assertions", []):
        result.results.append(grade_assertion(case, assertion, artifacts, evals_dir, judge_cmd))
    return result


def run_suite(
    skill: str,
    conditions: list[tuple[str, str]],
    judge_cmd: str | None,
) -> list[CaseResult]:
    skill_dir = SKILLS_DIR / skill
    suite = load_suite(skill_dir)
    evals_dir = skill_dir / "evals"
    results: list[CaseResult] = []
    for case in suite["evals"]:
        for label, template in conditions:
            path = Path(template.format(case=case["id"]))
            for trial in trial_dirs(path):
                trial_name = trial.name if trial != path else "trial-1"
                results.append(
                    grade_case(case, trial, label, trial_name, evals_dir, judge_cmd)
                )
    return results


def condition_specs(
    skill: str,
    requested: list[str] | None,
    compare: str | None,
) -> list[tuple[str, str]]:
    requested = requested or list(ALL_CONDITIONS)
    specs: list[tuple[str, str]] = []
    for condition in requested:
        if condition not in VALID_CONDITIONS:
            raise ValueError(f"unknown condition {condition!r}; use {ALL_CONDITIONS}")
        specs.append((condition, str(RUNS_DIR / skill / "{case}" / condition)))
    if compare:
        specs.append((f"compare:{compare}", str(RUNS_DIR / compare / "{case}" / CONDITION_WITH)))
    return specs


def summarize(results: list[CaseResult]) -> dict[str, Any]:
    by_condition: dict[str, list[CaseResult]] = {}
    for result in results:
        by_condition.setdefault(result.condition, []).append(result)
    summary: dict[str, Any] = {"conditions": {}, "cases": []}
    for condition, runs in by_condition.items():
        trials = len(runs)
        passed = sum(1 for r in runs if r.passed)
        checks = sum(r.score for r in runs)
        total = sum(r.total for r in runs)
        summary["conditions"][condition] = {
            "trials": trials,
            "passed": passed,
            "trial_pass_rate": (passed / trials) if trials else 0.0,
            "checks_passed": checks,
            "checks_total": total,
            "check_pass_rate": (checks / total) if total else 0.0,
        }
    case_ids: list[str] = []
    for result in results:
        if result.case_id not in case_ids:
            case_ids.append(result.case_id)
    for case_id in case_ids:
        row: dict[str, Any] = {"id": case_id}
        for condition, runs in by_condition.items():
            case_runs = [r for r in runs if r.case_id == case_id]
            if not case_runs:
                row[condition] = None
                continue
            passed = sum(1 for r in case_runs if r.passed)
            total_checks = sum(r.total for r in case_runs)
            checks = sum(r.score for r in case_runs)
            row[condition] = {
                "passed": passed,
                "trials": len(case_runs),
                "checks_passed": checks,
                "checks_total": total_checks,
            }
        summary["cases"].append(row)
    return summary


def render_markdown(skill: str, summary: dict[str, Any]) -> str:
    conditions = list(summary["conditions"])
    header = f"# Eval report: {skill}\n\n_Generated {dt.datetime.now().isoformat(timespec='seconds')}_\n\n"
    cols = "| Case | " + " | ".join(conditions) + " |\n"
    sep = "|------|" + "|".join(["------"] * len(conditions)) + "|\n"
    lines = [header, cols, sep]
    for row in summary["cases"]:
        cells = []
        for condition in conditions:
            cell = row.get(condition)
            if cell is None:
                cells.append("—")
            else:
                rate = (cell["passed"] / cell["trials"]) if cell["trials"] else 0
                cells.append(f"{cell['passed']}/{cell['trials']} ({rate:.0%}, {cell['checks_passed']}/{cell['checks_total']} checks)")
        lines.append(f"| {row['id']} | " + " | ".join(cells) + " |\n")
    lines.append("\n")
    for condition, stats in summary["conditions"].items():
        lines.append(
            f"**{condition}**: {stats['passed']}/{stats['trials']} trials passed "
            f"({stats['trial_pass_rate']:.0%}); checks {stats['checks_passed']}/{stats['checks_total']} "
            f"({stats['check_pass_rate']:.0%})\n"
        )
    if CONDITION_BASELINE in summary["conditions"] and CONDITION_WITH in summary["conditions"]:
        lift = (
            summary["conditions"][CONDITION_WITH]["trial_pass_rate"]
            - summary["conditions"][CONDITION_BASELINE]["trial_pass_rate"]
        )
        lines.append(f"\n**Lift (with_skill − without_skill)**: {lift:+.0%} trial pass rate\n")
    return "".join(lines)


def cmd_validate() -> int:
    suites = discover_suites()
    if not suites:
        print("No eval suites found.")
        return 0
    failed = False
    for skill_dir in suites:
        try:
            suite = load_suite(skill_dir)
        except ValueError as exc:
            print(f"FAIL {skill_dir}: {exc}")
            failed = True
            continue
        print(f"OK   {skill_dir} ({len(suite['evals'])} case(s))")
    return 1 if failed else 0


def cmd_list() -> int:
    suites = discover_suites()
    if not suites:
        print("No eval suites found.")
        return 0
    for skill_dir in suites:
        suite = load_suite(skill_dir)
        print(f"{skill_dir.name}: {len(suite['evals'])} case(s)")
        for case in suite["evals"]:
            print(f"  - {case['id']}: {case.get('label', '')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", help="skill directory name to evaluate")
    parser.add_argument("--all", action="store_true", help="evaluate every skill with evals")
    parser.add_argument("--list", action="store_true", help="list discovered eval suites")
    parser.add_argument("--validate", action="store_true", help="lint eval specs only")
    parser.add_argument("--conditions", nargs="+", choices=ALL_CONDITIONS, help="conditions to grade")
    parser.add_argument("--all-conditions", action="store_true", help="grade baseline and with_skill")
    parser.add_argument("--compare", help="also grade this skill's with_skill artifacts")
    parser.add_argument("--judge", action="store_true", help="enable LLM-judged assertions via EVAL_JUDGE_CMD")
    parser.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    parser.add_argument("--write-report", action="store_true", help="write a timestamped report under evals/reports/")
    args = parser.parse_args(argv)

    if args.validate:
        return cmd_validate()
    if args.list:
        return cmd_list()

    judge_cmd = os.environ.get("EVAL_JUDGE_CMD") if args.judge else None

    if args.all:
        targets = discover_suites()
        if not targets:
            print("No eval suites found.")
            return 1
    elif args.skill:
        targets = [SKILLS_DIR / args.skill]
        if not (targets[0] / "evals" / "evals.json").is_file():
            print(f"No eval suite for skill {args.skill!r}.", file=sys.stderr)
            return 1
    else:
        parser.error("provide --skill <name> or --all")

    exit_code = 0
    for skill_dir in targets:
        skill = skill_dir.name
        requested = args.conditions
        if args.all_conditions and requested is None:
            requested = list(ALL_CONDITIONS)
        try:
            specs = condition_specs(skill, requested, args.compare)
        except ValueError as exc:
            print(f"FAIL {skill}: {exc}", file=sys.stderr)
            exit_code = 1
            continue
        results = run_suite(skill, specs, judge_cmd)
        if not results:
            print(f"{skill}: no captured artifacts found for requested conditions.")
            exit_code = 1
            continue
        summary = summarize(results)
        report = json.dumps(summary, indent=2) if args.json else render_markdown(skill, summary)
        print(report)
        if args.write_report:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
            out = REPORTS_DIR / f"{skill}-{stamp}.md"
            out.write_text(render_markdown(skill, summary), encoding="utf-8")
            print(f"\nReport written to {out}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
