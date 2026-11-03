---
name: skill-pr
description: Draft and preflight one water-skills contribution against the current repository guidance and pull request template. Use when preparing or reviewing a contribution or PR description.
---

# Skill PR

Prepare a truthful draft and preflight for one contribution. Keep the work in the current checkout and return the draft for the human to review and submit.

## Procedure

1. **Read current guidance.** For each request, read `README.md`, `CONTRIBUTING.md`, and `.github/PULL_REQUEST_TEMPLATE.md` from the current checkout. Use the template as the draft structure, `CONTRIBUTING.md` for contributor requirements, and the README as project context. For PR procedure, follow explicit requirements in the template and `CONTRIBUTING.md`; report any conflict with README rather than silently reconciling it. Do not treat `AGENTS_obsolete.md` as authority or assume a missing referenced document is available.
2. **Bound one contribution.** Inspect the proposed change and its read-only working-tree diff when available. Establish the single problem and the files intended for this contribution. If the intended scope is unclear or includes unrelated work, ask the human to identify the contribution before drafting; do not stage, edit, or discard changes as part of preflight.
3. **Collect evidence.** Compare the contribution with every current template heading, field, checkbox, instruction, and applicable conditional section. Ask concise, specific questions for missing facts. In particular, obtain evidence for the experienced problem, project fit, alternatives, related open and closed PRs, authoring and test environments, validation and evaluation results, and human review wherever the current template requires them. Use only facts supplied by the human or directly verified in the available checkout or runtime. If a read-only PR search is unavailable, ask the human to search open and closed PRs and provide the result.
4. **Preflight the contribution.** Check that it addresses one concrete problem, fits the repository's stated scope, and accounts for the current contribution guidance and template. Run a relevant existing validation only when appropriate and already available; report the exact command and observed result. Do not install dependencies. Mark checks that were not run or could not be verified as pending.
5. **Draft and report status.** Follow the current template's section order and account for every section. Fill only evidence-backed answers. For unanswered fields, use a clearly labeled `[NEEDS HUMAN INPUT: …]` marker in a partial draft and identify the specific information needed; never imply the draft is complete. Report preflight findings and blockers separately from the draft.

## Evidence and handoffs

- Never invent an incident, transcript, prior-PR search result, test or evaluation outcome, model or harness version, installed plugin, author, reviewer, or approval. Distinguish what was observed from what remains unverified.
- Do not mark a human-review checkbox or claim approval until the human confirms review of the complete proposed diff. Hand the complete diff and any unresolved evidence requests to the human for review.
- The human handles any unavailable prior-PR search, supplies missing evidence, confirms the final text and target, and submits the PR themselves.
- This skill stops at drafting and preflight. It never creates branches, commits, pushes, or submits pull requests.

## Completion criteria

Drafting and preflight are complete when exactly one contribution is in scope, every current template section is represented, factual answers are supported by evidence, missing evidence and unrun checks are explicit, and the human handoffs are clear. Report the draft as **not ready** while required information or review is outstanding; only the human decides whether to submit.

**Evaluation status:** This skill's behavior has not been evaluated.
