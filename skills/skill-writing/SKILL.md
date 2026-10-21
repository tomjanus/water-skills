---
name: skill-writing
description: Creates, improves, and validates agent skills (SKILL.md files). Use when the user asks to author a new skill, improve an existing skill, or check a skill against the Agent Skills format.
license: Apache-2.0
metadata:
  author: Tomasz Janus
  version: "1.0.0"
---

# What is a skill?

Skills are reusable capabilities that give AI agents the procedural knowledge needed to perform specific tasks, including code generation, domain-specific work, and tool integration.

# Directory structure

A skill is a directory containing, at minimum, a `SKILL.md` file with metadata (at minimum, a name and description) and instructions for performing the task. It can also include scripts, reference materials, templates, and other resources.

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

# Frontmatter at a glance

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content. The required fields are `name` and `description`.

| Field | Required | Constraints |
| - | - | - |
| `name` | Yes | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen. Must match the parent directory name. |
| `description` | Yes | Max 1024 characters. Non-empty. Describes what the skill does and when to use it. |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Max 500 characters. Indicates environment requirements. |
| `metadata` | No | Arbitrary key-value mapping for additional metadata. |
| `allowed-tools` | No | Space-separated string of pre-approved tools. (Experimental) |

See [the skill format reference](references/skill-format.md) for field-by-field constraints, examples, and valid/invalid cases.

# Writing a skill

1. **Scope the skill.** Decide the single task the skill enables and the tools it will use. A skill should be a focused capability, not a general topic.
2. **Check for an existing skill.** Search the target skills directory for a skill that already covers the task. Extend it rather than creating a duplicate.
3. **Choose a name.** Lowercase letters, numbers, and hyphens only; no leading or trailing hyphen; no consecutive hyphens; must match the parent directory name.
4. **Write the description.** State what the skill does and when to use it. Include specific keywords that help agents identify relevant tasks. Keep it under 1024 characters.
5. **Write the body.** Prefer a concise procedure the agent can follow. Include step-by-step instructions, examples of inputs and outputs, and common edge cases. Omit generic knowledge the agent already has.
6. **Add references only when needed.** Move detailed reference material (field constraints, glossaries, templates) into `references/` and link to it from `SKILL.md`. Keep the main file under 500 lines.
7. **Validate.** Run the validation command below and fix any reported errors.
8. **Self-review.** Check the skill against the checklist below.

# Checklist

Before considering a skill complete, confirm:

- `name` matches the parent directory name and follows the naming rules.
- `description` states what the skill does, when to use it, and includes routing keywords.
- The body is a procedure, not a restatement of the Agent Skills spec.
- No generic information that the agent already possesses.
- Detailed reference material is in `references/`, not duplicated in `SKILL.md`.
- `SKILL.md` is under 500 lines.
- File references are relative and one level deep.
- The skill validates with `agentskills validate`.

# Worked examples

## Minimal skill

```
---
name: pdf-processing
description: Extract PDF text, fill forms, and merge files. Use when handling PDFs.
---

# PDF processing

1. Inspect the input PDF.
2. Extract text and tables.
3. Fill or merge as requested.
4. Report the output path.
```

## Skill with references

```
---
name: hydraulic-modelling
description: Build, validate, and analyse hydraulic models of water distribution networks.
---

# Hydraulic modelling

Consult [GLOSSARY.md](GLOSSARY.md) for terminology and conventions.

## Workflow

1. Inspect the network model and its input data.
2. Validate the hydraulic model and boundary conditions.
3. Run the requested simulations.
4. Check results against physical constraints and expected behaviour.
```

# Progressive disclosure

Agents load skills *progressively*, pulling in more detail only as a task calls for it:

1. **Metadata** (~100 tokens): `name` and `description` are loaded at startup for all skills.
2. **Instructions** (< 5000 tokens recommended): the full `SKILL.md` body is loaded when the skill is activated.
3. **Resources** (as needed): files in `scripts/`, `references/`, or `assets/` are loaded only when required.

Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files.

# File references

When referencing other files in your skill, use relative paths from the skill root:

```
See [the skill format reference](references/skill-format.md) for details.

Run the extraction script:
scripts/extract.py
```

Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains.

# Validation

Validate the skill directory after writing:

```
agentskills validate ./my-skill
```

The `agentskills` command is provided by the `skills-ref` package. If it is not installed:

```
pip install skills-ref
# or
uv add skills-ref
```

This checks that the `SKILL.md` frontmatter is valid and follows all naming conventions.
