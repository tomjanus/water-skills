---
title: Propose a skill with git
description: Lesson 5 — fork, branch, SKILL.md, validation, PR to dev. Track B only.
---

# 5 · Propose a skill with git

**Audience:** Engineers and agents comfortable with git and GitHub.
**Outcome:** You can fork, create a branch, author a `SKILL.md`, validate it, and open a pull request against `dev`.
**Duration:** ~10 minutes

## Plain-language path

If you use git, you can contribute a skill directly without going through the issue form.

1. Search open and closed issues and pull requests for related work. Extend an existing skill when appropriate.
2. Create a branch from `dev` (not `main`, which is the released branch):

   ```bash
   git checkout -b skill/<name> dev
   ```

3. Create `skills/<name>/SKILL.md` (see [`SKILL_TEMPLATE.md`](https://github.com/tomjanus/water-skills/blob/main/contributing/SKILL_TEMPLATE.md)).
4. Add optional folders (`references/`, `scripts/`, `evals/`, etc.) only when the skill uses them.
5. Validate:

   ```bash
   agentskills validate ./skills/<name>
   python evals/runner.py --validate
   ```

6. Open a PR against `dev`. Complete the PR template, disclose the model/harness used, and provide evidence of human review.

A human reviews the complete diff before submission. Domain review is required where scientific decisions are involved.

## Operational path

The `name` in `SKILL.md` frontmatter must match the directory name. Do not add a `license` field — the repository-wide MIT license applies.

Behavior-shaping skill changes require a relevant evaluation specification under `skills/<name>/evals/evals.json`. Documentation-only changes are exempt.

Run all repository checks:

```bash
agentskills validate ./skills/<name>
python evals/runner.py --validate
bash .github/workflows/validate-skills.sh
```

## Self-check

<details>
<summary>Q: Which branch do I target?</summary>
<p>`dev`. `main` is the released branch.</p>
</details>

<details>
<summary>Q: Do I need an eval for every skill?</summary>
<p>Behavior-shaping changes require an eval specification. Documentation-only changes are exempt.</p>
</details>

<details>
<summary>Q: Can I archive or rename a skill myself?</summary>
<p>No. Archive, rename, and publish decisions are maintainer decisions applied individually.</p>
</details>

## Next link

[Lesson 6 · How we know a skill works](../06-how-we-know-skill-works/)
