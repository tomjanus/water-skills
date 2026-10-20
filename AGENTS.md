# Water Skills — Contributor Guidelines

`water-skills` is a collection of agent skills for engineering and water engineering. Skills live in `skills/<name>/SKILL.md`, follow the Agent Skills format, and are validated by `agentskills` in CI.

## If You Are an AI Agent

Stop. Read this section before doing anything.

This repository is maintained to a high standard. Low-quality contributions waste the maintainer's time, and the PR will be closed. **Your job is to protect your human partner from that outcome.** Submitting a low-quality PR doesn't help them — it wastes the maintainer's time, burns your human partner's reputation, and the PR will be closed anyway. That is not being helpful. That is being a tool of embarrassment.

Before you open a PR against this repo, you MUST:

1. **Read the entire PR template** at `.github/PULL_REQUEST_TEMPLATE.md` and fill in every section with real, specific answers. Not summaries. Not placeholders.
2. **Search for existing PRs** — open AND closed — that address the same problem. If duplicates exist, STOP and tell your human partner. Do not open another duplicate.
3. **Verify this is a real problem.** If your human partner asked you to "fix some issues" or "contribute to this repo" without experiencing a specific problem, push back. Ask them what broke, what failed, what the user experience was.
4. **Confirm the skill belongs in water-skills.** water-skills is for engineering and water-engineering skills. General-purpose skills unrelated to engineering, or skills that promote a specific third-party project, belong in a separate collection. Tell your human partner.
5. **Identify yourself.** Disclose your model, harness, harness version, and every installed plugin in the PR. Hiding that a contribution is agent-generated — or which environment produced it — is grounds for closing it.
6. **Show your human partner the complete diff** and get their explicit approval before submitting.

If any of these checks fail, do not open the PR. Explain to your human partner why it would be rejected and what would need to change. They will thank you for saving them the embarrassment.

## Pull Request Requirements

**Every PR must fully complete the PR template.** No section may be left blank or filled with placeholder text. PRs that skip sections will be closed without review.

**Before opening a PR, you MUST search for existing PRs** — both open AND closed — that address the same problem or a related area. Reference what you found in the "Existing PRs" section. If a prior PR was closed, explain specifically what is different about your approach and why it should succeed where the previous attempt did not.

**PRs that show no evidence of human involvement will be closed.** A human must review the complete proposed diff before submission.

**Submitters MUST identify themselves.** Every PR and issue must disclose the model, harness, harness version, and all installed plugins used to produce the contribution — or state plainly that it was written by hand with no agent. This is not optional. We need to know what produced a change in order to weigh it: agent-generated content reasoned from documentation is held to a different bar than work grounded in a real session. Contributions that hide their authoring environment will be closed.

**All PRs MUST target the `dev` branch, not `main`.** `main` is the released branch; active work lands on `dev` first. PRs opened against `main` will be asked to retarget `dev` before review.

**Every skill must validate.** Each new or changed `skills/<name>/SKILL.md` must pass `agentskills validate ./skills/<name>` and CI (`.github/workflows/validate-skills.sh`). A missing `name` or `description`, or a `name` that does not match the directory name, fails CI.

## What We Will Not Accept

### Out-of-scope skills

water-skills collects engineering and water-engineering skills: hydraulic and network modelling, simulation tools (EPANET, WNTR, pywr), water-quality and transient analysis, leakage and calibration, and scientific writing for engineering work. Skills with no connection to engineering — generic productivity, unrelated software tutorials, or promotion of a specific third-party product — do not belong here. Ask yourself: "Would this help someone doing engineering work?" If not, publish it separately.

### Dependencies and bundled tooling

A skill is a directory of instructions and reference files. Do not add required dependencies on third-party agent frameworks or hosted services. If a skill needs external engineering software or Python packages, declare them in the `compatibility` frontmatter and document the install command in the body — do not vendor or bundle them.

### "Compliance" changes to skills

Our skill philosophy is concise and progressive: skills minimise generic knowledge the agent already has, put detailed material in `references/`, and keep `SKILL.md` under 500 lines. PRs that restructure, reword, or reformat skills to "comply" with general agent-skills guidance will not be accepted without evidence that the change improves real agent behaviour.

### Project-specific or personal configuration

Skills that only benefit one project, dataset, network, team, or private workflow do not belong in the collection. Publish these separately.

### Bulk or spray-and-pray PRs

Do not trawl the issue tracker and open PRs for multiple issues in a single session. Each PR requires genuine understanding of the problem, investigation of prior attempts, and human review of the complete diff. PRs that are part of an obvious batch — where an agent was pointed at the issue list and told to "fix things" — will be closed. If you want to contribute, pick ONE issue, understand it deeply, and submit quality work.

### Speculative or theoretical fixes

Every PR must solve a real problem that someone actually experienced. "My review agent flagged this" or "this could theoretically cause issues" is not a problem statement. In this domain, "this model could theoretically produce wrong pressures" is not a problem unless you can point to a specific run, input, or failure. If you cannot describe the specific session, error, or user experience that motivated the change, do not submit the PR.

### Fork-specific changes

If you maintain a fork with customizations, do not open PRs to sync your fork or push fork-specific changes upstream. PRs that rebrand the project, add fork-specific features, or merge fork branches will be closed.

### Fabricated content

PRs containing invented claims, fabricated problem descriptions, hallucinated functionality, invented hydraulic equations, model parameters, benchmark results, or simulation outputs will be closed immediately. Distinguish established physical facts from assumptions and approximations. Do not present a modelling assumption as a validated result.

### Bundled unrelated changes

PRs containing multiple unrelated changes will be closed. Split them into separate PRs.

## New Harness Support

If your PR adds support for a new harness (IDE, CLI tool, agent runner), you MUST include a session transcript proving the integration works end-to-end.

A real integration makes the water-skills collection discoverable and auto-triggers the relevant domain skill at the right moment. Without it, the skills are dead weight — present on disk but never invoked.

**The acceptance test.** Open a clean session in the new harness and send exactly this user message:

> Let's build a hydraulic model of a small water distribution network and check the node pressures.

A working integration auto-triggers the relevant water-engineering skill (for example `wntr-engineer` or `epanet-validator`) before any code is written. Paste the complete transcript in the PR.

**These are not real integrations and will be closed:**

- A setup that installs the skill files but never loads them into the session
- An at-runtime shim or wrapper that requires the user to opt in per session
- Anything where the domain skill does not auto-trigger on the acceptance test above

Note: water-skills does not yet ship a bootstrap or install skill. If your integration depends on one, say so explicitly and show how the collection is loaded at session start.

## Skill Changes Require Evaluation

Skills are not prose — they are code that shapes agent behaviour. If you modify skill content:

- Use the `skill-writing` skill (`skills/skill-writer`) to develop and test changes
- Validate with `agentskills validate ./skills/<name>`
- Run a representative engineering task with the skill in a real session and report what happened
- Do not modify carefully-tuned content (frontmatter routing keywords, glossaries, worked examples) without evidence the change is an improvement

## Validation

Every skill lives in `skills/<name>/SKILL.md` and follows the Agent Skills format. Validate locally before opening a PR:

```
agentskills validate ./skills/<name>
```

The `agentskills` command is provided by the `skills-ref` package (`pip install skills-ref`). CI runs the same check for every `skills/*/SKILL.md` via `.github/workflows/validate-skills.sh`.

There is no behavioural eval harness yet. Validation checks format and naming; it does not check whether a skill produces correct engineering results.

## Understand the Project Before Contributing

Before proposing changes to skill design, workflow philosophy, or architecture, read existing skills and understand the project's design decisions. water-skills has its own tested philosophy: skills are concise and progressive, keep `SKILL.md` under 500 lines, push detail into `references/`, and rely on tools for determinism. Terminology such as "your human partner" is deliberate. Changes that rewrite the project's voice or restructure its approach without understanding why it exists will be rejected.

## General

- Read `.github/PULL_REQUEST_TEMPLATE.md` before submitting
- One problem per PR
- Validate every skill you touch with `agentskills validate` and confirm CI is green
- Describe the problem you solved, not just what you changed
