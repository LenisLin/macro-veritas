# Project State

## Current Status

- Phase: Initialization / second narrow registry runtime slice
- Repository identity: MacroVeritas
- Scientific system status: not implemented
- Documentation set status: MVP documentation set established with narrow StudyCard and DatasetCard registry runtime implementations

## Implemented Now

- The repository has been initialized as a MacroVeritas project skeleton.
- The MVP documentation set now covers governance docs, architecture docs, registry/state/audit docs, and CLI contract docs.
- A documentation map exists at `docs/index.md` to support new contributors and new model sessions.
- A minimal CLI scaffold exists with `status`, `show-config`, and `init-layout`.
- A committed project config defines the current external data root and placeholder layout paths.
- The registry gateway now implements real file-backed `StudyCard` read, exists, list, create, and update behavior.
- The registry gateway now implements real file-backed `DatasetCard` read, exists, list, create, and update behavior.
- StudyCard serialization/deserialization now uses one YAML file per card at the canonical StudyCard path.
- DatasetCard serialization/deserialization now uses one YAML file per card at the canonical DatasetCard path.
- StudyCard single-card writes now use a temp-file-plus-replace atomic write flow.
- DatasetCard single-card writes now use the same temp-file-plus-replace atomic write flow.
- DatasetCard create/update now enforce parent StudyCard existence at the gateway boundary.
- Internal tests now cover the StudyCard and DatasetCard runtime slices.
- The public CLI remains `status`, `show-config`, and `init-layout` only.
- AVCP-derived governance assets remain in place as internal process scaffolding.

## Documented But Not Implemented

- The intended direction is a CLI-first, lightweight Python project with filesystem-oriented registry/persistence.
- `ClaimCard` runtime remains contract-only.
- Planned object families and future CLI growth beyond the current slice are documented at a placeholder level only.
- Future execution-layer patterns may draw limited inspiration from CellVoyager, but no such layer is implemented here.

## Explicitly Deferred

- scientific pipelines
- claim extraction
- evidence grading logic
- audit engine behavior
- ClaimCard filesystem registry business logic
- real multi-agent logic
- FastAPI or other web service layer
- SQL persistence
- notebook-centric primary workflow

## External Reference Boundary

- `reference/CellVoyager/` is present as reference material only.
- CellVoyager code is not integrated into the current MacroVeritas package, CLI, or architecture.
- MacroVeritas is not currently a CellVoyager-derived execution system.

## Next Milestone

- Extend runtime only where contracts remain narrow and honest, without introducing scientific inference logic, ClaimCard runtime, or widening the public CLI prematurely.
