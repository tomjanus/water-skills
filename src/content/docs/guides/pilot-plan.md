# No‑git pilot plan and transcript template

## Objective

Run one end‑to‑end pilot with a water‑engineer contributor who has **no git experience**. The pilot measures whether the issue‑form → scaffold → draft‑PR → review pathway works without the contributor needing a terminal. The transcript records every step, decision point, and failure mode so the runway can be labelled `supported` or remain `designed, not validated`.

## Recruitment (Step 1)

| Action | Who | What to record in transcript |
|---|---|---|
| Identify a contributor | Maintainer / office‑hours host | Name, contact, water‑engineering domain, stated git experience (or lack thereof) |
| Agree on a real problem | Contributor + maintainer | Problem description, software used, why it’s worth solving, expected outcome |
| Set timeline | Maintainer | 2‑week window, expected weekly time commitment (≤ 5 h/week) |

**Transcript section**: "Recruitment – <date>; contributor <name> agreed to solve <problem> using <software> v<ver>. No prior git experience."

## Issue form completion (Step 2)

| Action | Who | What to record |
|---|---|---|
| Open `propose-skill.yml` | Contributor | Issue number, URL |
| Fill required fields: domain, problem, prompt, expected, inputs, software, references | Contributor | Time spent, which fields were easy/hard, any guessed values |
| Optional: attach transcript of a real session (redacted) | Contributor | Time stamp, credentials removed |

**Transcript section**: "Form fill – <date>; took 22 min; fields `problem` and `prompt` filled, `references` left empty (to be added later)."

## Triage (Step 3)

| Action | Who | What to record |
|---|---|---|
| Maintainer reads the issue | Maintainer | Time spent, any clarifying questions asked |
| Apply labels per `ISSUE_TRIAGE.md` | Maintainer | Labels applied (`accepted`, `needs-info`, etc.) and rationale |
| Decision recorded in issue comments | Maintainer | Exact comment text |

**Transcript section**: "Triage – <date>; maintainer applied label `accepted` after checking duplicate search (no match) and field completeness."

## Scaffold run (Step 4)

| Action | Who | What to record |
|---|---|---|
| Maintainer runs `water-skills new --from-issue <number>` (dry‑run first) | Maintainer | `--dry-run` output: planned files, unresolved questions |
| Run without `--dry-run` | Maintainer | Full stdout/stderr, branch name created, files listed |
| Review created branch and file list | Maintainer | Confirm `SKILL.md`, `provenance.yaml`, `evals/evals.json` present; note any missing expected files |

**Transcript section**: "Scaffold – <date>; `water-skills new --from-issue 42` created branch `skill/42-new-epanet-transient`; files: `SKILL.md`, `provenance.yaml`, `evals/evals.json`; 2 unresolved questions printed."

## Browser review (Step 5)

| Action | Who | What to record |
|---|---|---|
| Contributor opens the draft PR in GitHub web UI | Contributor | Time spent, whether they could understand the files, questions asked |
| Contributor comments on the draft PR (no terminal) | Contributor | Screenshots or copy‑paste of web UI, any confusion noted |
| Maintainer converts draft → ready → merge (after domain review) | Maintainer | Time taken, decision |

**Transcript section**: "Browser review – <date>; contributor spent 15 min on the PR; could locate `SKILL.md` but asked what `method_status` means. Maintainer converted to ready and merged."

## Contract CI (Step 6)

| Action | Who | What to record |
|---|---|---|
| Run `bash .github/workflows/validate-skills.sh` on the draft PR | Maintainer | Full output, exit code, any failures |
| Contributor reviews the check run (no terminal) | Contributor | Whether the plain‑language messages were comprehensible |
| Any fix the contributor applied without a terminal | Contributor | Description of the fix |

**Transcript section**: "CI – <date>; `validate-skills.sh` exited 0; 9 skills validated, catalog current, 0 broken links, 0 secret patterns. Contributor understood all messages."

## Domain review (Step 7)

| Action | Who | What to record |
|---|---|---|
| Named domain expert reviews the merged PR | Domain expert | Time spent, units checked, assumptions verified, citations verified, eval adequacy |
| Review decision: accept / request‑changes / decline | Domain expert | Rationale in PR comment |
| Decision recorded in PR | Domain expert | Exact comment text |

**Transcript section**: "Domain review – <date>; expert <name> accepted the skill after verifying mass‑balance equations and citing [EPANET 2.2]; no changes requested."

## Transcript compilation and verdict

After step 7, compile all sections above into a single markdown file `pilot-transcripts/<issue-number>.md`. The file must contain:

1. A one‑sentence summary of the problem.
2. The seven sections above (recruitment through domain review).
3. A final verdict line:
   - `verdict: supported` – if all pass conditions are met (see below).
   - `verdict: designed, not validated` – if any pass condition fails or the pilot was not completed.

### Pass conditions (what makes the verdict `supported`)

| # | Condition | What is recorded |
|---|---|---|
| 1 | Contributor completed the issue form without terminal help | Form‑fill transcript section exists and all required fields are present. |
| 2 | Triage produced an `accepted` decision with documented rationale | Triage transcript section with label `accepted` and reason. |
| 3 | `water-skills new --from-issue` created a branch + `SKILL.md` + `provenance.yaml` + `evals/evals.json` in under 30 min | Scaffold transcript with branch name and file list + time. |
| 4 | Contributor could review the draft PR in the browser and report what they understood | Browser‑review transcript with contributor quotes. |
| 5 | `validate-skills.sh` passed on the draft (exit 0) and contributor understood the messages | CI transcript with exit code and contributor summary. |
| 6 | A named domain expert accepted the skill (or requested changes that were promptly applied) | Domain‑review transcript with expert name and decision. |

If **all six** pass conditions are met, the verdict is `supported` and the runway may be updated accordingly. If any pass condition is missing, the verdict is `designed, not validated` and the blocker is documented in the runway status.

## What to do with the verdict

- `supported`: Update `CONTRIBUTING.md` and `docs/guides/no-git-workflow.md` status badge from `designed, not validated` to `supported`. Add the skill to the catalog as `review_status: reviewed` if appropriate. Enable read‑only intake/scaffold agent specs (the agents already created) with the label `active`.
- `designed, not validated`: Keep the runway as-is. Document the specific failed pass condition(s). Do **not** enable agent automation for intake/scaffold beyond the read‑only recommendation already in place. Plan a follow‑up pilot or iterate the form/scaffold logic.

## Template file location

`src/content/docs/guides/pilot-transcripts/<issue-number>.md`

Example: `src/content/docs/guides/pilot-transcripts/42.md` for issue \#42.