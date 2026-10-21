---
name: skill-eval-writing
description: Write and iterate behavioural evals for agent skills. Use when the user asks to add eval cases, measure a skill against a baseline, compare two skills, or set up an eval harness in this repository. Triggers on "write an eval", "add evals", "evaluate this skill", "benchmark a skill", "compare skills".
license: Apache-2.0
metadata:
  author: Tomasz Janus
  version: "1.0.0"
---

# Writing skill evals

An eval is a **failing test for one observable behaviour**: a realistic prompt, a
captured run, a small set of checks, and a score you can compare over time.

A case that cannot fail proves nothing. Write the eval before the skill change
it is meant to protect.

## The test-driven loop

1. **RED.** Before writing or changing a skill, write a case that fails against
   current behaviour. Run it and record the baseline score.
2. **GREEN.** Make the smallest skill change that makes the case pass. Keep the
   skill and its eval in sync.
3. **REGRESSION.** Every real failure observed in a session becomes a case. A bug
   found once and not encoded will be found again.
4. **REVIEW.** Re-run on a second, holdout prompt set to check you did not
   overfit the skill to one case's wording.

A case that is green in both conditions is **not discriminating**. Sharpen it or
drop it.

## When to write an eval

Write one when a skill has behaviour worth protecting: a procedure the agent must
follow, a trigger it must honour, a file it must produce. Skip it for a trivial
skill whose correctness is already covered by `agentskills validate`.

## Layout

```
skills/<name>/
├── SKILL.md
└── evals/
    ├── evals.json          # required: cases, prompts, assertions
    ├── files/              # optional: input fixtures
    └── scripts/            # optional: deterministic assertion scripts
```

Shared infrastructure lives in `evals/` at the repository root: the runner, this
guide, and the gitignored `runs/` and `reports/` directories. Read
[`evals/README.md`](../../evals/README.md) before running anything.

## Case anatomy

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "my-skill-001",
      "label": "Human-readable name",
      "prompt": "The user request the agent receives.",
      "expected_output": "What a successful run produced, in outcome terms.",
      "expected_skill": "my-skill",
      "files": ["fixture.csv"],
      "routing": { "expect": ["my-skill"], "forbid": ["other-skill"] },
      "assertions": ["file:out.json", "script:check.py", "Output names the top 3."]
    }
  ]
}
```

- `skill_name` must match the directory name.
- `id` must be unique and stable across runs; it is the join key for conditions.
- `prompt` is concrete: include paths, columns, and context. Vague prompts make
  vague evals.
- `expected_output` describes the outcome, not the exact text.
- `expected_skill` is the skill that should be loaded; `null` for negative cases.

See [the eval schema](references/eval-schema.md) for the full field list and a
worked example.

## Assertions

Prefixed forms are graded deterministically in-repo; bare strings need the
optional judge.

| Assertion | Checks |
|-----------|--------|
| `file:<path>` | Path exists under the artifacts dir, `outputs/`, or by filename |
| `regex:<pattern>` | Pattern matches the transcript or outputs |
| `json:<path>.<field>` | JSON field exists (dot path) |
| `script:<name>` | `scripts/<name>` exits 0, receiving the artifacts dir |
| `agentskills` | `agentskills validate` passes on the produced skill |
| *(bare sentence)* | A qualitative property (LLM-judged) |

Write assertions as specific, observable statements. "The bar chart has labeled
axes" is testable; "the output is good" is not. Split a two-part requirement into
two assertions so a half-answer fails.

## Routing checks

Verify the agent *invoked* the right skill with a `routing` block, graded against
the transcript:

```json
"routing": { "expect": ["my-skill"], "forbid": ["other-skill"] }
```

Use `expect` for should-fire cases and `forbid` for negative, near-miss cases. A
skill that produces good output but never triggers is still a failure.

## Capturing a run

The runner grades artifacts; it does not drive an agent.

1. Create a fresh working directory per trial.
2. Run the prompt under the chosen condition (no skill, the skill, or a
   comparator).
3. Save produced files under `outputs/`, the transcript as `transcript.md`, and a
   `metadata.json` with `model`, `harness`, and `skill_revision`.
4. Place them under `evals/runs/<skill>/<case-id>/<condition>/trial-1/`.

Repeat for `trial-2`, `trial-3`, ... when reliability matters. One trial is
enough while developing; widen to 3–5 before trusting a score.

## Running

```
python evals/runner.py --validate
python evals/runner.py --skill my-skill --all-conditions
python evals/runner.py --skill my-skill --compare other-skill
```

`--validate` lints specs and runs in CI. `--compare` grades another skill's
`with_skill` artifacts on the same case ids. Use the
[`skill-evaluation`](../skill-evaluation/SKILL.md) skill to read the report and
decide whether to ship.

## Pitfalls

- **Saturated assertions** pass in both conditions; they do not discriminate.
- **Leakage** — asserting the skill's exact wording tests memory, not behaviour.
- **Single-trial noise** — one pass/fail is not a score.
- **Overfitting** — a case tuned to one prompt may not generalise.
- **Hardcoded paths** — anything machine-specific belongs in an env var.
- **Grading the sentence** — grade the artifact, not the agent's claim it is done.

## Checklist

- `skill_name` matches the directory name.
- Every case has a stable `id`, a concrete `prompt`, and an `expected_output`.
- The case can fail; it is not saturated.
- Assertions are specific and observable.
- `script:` and `files:` references exist.
- Routing is checked for trigger-sensitive skills.
- `python evals/runner.py --validate` passes.
