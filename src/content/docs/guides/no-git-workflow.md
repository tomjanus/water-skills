# Contribute without git – full workflow guide

## Quick start

1. **Open the issue form** – Go to the repository **Issues** tab, click **New issue**, and choose **Propose a skill**. Two variants are available:
   - [`propose-skill.yml`](https://github.com/tomjanus/water-skills/blob/main/.github/ISSUE_TEMPLATE/propose-skill.yml) – structured form with dropdowns and required fields.
   - [`propose-skill.md`](https://github.com/tomjanus/water-skills/blob/main/.github/ISSUE_TEMPLATE/propose-skill.md) – Markdown variant with the same fields.

2. **Fill in what automation cannot infer** – The form asks only for domain knowledge:
   - **Domain** – the water‑engineering area (e.g., hydraulic modelling, water quality, transient analysis)
   - **Problem** – the real task or failure you experienced
   - **Prompt** – what you would ask an agent to do
   - **Expected output** – what success looks like
   - **Inputs** – required data, files, or model inputs
   - **Software version** – the engineering software and version you actually used
   - **References** – manuals, standards, or internal documents that define correct practice
   - **Optional transcript** – a real session transcript, if you have one (remove credentials and confidential data)

3. **Triage** – A maintainer reviews the issue using the label set from `contributing/ISSUE_TRIAGE.md`:
   - `proposal` – new skill proposal
   - `needs-triage` – awaiting maintainer review
   - `needs-info` – problem, prompt, or expected result missing or incomplete
   - `accepted` – real problem, in scope, not a duplicate, reviewer available
   - `declined` – out of scope, duplicate, or not a real problem
   - `scaffolded` – draft PR exists (applied by maintainer or bot)
   - `domain-review` – ready for a named expert
   - `stale` – no response for 30 days

4. **Scaffold** – If the issue is **accepted**, a maintainer runs:
   ```bash
   water-skills new --from-issue <number> --dry-run
   ```
   This prints the planned files and unresolved questions **without changing the tree**. Review the output; if satisfied, run without `--dry-run`:
   ```bash
   water-skills new --from-issue <number>
   ```
   This creates a feature branch `skill/<number>-<slug>`, writes `SKILL.md`, `provenance.yaml`, and `evals/evals.json`, stages and commits the files, and prints instructions for opening a draft pull request on GitHub.

5. **Review the draft** – The draft PR appears in the web interface. You can review it in the browser — no terminal needed. A maintainer converts it from **draft** to **ready for review** and merges it after human and domain review.

## What is available today vs. what remains manual

| Aspect | Today (designed, not validated) | Near future (after pilot) |
|---|---|---|
| Issue form + dry‑run | ✅ fully functional | – |
| `water-skills new --from-issue` (write mode) | ✅ functional, creates branch + files | – |
| Draft PR automation | ✅ created, but **not** auto‑merged | Maintainer converts draft → ready → merge after human/domain review |
| Bot‑only scaffold (no human intervention) | ❌ not implemented | ✅ planned after pilot |
| Auto‑merge / self‑approval | ❌ blocked by `AGENTS.md` and `RELEASING.md` | – |
| Real no‑git pilot (end‑to‑end) | ❌ not yet run | ✅ pilot recruitment & execution (Step 7 in pilot plan) |

## Current status (Nov 2026)

- The issue form, dry‑run, and `water-skills new` command are **implemented and usable**.
- No real‑world pilot has been run yet; the runway is **labelled `designed, not validated`** (per `RELEASING.md` / `CHANGELOG.md`).
- The draft‑PR‑to‑merge path requires a maintainer’s manual step; there is **no auto‑merge**.
- Intake/scaffold agents (read‑only recommendation only) may suggest labels and file lists, but **must not** create branches or open PRs until a pilot is completed.

## Near‑future roadmap (after pilot)

1. **Run one real no‑git pilot** with a water engineer who has a recent problem they want to solve.
2. **Record the pilot transcript** (what form fields were filled, how long it took, any confusion, bot failures, reviewer work).
3. **Decide on automation level**:
   - If the pilot succeeds, add a read‑only intake/scaffold agent that emits labels and planned file lists (still human‑approved).
   - If the pilot uncovers gaps, document them and iterate the form or the `water-skills new` logic.
4. **Update `CONTRIBUTING.md` and this guide** to reflect the new validated state (change status from `designed, not validated` to `supported` where appropriate).

## How to teach new contributors

- Point new contributors to this guide first.
- Have them open the issue form and fill only the required fields (problem, prompt, expected). The form is designed so that **no terminal, git, or agent knowledge is required**.
- After the form is submitted, show them the triage labels and what happens next (maintainer reviews, scaffold command, draft PR).
- Reference the `water-skills new --from-issue` command output as the “planned files” step.
- Mention that the **real pilot** is the gate before any bot‑only automation is enabled.

## Where we are going

- After one successful pilot, the runway will move from `designed, not validated` to `supported`.
- At that point, read‑only intake/scaffold agents may be enabled to suggest labels and file lists, but **all branch/PR creation remains a manual maintainer step**.
- Longer term, the community may vote to add limited bot‑only automation (e.g., auto‑creating a draft PR from a fully‑filled form), but **any such change must pass a human gate** and be documented in `RELEASING.md`'s human‑approval clause.