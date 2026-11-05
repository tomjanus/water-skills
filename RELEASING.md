# Releasing water-skills

This repository uses one repository-wide semantic version. The annotated Git tag
`vX.Y.Z` is the release source of truth. Individual skills do not have
independent versions.

Active work lands on `dev`; releases flow through `main`. GitHub Pages deploys
from `main` only. The first release target is `v0.1.0`.

## Human approval gate

No public release action is automatic. Before merging to `main`, tagging, and
publishing a GitHub release, a maintainer must review and approve:

- the complete release-candidate diff;
- the public documentation and README claims;
- the changelog and proposed release notes;
- the verification results and any known limitations.

Approval to prepare a release candidate does not authorize the merge, tag,
GitHub release, or Pages deployment. Those actions require a separate explicit
decision. Agents and automation may prepare a candidate and report results, but
must not approve or publish it.

## Required checks

Run these from a clean checkout at the candidate revision:

```bash
bash .github/workflows/validate-skills.sh
python scripts/generate_catalog.py --check
python -m unittest discover -s tests -v
npm ci
npm run build
npm audit --audit-level=high
```

Also confirm:

- no page or README link uses the former repository-owner URL;
- `assets/banner.jpg` exists and renders in the built site;
- built HTML uses the `/water-skills/` asset and route prefix;
- no built page contains broken `../guides`, `./0N-`, or missing repository-file
  links;
- the catalog is deterministic on a second generation run;
- a clean-clone or clean-room copy passes the validator, tests, `npm ci`, and
  the docs build;
- no unrelated worktree changes are included.

Record the exact commands and results in the release-candidate report. Do not
claim a check passed unless it was run.

## Release procedure

1. Verify the release candidate locally and obtain maintainer approval of the
   complete diff, public claims, changelog, and release notes.
2. Merge the approved `dev` state to `main` through the established review
   path.
3. Create an annotated tag on `main`:

   ```bash
   git tag -a v0.1.0 -m "water-skills v0.1.0"
   git push origin main v0.1.0
   ```

4. Publish the GitHub release from the approved changelog entry.
5. Let the Pages workflow deploy from `main`.
6. Verify the live documentation URL, catalog links, tutorial navigation, and
   release notes.

Do not push, tag, publish, or deploy from an unapproved branch state.

## Rollback

If a release is defective, stop and obtain explicit maintainer approval before
changing public state. Preferred recovery is a new reverting commit on `main`.
Re-pointing or deleting a tag, force-pushing, or rewriting history requires
explicit maintainer approval and must not be done silently.

## Branches and deployment

- `dev` is the integration branch for active work.
- `main` is the released branch.
- `.github/workflows/deploy-docs.yml` deploys GitHub Pages from `main` only.
- Pull requests validate the docs build in CI, but do not deploy it.

## Versioning

Use semantic versioning:

- `MAJOR` for incompatible changes to documented repository contracts;
- `MINOR` for backwards-compatible capabilities;
- `PATCH` for backwards-compatible corrections.

Move the prepared entries from `## [Unreleased]` in
[`CHANGELOG.md`](CHANGELOG.md) under the release date only when the release is
approved. Do not invent a release date before then.
