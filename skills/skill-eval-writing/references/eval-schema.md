# Eval schema

Full reference for `skills/<name>/evals/evals.json` and captured run artifacts.
This file is loaded on demand; link to it from `SKILL.md` rather than duplicating
it there.

## Suite file

| Field | Required | Meaning |
|-------|----------|---------|
| `skill_name` | Yes | Must match the parent directory name. |
| `description` | No | One-line summary of what the suite measures. |
| `trials` | No | Expected number of trials per case (default 1). |
| `evals` | Yes | Non-empty array of cases. |

## Case

| Field | Required | Meaning |
|-------|----------|---------|
| `id` | Yes | Unique, stable identifier. Join key for conditions. |
| `label` | No | Human-readable name for reports. |
| `prompt` | Yes | The user request the agent receives. |
| `expected_output` | Yes | Outcome description of a successful run. |
| `expected_skill` | No | Skill that should load; `null` for negative cases. |
| `files` | No | Fixture paths relative to `evals/files/`. |
| `routing` | No | `{ "expect": [...], "forbid": [...] }`, graded on the transcript. |
| `assertions` | No | Array of assertion strings (see below). |

`id` must start with a letter or digit and contain only ASCII letters, digits,
`.`, `_`, and `-`. Keep it stable: renaming an `id` breaks comparison with
earlier runs.

## Assertions

| Form | Graded by | Example |
|------|-----------|---------|
| `file:<path>` | filesystem | `file:outputs/summary.json` |
| `regex:<pattern>` | `re.search` on transcript + outputs | `regex:^name:\s*[a-z0-9-]+$` |
| `json:<path>.<field>` | JSON load | `json:outputs/summary.json:nodes.0.id` |
| `script:<name>` | subprocess exit code | `script:check_frontmatter.py` |
| `agentskills` | `agentskills validate` | `agentskills` |
| *(bare sentence)* | optional LLM judge | `The description states when to use the skill.` |

`file:` resolves against the artifacts dir, then `outputs/`, then by filename
anywhere under the artifacts tree. `script:` files live in `evals/scripts/` and
receive the artifacts directory as their first argument; `.py` runs under the
current interpreter, `.sh` under `bash`.

## Captured run artifact

```
evals/runs/<skill>/<case-id>/<condition>/
└── trial-1/
    ├── outputs/            # files the agent produced
    ├── transcript.md       # the captured transcript
    └── metadata.json       # model, harness, skill_revision, timestamp
```

Conditions are `without_skill` (baseline), `with_skill`, and, for A/B
comparison, the comparator skill's `with_skill` directory under
`evals/runs/<comparator>/<case-id>/with_skill/`.

## Worked example

`skills/skill-writing/evals/evals.json` evaluates whether an agent that loads
`skill-writing` produces a valid skill:

```json
{
  "skill_name": "skill-writing",
  "evals": [
    {
      "id": "write-epanet-parser",
      "label": "Write an EPANET .inp parser skill",
      "prompt": "Create a skill that parses EPANET .inp files and emits a JSON summary.",
      "expected_output": "A new skill directory whose SKILL.md validates and follows the format.",
      "expected_skill": "skill-writing",
      "routing": { "expect": ["skill-writing"] },
      "assertions": [
        "file:SKILL.md",
        "regex:^name:\\s*[a-z0-9-]+$",
        "script:check_frontmatter.py",
        "script:check_body.py",
        "agentskills",
        "The description states what the skill does and when to use it, not the steps."
      ]
    }
  ]
}
```

The bare-string assertion is only graded when the judge is enabled; the rest are
deterministic and run in CI.

## Judge contract

Enable with `--judge` and set `EVAL_JUDGE_CMD` to any command that reads a JSON
request on stdin and writes a JSON verdict as the last stdout line:

Request:

```json
{
  "assertion": "The description states when to use the skill.",
  "case_id": "write-epanet-parser",
  "expected_output": "...",
  "transcript": "..."
}
```

Response:

```json
{"pass": true, "reason": "The description says 'Use when the user asks to read EPANET files'."}
```

The judge is optional, provider-agnostic, and never runs in CI.
