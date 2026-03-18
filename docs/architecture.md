# Architecture

## Intent

MacroVeritas is intentionally lightweight at v0.1. The current repository provides only the project skeleton and the minimum command-line surface needed to manage configuration and placeholder filesystem layout during the MVP documentation freeze.

## Governance And Roles

- Human PI / project leadership defines scientific scope, milestone boundaries, and acceptance criteria.
- The repository currently encodes those decisions through docs-first governance: `docs/state.md`, `docs/constraints.md`, and `docs/decisions.md`.
- A-header governance remains the intended standard for future non-trivial scripts and modules so purpose and contract boundaries stay auditable.
- AVCP-derived assets are retained as internal governance/process scaffolding, not as the public identity of the project.

## High-Level Shape

- CLI-first execution: local commands are the primary entrypoint.
- Filesystem-oriented registry direction: future records, run artifacts, and reports will live under the configured data root.
- Modular growth later: registry models, ingestion logic, grading logic, and reporting should be added incrementally once their contracts are documented.

## Current Components

- `docs/` for project memory and locked constraints
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
- no agent runtime

## Filesystem Layout Direction

The CLI initializes placeholder directories beneath the configured data root:

- `registry/`
- `runs/`
- `reports/`
- `raw/`
- `processed/`

These are scaffold placeholders only. Their detailed semantics remain TBD in later milestones.
