# Project State

## Current Status

- Phase: Initialization / first public read CLI exposure
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
  `ingest study`, `ingest dataset`, `ingest claim`, `show study`,
  `show dataset`, and `show claim`.
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
- The internal command layer implements a real ClaimCard ingest bridge.
- The internal command layer implements a real StudyCard show-by-id bridge.
- The internal command layer implements a real DatasetCard show-by-id bridge.
- The internal command layer implements a real ClaimCard show-by-id bridge.
- The public CLI exposes the create triangle for `StudyCard`, `DatasetCard`,
  and `ClaimCard` through `ingest study`, `ingest dataset`, and `ingest claim`.
- The public CLI exposes show-by-id for all three core cards through
  `show study`, `show dataset`, and `show claim`.
- The public show path adapts explicit CLI flags into narrow by-id input,
  calls `get_study_card` / `get_dataset_card` / `get_claim_card`, and returns
  stable JSON to stdout on success.
- Missing `StudyCard`, `DatasetCard`, and `ClaimCard` reads are translated into
  clean command-level failures.
- DatasetCard create/update enforce parent StudyCard existence at the gateway
  boundary.
- ClaimCard create/update enforce parent StudyCard existence and optional
  referenced DatasetCard existence at the gateway boundary.
- StudyCard, DatasetCard, and ClaimCard serialization/deserialization use one
  YAML file per card at the canonical path.
- StudyCard, DatasetCard, and ClaimCard single-card writes use a temp-file plus
  replace atomic write flow.
- Internal tests cover the StudyCard, DatasetCard, and ClaimCard runtime slices.
- Internal tests cover the public ingest and public show CLI paths for the
  three core card families.
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

- public list/search/filter for StudyCard, DatasetCard, or ClaimCard
- public update/delete for StudyCard, DatasetCard, or ClaimCard
- relationship expansion or reverse lookups in public reads
- StudyCard update or patch ingest
- DatasetCard update or patch ingest
- ClaimCard update or patch ingest
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
  introducing scientific inference logic and without implying public
  list/search/update/delete before those contracts are intentionally designed.
