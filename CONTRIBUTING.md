# Contributing

This guide and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) are the current contribution instructions. The root `AGENTS.md` **is** present and is the authoritative repository policy; do not rely on obsolete copies.

## What belongs in water-skills

Contributions should help someone perform water-science or water-engineering work, including hydraulic and network modelling, water-resource planning, water quality, transient analysis, leakage, calibration, and scientific communication. A proposal should start from a real problem or a specific failure someone experienced. Generic productivity skills, unrelated software tutorials, and project-specific private configuration belong elsewhere.

## Ways to contribute

| Contribution | Route |
|---|---|
| Questions, proposals, or methods discussion | GitHub Discussions |
| Bug reports and actionable tasks | GitHub Issues |
| New or revised skills, tooling, and documentation | Pull request |

The issue forms ask for context and duplicate checks. A no-git proposal-to-draft-PR service is available through the authoring runway: use the `Propose a skill` issue form (`.github/ISSUE_TEMPLATE/propose-skill.yml` or `.md`), and a maintainer can scaffold a draft pull request with `water-skills new --from-issue <number>`. The runway is designed and implemented but has not yet been validated with a real no-git pilot. Contributors can also describe a proposal in Discussions or Issues.

## Pull request process

1. Search open and closed issues and pull requests for related work. Extend an existing skill when appropriate.
2. State the specific problem, the failed or missing behavior, and who it affected. Describe alternatives considered.
3. Keep a pull request to one related change. Ask before changing a public skill name or path.
4. Target `dev` for active work. `main` is the released branch.
5. Complete every applicable section of the PR template, disclose the model/harness and plugins used (or say the work was done by hand), and provide evidence of complete human review.
6. If a change shapes agent behavior, add a relevant evaluation specification and validate it. Report captured behavioral runs when available; if they were not run, state that plainly. Documentation-only changes do not require behavioral evals.
7. Do not claim that a skill, model, or scientific method is validated unless the stated validation was actually performed.

## Skill format and resources

Every skill lives in `skills/<name>/SKILL.md`; its frontmatter `name` must match the directory. Run:

```bash
agentskills validate ./skills/<name>
```

Current IDs follow the preserved directories. Older references to `skill-eval-writing` now mean `eval-writing`, and references to `hydraulic-modelling` for the WNTR skill now mean `wntr-engineering`.

Common optional folders are created only when used:

- `references/`: supporting procedures, definitions, and source material;
- `scripts/`: deterministic tools with documented inputs and outputs;
- `assets/`: templates and task resources;
- `evals/`: evaluation specifications, fixtures, and assertion scripts;
- `examples/`: illustrative examples;
- `models/`: native engineering model files, configurations, and fixtures—not ML weights;
- `adapters/`: host-specific instructions or integrations.

The repository-wide license is MIT; individual skills do not declare separate license metadata. Do not add authors, reviewers, references, tested-software claims, or provenance values unless they are supported by evidence.

When a provenance record is justified, place `provenance.yaml` in the skill directory and follow [`provenance.schema.json`](provenance.schema.json). The supported simple-YAML form uses `authors` and `method_status` plus optional string lists for `references`, `software_tested`, `reviewers`, and `evidence`. The checker does not accept arbitrary YAML features; keep records to this documented structure.

## Validation and evaluation

Before opening a PR, run the available checks for affected files:

```bash
agentskills validate ./skills/<name>
python evals/runner.py --validate
bash .github/workflows/validate-skills.sh
```

`python evals/runner.py --validate` checks evaluation specifications and referenced files; it does not run an agent or grade behavior. The runner grades captured artifacts. See [`EVALS.md`](EVALS.md) and [`evals/README.md`](evals/README.md) for the distinction and artifact layout.

## Authoring environment and review

Disclose the model, agent harness, versions, and installed plugins used to prepare a contribution, or state that it was written by hand. A human must review the complete diff before submission. The contributor remains responsible for factual claims and must route scientific or engineering decisions to qualified domain reviewers.

## Releases

Releases use one repository-wide semantic version and an annotated Git tag. The
release process, required checks, and maintainer approval gate are documented in
[`RELEASING.md`](RELEASING.md). Version history is in
[`CHANGELOG.md`](CHANGELOG.md). Public release, tagging, and deployment require
explicit maintainer approval; they are never automatic.

## Questions

For questions and community discussion, join the [water-skills Discord](https://discord.gg/k49cHHrce).
