---
title: How we know a skill works
description: Lesson 6 — task/trial/outcome vocabulary, pass@k/pass^k, GUI grading. Track B only.
---

# 6 · How we know a skill works

**Audience:** Engineers and agents who want to understand evaluation.
**Outcome:** You can explain the difference between an evaluation specification and a captured run, interpret pass@k/pass^k, and understand how GUI skills are graded.
**Duration:** ~10 minutes

## Plain-language path

An evaluation specification describes a task, expected outcome, and checks. It is a test design — not a result. A captured run records what an agent actually did.

You know a skill works when a paired evaluation shows the same task performed better *with* the skill than *without* it. A case that passes in both conditions proves nothing.

## The evaluation vocabulary

| Term | Meaning |
|---|---|
| Task | A single test with defined inputs and success criteria |
| Trial | One execution attempt at a task |
| Transcript | The complete trace of outputs, tool calls, and reasoning |
| Outcome | The final state of the environment or exported artifacts |
| pass@k | Probability that at least 1 of _k_ trials succeeds |
| pass^k | Probability that all _k_ trials succeed |

## Conditions

The runner grades the same case under several conditions:

| Condition | Meaning |
|---|---|
| `without_skill` | Baseline. No skill loaded. |
| `with_skill` | The skill under test is loaded. |
| `compare:<skill>` | A different skill is loaded, for A/B comparison. |

The report shows each condition's pass rate and the **lift** of `with_skill` over `without_skill`.

## Runner boundary

The repository runner validates evaluation specifications and grades **captured artifacts**. It does not launch an agent, create transcripts, or capture GUI/application state. Capture happens in an external agent harness. Missing artifacts mean there is no behavioral result to interpret.

## GUI tasks

For GUI water-engineering software (EPANET, HAMMER, GPS-X), grade application-exported state and reports — not fixed click paths or pixel matches. Agents may reach valid outcomes through different UI navigation sequences.

Reset a clean VM snapshot per trial, record OS/app version/locale/display/licence mode, and check exported state. Screenshots and click traces diagnose failures; they are not the primary correctness criterion.

GUI runs are label-gated (`run-gui-evals`), maintainer-dispatched, or nightly. Never commit proprietary installers, licence keys, or vendor binaries. Redact client/network data from screenshots and transcripts before saving.

## Operational path

```bash
python evals/runner.py --validate
python evals/runner.py --list
python evals/runner.py --skill <name> --all-conditions
python evals/runner.py --skill <name> --compare <other-name>
```

See [`EVALS.md`](../guides/repository-reference.md) and [`evals/README.md`](../guides/repository-reference.md) for the suite schema, artifact layout, and assertion syntax.

## Self-check

<details>
<summary>Q: Does a passing eval-spec validation mean the skill works?</summary>
<p>No. It only checks the specification is well-formed. Behavioral results require captured runs.</p>
</details>

<details>
<summary>Q: What is pass^k?</summary>
<p>The probability that all _k_ trials succeed — measures consistency required for customer-facing reliability.</p>
</details>

<details>
<summary>Q: Are GUI evals run on every PR?</summary>
<p>No. GUI runs are label-gated, maintainer-dispatched, or nightly — never in ordinary PR CI.</p>
</details>

## Next link

[Lesson 7 · Review and lifecycle](./07-review-and-lifecycle/)
