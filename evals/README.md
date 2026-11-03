# Skill evals

An eval is a **failing test for one observable behaviour**: a realistic prompt,
a captured run, a small set of checks, and a score you can compare over time.

Evals let you answer questions that "it works" cannot:

- Does the skill help, compared to not loading it?
- Which of two skills is better on the same task?
- Did a wording change improve or regress behaviour?
- Did the agent actually invoke the skill?

Add a relevant eval specification for behavior-shaping skill changes. Docs-only
changes do not require behavioral evals. A specification describes what to test;
it is not evidence that the behavior passed.

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
├── schema.py               # additive V1 run metadata validation
├── capture/                 # CLI and guided manual capture adapters
├── runs/                   # gitignored: captured runs
└── reports/                # gitignored: generated reports
```

A captured run is stored as:

```
evals/runs/<skill>/<case-id>/<condition>/
├── trial-1/                # trials are optional; one dir is enough
│   ├── outputs/            # artifacts the task produced
│   ├── state/               # optional exported application/environment state
│   ├── screenshots/         # optional, redacted diagnostic images
│   ├── actions.jsonl        # optional action trace
│   ├── transcript.md        # readable captured transcript
│   └── metadata.json        # run identity, environment, timing, cost
└── trial-2/                # repeat for reliability
```

`evals/schema.py` defines the additive V1 `metadata.json` contract. New captures
record `schema_version`, `task_id`, `condition`, `trial`, `model`, and
`timestamp`; optional fields include agent/evaluation harness names and
versions, `skill_revision`, `software_versions`, `os_info`, `licence_mode`,
`cost`, and `time_seconds`.
Unknown fields remain allowed for forward compatibility. The runner uses
available metadata to enrich reports; missing or malformed metadata does not
make an otherwise gradeable capture fail.

Both adapters create the run directory, `outputs/`, `state/`, and
`metadata.json`. The CLI adapter also writes `transcript.md` from stdout/stderr.
The manual adapter writes a guide; a human adds the transcript and reviewed
artifacts. Screenshots and `actions.jsonl` are optional and are not produced by
these adapters. Keep `evals/runs/` out of git except for small, synthetic,
reviewed fixtures.

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
| `json:<path>:<field>` | JSON field exists (dot-separated object keys and zero-based array indexes) | no |
| `script:<name>` | `scripts/<name>` exits 0 (receives the artifacts dir) | no |
| `agentskills` | `agentskills validate` passes on the produced skill | no |
| *(bare sentence)* | A qualitative property | yes |

Write assertions as specific, observable statements, not vague ones. Prefer
"the output contains a YAML block with an `id` field" over "the output is good".
Split a two-part requirement into two assertions so a half-answer fails.

## Textual routing checks

Add a `routing` block to check whether expected skill IDs are mentioned in the
captured text artifacts:

```json
"routing": {
  "expect": ["skill-writing"],
  "forbid": ["eval-writing"]
}
```

Use `expect` for should-fire cases and `forbid` for negative (near-miss) cases.
The current runner searches recognized text artifacts, including transcripts
and output files. This is a text-mention check, not proof that an agent host
loaded or invoked the skill. Use host-provided invocation metadata when actual
load evidence is needed.

## Running evals

```
python evals/runner.py --list
python evals/runner.py --validate
python evals/runner.py --skill skill-writing --all-conditions
python evals/runner.py --skill skill-writing --compare eval-writing
python evals/runner.py --all --write-report
```

`--validate` lints every eval spec (JSON parses, `skill_name` matches the
directory, required fields and referenced scripts/fixtures exist). It runs in CI
and never touches the network.

`--validate` checks specifications and referenced scripts/fixtures; it does not
launch an agent or grade behavior. `--all-conditions` grades captured baseline
and skill artifacts; add `--compare <skill>` to grade a second skill's
`with_skill` artifacts on the same case ids. To compare two
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

The runner grades artifacts; it does not launch an agent. The CLI adapter runs
an explicitly supplied command without a shell and captures its output. The
manual adapter prepares a directory and guide for a human-run task. Neither
adapter drives an agent harness, captures an API session, or operates GUI
software.

For each trial, use an isolated directory and the corresponding condition
(`without_skill`, `with_skill`, or a comparator). Save produced files under
`outputs/`, exported state under `state/`, a readable transcript, and run
metadata. Never share mutable state between trials.

Repeat for `trial-2`, `trial-3`, ... when reliability matters. One trial is
enough while developing the harness; widen to 3–5 trials before trusting a
score. `pass@k` (any trial passes) is the default reading. Reports include the
population variance of binary pass/fail outcomes as a descriptive statistic;
condition-level variance pools across cases and is not an estimate of model
variance. Review per-case results and transcripts before drawing conclusions.

## GUI evaluation status: planned

GUI evaluation is **not currently available**. No approved GUI VM, software
licence, or independently checkable application-export path has been confirmed,
and no GUI evaluation has been run. Keep GUI support marked planned until those
requirements are approved and demonstrated.

An eventual GUI trial requires a clean VM snapshot per trial and metadata for
OS, application version, locale, display configuration, and licence mode. Grade
exported application state and reports; screenshots and action traces are
diagnostic only, not correctness evidence. Redact client/network information.
Do not commit installers, licence keys, proprietary binaries, confidential
models, or unredacted captures. GUI evaluations must not run in ordinary PR CI;
if introduced later, use a maintainer-dispatched or explicitly gated workflow
with resource caps.

## Pitfalls

- **Saturated assertions** — pass in both conditions; they do not discriminate.
- **Leakage** — asserting the skill's exact wording tests memory, not behaviour.
- **Single-trial noise** — one pass/fail is not a score.
- **Overfitting** — a case tuned to one prompt may not generalise; hold out prompts.
- **Hardcoded paths** — anything machine-specific belongs in an env var.
- **Grading the sentence** — grade the artifact (files, commands, structure),
  not the agent's claim that it is done.

## Writing an eval

Use the [`eval-writing`](../skills/eval-writing/SKILL.md) skill to
author and iterate cases. Use the
[`skill-evaluation`](../skills/skill-evaluation/SKILL.md) skill to run a suite,
read the report, and decide whether to ship.
