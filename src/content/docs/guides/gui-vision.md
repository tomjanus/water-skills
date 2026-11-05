# GUI evaluation – vision and future expansion

## Current status (Nov 2026)

- **No approved GUI VM, licence, or independently checkable export path** exists for any target application (EPANET, HAMMER, GPS‑X, etc.).
- **GUI evaluation is not currently available** – the runner grades captured artifacts only; there is no deterministic grading of GUI click paths or pixel matching.
- All GUI‑related claims in the README and catalog are **explicitly marked `planned`** and carry a documented blocker.

## Why GUI evaluation is hard for water engineers

- Vendor UIs vary between versions and operating systems; fixed click‑path checks fail on minor dialog updates.
- Agents may reach valid outcomes through different navigation sequences; correctness must be judged on **exported state and reports**, not on UI mechanics.
- Proprietary installers, licence keys, and vendor binaries **must never** be committed to git.
- Screenshots and transcripts must be **redacted** of client names, network locations, and personal data before saving.

## Vision for GUI evaluation (when approved)

| Component | Requirement | Owner |
|---|---|---|
| **Clean VM snapshot per trial** | Brought‑your‑own licence; reset between trials; no shared licence state | Maintainer / licensed partner |
| **Exported state / reports** | Node pressures, mass‑balance summaries, database dumps, CSV/JSON exports; a completion dialog is **not** an outcome | Agent harness / capture adapter |
| **Redacted screenshots / action logs** | Diagnostic only, never primary correctness evidence; client/network data removed | Maintainer / reviewer |
| **Licence mode** | Recorded in `metadata.json`; never stored as a key or installer in git | Maintainer |
| **OS / app version / locale / display configuration** | Recorded in `metadata.json` for each trial | Maintainer |
| **Evaluation tier** | Tier 4 (human) for new GUI skills, new method claims, or calibration samples; tier 3 (label‑gated/nightly) only after a licence/host is approved | Maintainer + CI config |

## Near‑future roadmap

1. **Confirm a licensed environment** – Identify one target application (e.g., EPANET with a documented CLI path) and secure a bring‑your‑own‑licence VM image.
2. **Add a `manual` capture adapter** – Write an `evals/capture/manual.py` that:
   - Spins up the approved VM,
   - Runs the task,
   - Exports the state/report,
   - Writes a redacted transcript and,
   - Records `metadata.json` with OS, app version, licence mode, and trial count.
3. **Add tier‑3 label‑gated workflow** – `.github/workflows/evals-nightly.yml` that runs the manual adapter on a **label‑gated** basis (only issues labelled `run-gui-evals`).
4. **Add tier‑4 human review** – After a nightly run, a named domain expert reads the transcript and inspects the exported outcome; the review result is recorded in the report.
5. **Publish the first GUI‑capable skill** – Once the above is in place, a skill that targets the approved GUI may be marked `review_status: reviewed` with a named domain reviewer.
6. **Iterate** – After the first GUI skill, evaluate whether to add support for additional applications; keep the gate strict: **no GUI agent work without an approved licence and export path**.

## What stays “planned” until step 1

- Any agent or CI job that claims GUI evaluation **without** an approved licence/VM/export path.
- The `gui-vision.md` document itself, which records the blocker and the roadmap.
- All GUI‑related claims in the README and catalog remain `planned` with a link to this vision doc.

## How to teach contributors

- State clearly: “GUI evaluation is not available. If you need a GUI skill, file an issue labelled `run-gui-evals` and a maintainer will assess licence availability.”
- Do **not** write GUI‑grade assertions in `evals.json` unless an approved adapter exists.
- When a licence is secured, update `gui-vision.md` to reflect the new capability and move the relevant skills from `planned` to `supported`.

## Summary

- **Now**: deterministic CLI and manual capture adapters only; GUI evaluation **planned**.
- **Next**: secure a licensed environment, add a manual capture adapter, add nightly label‑gated workflow, then add tier‑4 human review.
- **Goal**: a small, controlled set of GUI‑capable skills with full auditability, never bundled installers or keys in git.