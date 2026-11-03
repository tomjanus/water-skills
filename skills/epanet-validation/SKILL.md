---
name: epanet-validation
description: Parse EPANET INP or WNTR JSON inputs and review epanetparser structural/static findings. Use for file-format, model-structure, or ruleset checks; request simulation-layer checks only when explicitly needed. WNTR engineering workflows belong to wntr-engineering.
---

# EPANET model validation

Use the external [`epanetparser`](https://github.com/tomjanus/epanetparser) tool for EPANET INP and WNTR JSON models. It is not bundled here; use the user's existing environment and the tool's current documentation. Keep parsing, static rules, and optional simulation results distinct in both actions and reporting.

## Procedure

1. **Define the check.** Identify the input model, format, its source/version if known, and the intended application or simulator. Ask which project-specific rules apply if that choice changes what counts as acceptable. Preserve an untouched input copy or record its checksum before any repair. This step is complete when the file and requested scope are explicit.
2. **Check tool availability and rulesets.** Inspect the installed `epanetparser` version and its `validate` help and available rulesets (`epanetparser --version`, `epanetparser validate --help`, `epanetparser info --list-rulesets`). If the tool is absent, report the documented installation route and obtain permission before changing the environment. This step is complete when the version and selected core/custom rulesets are known.
3. **Parse and classify structural findings.** Run `epanetparser validate -f <model.inp> --json-output --no-digest` (substitute the actual input path). Review the structured report and separate failures that prevent model construction from later rule findings; static checks cannot run on a model that failed to parse. Treat parse success only as evidence that this input was read into the tool's model representation. This step is complete when parse status and every structural error are recorded.
4. **Review static rules.** The default core ruleset checks simulator-independent model requirements. Add a custom ruleset only when the user names the application constraints it represents, for example `--ruleset <key>`. Inspect every error and warning, rule code, and fix suggestion; apply a correction only when supported by the source model or an explicit engineering instruction. Rerun after edits. This step is complete when the selected ruleset run is recorded and each finding is fixed, accepted with rationale, or left unresolved.
5. **Run simulation checks only when requested.** Confirm WNTR and its EPANET engine are available, select and record the intended simulator and relevant hydraulic options, then use `epanetparser validate -f <model.inp> --simulate --simulation-ruleset hydraulic --json-output --no-digest`. Add other simulation rulesets only when requested and supported by the installed version. Record run failures separately from rule findings and retain the results metadata. This step is complete when the run outcome and all simulation-layer findings are captured, or the unmet dependency/unsupported feature is reported.
6. **Return an auditable result.** Report the input identity, tool version, file format, exact rulesets/layers run, findings by layer and severity, edits made, and remaining issues. State clearly that parsing, static rules, and optional simulation checks do not establish calibration, agreement with field observations, or field validity. This step is complete when another reviewer can identify exactly what was checked and what was not.

## Interpretation boundaries

- **Structural parsing** asks whether the file can be read and references/values can be represented. **Static rules** assess the parsed model against the selected rule set. **Simulation rules** assess outputs from a hydraulic run. These are separate evidence layers, not interchangeable pass/fail claims.
- A custom ruleset may encode constraints of one application or solver; its findings are not universal EPANET requirements. Preserve warning severity and context rather than hiding warnings to make a report appear clean.
- A simulation can fail to run or produce rule findings without showing that the model is calibrated or field-accurate. Do not infer missing elevations, demands, roughnesses, controls, leak parameters, or acceptance thresholds.
- Keep `epanetparser` an external tool. Do not copy, vendor, or bundle its source code in this skill or repository.

## Official sources

- [epanetparser documentation](https://tomjanus.github.io/epanetparser/), especially [basic usage](https://tomjanus.github.io/epanetparser/usage.html), [validation layers](https://tomjanus.github.io/epanetparser/validation_layers.html), [rules and rulesets](https://tomjanus.github.io/epanetparser/rules.html), and [simulation validation](https://tomjanus.github.io/epanetparser/simulation_validation.html).
- [epanetparser source repository](https://github.com/tomjanus/epanetparser) — consult for current CLI options and installation details.

**Evaluation status:** The evaluation specification is checked for structure; no EPANET model was run and this skill has not been behaviorally or domain validated.
