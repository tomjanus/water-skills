---
description: Scaffold agent – runs water-skills new and outputs draft-PR instructions.
mode: subagent
model: ""
permission:
  edit: ask
  bash: ask
  task: deny
---

# Scaffold agent

## Purpose

Run `water-skills new --from-issue <number>` (or the equivalent write mode) and produce the exact branch name, file list, and draft PR instructions that a contributor can review in the GitHub web UI. Never open a PR, never merge, never push to `main`.

## Inputs

- Issue number `<number>` from the accepted proposal.
- `water-skills new` command availability (read PATH).
- Current `git status` (read-only, to verify no unexpected modifications).
- `contributing/AGENT_TEMPLATE.md` permission model.

## Procedure

1. **Execute** `water-skills new --from-issue <number>` and capture the full stdout/stderr.
2. **Parse** the output to extract:
   - Feature branch name (`skill/<number>-<slug>`).
   - List of created/updated files (`SKILL.md`, `provenance.yaml`, `evals/evals.json`, any references/metadata).
   - Any "unresolved questions" the command printed.
3. **Summarise** in a structured format:
   - Branch name.
   - Files created (path + brief description).
   - Unresolved questions (verbatim if short, summarized if long).
4. **Post a comment** on the PR (or as a GitHub issue) with the summary. Include the exact command and its output so a maintainer can reproduce. Stop – do not proceed to any write operation.

## Stop conditions

- If `water-skills new` exits non‑zero, report the error message and stop; do not fabricate a successful result.
- If the issue number does not correspond to an `accepted` proposal, report "scaffold agent: issue <number> not accepted; cannot scaffold" and stop.
- If the agent encounters an unexpected error, report "scaffold agent encountered an error: <error>" and stop.

## Report format example

```
## Scaffold output

- **Branch**: `skill/42-new-epanet-transient`
- **Files created**:
  - `skills/epanet-validation/SKILL.md`
  - `skills/epanet-validation/provenance.yaml`
  - `skills/epanet-validation/evals/evals.json`
  - `skills/epanet-validation/references/epanet-manual.pdf`
- **Unresolved questions**:
  - "Please verify the EPANET model boundary conditions on page 12."
  - "Confirm the required software version is 10.5 (not 10.4)."

_Commands run:_
```
water-skills new --from-issue 42
```
```