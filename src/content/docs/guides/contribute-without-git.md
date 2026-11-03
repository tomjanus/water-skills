---
title: Contribute without git
description: Propose a skill through the issue form — no terminal, no git, no agent required.
---

# Contribute without git

You do not need git, GitHub, or agent tooling to propose a skill. Use the **Propose a skill** issue form, and a maintainer scaffolds a draft pull request for you.

## Step 1: Open the issue form

Go to the repository's **Issues** tab, click **New issue**, and choose **Propose a skill**. The form is available in two variants:

- [`propose-skill.yml`](https://github.com/lepton/water-skills/tree/main/.github/ISSUE_TEMPLATE/propose-skill.yml) — structured form with dropdowns and required fields
- [`propose-skill.md`](https://github.com/lepton/water-skills/tree/main/.github/ISSUE_TEMPLATE/propose-skill.md) — Markdown variant with the same fields

## Step 2: Fill in what automation cannot infer

The form asks only for domain knowledge:

- **Domain** — the water-engineering area (e.g., hydraulic modelling, water quality, transient analysis)
- **Problem** — the real task or failure you experienced
- **Prompt** — what you would ask an agent to do
- **Expected output** — what success looks like
- **Inputs** — required data, files, or model inputs
- **Software version** — the engineering software and version you used
- **References** — sources, manuals, or procedures you relied on
- **Optional transcript** — a real session transcript, if you have one

## Step 3: Triage and scaffold

A maintainer triages the issue using labels (`proposal`, `needs-triage`, `needs-info`, `accepted`, `declined`, `scaffolded`, `domain-review`, `stale`). If accepted, the maintainer runs:

```bash
water-skills new --from-issue <number>
```

This creates a feature branch, writes `SKILL.md`, `provenance.yaml`, and `evals/evals.json`, stages and commits the files, and prints instructions for opening the draft pull request through GitHub's web interface.

## Step 4: Review the draft

The draft PR appears in the repository. You can review it in your browser — no terminal needed. A maintainer converts it from draft to ready for review and merges it after human and domain review.
