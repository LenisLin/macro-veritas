# Project State

## Current Status

- Phase: Initialization / second public ingest command
- Repository identity: MacroVeritas
- Scientific system status: not implemented
- Documentation set status: MVP documentation set established with narrow
  StudyCard, DatasetCard, and ClaimCard registry runtime implementations

## Implemented Now

- The repository has been initialized as a MacroVeritas project skeleton.
- The MVP documentation set covers governance docs, architecture docs,
  registry/state/audit docs, and CLI contract docs.
- A documentation map exists at `docs/index.md` to support new contributors and
  new model sessions.
- A minimal public CLI exists with `status`, `show-config`, `init-layout`,
  `ingest study`, and `ingest dataset`.
- A committed project config defines the current external data root and
  placeholder layout paths.
- The registry gateway implements real file-backed `StudyCard` read, exists,
  list, create, and update behavior.
- The registry gateway implements real file-backed `DatasetCard` read, exists,
  list, create, and update behavior.
- The registry gateway implements real file-backed `ClaimCard` read, exists,
  list, create, and update behavior.
- The internal command layer implements a real StudyCard ingest bridge.
- The internal command layer implements a real DatasetCard ingest bridge.
- The public CLI exposes two real domain commands: create-only `StudyCard`
  ingest at `ingest study` and create-only `DatasetCard` ingest at
  `ingest dataset`.
- The StudyCard ingest path adapts public CLI flags into normalized command
  input, prepares a `StudyCardPayload`, calls StudyCard gateway planning and
  runtime create, and returns a narrow command result mapping.
- The DatasetCard ingest path adapts public CLI flags into normalized command
  input, prepares a `DatasetCardPayload`, calls DatasetCard gateway planning
  and runtime create, and returns a narrow command result mapping.
- DatasetCard create/update enforce parent StudyCard existence at the gateway
  boundary.
- ClaimCard create/update enforce parent StudyCard existence and optional
  referenced DatasetCard existence at the gateway boundary.
- StudyCard, DatasetCard, and ClaimCard serialization/deserialization use one
  YAML file per card at the canonical path.
- StudyCard, DatasetCard, and ClaimCard single-card writes use a temp-file plus
  replace atomic write flow.
- Internal tests cover the StudyCard, DatasetCard, and ClaimCard runtime slices.
- Internal tests cover the StudyCard ingest bridge and the public StudyCard and
  DatasetCard CLI paths.
- ClaimCard ingest remains non-public and skeleton-only.
- The public CLI otherwise remains minimal.
- `bind`, `extract`, `audit`, `review`, `run`, and `grade` remain skeleton-only.
- AVCP-derived governance assets remain in place as internal process
  scaffolding.

## Documented But Not Implemented

- The intended direction is a CLI-first, lightweight Python project with
  filesystem-oriented registry/persistence.
- Planned object families and future CLI growth beyond the current slice are
  documented at a placeholder level only.
- Future execution-layer patterns may draw limited inspiration from
  CellVoyager, but no such layer is implemented here.

## Explicitly Deferred

- ClaimCard public ingest
- StudyCard update or patch ingest
- DatasetCard update or patch ingest
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
- CellVoyager code is not integrated into the current MacroVeritas package,
  CLI, or architecture.
- MacroVeritas is not currently a CellVoyager-derived execution system.

## Next Milestone

- Extend runtime only where contracts remain narrow and honest, without
  introducing scientific inference logic or widening the public CLI beyond the
  current create-only StudyCard and DatasetCard ingest paths prematurely.
