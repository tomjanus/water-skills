---
title: Review and lifecycle
description: Lesson 7 — PR template, human and domain review, review status labels, merge policy. Track B only.
---

# 7 · Review and lifecycle

**Audience:** Engineers, agents, and reviewers who evaluate contributions.
**Outcome:** You can explain the pull request process, human and domain review requirements, review status labels, and the merge policy.
**Duration:** ~10 minutes

## Plain-language path

Every pull request is reviewed by a human before submission. Domain review is required where scientific decisions are involved. No automated pull-request approval or merge is provided.

## Pull request process

1. Search open and closed issues and pull requests for related work. Extend an existing skill when appropriate.
2. State the specific problem, the failed or missing behavior, and who it affected. Describe alternatives considered.
3. Keep a pull request to one related change. Ask before changing a public skill name or path.
4. Target `dev` for active work. `main` is the released branch.
5. Complete every applicable section of the PR template, disclose the model/harness and plugins used (or say the work was done by hand), and provide evidence of complete human review.
6. If a change shapes agent behavior, add a relevant evaluation specification and validate it. Report captured behavioral runs when available; if they were not run, state that plainly. Documentation-only changes do not require behavioral evals.
7. Do not claim that a skill, model, or scientific method is validated unless the stated validation was actually performed.

## Human and domain review

A human must review the complete diff before submission. The contributor remains responsible for factual claims and must route scientific or engineering decisions to qualified domain reviewers.

## Review status

Provenance records carry a `review_status` field:

- `not_reviewed` — no review has occurred
- `under_review` — review is in progress
- `reviewed` — a named domain reviewer has reviewed the record

A `reviewed` record requires a `reviewers` entry. Do not populate reviewer or evidence fields without evidence.

## Lifecycle

Skill directories may be in states: `publish`, `finish`, `archive`, `duplicate`, or `unknown`. These are maintainer decisions applied individually — no skill is archived, renamed, or published without explicit approval. Record the state in `provenance.yaml` as `status`; the catalog reflects it.

The generated catalog reads `SKILL.md`, `provenance.yaml`, and eval suite metadata. It shows missing provenance as `not_recorded` and lists review dates from `last_reviewed` and `review_interval_days`. CI regenerates it and fails if the checked-in outputs differ. Run `python scripts/check_staleness.py` to see reviews that are due or have no recorded date.

## Operational path

Before opening a PR:

```bash
agentskills validate ./skills/<name>
python evals/runner.py --validate
bash .github/workflows/validate-skills.sh
```

Complete the [pull request template](.github/PULL_REQUEST_TEMPLATE.md), including model/harness disclosure and any applicable eval evidence.

## Self-check

<details>
<summary>Q: Who merges a pull request?</summary>
<p>A maintainer, after human and domain review. No automated merge.</p>
</details>

<details>
<summary>Q: What does `review_status: reviewed` require?</summary>
<p>A `reviewers` entry naming the domain reviewer.</p>
</details>

<details>
<summary>Q: Can I claim a skill is validated?</summary>
<p>Only if the stated validation was actually performed and reported.</p>
</details>

## Next link

[Lesson 8 · Work with agents in this repository](./08-work-with-agents/)
