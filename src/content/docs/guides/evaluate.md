---
title: Evaluate a skill
description: Evaluation specification, runner boundary, captured runs, pass@k/pass^k, GUI grading.
---

# Evaluate a skill

An evaluation specification describes a task, expected outcome, and checks for a skill-shaped behavior. A captured run records what an agent actually did for that task under a named condition. A specification is a test design, not a result.

## Repository policy

- Behavior-shaping skill changes require a relevant evaluation specification. Documentation-only changes do not require behavioral evals.
- Validate the specification with `python evals/runner.py --validate`.
- Report captured runs, model, agent harness, software versions, conditions, and trial count when those runs were performed. Do not invent or imply results when there are no captures.
- Format validation and eval-spec validation do not establish skill usefulness, engineering correctness, or scientific validity.

## Runner boundary

The repository runner validates evaluation specifications and grades **captured artifacts**. It does not launch an agent, create transcripts, or capture GUI/application state. Capture happens in an external agent harness and is not automated by this repository. Missing artifacts mean there is no behavioral result to interpret.

## Add an evaluation specification

1. Put `evals/evals.json` under the skill directory.
2. Use stable case IDs, concrete prompts, expected outcomes, and checks that can distinguish successful from unsuccessful behavior.
3. Add only required fixtures and scripts under `evals/files/` and `evals/scripts/`.
4. Use deterministic assertions where possible. Bare sentence assertions require the optional judge and are not deterministic.
5. Run `python evals/runner.py --validate` and report its exact output.
6. Run behavioral trials only when captures are available; save them under `evals/runs/` and report conditions and limitations.

## Conditions

The runner grades the same case under several conditions:

| Condition | Meaning |
|---|---|
| `without_skill` | Baseline. No skill loaded. |
| `with_skill` | The skill under test is loaded. |
| `compare:<skill>` | A different skill is loaded, for A/B comparison. |

The report shows each condition's pass rate and the **lift** of `with_skill` over `without_skill`.

## Vocabulary

| Term | Meaning |
|---|---|
| Task | A single test with defined inputs and success criteria |
| Trial | One execution attempt at a task |
| Transcript | The complete trace of outputs, tool calls, and reasoning |
| Outcome | The final state of the environment or exported artifacts |
| pass@k | Probability that at least 1 of _k_ trials succeeds |
| pass^k | Probability that all _k_ trials succeed |

## GUI tasks

For GUI water-engineering software (EPANET, HAMMER, GPS-X), grade application-exported state and reports — not fixed click paths or pixel matches. Reset a clean VM snapshot per trial, record OS/app version/locale/display/licence mode, and check exported state. Screenshots and click traces diagnose failures; they are not the primary correctness criterion.

GUI runs are label-gated (`run-gui-evals`), maintainer-dispatched, or nightly. Never commit proprietary installers, licence keys, or vendor binaries. Redact client/network data from screenshots and transcripts before saving.

## Useful commands

```bash
python evals/runner.py --validate
python evals/runner.py --list
python evals/runner.py --skill <name> --all-conditions
python evals/runner.py --skill <name> --compare <other-name>
```

See [`EVALS.md`](EVALS.md) and [`evals/README.md`](evals/README.md) for the suite schema, artifact layout, and assertion syntax.
