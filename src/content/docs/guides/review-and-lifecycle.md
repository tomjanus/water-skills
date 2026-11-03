---
title: Review & lifecycle
description: Pull request review process, human and domain review, review status labels, merge policy.
---

# Review & lifecycle

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

Skill directories may be in one of several states: `publish`, `finish`, `archive`, `duplicate`, or `unknown`. These are maintainer decisions applied individually — no skill is archived, renamed, or published without explicit approval.

Generated catalogs (planned) will reflect review status, provenance, and compatibility from canonical source data — not hand-maintained lists.
