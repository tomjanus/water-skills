# Issue triage — labels, states, and acceptance criteria

This document defines the label set, triage state transitions, and
acceptance criteria for skill proposals submitted through the authoring
runway issue forms (`propose-skill.yml`, `propose-skill.md`).

## Labels

| Label | Meaning | Who applies it | Next action |
|---|---|---|---|
| `proposal` | New skill proposal. | Issue form | Duplicate search and scope check. |
| `needs-triage` | Awaiting maintainer triage. | Issue form | Maintainer reviews and applies `accepted`, `needs-info`, or `declined`. |
| `needs-info` | Problem, prompt, or expected result missing or incomplete. | Maintainer or bot | Ask one consolidated question; do not drip-feed. |
| `accepted` | Real problem, in scope, not a duplicate, reviewer available. | Maintainer | Scaffold the draft PR. |
| `declined` | Out of scope, duplicate, or not a real problem. | Maintainer | Explain which criterion failed and link to scope policy. |
| `scaffolded` | Draft PR exists. | Bot | Contributor fills domain gaps; CI runs. |
| `run-evals` | Request paid behavioural runs. | Maintainer | Label-gated workflow with a token cap. |
| `run-gui-evals` | Request a licensed GUI or VM run. | Maintainer | Controlled runner, clean snapshot, state export, no installer in git. |
| `domain-review` | Ready for a named expert. | Maintainer | Review units, assumptions, method, citations, eval. |
| `stale` | No response for 30 days. | Bot | One reminder, then close with a reopen path. |

Labels `run-evals` and `run-gui-evals` are reserved for post-pilot stages;
they are defined here but not acted on until Stage 2c or later.

## Triage states

The lifecycle of a proposal issue:

1. **Submitted** — Contributor opens `propose-skill.yml` or `propose-skill.md`.
   - Labels applied automatically: `proposal`, `needs-triage`.
2. **Triage** — Maintainer reviews within one business day.
   - If incomplete: apply `needs-info`, ask one consolidated question.
   - If out of scope or duplicate: apply `declined`, explain which criterion failed.
   - If accepted: apply `accepted`, assign a named domain reviewer.
3. **Scaffolded** — Draft PR created from the accepted proposal.
   - Label `scaffolded` applied by the automation or maintainer.
4. **Review** — Contributor fills domain gaps in the draft PR; CI runs.
   - Label `domain-review` applied when ready for expert review.
5. **Merged** or **closed** — Maintainer merges after domain review, or closes
   if the skill cannot be brought to publication quality.

## Acceptance test

A proposal is **accepted** only when all five criteria are true:

1. The problem is real and specific — it describes a task the contributor
   actually encountered, not a hypothetical improvement.
2. It is within water-engineering scope — hydraulic and network modelling,
   water-resource planning, water quality, transient analysis, leakage,
   calibration, or scientific communication for engineering work.
3. No existing skill covers it — duplicate search found nothing equivalent.
4. The expected result is checkable — a reviewer can verify whether the
   agent's output is correct.
5. A named domain reviewer is available — someone who can judge units,
   assumptions, method validity, and citations.

If any criterion is false, say which one and stop. Do not accept provisionally.

## Plain-language CI feedback

Every CI failure posted to a draft PR must answer four questions, in this order:

1. **What failed:** the file and the rule, in plain words.
2. **Why it matters:** what a user would experience if it shipped.
3. **How to fix it:** the exact edit, with a link to the relevant line.
4. **What to do next:** one action, not a menu.

Rules: no stack traces, no unexplained rule codes, no more than three failures per comment, and never ask the contributor to run anything locally.
