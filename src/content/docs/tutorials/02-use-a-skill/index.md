---
title: Use a skill
description: Lesson 2 — browse skills, read SKILL.md, check inputs and limitations.
---

# 2 · Use a skill

**Audience:** Water engineers and managers who want to apply a skill; agents that load skills.
**Outcome:** You can find a skill, read its `SKILL.md`, check its required software/inputs/units/limitations, and load it into your agent host.
**Duration:** ~10 minutes

## Plain-language path

1. Browse the [`skills/`](https://github.com/tomjanus/water-skills/tree/main/skills) directory.
2. Open a skill's `SKILL.md`. It states:
   - What the skill does and when to use it (frontmatter `description`)
   - The focused task and workflow
   - Required inputs, task scope, and evidence available
   - Completion criteria and limits
   - "Do not use when" conditions
3. Check the skill's required software, inputs, units, and limitations before use.
4. Load the skill using your agent host's documented method for adding a skill directory.
5. Review the result against the task's data, criteria, and applicable engineering requirements.

A skill passes validation only if it is structurally valid — that does not establish calibration, field agreement, or scientific validity. Keep domain decisions with qualified people.

## Operational path

Each skill directory follows this layout:

```text
skills/<name>/
├── SKILL.md              # required: procedure, decision rules, thresholds
├── references/           # optional: deep method notes, software quirks
├── scripts/              # optional: deterministic tools
├── assets/               # optional: templates and task resources
├── evals/                # optional: evals.json, fixtures, scripts
├── examples/             # optional: illustrative inputs/outputs
├── models/               # optional: native engineering model files (not ML weights)
└── adapters/             # optional: host-specific instructions
```

Optional folders are created only when the skill uses them.

Validation commands (from the repository root):

```bash
agentskills validate ./skills/<name>
python evals/runner.py --validate
```

## Self-check

<details>
<summary>Q: Where does a skill's name come from?</summary>
<p>The `name` field in `SKILL.md` frontmatter must match the skill directory name.</p>
</details>

<details>
<summary>Q: Does a passing validation mean the skill is scientifically correct?</summary>
<p>No. Validation checks structure and naming only. Domain correctness requires human review.</p>
</details>

<details>
<summary>Q: Can I use a skill without installing anything?</summary>
<p>The repository does not provide a project-specific installer. You load a skill by pointing your agent host at the skill directory.</p>
</details>

## Next link

[Lesson 3 · Write knowledge, not documentation](../03-write-knowledge-not-docs/)
