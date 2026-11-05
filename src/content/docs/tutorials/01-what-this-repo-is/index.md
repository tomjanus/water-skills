---
title: What this repository is
description: Lesson 1 — collection vs platform, the five loops, authoring-first order.
---

# 1 · What this repository is

**Audience:** Anyone encountering water-skills for the first time — water engineers, managers, agents.
**Outcome:** You can explain what water-skills is, how it differs from a plain skill collection, and which loop (authoring, contract, evidence, curation, distribution) it currently implements.
**Duration:** ~10 minutes

## Plain-language path

water-skills is a collection of agent skills for water science and engineering — hydraulic modelling, water quality, transient analysis, leakage, calibration, and more.

A **collection** stores skills: someone writes a `SKILL.md`, commits it, and hopes others find it. A **platform** compounds: each pass through the system leaves the next pass cheaper. Contribution produces evidence, evidence makes curation objective, curation makes distribution trustworthy, and distribution produces more contributors.

The difference is not the number of skills. It is whether each pass through the system makes the next one cheaper.

## The five loops

| Loop | Question it answers | Status in this repository |
|---|---|---|
| **Authoring** | How does tacit knowledge become a draft? | Implemented — issue form + `water-skills new --from-issue`; no-git pilot not yet run |
| **Contract** | Is the skill valid and safe? | Implemented — `agentskills validate`, provenance schema, link/secret checks |
| **Evidence** | Does it change agent behaviour against a baseline? | Partial — eval runner validates specs; captured runs deferred |
| **Curation** | Is it distinct, provenance-backed, and current? | Implemented — generated catalog and staleness report; provenance gaps remain visible |
| **Distribution** | Can someone install, update, and trust it? | Implemented — docs site, release policy, and `v0.1.0` release candidate pending approval |

The binding constraint is the authoring runway: a water engineer should be able to go from "I have a useful workflow" to "here is a reviewable draft" without learning git. That path is implemented (Stage 2), but it has not yet been validated with a real no-git pilot. Evidence and curation continue to improve independently.

## Operational path

1. Browse [`skills/`](https://github.com/tomjanus/water-skills/tree/main/skills) to see existing skills.
2. Read the [repository README](https://github.com/tomjanus/water-skills/blob/main/README.md) for platform scope and constraints.
3. Read [`GLOSSARY.md`](https://github.com/tomjanus/water-skills/blob/main/GLOSSARY.md) for canonical terms (skill, trial, outcome, provenance, method status).

## Self-check

<details>
<summary>Q: Is water-skills just a folder of SKILL.md files?</summary>
<p>No. It is a platform of loops around skills: authoring, contract, evidence, curation, distribution. Not every loop is fully implemented yet.</p>
</details>

<details>
<summary>Q: Which loop is implemented first?</summary>
<p>Authoring — so a non-git contributor can propose a skill. Contract is already strong. Evidence, curation, and distribution follow.</p>
</details>

<details>
<summary>Q: Can I propose a skill without git?</summary>
<p>Yes — through the "Propose a skill" issue form. A maintainer scaffolds a draft pull request with `water-skills new --from-issue`.</p>
</details>

## Next link

[Lesson 2 · Use a skill](../02-use-a-skill/)
