---
title: Contribute with git
description: Direct git contribution path — fork, branch, skill directory, PR to dev.
---

# Contribute with git

If you use git and GitHub, you can contribute a skill directly without going through the issue form.

## Step 1: Search for existing work

Before creating anything, search open and closed issues and pull requests for related work. Extend an existing skill when appropriate rather than duplicating it.

## Step 2: Create a branch

Target `dev` — `main` is the released branch.

```bash
git checkout -b skill/<name> dev
```

## Step 3: Create the skill directory

Create `skills/<name>/` with at minimum a `SKILL.md`:

```markdown
---
name: <name>
description: State what this skill does and when to use it. Use when ...
---

# Focused task

## Workflow

1. Establish the required inputs, task scope, and evidence available.
2. Perform the task using supplied criteria and documented tools.
3. Check outputs and limitations; ask before filling material gaps.
4. Report what was done, what remains uncertain, and where human review is needed.

## Completion criteria

- State observable conditions for completion.
- Separate format/tool success from domain or scientific validity.

## Limits

- Name assumptions and unsupported claims the skill must not make.
- Route domain decisions to qualified reviewers.
```

The `name` in frontmatter must match the directory name. Do not add a `license` field — the repository-wide MIT license applies.

## Step 4: Add optional resources (only when used)

Create optional folders only when the skill needs them:

- `references/` — supporting procedures, definitions, source material
- `scripts/` — deterministic tools with documented inputs and outputs
- `assets/` — templates and task resources
- `evals/` — evaluation specifications, fixtures, assertion scripts
- `examples/` — illustrative examples
- `models/` — native engineering model files, configurations, fixtures (not ML weights)
- `adapters/` — host-specific instructions or integrations

## Step 5: Validate

Run the repository checks:

```bash
agentskills validate ./skills/<name>
python evals/runner.py --validate
bash .github/workflows/validate-skills.sh
```

Behavior-shaping skill changes require a relevant evaluation specification under `skills/<name>/evals/evals.json`. Documentation-only changes are exempt.

## Step 6: Open a pull request

Open a PR against `dev`. Complete every section of the [pull request template](https://github.com/tomjanus/water-skills/blob/main/.github/PULL_REQUEST_TEMPLATE.md), disclose the model/harness and plugins used (or say the work was done by hand), and provide evidence of complete human review.

A human must review the complete diff before submission. Domain review is required where scientific decisions are involved. No automated pull-request approval or merge is provided.
