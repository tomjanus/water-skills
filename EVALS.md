# Evaluations

An evaluation specification describes a task, expected outcome, and checks for a skill-shaped behavior. A captured run records what an agent actually did for that task under a named condition. A specification is a test design, not a result.

## Repository policy

- Behavior-shaping skill changes require a relevant evaluation specification. Documentation-only changes do not require behavioral evals.
- Validate the specification with `python evals/runner.py --validate`.
- Report captured runs, model, agent harness, software versions, conditions, and trial count when those runs were performed. Do not invent or imply results when there are no captures.
- Format validation and eval-spec validation do not establish skill usefulness, engineering correctness, or scientific validity.

## Runner boundary

The repository runner validates evaluation specifications and grades **captured artifacts**. It does not launch an agent or capture agent-harness sessions. The CLI capture adapter runs a supplied command without a shell and records its outputs; the manual adapter prepares a trial directory and guide for a human-run task. Neither launches agents, captures API sessions, or operates GUI applications. Missing captures mean there is no behavioral result to interpret.

New run metadata follows the additive V1 contract in [`evals/schema.py`](evals/schema.py). Required fields are `task_id`, `condition`, `trial`, `model`, and `timestamp`; captures also record `schema_version`. Optional metadata includes agent/evaluation harness identity and version, skill revision, software/OS information, licence mode, cost, and elapsed time. Unknown fields are allowed. The runner uses well-formed object metadata for report enrichment but does not fail grading when metadata is missing or malformed.

## GUI evaluation status: planned

GUI evaluation is not currently available: there is no confirmed approved VM, software licence, or independently checkable application-export path, and no GUI run has been performed. Do not claim GUI support as validated or available.

Any future GUI evaluation requires an approved licence and host, a clean VM snapshot per trial, and exported application state that can be checked independently. Record OS/application version, locale, display configuration, and licence mode. Grade exported state rather than click sequences or screenshot similarity; use screenshots and action traces only for diagnosis. Redact client/network data. GUI evaluations must remain outside ordinary PR CI and use a maintainer-dispatched or explicitly gated workflow with resource caps.

## Add an evaluation specification

1. Put `evals/evals.json` under the skill directory.
2. Use stable case IDs, concrete prompts, expected outcomes, and checks that can distinguish successful from unsuccessful behavior.
3. Add only required fixtures and scripts under `evals/files/` and `evals/scripts/`.
4. Use deterministic assertions where possible. Bare sentence assertions require the optional judge and are not deterministic.
5. Run `python evals/runner.py --validate` and report its exact output.
6. Run behavioral trials only when captures are available; save them under `evals/runs/` and report conditions and limitations.

## Useful commands

```bash
python evals/runner.py --validate
python evals/runner.py --list
python evals/runner.py --skill <name> --all-conditions
python evals/runner.py --skill <name> --conditions with_skill --compare <other-name>
```

See [`evals/README.md`](evals/README.md) for the suite schema, artifact layout, and assertion syntax.
