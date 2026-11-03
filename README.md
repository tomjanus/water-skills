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

## What makes water-skills different

| Dimension | Status | Evidence |
|---|---|---|
| Single domain carried deep | supported | `skills/*/SKILL.md` — water science and engineering only |
| Judgement rather than paraphrase | supported | `MISSION.md`, Lesson 3 — knowledge-delta test, delete test |
| Evidence rather than popularity | supported | `evals/runner.py`, `EVALS.md` — captured runs, pass@k/pass^k |
| Labelled method status | supported | `provenance.schema.json`, `GLOSSARY.md` — established/adapted/heuristic/hypothesis |
| Real engineering software incl. Windows desktop | supported | `epanet-validation`, `wntr-engineering`, `pywr-engineering` |
| Contribution without git | supported | Stage 2 — `propose-skill.yml`, `water-skills new --from-issue` |
| One canonical document per fact | supported | `GLOSSARY.md`, skills layout contract |
| Ramp-on curriculum | planned | `docs/tutorials/` — 8 lessons, two tracks (Stage 3) |
| Generated catalog | planned | Not yet built; catalog generation is Stage 5 |

Statuses are `supported` (implemented and verified) or `planned` (documented, not yet built). No dimension claims a capability that does not exist.

## Documentation

- [Contributor guides](src/content/docs/guides/) — installation, contribution without git, contribution with git, skill authoring, review & lifecycle, evaluation, repository reference
- [Ramp-on tutorials](src/content/docs/tutorials/) — 8 lessons, two tracks (Track A: no git, no agent; Track B: engineering and agent)

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
