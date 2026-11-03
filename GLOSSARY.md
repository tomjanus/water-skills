# Glossary

Use these terms consistently in skills, evaluations, and contribution guidance.

## Skills and models

**Skill** — A directory containing a `SKILL.md` and optional supporting resources that transfers task-specific procedure or expert knowledge to an agent.

**Agent Skills format validation** — A structural check of `SKILL.md` metadata and naming. Passing it does not establish behavior or domain correctness.

**Water distribution network (WDN)** — A network of pipes, nodes, storage, pumps, valves, and controls used to represent water distribution.

**Demand-driven analysis (DDA)** — A hydraulic analysis formulation that assumes requested demand is delivered; suitability depends on the task and operating conditions.

**Pressure-dependent demand (PDD)** — A formulation in which delivered demand varies with available pressure according to a selected pressure-demand relation. The relation and parameters are project assumptions, not universal defaults.

**Scenario** — A documented set of model inputs, events, or operating conditions used for one analysis case.

## Evaluation

**Evaluation specification** — A file defining a task prompt, expected outcome, and grading checks. It describes how a behavior could be tested; it is not an observed result.

**Captured run** — An actual agent execution with saved outputs, transcript, and metadata for one task and condition.

**Trial** — One execution of a task under a defined condition. Multiple trials may be needed when behavior varies.

**Evaluation runner** — Repository code that validates evaluation specifications and grades captured artifacts. The current runner does not launch an agent or capture runs.

**Agent harness** — The system that lets a model act as an agent and invoke tools. Record its identity and version when reporting a captured run.

## Provenance

**Provenance record** — Evidence-linked metadata for a skill's authorship and method status. The schema is in [`provenance.schema.json`](provenance.schema.json); do not populate fields without evidence.

**Method status** — A description of how a method relates to its sources, not a quality rating:

- `established`: used as documented in a recognized source without material adaptation;
- `adapted`: a documented method changed for the stated context;
- `heuristic`: a practitioner rule of thumb whose general validity is not established;
- `hypothesis`: an unverified proposition intended for testing.

These labels do not establish that a method is appropriate for a particular system or decision.
