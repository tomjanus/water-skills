# Repository roadmap

## Philosophy

`water-skills` exists to transfer **expert water‑engineering knowledge** that a capable model does **not** have. Every skill must pass the **knowledge‑delta test** (“what would the model get wrong without this skill?”) and be **terse, layered, and labelled** (established / adapted / heuristic / hypothesis). The repository is **not** a general‑purpose skill marketplace; it is a focused, evidence‑backed collection for hydraulic and water‑resource engineering.

## Current state (Nov 2026)

| Layer | Status | Evidence |
|---|---|---|
| **Contract** | ✅ `agentskills` validator in CI; schema‑validated `SKILL.md` frontmatter | Every PR gets an immediate, plain‑language verdict |
| **Authoring runway** | 🟡 Designed, not validated – issue form + `water-skills new --from-issue --dry-run` exist; no real no‑git pilot yet |
| **Evidence** | 🟡 Partial – `evals/runner.py` grades captured runs; one paired `skill‑writing` run exists; no behavioural lift reported in CI |
| **Curation** | ✅ Catalog generated from `SKILL.md` frontmatter, `provenance.yaml`, and `evals/evals.json`; staleness report exists; no hand‑maintained skill list |
| **Distribution** | ✅ v0.1.0 released; GitHub Pages live at <https://tomjanus.github.io/water-skills/>; `RELEASING.md` human gate |
| **Agentic maintenance** | 🟡 Stage 7 plan finalised (read‑only roles first, intake/scaffold after pilot, release assistant never publishes) |

## Phased roadmap (as described in the parent‑repo implementation plan)

| Phase | Deliverables | Acceptance |
|---|---|---|
| **0. Contract** | Schemas; `provenance.yaml` for every skill; `water-skills validate` aggregates `agentskills`, schema, links, line budget, and secrets; blocking CI | Every existing skill validates; every failure message includes what, why, and fix; no false positives on the current collection |
| **1. Authoring runway** | Issue forms; template; `water-skills new`; scaffold workflow; “write a skill in 15 minutes” guide; **pilot** with one water engineer who has no git experience | One water engineer completes a draft PR end‑to‑end, the agent asks only domain questions |
| **2. Evidence** | Capture adapters for Claude Code and OpenCode; report schema; routing checks; label‑gated and nightly workflows; evidence badge | One skill has a discriminating case and a published report; CI catches a deliberate regression; a full run stays within the token budget |
| **3. Curation** | Catalog generation; taxonomy; duplicate and collision checks; lifecycle; staleness and link‑rot bot | Catalog site regenerates from source; a duplicate proposal is blocked with a useful message; a stale skill opens an issue automatically |
| **4. Distribution & community** | Docs site; `skills.sh` listing; plugin marketplace; per‑skill release workflow; contributor recognition; office hours | Install works from a clean machine; first external contributor is merged; release is tagged and documented |
| **5. Boundary bets** (ongoing) | Transcript‑to‑skill compiler; semantic dedupe; composition graph; cross‑harness leaderboard; skill doctor | One bet ships with a measured impact on contributor time, review load, or eval quality |

## What is “supported”, “designed, not validated”, and “planned”

| Status | Meaning | When it becomes `supported` |
|---|---|---|
| **supported** | Implemented and verified (e.g., contract checks, catalogue generation, Pages deployment) | CI passes, human pilot completed where applicable |
| **designed, not validated** | Implemented or documented, but not yet validated with the intended users (e.g., authoring runway, no‑git pilot) | Pilot completed and recorded |
| **planned** | Documented, not yet built (e.g., GUI evaluation, per‑skill versioning, GUI‑specific adapters) | Blocker resolved (licence, VM, export path) or explicitly deferred |

## Explicit open decisions (do not resolve by invention)

1. **Which skill directories are to be published, finished, renamed with aliases, or archived?** – Decision belongs to the maintainer; keep a catalog of choices.
2. **Canonical provenance filename and method‑status vocabulary** – `provenance.yaml` with `method_status: established \| adapted \| heuristic \| hypothesis`; do not invent new statuses.
3. **Which docs platform is approved, and is a hosted docs site required for v1?** – `MkDocs Material` is the working default; a hosted site is not required yet.
4. **Which agent harnesses can be tested end‑to‑end in the available environment?** – Claude Code and OpenCode are the current candidates; any new harness must pass the exact clean‑session acceptance transcript in `AGENTS.md`.
5. **Who is the first no‑git pilot contributor, and who are the named domain reviewers?** – Not yet assigned; record when decided.
6. **What are the live‑eval monthly token and time budgets?** – Not yet set; will be configured before any label‑gated or nightly model‑graded runs.
7. **Is an approved GUI VM/license available for any target application?** – No; GUI evaluation remains `planned` until a licence/host is secured.
8. **Are skills independently versioned, and what public distribution channels are authorized for v1?** – `RELEASING.md` uses one repository‑wide SemVer; per‑skill versions are not yet authorized.

## How the roadmap is maintained

- **Every six months** the maintainer reviews the table above, updates the “Current state” column, and moves any `planned` items to `supported` or `designed, not validated` as appropriate.
- **Any new decision** (e.g., adding a new harness, changing the docs stack) is recorded as an explicit open decision in this file, not as an implicit assumption.
- **The roadmap is human‑driven** – no agent may autonomously promote a `planned` item to `supported` without a recorded pilot or maintainer sign‑off.

## Relation to other documents

- `RELEASING.md` – release policy and human gate; overrides any versioning ambiguity.
- `AGENTS.md` – binding contributor rules; any agent work must respect its gates.
- `CONTRIBUTING.md` – contribution process; must be consistent with the roadmap’s “supported” statuses.
- `skills/skill-writing/SKILL.md` – skill format; any new skill must obey its progressive‑disclosure layout.
- `evals/README.md` – eval contract; any new eval type must respect the V1 metadata schema.

## How to contribute to the roadmap

- **File an issue** tagged `roadmap` with a proposed change, the decision it affects, and the evidence or pilot result that supports it.
- **Do not** silently change a status from `planned` to `supported` without a recorded pilot or maintainer sign‑off.
- **If you are a domain reviewer**, record your review in the skill’s `provenance.yaml` and update the catalog’s `review_status` accordingly.