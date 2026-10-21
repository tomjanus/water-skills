# Skill evals

An eval is a **failing test for one observable behaviour**: a realistic prompt,
a captured run, a small set of checks, and a score you can compare over time.

Evals let you answer questions that "it works" cannot:

- Does the skill help, compared to not loading it?
- Which of two skills is better on the same task?
- Did a wording change improve or regress behaviour?
- Did the agent actually invoke the skill?

Evals are **encouraged, not mandatory**. Add them when a skill has behaviour
worth protecting, and when you have a real failure or a real decision to make.

## Test-driven design pattern

Follow the same loop you would for code. Skills are code that shapes agent
behaviour, so test them the same way.

1. **RED** — Before writing or changing a skill, write a case that fails
   against the current behaviour. Run it and record the baseline score. A case
   that cannot fail proves nothing.
2. **GREEN** — Make the smallest skill change that makes the case pass. Keep the
   skill and its eval in sync.
3. **REGRESSION** — Every real failure you observe in a session becomes a case.
   A bug found once and not encoded will be found again.
4. **REVIEW** — Re-run on a second, holdout prompt set to check you did not
   overfit the skill to the wording of one case.

A case that is always green in both conditions is **not discriminating** — it
does not measure the skill. Either sharpen it or drop it.

## Layout

Cases live beside the skill they test:

```
skills/<name>/
├── SKILL.md
└── evals/
    ├── evals.json          # required: cases, prompts, assertions
    ├── files/              # optional: input fixtures
    └── scripts/            # optional: deterministic assertion scripts
```

Shared infrastructure lives here, in `evals/`:

```
evals/
├── README.md               # this file
├── runner.py               # discover, grade, report
├── runs/                   # gitignored: captured runs
└── reports/                # gitignored: generated reports
```

A captured run is stored as:

```
evals/runs/<skill>/<case-id>/<condition>/
├── trial-1/                # trials are optional; one dir is enough
│   ├── outputs/            # artifacts the agent produced
│   ├── transcript.md       # the captured transcript
│   └── metadata.json       # model, harness, skill hash, timestamp
└── trial-2/                # repeat for reliability
```

`metadata.json` is free-form, but record at least `model`, `harness`, and a
short `skill_revision` so runs remain comparable over time.

## Conditions

The runner grades the same case under several conditions:

| Condition | Meaning |
|-----------|---------|
| `without_skill` | Baseline. No skill loaded. |
| `with_skill` | The skill under test is loaded. |
| `compare:<skill>` | A different skill is loaded, for A/B comparison. |

The report shows each condition's pass rate and the **lift** of `with_skill`
over `without_skill`.

## Assertion types

Assertions are strings in `evals.json`. Prefixed forms are graded
deterministically in-repo; bare strings need the optional judge.

| Assertion | Checks | Needs judge |
|-----------|--------|-------------|
| `file:<path>` | `<path>` exists under the artifacts dir (or under `outputs/`, or by filename anywhere) | no |
| `regex:<pattern>` | Pattern matches the transcript or outputs | no |
| `json:<path>.<field>` | JSON field exists (dot path) | no |
| `script:<name>` | `scripts/<name>` exits 0 (receives the artifacts dir) | no |
| `agentskills` | `agentskills validate` passes on the produced skill | no |
| *(bare sentence)* | A qualitative property | yes |

Write assertions as specific, observable statements, not vague ones. Prefer
"the output contains a YAML block with an `id` field" over "the output is good".
Split a two-part requirement into two assertions so a half-answer fails.

## Routing checks

To verify the agent *invoked* the right skill, add a `routing` block. It is
graded against the transcript, not the output:

```json
"routing": {
  "expect": ["skill-writing"],
  "forbid": ["skill-eval-writing"]
}
```

Use `expect` for should-fire cases and `forbid` for negative (near-miss)
cases. A skill that produces good output but never triggers is still a failure.

## Running evals

```
python evals/runner.py --list
python evals/runner.py --validate
python evals/runner.py --skill skill-writing --all-conditions
python evals/runner.py --skill skill-writing --compare skill-eval-writing
python evals/runner.py --all --write-report
```

`--validate` lints every eval spec (JSON parses, `skill_name` matches the
directory, required fields and referenced scripts/fixtures exist). It runs in CI
and never touches the network.

`--all-conditions` grades baseline and skill; add `--compare <skill>` to grade a
second skill's `with_skill` artifacts on the same case ids. To compare two
skills, run the target skill's cases with the comparator loaded and save them to
`evals/runs/<comparator>/<case-id>/with_skill/`.

### Optional LLM judge

Deterministic assertions cover outcome, process, and style. Use bare-string
assertions only for properties a regex genuinely cannot reach. Enable the judge
with `--judge` and point `EVAL_JUDGE_CMD` at any command that reads a JSON
request on stdin and prints a JSON verdict on the last line of stdout:

```json
{"assertion": "...", "expected_output": "...", "transcript": "..."}
```

```json
{"pass": true, "reason": "..."}
```

The judge is never required, never bundled, and never runs in CI.

## Capturing a run

The runner grades artifacts; it does not drive an agent. Capture runs in
whatever harness you use:

1. Create a fresh working directory per trial. Never share state between trials.
2. Run the case prompt with the chosen condition (no skill, the skill, or the
   comparator).
3. Save the produced files under `outputs/`, the transcript as `transcript.md`,
   and a `metadata.json`.
4. Place them under `evals/runs/<skill>/<case-id>/<condition>/trial-1/`.

Repeat for `trial-2`, `trial-3`, ... when reliability matters. One trial is
enough while developing the harness; widen to 3–5 trials before trusting a
score. `pass@k` (any trial passes) is the default reading; a high-variance case
is a signal to tighten the skill, not to average it away.

## Pitfalls

- **Saturated assertions** — pass in both conditions; they do not discriminate.
- **Leakage** — asserting the skill's exact wording tests memory, not behaviour.
- **Single-trial noise** — one pass/fail is not a score.
- **Overfitting** — a case tuned to one prompt may not generalise; hold out prompts.
- **Hardcoded paths** — anything machine-specific belongs in an env var.
- **Grading the sentence** — grade the artifact (files, commands, structure),
  not the agent's claim that it is done.

## Writing an eval

Use the [`skill-eval-writing`](../skills/skill-eval-writing/SKILL.md) skill to
author and iterate cases. Use the
[`skill-evaluation`](../skills/skill-evaluation/SKILL.md) skill to run a suite,
read the report, and decide whether to ship.
