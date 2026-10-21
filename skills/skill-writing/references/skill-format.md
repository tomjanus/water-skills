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

A skill directory may contain any files and directories beyond the required `SKILL.md`. The conventions below are recommendations for organizing common types of content.

### `scripts/`

Contains executable code that agents can run. Scripts should:

- Be self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully

### `references/`

Contains additional documentation that agents can read when needed:

- `REFERENCE.md` - Detailed technical reference
- `FORMS.md` - Form templates or structured data formats
- Domain-specific files (`finance.md`, `legal.md`, etc.)

Keep individual reference files focused and small.

### `assets/`

Contains static resources:

- Templates (document templates, configuration templates)
- Images (diagrams, examples)
- Data files (lookup tables, schemas)
