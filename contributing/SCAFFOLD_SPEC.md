# Scaffold output specification

This document specifies what `water-skills new --from-issue <number>` produces,
in both `--dry-run` (read-only) and write-enabled modes. It is a Stage 2a
design document; no implementation code exists yet.

## Command interface

```
water-skills new --from-issue <number> --dry-run
water-skills new --from-issue <number>
```

- `--dry-run` prints the planned file list and unresolved questions without
  changing the tree. It is the safe default; write mode is enabled only after
  dry-run output has been reviewed.
- Write mode creates a branch `skill/<number>-<slug>` and a skill directory.

## Scaffold directory tree

```
skills/<skill-name>/
├── SKILL.md
├── provenance.yaml
├── evals/
│   ├── evals.json          # one placeholder case, clearly marked
│   ├── files/              # only when the issue supplies a fixture
│   ├── scripts/            # only when a deterministic check is requested
│   ├── rubrics/            # only when a judgement needs a model grader
│   └── environments/       # only for GUI or licensed-software tasks
├── models/                 # only when the issue supplies a native model file
├── examples/               # only when the issue supplies a worked example
├── adapters/               # only for a named host integration
└── references/             # only when the issue cites material to consult
```

Rules:
- Create one optional folder only when the proposal supplies content for it,
  or the acceptance test requires it. An empty folder is a question, not a
  scaffold. Do not create every optional folder by default.
- The scaffold must never copy an installer, licence key, proprietary model,
  or unredacted capture into the repository.

## SKILL.md template

The scaffold renders a `SKILL.md` with placeholders the contributor can edit
in the GitHub web editor:

```markdown
---
name: <skill-name>
description: <what it does and when to use it>
license: Apache-2.0
metadata:
  author: <contributor>
  version: "0.1.0"
---

# <Title>

<One paragraph: the task this skill enables.>

## When to use this skill

<The specific triggers and the boundary.>

## Procedure

1. <Step grounded in the contributor's workflow.>
2. <Step.>
3. <Step.>

## Checks

- <Units, assumptions, and physical plausibility checks.>
- <What to report when a check fails.>

## References

- <Only references supplied or verified by the contributor.>
```

Note: `license` and `metadata.author` are placeholders from the authoring
runway design. The repository-wide license is MIT (Stage 1), and per-skill
license metadata is not used in published skills. These fields are scaffold
placeholders and must be reconciled before the skill is accepted for
publication.

## provenance.yaml

Generated with explicit nulls so an incomplete record is visible rather than
silently defaulted:

```yaml
schema_version: 1
title: "<Title>"
summary: "<One sentence for the catalog>"
version: 0.1.0
domain:
  - <taxonomy value>
software: []
authors:
  - name: "<Contributor>"
    role: author
method_type: null          # established_method | adapted_method | novel_method
references: []
reviewers: []
review_status: unreviewed
last_reviewed: null
supersedes: []
superseded_by: null
aliases: []
ai_assistance: []
```

## evals/evals.json

The first eval case is a stub with the contributor's prompt and expected
output, not a fabricated result:

```json
{
  "schema_version": 1,
  "skill": "<skill-name>",
  "cases": [
    {
      "id": "0001-<case-slug>",
      "prompt": "<contributor prompt>",
      "conditions": ["without_skill", "with_skill"],
      "assertions": [
        {
          "type": "human_review",
          "description": "<what a correct result must contain>"
        }
      ]
    }
  ]
}
```

Assertions become deterministic only when the contributor or reviewer can
state a checkable condition. `human_review` is honest; a fabricated automated
assertion is worse than an explicit manual one.

## Draft PR body

The scaffold opens a draft PR whose body contains:

1. The contributor's problem statement (from the issue form).
2. The generated file list.
3. The questions the bot could not answer (explicit, not guessed).
4. A short "what happens next" section.

The PR is always a draft. The bot never marks it ready for review.

## No invented engineering

The scaffold may render placeholders, move the contributor's words into the
right fields, derive a slug, and create an empty eval case. It must **not**
invent a procedure, a threshold, a citation, a software version, or an
expected numeric result. Missing domain content becomes an explicit question
in the PR, not plausible text.

## Fail-safe

If the bot fails, the issue must remain a complete, useful record. A
maintainer can run `water-skills new --from-issue <number>` locally and open
the draft PR by hand. The contributor is never asked to debug the bot.
