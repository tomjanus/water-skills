---
name: pywr-engineering
description: Set up, inspect, modify, run, and analyze Pywr resource-allocation models. Use for Pywr JSON/Python models, scenario ensembles, solver runs, recorders/results, or explicitly requested capacity/design searches.
---

# Pywr model engineering

Pywr is a network resource-allocation model that formulates supply-demand allocation as a linear program. It is not a water-distribution hydraulic simulator: Pywr results do not provide pipe-network pressure or establish hydraulic feasibility. Use this workflow for Pywr models and hand hydraulic questions to an appropriate hydraulic tool.

## Workflows

### Environment and setup

1. Inspect the repository's Python version, environment files, dependency constraints, and existing Pywr version before changing anything. Read the official installation instructions for that release and platform.
2. Confirm that a supported linear-programming solver is available as well as Pywr. Create or modify an isolated environment only when setup is requested; preserve existing dependency-management conventions.
3. Verify the active interpreter imports Pywr, report its version and solver configuration, and load/run a minimal or supplied model as appropriate. Stop with the concrete import, solver, or build error if verification fails.

**Completion:** the active environment, Pywr release, and usable solver are recorded, and the requested minimal-model check succeeds.

### Inspect an existing model

1. Identify the entry point (JSON or Python), model metadata, external data files, and any runner script. Keep model-relative file paths anchored to the model document when the format specifies them.
2. For JSON models, load with the documented `Model.load(path)` interface. Inventory the timestepper, solver, nodes and connections, flow bounds/costs, parameters and data sources, scenario dimensions/combinations, and configured recorders.
3. Compare the model's declared units, time horizon, inputs, and outputs with the user's question. Record unknown or absent values rather than filling them by convention.

**Completion:** the model structure and its external inputs, temporal/scenario coverage, solver, and recorded outputs are summarized, with material gaps called out.

### Modify a model or define scenarios

1. Translate the request into a small change list naming the affected nodes, edges, parameters, timestep settings, scenarios, or recorders. Preserve an unmodified source or create a focused diff.
2. Make only changes supported by supplied data or explicit user choices. For uncertainty or alternatives, define labeled scenario ensembles and document each input value and its meaning. Check the resulting scenario combinations: Pywr can execute the product of ensemble choices unless the model restricts combinations.
3. Keep the model's resource-allocation formulation explicit: node capacities, costs/benefits, demand requirements, and constraints determine allocation. Confirm that JSON references, external data paths, node names, and parameter dependencies resolve when loaded.

**Completion:** each requested change is traceable, scenario combinations match the intended experiment, and the model loads without unresolved references.

### Execute and diagnose

1. Use the selected solver configured by the model/environment. Load the exact edited model and run through the model's documented Python API or existing project runner (for example, `model = Model.load(path); model.run()`).
2. Capture the command/script, environment and Pywr/solver versions, model inputs, run status, warnings, and errors. Distinguish model-load errors, missing solver/build issues, and infeasible or failed optimization runs; do not silently change constraints or solver settings to force completion.
3. For repeated runs, ensure scenario and input changes are intentional and that outputs cannot be confused with a previous run.

**Completion:** the run status is known for the requested model/scenario set and the recorded execution details are sufficient to reproduce the attempt.

### Record and interpret results

1. Before execution, select recorders that correspond to the requested quantities: node flows, storage, parameter values, deficits, aggregates, or file output. Use in-memory recorders for focused runs and CSV/HDF-style recorders only when useful and supported by the installed version/dependencies.
2. After execution, inspect recorder names, dimensions, time indexing, scenario combinations, units, and missing values. Pywr's in-memory recorder data can be scenario-by-timestep; label and align those axes before comparing scenarios.
3. Summarize only requested metrics and distinguish objective values, operational flows/storage, and scenario-specific results. Check that every requested scenario and timestep is present before drawing a comparison.

**Completion:** every reported result maps to a named recorder/quantity, unit, timestep range, and scenario, with any missing or failed outputs identified.

### Explicit capacity or design search (optional)

1. Enter this branch only when the user asks for design search or alternative sizing. Get the candidate decision variables/ranges, objective, constraints, scenario set, and acceptance criteria from the user or supplied project specification.
2. Establish how candidate capacity choices enter the model. Pywr's standard run optimizes resource allocation for the encoded model; it does not automatically search arbitrary infrastructure designs. Use an explicit outer candidate search or a supported, deliberately formulated optimization only when its mathematical representation and solver support are clear.
3. Evaluate candidates against the same inputs and scenarios, retain candidate definitions and run status, and compare the requested objective and constraints. Identify any design choice requiring a separate hydraulic assessment.

**Completion:** the candidate set, formulation/search method, objective and constraints, and comparable result for each candidate are recorded; no unrequested search or design recommendation is implied.

## Interpretation boundaries

- Pywr's objective and constraints express the modeler's resource-allocation formulation. A successful optimization verifies a solution to that encoded formulation, not whether its assumptions or data represent a real system.
- Do not infer demand, costs, priorities, capacities, operating rules, scenario probabilities, or feasibility thresholds. Ask for values that materially change the formulation.
- Keep resource allocation distinct from pipe hydraulics. Hydraulic pressures, velocities, headloss, or pipe sizing require a hydraulic model and explicitly linked assumptions.

## Official sources

- [Pywr documentation](https://pywr.github.io/pywr/) — use the documentation matching the installed release.
- [Installation](https://pywr.github.io/pywr/install.html), [tutorial](https://pywr.github.io/pywr/tutorial.html), [problem formulation](https://pywr.github.io/pywr/formulation.html), and [JSON model format](https://pywr.github.io/pywr/json.html).
- [Core classes and scenario API](https://pywr.github.io/pywr/api/pywr.core.html) and [recorder API](https://pywr.github.io/pywr/api/pywr.recorders.html).

**Evaluation status:** The evaluation specification is checked for structure; no Pywr model was run and this skill has not been behaviorally or domain validated.
