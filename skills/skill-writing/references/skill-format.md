# Skill format reference

Detailed constraints and examples for the `SKILL.md` frontmatter fields. This file is loaded on demand; the `SKILL.md` body should link here rather than duplicating this content.

## Frontmatter

The `SKILL.md` file must contain YAML frontmatter followed by Markdown content.

### Minimal example

```
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

### Example with optional fields

```
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
metadata:
  author: example-org
  version: "1.0"
---
```

## `name` field

The required `name` field:

- Must be 1-64 characters
- May only contain lowercase ASCII alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`)
- Must not start or end with a hyphen (`-`)
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

**Valid examples:**

```
name: pdf-processing
```

```
name: data-analysis
```

```
name: code-review
```

**Invalid examples:**

```
name: PDF-Processing  # uppercase not allowed
```

```
name: -pdf  # cannot start with hyphen
```

```
name: pdf--processing  # consecutive hyphens not allowed
```

## `description` field

The required `description` field:

- Must be 1-1024 characters
- Should describe both what the skill does and when to use it
- Should include specific keywords that help agents identify relevant tasks

**Good example:**

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents or when the user mentions PDFs, forms, or document extraction.
```

**Poor example:**

```
description: Helps with PDFs.
```

## `license` field

The optional `license` field:

- Specifies the license applied to the skill
- Keep it short (either the name of a license or the name of a bundled license file)

This field is part of the general format. In this repository, the root MIT
license applies to all repository content, so skill frontmatter omits `license`.

**Example:**

```
license: Proprietary. LICENSE.txt has complete terms
```

## `compatibility` field

The optional `compatibility` field:

- Must be 1-500 characters if provided
- Should only be included if your skill has specific environment requirements
- Can indicate intended product, required system packages, network access needs, etc.

**Examples:**

```
compatibility: Designed for Claude Code (or similar products)
```

```
compatibility: Requires git, docker, jq, and access to the internet
```

```
compatibility: Requires Python 3.14+ and uv
```

Note: Most skills do not need the `compatibility` field.

## `metadata` field

The optional `metadata` field:

- A map from string keys to string values
- Clients can use this to store additional properties not defined by the Agent Skills spec
- Make key names reasonably unique to avoid accidental conflicts

**Example:**

```yaml
metadata:
  author: example-org
  version: "1.0"
```

## `allowed-tools` field

The optional `allowed-tools` field:

- A space-separated string of tools that are pre-approved to run
- Experimental. Support may vary between agent implementations

**Example:**

```
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

## Body content

The Markdown body after the frontmatter contains the skill instructions. There are no format restrictions. Write whatever helps agents perform the task effectively.

Recommended sections:

- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases

Note that the agent will load this entire file once it decides to activate a skill. Consider splitting longer `SKILL.md` content into referenced files.

## Optional directories

Every skill requires `SKILL.md`. In this repository, use only the documented
optional top-level directories below and create one only when it contains a
resource the skill uses. Additional files may live at the skill root; ask for
review before introducing a new directory type.

### `scripts/`

Executable deterministic tools used by the skill. Document inputs, outputs,
dependencies, and failure messages.

### `references/`

Supporting source material, procedures, constraints, and definitions loaded only
when the task needs them. Keep files focused and linked from `SKILL.md`.

### `assets/`

Input templates and static task resources. Do not put confidential or
proprietary model data in the repository.

### `evals/`

Evaluation specifications, fixtures, and assertion scripts for behavior that
should be protected. Captured runs and reports are stored outside version
control unless explicitly approved as small synthetic fixtures.
For this repository, behavior-shaping changes require a relevant specification;
docs-only changes do not require behavioral evals.

### `examples/`

Illustrative inputs and outputs. Label synthetic examples and do not present
them as observed engineering results.

### `models/`

Native engineering model files, configurations, and fixtures used by the skill.
This directory is not for machine-learning weights.

### `adapters/`

Host-specific instructions or integration files. Keep the core skill usable
without a particular agent host where possible.
