---
name: skill-evaluation
description: Run and interpret skill evaluations, compare two skills or two versions, and decide whether to ship. Use when the user asks to run evals, read eval results, benchmark a skill against a baseline, check for regressions, or compare skills. Triggers on "run evals", "evaluate this skill", "how did it do", "compare skills", "did I break anything", "benchmark".
license: Apache-2.0
metadata:
  author: Tomasz Janus
  version: "1.0.0"
---

# Evaluating skills

Run a suite, read the report, and turn per-case results into a decision. This is
the runtime counterpart to [`skill-eval-writing`](../skill-eval-writing/SKILL.md),
which authors the cases. Both use the runner documented in
[`evals/README.md`](../../evals/README.md).

## Run

```
python evals/runner.py --validate
python evals/runner.py --skill <name> --all-conditions
python evals/runner.py --skill <name> --compare <other-skill>
python evals/runner.py --all --write-report
```

- `--validate` lints specs; run it first and in CI. It never touches the network.
- `--all-conditions` grades the `without_skill` baseline and `with_skill`.
- `--compare` grades another skill's `with_skill` artifacts on the same case ids.
- `--judge` enables bare-string assertions via `EVAL_JUDGE_CMD`. Off by default.

The runner grades captured artifacts under `evals/runs/`. Capture runs in your own
harness; the contract is in [`evals/README.md`](../../evals/README.md#capturing-a-run).

## Read the report

Each row is a case; each column is a condition. A cell reads
`passed/trials (rate, checks passed/total)`.

| Signal | Meaning |
|--------|---------|
| High lift, high pass rate | The skill works and is worth keeping. |
| High lift, noisy across trials | Tighten the skill or widen the rubric, then rerun. |
| Low lift | The case does not exercise the skill, or the skill does not help. |
| Negative lift | The skill is making things worse. Investigate before shipping. |

Read per-case failures, not just the aggregate. A single failing check tells you
what to fix.

## Interpret per-case patterns

- **Pass in both conditions** — the case is saturated; it does not discriminate.
  Sharpen it or drop it.
- **Fail in both conditions** — the assertion is wrong, the task is impossible, or
  the fixture is broken. Fix it before trusting the suite.
- **Pass with the skill, fail without** — the case captures real value. Understand
  why, and make sure the skill change generalises.
- **High variance across trials** — the instructions are ambiguous. Add an example
  or tighten the wording.

## Compare two skills or versions

To compare skill A and skill B on the same cases:

1. Run A's cases with B loaded and save the artifacts to
   `evals/runs/B/<case-id>/with_skill/`.
2. `python evals/runner.py --skill A --conditions with_skill --compare B`.
3. Read the per-case delta. A higher aggregate with a worse per-case profile is a
   trade-off, not a win — say which cases regressed.

For a version comparison, keep the case ids stable and record `skill_revision` in
each run's `metadata.json`.

## Size the trials

One trial is enough to develop the harness. Before trusting a number, run 3–5
trials per case. The default reading is `pass@k` (any trial passes). High variance
between trials is a signal about the skill, not noise to average away.

## Decide whether to ship

Ship when:

- `with_skill` beats `without_skill` on cases that exercise the skill;
- routing checks pass for should-fire and negative cases;
- deterministic checks pass without the judge;
- the improvement is stable across trials;
- you can point to the per-case evidence, not a vibe.

Do not ship on a single green run, on a saturated suite, or on a change to
behaviour-shaping wording without a before/after comparison.

## Report in a PR

State the exact prompt, the conditions compared, the number of trials, and the
per-case delta. "It works" is not evaluation. If you could not measure it, say so.

## Checklist

- `python evals/runner.py --validate` passes.
- Baseline and skill conditions were captured for the same case ids.
- At least one case shows positive lift; no case shows a regression you cannot explain.
- Routing is verified for trigger-sensitive skills.
- The report names the model, harness, and number of trials.
