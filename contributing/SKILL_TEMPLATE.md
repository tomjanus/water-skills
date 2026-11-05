# Skill template

Start with one task the skill enables. Keep `SKILL.md` procedural, cite sources
for non-obvious domain claims, and put longer reference material in a resource
folder only when it is needed.

```markdown
---
name: replace-with-directory-name
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

Before submitting, match `name` to the skill directory, run
`agentskills validate ./skills/<name>`, and add an eval specification for
behavior-shaping changes. Do not add a `license` field; the repository-wide
license is in `LICENSE`.
