---
title: Installation & use
description: Install the water-skills documentation site and load a skill into your agent host.
---

# Installation & use

## About this repository

water-skills is a collection of agent skills for water science and engineering. Each skill is a directory containing a `SKILL.md` and optional supporting resources (references, scripts, examples, models, adapters, evals). The repository does not provide a project-specific installer; you load a skill by pointing your agent host at the skill directory.

## Install the documentation site

The docs site is built with [Starlight](https://starlight.astro.build/) on [Astro](https://astro.build/). It is deployed to GitHub Pages from `main`.

To run the docs site locally:

```bash
npm ci
npm run dev
```

Then open `http://localhost:4321`. The build output goes to `dist/` and is published by the [deploy-docs workflow](.github/workflows/deploy-docs.yml).

## Load a skill

1. Browse the [`skills/`](https://github.com/lepton/water-skills/tree/main/skills) directory and select a skill.
2. Read the skill's `SKILL.md` — it states the task scope, required inputs, procedure, and limitations.
3. Check the skill's required software, inputs, units, and limitations before use.
4. Load the skill using your agent host's documented method for adding a skill directory.
5. Review the result against the task's data, criteria, and applicable engineering requirements.

Keep domain decisions with qualified people. A skill passes validation only if it is structurally valid — that does not establish calibration, field agreement, or scientific validity.
