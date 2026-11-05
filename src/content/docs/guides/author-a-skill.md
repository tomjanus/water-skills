---
title: Author a skill
description: Skill authoring standard — knowledge delta, delete test, layered structure, method status labels.
---

# Author a skill

A skill transfers expert knowledge that a capable model may lack. It is not a tutorial, a vendor manual, or a restatement of generic information.

## One test: the knowledge delta

Before writing or accepting a skill, answer one question:

> **What would a capable model get wrong without this skill?**

If you cannot name one thing, the skill is not justified. If you can, that gap is the first sentence of the skill and the first eval case.

**"Wrong"** is stronger than "less detailed". A model can write a plausible EPANET workflow from general knowledge. It is more likely to miss the project-specific threshold, the unit conversion, the solver warning that matters, or the assumption that invalidates the result. That gap is the skill.

| Not a knowledge delta | A knowledge delta |
|---|---|
| "Explain what EPANET is." | "Reject a calibration result when the mass-balance error exceeds the project tolerance, even if the solver reports convergence." |
| "List the steps of calibration." | "Report the largest residual and the node or link where it occurs." |
| "Describe why water quality matters." | — |

## Terse: the delete test

Read every sentence and ask: *if I delete this, does the agent's output change?* If not, delete it. This removes generic definitions, motivational prose, repeated warnings, and copied manual sections.

| Weak sentence | Why it fails | Terse replacement |
|---|---|---|
| "EPANET is a widely used hydraulic modelling package developed by the US EPA." | A capable model already knows this. It changes no decision. | Delete it. Start with the check or decision the skill exists for. |
| "It is important to carefully validate your results." | "Validate" is not an action. The agent cannot execute it. | "Reject the run if mass-balance error exceeds the project tolerance; report the largest residual." |
| "For more information, see the EPANET manual." | The model may not have the manual, and the link does not tell it what to look for. | "For demand-pattern options, read `references/epanet-demand.md` before choosing a pattern." |

## Layered: progressive disclosure

Load depth only when the task needs it:

| Layer | What belongs there | What must not |
|---|---|---|
| **Frontmatter** | Name and a routing description naming the task and trigger | A summary of the whole method |
| **`SKILL.md`** | Procedure, decision rules, thresholds, checks, failure modes, "do not use when" | Generic definitions, long background, copied manual text |
| **`references/`** | Deep method notes, diagnostic tables, software quirks, worked examples | Content the procedure never points to |
| **`scripts/`** | Deterministic parsing, unit checks, report generation | Hidden domain judgement that should be reviewed |
| **`evals/`** | A case that fails without the skill and passes with it | An assertion that passes in both conditions |

## Label the epistemic status

Say whether the method is `established`, `adapted`, `heuristic`, or `hypothesis`. A heuristic is acceptable when named as one and tested. An unlabelled guess presented as established method is not.

The [provenance schema](https://github.com/tomjanus/water-skills/blob/main/provenance.schema.json) governs `provenance.yaml` records: required `authors` and `method_status`, optional string lists for `references`, `software_tested`, `reviewers`, and `evidence`. Do not populate fields without evidence.

## Two audiences, one source

The same Markdown file serves a water engineer who has never used git and an agent that needs exact operational rules. Write one document with two paths:

- **Plain-language path**: why it matters, one worked example, a clear next link, no terminal
- **Operational path**: exact commands, paths, schemas, expected output, failure messages, stop conditions

## Before submitting

- Match `name` to the skill directory
- Run `agentskills validate ./skills/<name>`
- Add an eval specification for behavior-shaping changes
- Do not invent authors, reviewers, tested versions, results, or provenance
