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
| **Authoring** | How does tacit knowledge become a draft? | Implemented — issue form + `water-skills new --from-issue` |
| **Contract** | Is the skill valid and safe? | Implemented — `agentskills validate`, provenance schema, link/secret checks |
| **Evidence** | Does it change agent behaviour against a baseline? | Partial — eval runner validates specs; captured runs deferred |
| **Curation** | Is it distinct, provenance-backed, and current? | Planned — generated catalog not yet built |
| **Distribution** | Can someone install, update, and trust it? | Planned — docs site (this guide) is step one |

The binding constraint is the authoring runway: a water engineer should be able to go from "I have a useful workflow" to "here is a reviewable draft" without learning git. That path now exists (Stage 2). Evidence and curation follow.

## Operational path

1. Browse [`skills/`](../guides/repository-reference.md) to see existing skills.
2. Read [`MISSION.md`](../MISSION.md) for the platform mission and constraints.
3. Read [`GLOSSARY.md`](../GLOSSARY.md) for canonical terms (skill, trial, outcome, provenance, method status).
4. The [`README.md`](../README.md) is the landing page; it links to guides, tutorials, and contribution entry points.

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

[Lesson 2 · Use a skill](./02-use-a-skill/)
