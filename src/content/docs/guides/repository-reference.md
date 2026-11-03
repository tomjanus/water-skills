---
title: Repository reference
description: Directory layout, scripts, configs, validation checks, and contribution templates.
---

# Repository reference

## Directory layout

```text
skills/<name>/SKILL.md         Agent Skills and their used resources/evals
evals/runner.py                Validator/grader for captured eval artifacts
evals/README.md                Eval suite and capture contract
scripts/                       Dependency-free repository checks
tests/                         Standard-library tests for repository checks
contributing/                  Contribution checklist and templates
.github/                       Issue/PR templates and CI validation workflow
README.md                      Project entry point
CONTRIBUTING.md                Contribution process and validation policy
EVALS.md                       Evaluation policy and runner boundary
GLOSSARY.md                    Canonical repository terminology
provenance.schema.json         Schema for per-skill provenance records
LICENSE                        Repository-wide MIT license
```

Optional skill resources are created only when used: `references/`, `scripts/`, `assets/`, `evals/`, `examples/`, `models/`, and `adapters/`. See [`contributing/SKILL_TEMPLATE.md`](contributing/SKILL_TEMPLATE.md) and [`skills/skill-writing/SKILL.md`](skills/skill-writing/SKILL.md) for authoring guidance.

CI validates Agent Skills metadata, eval specifications, layout, provenance records, local Markdown links, and high-confidence secret patterns.

## Scripts

| Script | Purpose |
|---|---|
| `scripts/check_skill_layout.py` | Validates skill directory layout and optional folder names |
| `scripts/check_provenance.py` | Validates provenance.yaml against provenance.schema.json |
| `scripts/check_links.py` | Validates local Markdown links |
| `scripts/check_secrets.py` | Scans for high-confidence credential patterns |
| `scripts/water_skills.py` | Authoring runway CLI: `water-skills new --from-issue <number>` |

## Validation checks

```bash
agentskills validate ./skills/<name>
python evals/runner.py --validate
bash .github/workflows/validate-skills.sh
```

## Contribution templates

| File | Purpose |
|---|---|
| `contributing/CONTRIBUTION_CHECKLIST.md` | Pre-PR checklist |
| `contributing/SKILL_TEMPLATE.md` | SKILL.md template |
| `contributing/AGENT_TEMPLATE.md` | Subagent template |
| `contributing/ISSUE_TRIAGE.md` | Triage labels, states, acceptance criteria |
| `contributing/SCAFFOLD_SPEC.md` | Scaffold output specification |
| `.github/ISSUE_TEMPLATE/propose-skill.yml` | Structured issue form |
| `.github/ISSUE_TEMPLATE/propose-skill.md` | Markdown issue form |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template |

## Glossary

Canonical terms for skills, evaluations, trials, harnesses, GUI work, provenance, and contribution are in [`GLOSSARY.md`](GLOSSARY.md). Link to it rather than copying definitions.

## Provenance schema

The supported simple-YAML form uses `authors` and `method_status` plus optional string lists for `references`, `software_tested`, `reviewers`, and `evidence`. The checker does not accept arbitrary YAML features — keep records to this documented structure.
