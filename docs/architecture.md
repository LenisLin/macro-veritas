# Architecture

## Intent

MacroVeritas is intentionally lightweight at v0.1. The current repository provides only the project skeleton and the minimum command-line surface needed to manage configuration and placeholder filesystem layout during the MVP documentation freeze.

The current step locks the governance function layer and the first registry filesystem layout one level deeper in documentation and static descriptor modules without implying that domain behavior, orchestration, or enforcement already exists.

## Governance And Roles

- Human PI / project leadership defines scientific scope, milestone boundaries, and acceptance criteria.
- The repository currently encodes those decisions through docs-first governance: `docs/state.md`, `docs/constraints.md`, and `docs/decisions.md`.
- A-header governance remains the intended coordination standard for future non-trivial scripts and modules so purpose and contract boundaries stay auditable.
- The function-level governance freeze now lives in `docs/governance_spec.md`.
- The governance-to-code bridge for the package skeleton remains documented in `docs/module_map.md`.
- The filesystem source of truth for first-slice card placement now lives in `docs/registry_layout.md`.
- The registry access-boundary source of truth now lives in `docs/registry_io_boundary.md`.
- The gateway communication-contract source of truth now lives in `docs/gateway_contracts.md`.
- The internal command-family contract source of truth now lives in `docs/cli_command_contracts.md`.
- AVCP-derived assets are retained as internal governance/process scaffolding, not as the public identity of the project.

## High-Level Shape

- CLI-first execution: local commands are the primary entrypoint.
- Internal command-family layer by plan: reserved `macro_veritas.commands.*` modules sit between the current public CLI scaffold and future gateway/governance operations.
- Filesystem-oriented registry direction: future records, run artifacts, and reports will live under the configured data root.
- Gateway-centered registry access by plan: future card retrieval and persistence should go through `macro_veritas.registry.gateway`, not direct CLI or governance file access.
- A lightweight governance layer should remain documentation-led first and code-light later.
- Six departments are treated as organizational overlays whose current code form is office-level descriptor content inside department modules, not as an implemented workflow engine.
- Prosecution remains a separate escalation lane outside the routine review department.
- Modular growth later: registry models, ingestion logic, grading logic, and reporting should be added incrementally once their contracts are documented.
- Reserved command families may be skeletonized internally before they are exposed as stable public CLI commands.

## Governance Layer Direction

- A-header is a governance and header standard, not an implemented orchestration engine.
- `docs/governance_spec.md` is the function-level source of truth for A-header lanes, department offices, and prosecution lanes.
- `docs/module_map.md` maps those frozen responsibilities onto the current package layout.
- The code skeleton may expose office-level descriptor APIs inside `macro_veritas.governance.a_header`, `macro_veritas.governance.departments.*`, and `macro_veritas.prosecution.specs`.
- Routine review remains the lightweight audit domain described in `docs/audit_policy.md` and aligns with the future `刑部`-like review concept.
- The future `检察院` concept is a distinct escalation and prosecution lane rather than the default review path.
- Chinese governance labels remain documentation labels. Code package paths should stay ASCII / English.

## Current Components

- `docs/` for project memory, locked constraints, and code-organization planning
- `config/project.yaml` for committed path configuration
- `macro_veritas/` as a thin repo-root bootstrap so `python -m macro_veritas` works from the checkout
- `src/macro_veritas/` for package code and CLI scaffold
- `scripts/dev/` for lightweight repository maintenance helpers retained from the template

## CellVoyager Boundary

- `reference/CellVoyager/` is retained as external reference material only.
- CellVoyager may inform future execution-layer patterns at a conceptual level.
- CellVoyager is not used as the current MacroVeritas core architecture.
- MacroVeritas is not being built as a CellVoyager fork or notebook-centered system in v0.1.

## Current Non-Components

- no FastAPI app
- no web service layer
- no SQL persistence layer
- no notebook-centric primary workflow
- no scientific pipeline modules
- no claim extraction pipeline
- no evidence grading engine
- no audit engine
- no prosecution engine
- no agent runtime

## Filesystem Layout Direction

The CLI initializes placeholder directories beneath the configured data root:

- `registry/`
- `runs/`
- `reports/`
- `raw/`
- `processed/`

These are scaffold placeholders only at the top level.

Within the resolved registry root, the first frozen card slice now uses the
entity-segregated layout defined in `docs/registry_layout.md`:

- `studies/`
- `datasets/`
- `claims/`

That layout freeze is documentation and static-descriptor only. It does not add
registry IO or a runtime state engine.

Planned access and mutation responsibility is frozen separately in
`docs/registry_io_boundary.md`. Layout helpers remain a static naming/path
layer, not a registry access API.
