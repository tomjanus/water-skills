# water-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Join Discord](https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white)](https://discord.gg/k49cHHrce)

Agent skills for water science and engineering. The repository aims to transfer practical engineering knowledge—assumptions, checks, software-specific procedures, failure signatures, and limits—into concise instructions that an agent can apply with a human engineer.

Skills are procedures, not endorsements that a model, simulation, or engineering decision is correct. Review each skill's scope and assumptions before using it. Successful parsing, software execution, and format validation do not establish calibration, field agreement, or scientific validity.

## Use a skill

1. Browse the `skills/` directory and read the selected `SKILL.md` and any linked references.
2. Check its required software, inputs, units, and limitations.
3. Load the skill using your agent host's documented method. This repository does not currently provide a project-specific installer.
4. Review the result against the task's data, criteria, and applicable engineering requirements. Keep domain decisions with qualified people.

## Skill collection

Browse the [`skills/`](skills/) directory. Each skill's `SKILL.md` states its task scope, required inputs, procedure, and limitations. A generated catalog is not available yet.

Skill format checks and evaluation-spec checks are not behavioral test results. The repository's eval runner grades captured artifacts; it does not launch an agent. Behavioral and domain validation must be reported only when actually performed.

## Contribute

- Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md).
- Use Discussions for questions and proposals, and Issues for actionable problems, as described in the contribution guide.
- Active work and pull requests target `dev`; `main` is the released branch.
- Behavior-shaping skill changes need a relevant evaluation specification. State clearly when behavioral captures are unavailable; do not present specification validation as a performance result.
- Human review is required before submission. No automated pull-request approval or merge process is provided.

## Validation

From the repository root:

```bash
agentskills validate ./skills/<name>
python evals/runner.py --validate
bash .github/workflows/validate-skills.sh
```

The CI workflow installs `skills-ref` and runs the repository validator. For evaluation concepts and captured-run limitations, see [`EVALS.md`](EVALS.md) and [`evals/README.md`](evals/README.md). For current folders and tooling, see [`REPOSITORY_STRUCTURE.md`](REPOSITORY_STRUCTURE.md) and the [glossary](GLOSSARY.md).

## License

This repository uses the [MIT License](LICENSE). Skills do not declare a separate license in their frontmatter.
