# MacroVeritas

## Project Overview

MacroVeritas is a docs-first, CLI-first Python project scaffold for a future claim-centered evidence grading and data-level verification system focused on melanoma, immune checkpoint inhibition, and macrophage literature.

This repository is in the initialization / MVP documentation freeze stage. No scientific system, evidence grading engine, registry business logic, or analysis pipeline is implemented yet.

## Current Status

- Stage: initialization / MVP documentation freeze
- Package name: `macro_veritas`
- Repository name: `macro-veritas`
- Implemented now:
  - lightweight Python package scaffold
  - minimal CLI commands for status, config inspection, and layout initialization
  - docs describing scope, constraints, and intended architecture
  - committed project config with explicit external data root
- Not implemented now:
  - scientific pipelines
  - claim extraction
  - real claim, study, dataset, or evidence registry logic
  - evidence grading rules
  - audit engine behavior
  - multi-agent orchestration
  - web API or service layer

## Documentation Map

For the recommended reading order and a grouped map of the MVP documentation set, see [`docs/index.md`](docs/index.md).

## Freeze Boundaries

- MacroVeritas is a docs-first, CLI-first, lightweight Python project with a filesystem-oriented registry direction.
- v0.1 does not use FastAPI.
- v0.1 does not use SQL.
- v0.1 does not use a notebook-centric primary workflow.
- `reference/CellVoyager/` is retained only as reference material and possible execution-layer inspiration. MacroVeritas is not being built as a CellVoyager fork or notebook-centered system.
- AVCP-derived assets are retained as internal governance and process scaffolding at this stage. They are not the end-user identity of the project.
- Current package and layout details may still reflect initialization-stage transition and are not yet fully stabilized.

## Design Principles

- docs-first
- CLI-first
- filesystem-based registry and persistence
- lightweight native Python
- conda for development environment management
- Docker only for reproducibility, not as the primary workflow

## Repository Layout

```text
config/                 # committed project configuration scaffold
docs/                   # charter, state, constraints, decisions, contracts, architecture
macro_veritas/          # repo-root bootstrap package for `python -m macro_veritas`
prompts/                # retained AVCP operating prompt from the template
reference/CellVoyager/  # external reference material only; not integrated architecture
scripts/dev/            # lightweight maintenance helpers kept from the template
src/macro_veritas/      # installable package and minimal CLI scaffold
tests/                  # lightweight validation checks
```

## Local Paths

- Project root: `/home/lenislin/Experiment/projects/MacroVeritas`
- Data root: `/mnt/NAS_21T/ProjectData/MacroVeritas_Data`
- Default config file: `config/project.yaml`

The configured data root is external to the repository. Placeholder runtime directories such as `registry/`, `runs/`, `reports/`, `raw/`, and `processed/` are created under the data root by the CLI when requested.

## Initialization Notes

- This repository was converted from an AVCP template and keeps the useful docs-first repo-memory structure.
- A tiny repo-root bootstrap package is present so `python -m macro_veritas` works directly from this checkout.
- The primary workflow is command-line driven. There is no FastAPI app, SQL database, or notebook-centric primary workflow in v0.1.
- The current CLI is intentionally small and honest:
  - `status`
  - `show-config`
  - `init-layout`
- The scaffold does not claim any scientific capability beyond configuration and filesystem layout management.
- CellVoyager code is not integrated into the current MacroVeritas package or CLI surface.

## Next Milestone

The next milestone is to define the first concrete registry object contracts and add a narrow ingestion and audit path for claim, study, and evidence records without introducing scientific inference logic.
