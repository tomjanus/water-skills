---
title: Work with agents in this repository
description: Lesson 8 — disclose model/harness, agent templates, one canonical source. Track B only.
---

# 8 · Work with agents in this repository

**Audience:** Agents and engineers using AI tooling to contribute.
**Outcome:** You can disclose model/harness usage, apply agent templates, and follow the one-canonical-source rule.
**Duration:** ~10 minutes

## Plain-language path

Agents can propose and report; people retain scope, science, archive, review, merge, and release authority. Every agent contribution must disclose the model, agent harness, versions, and installed plugins — or state that the work was done by hand.

A human must review the complete diff before submission. The contributor remains responsible for factual claims.

## Disclose model and harness

When preparing a contribution with an agent, state:

- Model name and version
- Agent harness name and version (e.g., Claude Code, OpenCode)
- Installed plugins
- Or: "This work was done by hand"

## Agent templates

The [`contributing/AGENT_TEMPLATE.md`](../guides/repository-reference.md) defines the subagent contract:

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

Agents have bounded permissions — `edit: ask`, `bash: ask`, `task: deny` by default. Stop before destructive Git actions, licensing decisions, domain approval, or publication. Never invent scientific results, authorship, reviewer approval, or validation evidence.

## One canonical source

Skill lists, install commands, versions, evidence badges, and review status come from canonical source data — not hand-maintained tables that drift from reality. Link to [`GLOSSARY.md`](../guides/repository-reference.md) rather than copying definitions.

## Operational path

1. Read [`CONTRIBUTING.md`](../guides/repository-reference.md) and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).
2. Follow [`contributing/CONTRIBUTION_CHECKLIST.md`](../guides/repository-reference.md).
3. Disclose model/harness in the PR.
4. Validate changed skills and eval specs.
5. Request human and domain review before submission.

## Self-check

<details>
<summary>Q: Can an agent merge its own PR?</summary>
<p>No. People retain merge and release authority.</p>
</details>

<details>
<summary>Q: What must an agent disclose?</summary>
<p>Model name/version, agent harness name/version, installed plugins — or "done by hand".</p>
</details>

<details>
<summary>Q: Where do agent permission rules live?</summary>
<p>`contributing/AGENT_TEMPLATE.md` — `edit: ask`, `bash: ask`, `task: deny`.</p>
</details>

## Next link

You have completed the curriculum. Return to the [tutorial index](./) or read the [repository reference](../guides/repository-reference/).
