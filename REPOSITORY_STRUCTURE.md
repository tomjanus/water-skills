# Repository structure

```text
skills/<name>/SKILL.md         Agent Skills and their used resources/evals
evals/runner.py                Validator/grader for captured eval artifacts
evals/README.md                Eval suite and capture contract
catalog/                       Generated catalog data and staleness report
src/content/docs/catalog/      Generated catalog docs page
scripts/                       Dependency-free repository checks and generators
tests/                         Standard-library tests for repository checks
contributing/                  Contribution checklist and templates
.github/                       Issue/PR templates and CI validation workflow
README.md                      Project entry point
CONTRIBUTING.md                Contribution process and validation policy
RELEASING.md                   Release policy and human approval gate
CHANGELOG.md                   Version history and known limitations
EVALS.md                       Evaluation policy and runner boundary
GLOSSARY.md                    Canonical repository terminology
provenance.schema.json         Schema for per-skill provenance records
LICENSE                        Repository-wide MIT license
```

Optional skill resources are created only when used: `references/`, `scripts/`,
`assets/`, `evals/`, `examples/`, `models/`, and `adapters/`. See
[`contributing/SKILL_TEMPLATE.md`](contributing/SKILL_TEMPLATE.md) and
[`skills/skill-writing/SKILL.md`](skills/skill-writing/SKILL.md) for authoring
guidance. CI validates Agent Skills metadata, eval specifications, layout,
provenance records, catalog freshness, local Markdown links, documentation links,
and high-confidence secret patterns. CI also builds the documentation site.
