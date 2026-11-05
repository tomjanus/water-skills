# Changelog

All notable changes to this repository are recorded here. The project uses one
repository-wide semantic version; see [`RELEASING.md`](RELEASING.md).

## [Unreleased]

### Added

- No-git authoring runway: proposal issue forms, repository guidance, and the
  `water-skills new --from-issue <number>` scaffold command (Stage 2).
- Eight-lesson ramp-on curriculum with a no-git/no-agent track and an
  engineering/agent track (Stage 3).
- Evaluation harness metadata, CLI and manual capture adapters, same-task paired
  grading, trial variance, cost and time reporting, and documented GUI limits
  (Stage 4).
- Generated skill catalog, provenance/review fields, staleness report, and
  Starlight documentation site (Stage 5).
- Release policy in [`RELEASING.md`](RELEASING.md) and this changelog.
- Documentation link checks and a pull-request docs build job.
- Centered README banner and release/changelog links.

### Changed

- Renamed the `skill-eval-writing` skill to `eval-writing`. Existing references
  now use the current name. No alias is provided because no provenance record
  exists for the former name.
- Corrected repository URLs, documentation route links, and documentation links
  to repository files outside the docs tree.
- Corrected README capability claims: the no-git contribution path is
  `designed, not validated`; the ramp-on curriculum is `supported`.
- Generated catalog links now target `main`, the released branch.

### Known limitations

- The no-git authoring runway has not been validated with a real pilot
  contributor. It remains labelled `designed, not validated`.
- No per-skill provenance records, named domain reviewers, or reviewer evidence
  are present yet; the catalog reports these gaps explicitly.
- GUI evaluation remains planned. No approved GUI VM, licence, or independently
  checkable application-export path is recorded.
- Behavioral evaluation results are limited to the captured runs documented in
  Stage 4. Format and eval-spec validation do not establish scientific or
  domain correctness.
- Public release, tagging, and GitHub Pages deployment remain subject to the
  maintainer approval gate.
