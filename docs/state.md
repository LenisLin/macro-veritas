# Project State

## Current Status

- Phase: Initialization / MVP documentation freeze
- Repository identity: MacroVeritas
- Scientific system status: not implemented
- Documentation set status: MVP documentation set established for the current freeze

## Implemented Now

- The repository has been initialized as a MacroVeritas project skeleton.
- The MVP documentation set now covers governance docs, architecture docs, registry/state/audit docs, and CLI contract docs.
- A documentation map exists at `docs/index.md` to support new contributors and new model sessions.
- A minimal CLI scaffold exists with `status`, `show-config`, and `init-layout`.
- A committed project config defines the current external data root and placeholder layout paths.
- AVCP-derived governance assets remain in place as internal process scaffolding.

## Documented But Not Implemented

- The intended direction is a CLI-first, lightweight Python project with filesystem-oriented registry/persistence.
- Planned object families and future CLI growth are documented at a placeholder level only.
- Future execution-layer patterns may draw limited inspiration from CellVoyager, but no such layer is implemented here.

## Explicitly Deferred

- scientific pipelines
- claim extraction
- evidence grading logic
- audit engine behavior
- real filesystem registry business logic
- real multi-agent logic
- FastAPI or other web service layer
- SQL persistence
- notebook-centric primary workflow

## External Reference Boundary

- `reference/CellVoyager/` is present as reference material only.
- CellVoyager code is not integrated into the current MacroVeritas package, CLI, or architecture.
- MacroVeritas is not currently a CellVoyager-derived execution system.

## Next Milestone

- Define the first narrow registry contracts and a small ingestion/audit path without introducing scientific inference logic.
