---
name: skill-browser
description: Find repository-local water-skills relevant to a task. Use when asked to discover, locate, or choose skills in this repository.
---

# Skill browser

Find relevant skills in this checkout and report their exact identifiers, paths, and relevance. This is a discovery task; the human decides what to use.

## Procedure

1. Reduce the request to the task or capability the user wants help with.
2. Inspect only files matching the repository-local pattern `skills/*/SKILL.md`. Read each matching skill file's frontmatter and body to assess its stated purpose and scope. Do not search nested directories, other repository files, or external registries.
3. Report each relevant candidate with:
   - **ID:** the exact `name` value in its frontmatter;
   - **Path:** its exact repository-relative path;
   - **Relevance:** `direct` or `partial`, with a brief reason grounded in the skill's text.
4. If a candidate has missing or malformed `name` metadata, report that fact and its exact path; do not invent an ID. If no candidate is relevant, say no repository-local match was found.

Use `direct` when the skill's primary purpose matches the request; use `partial` when it covers a meaningful component but not the whole request.

## Scope and handoff

Discovery ends with the results and any scope gaps. Do not search external registries, use star counts or popularity to order candidates, install skills, execute skills, or produce an execution plan or prompt. Present the matches for the human to select and let them decide whether to invoke a skill separately.

## Completion criteria

The search is complete when the `skills/*/SKILL.md` candidates have been checked, every reported match has an exact ID (or an explicit metadata problem), exact path, and text-based relevance reason, and the human has been told if there is no match or if the request exceeds the repository-local scope.

**Evaluation status:** This skill's behavior has not been evaluated.
