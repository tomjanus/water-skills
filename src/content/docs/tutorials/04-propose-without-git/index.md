---
title: Propose a skill without git
description: Lesson 4 — issue form, triage, draft PR review. Track A only.
---

# 4 · Propose a skill without git

**Audience:** Water engineers and managers who want to contribute a skill but do not use git.
**Outcome:** You can submit a skill proposal through the issue form and review the generated draft pull request in your browser.
**Duration:** ~10 minutes

## Plain-language path

You do not need git, GitHub, or agent tooling to propose a skill.

### Step 1: Open the issue form

Go to the repository's **Issues** tab, click **New issue**, and choose **Propose a skill**. Two variants exist:

- [`propose-skill.yml`](../guides/repository-reference.md) — structured form with dropdowns and required fields
- [`propose-skill.md`](../guides/repository-reference.md) — Markdown variant with the same fields

### Step 2: Fill in what automation cannot infer

The form asks only for domain knowledge:

- **Domain** — the water-engineering area
- **Problem** — the real task or failure you experienced
- **Prompt** — what you would ask an agent to do
- **Expected output** — what success looks like
- **Inputs** — required data, files, or model inputs
- **Software version** — the engineering software and version you used
- **References** — sources, manuals, or procedures you relied on
- **Optional transcript** — a real session transcript, if you have one

### Step 3: Triage and scaffold

A maintainer triages the issue using labels (`proposal`, `needs-triage`, `needs-info`, `accepted`, `declined`, `scaffolded`, `domain-review`, `stale`). If accepted, the maintainer runs:

```bash
water-skills new --from-issue <number>
```

This creates a feature branch, writes `SKILL.md`, `provenance.yaml`, and `evals/evals.json`, stages and commits the files, and prints instructions for opening the draft pull request through GitHub's web interface.

### Step 4: Review the draft

The draft PR appears in the repository. Review it in your browser — no terminal needed. A maintainer converts it from draft to ready for review and merges it after human and domain review.

## Operational path

The scaffold writes:

- `skills/<name>/SKILL.md` — no per-skill license; repository-wide MIT applies
- `skills/<name>/provenance.yaml` — `method_status: hypothesis`, `review_status: not_reviewed` (incomplete records are visible, not defaulted)
- `skills/<name>/evals/evals.json` — human review placeholder assertion

Issue content is treated as untrusted data: read from a file only, never interpolated into shell commands, never executed. Draft PRs stay in draft; the CLI never auto-approves or marks ready.

## Self-check

<details>
<summary>Q: Do I need to know git to propose a skill?</summary>
<p>No. The issue form handles everything; a maintainer does the git work.</p>
</details>

<details>
<summary>Q: What happens after I submit the form?</summary>
<p>A maintainer triages it. If accepted, they scaffold a draft PR. You review it in your browser.</p>
</details>

<details>
<summary>Q: Can the automation merge my PR without review?</summary>
<p>No. Draft PRs stay in draft. A maintainer converts to ready and merges after human and domain review.</p>
</details>

## Next link

Track A ends here. You can propose a skill through the issue form. Track B continues with [Lesson 5 · Propose a skill with git](./05-propose-with-git/).
