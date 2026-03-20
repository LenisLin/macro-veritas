# Project State

## Current Status

- Phase: Initialization / first internal command execution bridge
- Repository identity: MacroVeritas
- Scientific system status: not implemented
- Documentation set status: MVP documentation set established with narrow StudyCard, DatasetCard, and ClaimCard registry runtime implementations

## Implemented Now

- The repository has been initialized as a MacroVeritas project skeleton.
- The MVP documentation set now covers governance docs, architecture docs, registry/state/audit docs, and CLI contract docs.
- A documentation map exists at `docs/index.md` to support new contributors and new model sessions.
- A minimal CLI scaffold exists with `status`, `show-config`, and `init-layout`.
- A committed project config defines the current external data root and placeholder layout paths.
- The registry gateway now implements real file-backed `StudyCard` read, exists, list, create, and update behavior.
- The registry gateway now implements real file-backed `DatasetCard` read, exists, list, create, and update behavior.
- The registry gateway now implements real file-backed `ClaimCard` read, exists, list, create, and update behavior.
- The internal command layer now implements a real StudyCard-only ingest bridge.
- The internal StudyCard ingest bridge now normalizes command-facing input into
  a `StudyCardPayload`, calls StudyCard gateway planning and runtime create,
  and returns a narrow internal command result mapping.
- StudyCard serialization/deserialization now uses one YAML file per card at the canonical StudyCard path.
- DatasetCard serialization/deserialization now uses one YAML file per card at the canonical DatasetCard path.
- ClaimCard serialization/deserialization now uses one YAML file per card at the canonical ClaimCard path.
- StudyCard single-card writes now use a temp-file-plus-replace atomic write flow.
- DatasetCard single-card writes now use the same temp-file-plus-replace atomic write flow.
- ClaimCard single-card writes now use the same temp-file-plus-replace atomic write flow.
- DatasetCard create/update now enforce parent StudyCard existence at the gateway boundary.
- ClaimCard create/update now enforce parent StudyCard existence and optional referenced DatasetCard existence at the gateway boundary.
- Internal tests now cover the StudyCard, DatasetCard, and ClaimCard runtime slices.
- Internal tests now cover the StudyCard ingest command bridge.
- The public CLI remains `status`, `show-config`, and `init-layout` only.
- Reserved command families remain internal and non-public.
- DatasetCard and ClaimCard ingest command execution remain skeleton-only.
- `bind`, `extract`, `audit`, `review`, `run`, and `grade` remain skeleton-only.
- AVCP-derived governance assets remain in place as internal process scaffolding.

## Documented But Not Implemented

- The intended direction is a CLI-first, lightweight Python project with filesystem-oriented registry/persistence.
- Planned object families and future CLI growth beyond the current slice are documented at a placeholder level only.
- Future execution-layer patterns may draw limited inspiration from CellVoyager, but no such layer is implemented here.

## Explicitly Deferred

- scientific pipelines
- claim extraction
- evidence grading logic
- audit engine behavior
- real multi-agent logic
- FastAPI or other web service layer
- SQL persistence
- notebook-centric primary workflow

## External Reference Boundary

- `reference/CellVoyager/` is present as reference material only.
- CellVoyager code is not integrated into the current MacroVeritas package, CLI, or architecture.
- MacroVeritas is not currently a CellVoyager-derived execution system.

## Next Milestone

- Extend runtime only where contracts remain narrow and honest, without introducing scientific inference logic or widening the public CLI prematurely.
