---
name: skill-evaluation
description: Grade captured skill-evaluation artifacts and interpret per-case results. Use when asked to read or compare completed eval reports or assess regressions; authoring eval specifications belongs to eval-writing.
metadata:
  author: Tomasz Janus
  version: "1.0.0"
---

# Evaluating skills

Grade captured eval artifacts, inspect per-case results, and report what the
evidence supports. This is the interpretation counterpart to
[`eval-writing`](../eval-writing/SKILL.md), which authors the cases. Both use the runner documented in
[`evals/README.md`](../../evals/README.md).

## Run

```
python evals/runner.py --validate
python evals/runner.py --skill <name> --all-conditions
python evals/runner.py --skill <name> --compare <other-skill>
python evals/runner.py --all --write-report
```

- `--validate` lints specs; run it first and in CI. It never touches the network
  and does not grade behavior.
- `--all-conditions` grades the `without_skill` baseline and `with_skill`.
- `--compare` grades another skill's `with_skill` artifacts on the same case ids.
- `--judge` enables bare-string assertions via `EVAL_JUDGE_CMD`. Off by default.

The runner grades captured artifacts under `evals/runs/`; it does not launch an
agent or capture a run. If the required artifacts are missing, report that no
behavioral result is available. Capture runs in a separate harness; the contract
is in [`evals/README.md`](../../evals/README.md#capturing-a-run).

## Read the report

Each row is a case; each column is a condition. A cell reads
`passed/trials (rate, checks passed/total)`.

| Signal | Meaning |
|--------|---------|
| High lift, high pass rate | The skill helped on these captured cases and conditions; inspect case evidence before generalizing. |
| High lift, noisy across trials | Check task ambiguity and variance; inspect cases before changing the skill or rubric. |
| Low lift | The case may not exercise a difference, or no difference was observed; inspect the prompts, captures, and checks. |
| Negative lift | A regression was observed in these cases; investigate before making a release decision. |

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

Evidence may support a ship recommendation when:

- `with_skill` outperforms `without_skill` on discriminating cases;
- textual routing-mention checks match expected IDs; this is not proof a host loaded the skill;
- deterministic checks pass without the judge;
- the observed improvement is stable across the captured trials;
- you can point to the per-case evidence, not a vibe.

These conditions do not establish scientific or engineering validity. A human
owns the final ship decision. Do not recommend shipping from a single green run,
a saturated suite, or a behavior-shaping change without a before/after comparison.

## Report in a PR

State the exact prompt, the conditions compared, the number of trials, and the
per-case delta. "It works" is not evaluation. If you could not measure it, say so.

## Checklist

- `python evals/runner.py --validate` passes.
- Baseline and skill conditions were captured for the same case ids.
- At least one case shows positive lift; no case shows a regression you cannot explain.
- Textual routing-mention checks match expected IDs; host invocation is not inferred from them.
- The report names the model, harness, and number of trials.
- The conclusion is limited to the captured tasks, conditions, and trials.

## Evaluation status

The suite specification is checked for structure. No captured agent runs have been graded, so the behavior of this skill has not been evaluated.
