---
title: Write knowledge, not documentation
description: Lesson 3 — knowledge-delta test, delete test, layered structure, method status labels.
---

# 3 · Write knowledge, not documentation

**Audience:** Skill authors — water engineers and agents writing or reviewing skills.
**Outcome:** You can apply the knowledge-delta test, delete test, and layered structure to write a terse, expert-level skill.
**Duration:** ~10 minutes

## Plain-language path

A skill is not a tutorial, a vendor manual, or generic background. It transfers the expert judgement a capable model lacks: thresholds, failure signatures, unit traps, checks, and limits.

### One test: the knowledge delta

Before writing or accepting a skill, answer:

> **What would a capable model get wrong without this skill?**

If you cannot name one thing, the skill is not justified. If you can, that gap is the first sentence of the skill and the first eval case.

| Not a knowledge delta | A knowledge delta |
|---|---|
| "Explain what EPANET is." | "Reject a calibration result when mass-balance error exceeds the project tolerance, even if the solver reports convergence." |
| "List the steps of calibration." | "Report the largest residual and the node or link where it occurs." |

### Terse: the delete test

Read every sentence and ask: *if I delete this, does the agent's output change?* If not, delete it.

| Weak sentence | Terse replacement |
|---|---|
| "EPANET is a widely used hydraulic modelling package developed by the US EPA." | Delete it. Start with the check or decision the skill exists for. |
| "It is important to carefully validate your results." | "Reject the run if mass-balance error exceeds the project tolerance; report the largest residual." |
| "For more information, see the EPANET manual." | "For demand-pattern options, read `references/epanet-demand.md` before choosing a pattern." |

### Layered: progressive disclosure

Load depth only when the task needs it:

| Layer | What belongs there | What must not |
|---|---|---|
| Frontmatter | Name and routing description | A summary of the whole method |
| `SKILL.md` | Procedure, decision rules, thresholds, checks, failure modes | Generic definitions, long background, copied manual text |
| `references/` | Deep method notes, diagnostic tables, software quirks | Content the procedure never points to |
| `scripts/` | Deterministic parsing, unit checks, report generation | Hidden domain judgement that should be reviewed |
| `evals/` | A case that fails without the skill and passes with it | An assertion that passes in both conditions |

### Label the epistemic status

Say whether the method is `established`, `adapted`, `heuristic`, or `hypothesis`. A heuristic is acceptable when named as one and tested. An unlabelled guess presented as established method is not.

## Operational path

The [`SKILL_TEMPLATE.md`](https://github.com/tomjanus/water-skills/blob/main/contributing/SKILL_TEMPLATE.md) shows the required structure:

```markdown
---
name: <directory-name>
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

Before submitting:
- Match `name` to the skill directory
- Run `agentskills validate ./skills/<name>`
- Add an eval specification for behavior-shaping changes
- Do not invent authors, reviewers, tested versions, results, or provenance

## Two audiences, one source

The same Markdown serves a water engineer who has never used git and an agent that needs exact operational rules. Write one document with two paths — plain-language first, operational second.

## Self-check

<details>
<summary>Q: Where do deep method notes go?</summary>
<p>In `references/` — loaded only when the procedure points to them. `SKILL.md` stays terse.</p>
</details>

<details>
<summary>Q: What does `method_status: hypothesis` mean?</summary>
<p>An unverified proposition intended for testing — visible, not silently defaulted to established.</p>
</details>

## Next link

Track A: [Lesson 4 · Propose a skill without git](../04-propose-without-git/)
Track B: [Lesson 5 · Propose a skill with git](../05-propose-with-git/)
