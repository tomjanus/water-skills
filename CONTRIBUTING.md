# Contributing to water-skills

water-skills is a central collection of agent skills for engineering and
water engineering. Skills live in `skills/<name>/SKILL.md`, follow the
Agent Skills format, and are validated by `agentskills` in CI.

This document is the public-facing summary. The full contributor rules live
in [`AGENTS.md`](AGENTS.md) and the PR template at
[`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).
Read both before submitting.

## What belongs here

water-skills collects engineering and water-engineering skills:

- hydraulic and network modelling;
- simulation tools (EPANET, WNTR, pywr);
- water-quality and transient analysis;
- leakage and calibration;
- scientific writing for engineering work.

We do **not** accept generic productivity skills, unrelated software
tutorials, skills that promote a specific third-party product, or
configuration that only benefits one project, dataset, team, or private
workflow. Ask yourself: "Would this help someone doing engineering work?"
If not, publish it separately.

## How to propose or contribute a skill

1. **Search first.** Check open and closed issues and PRs for existing
   skills or prior proposals covering the same task. Extend an existing
   skill rather than creating a duplicate.
2. **Describe the problem.** A proposal must state the specific problem
   someone actually experienced — what broke, what failed, and the user
   experience that motivated it. "It would be cool if..." is not a problem
   statement.
3. **Open a PR against `dev`.** `main` is the released branch; active work
   lands on `dev` first.
4. **Fill in every section of the PR template.** PRs that leave sections
   blank, bundle unrelated changes, or show no evidence of human review are
   closed without review.

## Validation

Every `skills/<name>/SKILL.md` must pass:

```
agentskills validate ./skills/<name>
```

The `agentskills` command is provided by the `skills-ref` package
(`pip install skills-ref`). CI runs the same check for every skill via
`.github/workflows/validate-skills.sh`. A missing `name` or `description`,
or a `name` that does not match the directory name, fails CI.

## Evals

Evals are encouraged, not mandatory. When a skill has behaviour worth
protecting, add cases under `skills/<name>/evals/` and run them against a
baseline:

```
python evals/runner.py --skill <name> --all-conditions
```

The harness grades captured runs and reports the lift of the skill over no
skill, and can compare two skills on the same cases. It is harness-agnostic and
adds no required dependencies. See [`evals/README.md`](evals/README.md) and
the [`skill-eval-writing`](skills/skill-eval-writing/SKILL.md) skill for the
test-driven pattern.

## Dependencies and bundled tooling

A skill is a directory of instructions and reference files. Do not add
required dependencies on third-party agent frameworks or hosted services.
If a skill needs external engineering software or Python packages, declare
them in the `compatibility` frontmatter and document the install command in
the body — do not vendor or bundle them.

## Disclosure

Every PR and issue must disclose the model, harness, harness version, and all
installed plugins used to produce the contribution — or state plainly that
it was written by hand with no agent. We weigh contributions by what produced
them: content reasoned from documentation is held to a different bar than
work grounded in a real session. Contributions that hide their authoring
environment will be closed.

## Questions

For usage questions, troubleshooting help, and general discussion, join the
[water-skills Discord](https://discord.gg/k49cHHrce).
