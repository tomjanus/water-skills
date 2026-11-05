# Stage 5 plan — Curation, generated catalog, and lifecycle

**Status:** complete — implementation, repository validation, and local Astro docs build finished
**Source plan:** [`parent-repo-implementation-plan.md`](parent-repo-implementation-plan.md)
**Execution protocol:** [`agentic-implementation-prompt.md`](agentic-implementation-prompt.md)
**Prior stage:** [`plan_stage_4.md`](plan_stage_4.md)

## Objective

Use verified metadata and evidence to make the collection trustworthy and searchable: generate the catalog from canonical sources, enforce duplicate/name/alias checks, expose lifecycle and review status, and report staleness so review work is visible rather than silently lost. A controlled taxonomy is deferred.

## Verified current state

- 9 skills validate; 9 eval suites contain 24 cases; all pass the repository validator.
- `provenance.schema.json` exists and is the Stage 1 authority. Required fields: `authors` (non-empty string array) and `method_status` (`established`, `adapted`, `heuristic`, `hypothesis`). Optional: `references`, `software_tested`, `reviewers`, `evidence`, `review_status` (`not_reviewed`, `under_review`, `reviewed`). A `reviewed` record requires at least one reviewer.
- No per-skill `provenance.yaml` records are present yet; the validator reports this explicitly.
- `contributing/SCAFFOLD_SPEC.md` is stale relative to the schema. It uses `schema_version`, `title`, `summary`, `version`, `domain`, `software`, object-shaped `authors`, `method_type` (`established_method`, `adapted_method`, `novel_method`), `review_status: unreviewed`, `last_reviewed`, `supersedes`, `superseded_by`, `aliases`, and `ai_assistance`. Several names and vocabularies conflict with the canonical schema.
- `scripts/water_skills.py` already renders scaffold provenance with catalog-oriented fields, so the scaffold and the validator currently disagree.
- `README.md` states that a generated catalog is planned for Stage 5; the docs site has no catalog page.
- Lifecycle language already exists in `contributing/ISSUE_TRIAGE.md` and `src/content/docs/guides/review-and-lifecycle.md`: states `publish`, `finish`, `archive`, `duplicate`, `unknown`; review status is separate.
- The docs site is Astro/Starlight with 16 content files. `node_modules` is absent, so a local docs build is not currently possible without installing dependencies.

## Proposed design

### 1. Canonical metadata contract

Resolve the schema conflict before writing the generator.

- Keep `provenance.schema.json` as the authority for provenance and review fields.
- Add optional catalog fields to the schema (required fields unchanged): `title`, `summary`, `status`, `aliases`, `supersedes`, `superseded_by`, `last_reviewed`, and `review_interval_days`.
- Represent catalog software with the existing `software_tested` field; do not add a duplicate `software` field.
- Defer the taxonomy and the `domain` field until a controlled vocabulary is approved.
- Update `contributing/SCAFFOLD_SPEC.md` and `scripts/water_skills.py` to use the canonical names and vocabularies.
- Do not silently reinterpret `method_type` as `method_status`; either migrate the scaffold output or document the mapping explicitly.
- Keep provenance values evidence-gated. Missing values stay missing; the catalog reports them as gaps.

### 2. Generated catalog

Add `scripts/generate_catalog.py` using only the Python standard library.

Inputs:

- `SKILL.md` frontmatter: `name`, `description`.
- `provenance.yaml` when present.
- Eval suite metadata: case count and suite trial count. Captured reports remain outside the checked-in catalog.
- Repository state: directory path, lifecycle status, and review status.

Outputs:

- `catalog/catalog.json`: deterministic, sorted by skill name, stable formatting, no wall-clock timestamps.
- `src/content/docs/catalog/index.md`: generated catalog page for Starlight.
- `README.md`: generated section between explicit `<!-- catalog:start -->` and `<!-- catalog:end -->` markers.
- `catalog/staleness.json` and a readable staleness section: skills due or unknown for review.

The generator must be byte-identical on repeated runs and must not use the network.

### 3. Deterministic checks

The generator validates the catalog before writing it:

- Exact-name collisions and directory/name mismatches.
- Alias uniqueness and conflicts with skill names.
- `supersedes`/`superseded_by` symmetry and target existence.
- Taxonomy membership is deferred with the taxonomy decision.
- Duplicate `description`/`summary` values, using deterministic normalization only.
- Status consistency: `reviewed` requires reviewers; lifecycle status is one of the approved values.
- Missing provenance is a reported gap, not an invented record and not a hard catalog failure.

### 4. Lifecycle and staleness

- Treat lifecycle state (`publish`, `finish`, `archive`, `duplicate`, `unknown`) and review status (`not_reviewed`, `under_review`, `reviewed`) as separate axes.
- Validate state values and supersedes links; do not auto-transition. Maintainers retain archive, rename, review, and publish authority.
- Staleness: use `last_reviewed` plus `review_interval_days` (default 180). A null `last_reviewed` yields `review_due: unknown`, not a fabricated date.
- Stale skills stay in the catalog and appear in the staleness report as review work. CI reports and warns, and does not fail unrelated pull requests.

### 5. CI and docs

- Extend `.github/workflows/validate-skills.sh` with a catalog regeneration step and a diff check on the generated files, or add a separate dependency-free CI job if that keeps the shell validator readable.
- Add the generated catalog page to the Starlight sidebar in `astro.config.mjs`.
- Update `README.md` to link the catalog and keep the generated block marker-delimited.
- Update `src/content/docs/guides/review-and-lifecycle.md` and the review tutorial to describe the generated catalog, status axes, and staleness.
- Do not hand-maintain the catalog, duplicate list, or evidence badges.

### 6. Tests

Add tests using synthetic temporary skill trees and the real repository:

- Deterministic output and stable ordering.
- Alias collision and alias resolution.
- Duplicate name and directory/name mismatch detection.
- `supersedes`/`superseded_by` symmetry.
- Missing provenance handling.
- Lifecycle validation and staleness calculation, including null `last_reviewed`.
- Generated real-repository catalog matches the checked-in files.
- Existing tests remain green.

## Phased checklist

### Phase 5a — contract decisions (approval gate)

- [x] Extend `provenance.schema.json` with optional catalog fields; keep required fields unchanged.
- [x] Defer the taxonomy vocabulary and `domain` field until a later decision.
- [x] Include skills without provenance, marked with an explicit `not_recorded` gap.
- [x] Use a 180-day staleness default; null `last_reviewed` means `unknown`; warn in CI rather than fail unrelated PRs.
- [x] Approve the generated docs page, README markers, and sidebar entry.
- [x] Enable and run the Astro docs build locally after dependency installation was approved; `npm ci` and `npm run build` pass.
- [x] Extend the existing validator with a catalog-freshness check.

### Phase 5b — generator and checks

- [x] Reconcile `provenance.schema.json`, `contributing/SCAFFOLD_SPEC.md`, and `scripts/water_skills.py`.
- [x] Implement `scripts/generate_catalog.py` and the deterministic checks.
- [x] Implement the staleness report and `scripts/check_staleness.py`.
- [x] Add synthetic-fixture tests and a real-repository freshness check.

### Phase 5c — CI, docs, README

- [x] Wire catalog regeneration and freshness checking into CI.
- [x] Generate `catalog/catalog.json`, `catalog/staleness.json`, and `src/content/docs/catalog/index.md`.
- [x] Add the catalog to the Starlight sidebar and README markers.
- [x] Update the lifecycle and review documentation.
- [x] Verify link checks and build the Astro docs locally; the Pages workflow's `npm ci` is reproducible from the new lockfile.

### Phase 5d — validation and report

- [x] Run the full repository validator and all tests.
- [x] Confirm deterministic regeneration with a clean second run.
- [x] Confirm no hand-maintained catalog or duplicate list remains.
- [x] Record exact commands, outputs, risks, and the Stage 5 completion state.

## Acceptance mapping

| Parent-plan acceptance criterion | Planned evidence |
|---|---|
| Catalog regeneration is deterministic and checked in CI | Generator is byte-identical on repeat; CI runs `generate_catalog.py --check` against the checked-in outputs |
| No hand-maintained duplicate skill list | Duplicate/name checks derive from the directory scan; catalog is generated, not edited |
| Aliases preserve an approved rename | Alias validation resolves to an existing skill; synthetic rename test proves the old name still resolves |
| Status/evidence wording matches actual run data | Catalog reads provenance and eval suite metadata; tests reject hard-coded pass claims; missing evidence is shown as missing |
| Stale items create review work rather than disappearing | Staleness report lists due/unknown items; catalog keeps them visible |

## Resolved decisions

1. **Schema reconciliation:** extend `provenance.schema.json` with optional catalog fields; keep the required fields unchanged and update the scaffold spec/CLI.
2. **Taxonomy:** deferred. Do not add a controlled vocabulary or `domain` field yet.
3. **Skills without provenance:** include them with `provenance_status: not_recorded` and a warning; do not invent authors or evidence.
4. **Staleness policy:** default 180 days; null `last_reviewed` means `unknown`; publish the report and warn in CI rather than fail unrelated PRs.
5. **Eval evidence:** the checked-in catalog includes eval suite case and trial counts only. Captured report summaries remain gitignored and are not embedded, preserving deterministic regeneration.

## Remaining implementation assumptions

- **Docs build:** use the checked-in `package-lock.json` with `npm ci`; the content collection is declared in `src/content/config.ts`.
- **CI placement:** extend `.github/workflows/validate-skills.sh` to keep one dependency-free entry point.

## Guardrails

- Do not invent authors, reviewers, references, evidence, lifecycle decisions, or validation claims.
- Do not archive, rename, or publish any skill without explicit maintainer approval.
- Do not add dependencies or use the network in the generator.
- Do not modify unrelated files or hand-edit generated outputs.
- Preserve the existing worktree; no staging, commit, push, or pull request without explicit approval.
- Keep GUI evaluation marked planned and do not claim screenshot-based validation.

## Assumptions

- The catalog can be generated before every skill has a provenance record, provided gaps are explicit.
- The generated catalog and staleness report are tracked repository artifacts, while full eval captures and reports remain gitignored.
- Deterministic normalization is sufficient for duplicate detection; semantic embeddings are deferred until catalog size and real failures justify them.

## Stage record

- **Implementation:** added `scripts/generate_catalog.py` and `scripts/check_staleness.py`; extended `provenance.schema.json`, `scripts/check_provenance.py`, `scripts/water_skills.py`, `contributing/SCAFFOLD_SPEC.md`, the CI validator, the Starlight sidebar, README, and the lifecycle docs. Enabled reproducible Astro installs with `package-lock.json`, declared the Starlight docs collection, corrected the Starlight `social` config shape, and ignored Astro's generated `.astro/` cache.
- **Generated outputs:** `catalog/catalog.json` (9 skills, 24 eval cases), `catalog/staleness.json` (9 unknown review dates), `src/content/docs/catalog/index.md`, and the README catalog block.
- **Validation command:** `bash .github/workflows/validate-skills.sh` — exit 0.
  - 9 skills valid; 9 eval suites/24 cases valid.
  - Layout: 9 directories checked; 6 pre-existing empty optional directories warned.
  - Provenance: schema valid; no per-skill records present.
  - Catalog freshness: `generate_catalog.py --check` reports current.
  - Staleness: 9 warnings for unrecorded `last_reviewed`; exit 0.
  - Local Markdown links: 30 files, 72 links checked.
  - Secret scan: no selected high-confidence credential patterns.
  - Tests: 88 passed (69 existing + 19 catalog/staleness).
- **Determinism:** a second `generate_catalog.py --check` reports current; generated files contain no absolute paths or wall-clock timestamps.
- **Astro build:** `npm ci && npm run build` succeeded; Astro generated 18 pages (17 docs pages plus 404), and Pagefind indexed 17 docs pages. Sitemap generation was skipped because `astro.config.mjs` has no `site` URL.
- **Dependency audit:** npm reported 9 vulnerabilities (4 moderate, 4 high, 1 critical); npm's suggested fix requires a breaking Astro major upgrade, which was not applied.
- **Worktree:** Stage 5 files are staged for review; no commit or push was made. Pre-existing tracked deletions and unrelated untracked user files remain untouched.
- **Execution state:** Stage 5 complete. Stage 6 (distribution and release) has not started.
