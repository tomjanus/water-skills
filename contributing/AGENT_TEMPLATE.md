<!-- Template for a narrowly scoped repository subagent. This does not replace
     repository-wide agent instructions or establish repository-wide authority. -->

```yaml
---
description: State the task and when to use this agent.
mode: subagent
model: ""
permission:
  edit: ask
  bash: ask
  task: deny
---
```

# Purpose

Describe one bounded task and its owner.

## Inputs

- Required files, user decisions, and evidence.
- Assumptions that must be verified before action.

## Procedure

1. Read the assigned sources and current working-tree state.
2. Perform only the named task.
3. Validate the result with the specified checks.
4. Report changed paths, exact commands/results, limitations, and unresolved questions.

## Permissions and stop conditions

- List files the agent may edit; treat all other files as read-only.
- State whether network access, package installation, and external tools are allowed.
- Stop before destructive Git actions, licensing decisions, domain approval, or publication.
- Never invent scientific results, authorship, reviewer approval, or validation evidence.
