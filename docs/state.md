# Project State

## Current Status

- Phase: Initialization / public StudyCard, DatasetCard, and ClaimCard
  full-replace update with pre-update snapshot preservation plus single-card
  exclusive update/delete locking
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
  `ingest study`, `ingest study --from-file`, `ingest dataset`,
  `ingest dataset --from-file`, `ingest claim`, `ingest claim --from-file`,
  `update study`, `update dataset`, `update claim`, `show study`,
  `show dataset`, `show claim`, `list studies`, `list datasets`,
  `list claims`, `delete study`, `delete dataset`, and `delete claim`.
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
- The internal command layer implements single-file YAML ingest bridges for StudyCard, DatasetCard, and ClaimCard that each load one mapping, normalize it to the same card-family ingest input used by the flag-based path, and then reuse the existing payload/create path.
- The internal command layer implements a real StudyCard show-by-id bridge.
- The internal command layer implements a real DatasetCard show-by-id bridge.
- The internal command layer implements a real ClaimCard show-by-id bridge.
- The internal command layer implements a real StudyCard family-list bridge.
- The internal command layer implements a real DatasetCard family-list bridge.
- The internal command layer implements a real ClaimCard family-list bridge.
- The internal command layer implements a real StudyCard delete bridge.
- The internal command layer implements a real DatasetCard delete bridge.
- The internal command layer implements a real ClaimCard delete bridge.
- The internal command layer implements a real StudyCard full-replace update bridge.
- The internal command layer implements a real DatasetCard full-replace update bridge.
- The internal command layer implements a real ClaimCard full-replace update bridge.
- The public CLI exposes the create triangle for `StudyCard`, `DatasetCard`,
  and `ClaimCard` through `ingest study`, `ingest dataset`, and `ingest claim`.
- The public CLI also exposes single-file YAML create-only ingest through `ingest study --from-file <path.yaml>`, `ingest dataset --from-file <path.yaml>`, and `ingest claim --from-file <path.yaml>`.
- The public CLI exposes show-by-id for all three core cards through
  `show study`, `show dataset`, and `show claim`.
- The public CLI exposes family-level discovery for all three core cards
  through `list studies`, `list datasets`, and `list claims`.
- The public CLI now exposes referentially-aware by-id delete for all three
  core cards through `delete study`, `delete dataset`, and `delete claim`.
- The public CLI now exposes file-based full-replace StudyCard update through
  `update study --study-id <ID> --from-file <path.yaml>`.
- The public CLI now exposes file-based full-replace DatasetCard update through
  `update dataset --dataset-id <ID> --from-file <path.yaml>`.
- The public CLI now exposes file-based full-replace ClaimCard update through
  `update claim --claim-id <ID> --from-file <path.yaml>`.
- StudyCard update preserves the existing closed-to-active status rejection rule
  at the registry gateway/runtime boundary.
- Public full-replace update for StudyCard, DatasetCard, and ClaimCard now
  preserves the exact prior on-disk YAML in an internal append-only
  `<registry_root>/history/` tree before overwrite.
- Public full-replace update for StudyCard, DatasetCard, and ClaimCard now
  also acquires one exclusive target-card lock beneath
  `<registry_root>/.locks/` for the snapshot-plus-overwrite critical section.
- Public by-id delete for StudyCard, DatasetCard, and ClaimCard now also
  acquires one exclusive target-card lock beneath `<registry_root>/.locks/`
  for the dependency-check-plus-delete critical section.
- The public show path adapts explicit CLI flags into narrow by-id input,
  calls `get_study_card` / `get_dataset_card` / `get_claim_card`, and returns
  stable JSON to stdout on success.
- The public list path adapts plural collection commands into narrow
  family-level input, calls `list_study_cards` / `list_dataset_cards` /
  `list_claim_cards`, and returns compact summary JSON arrays to stdout on
  success.
- Missing `StudyCard`, `DatasetCard`, and `ClaimCard` reads are translated into
  clean command-level failures.
- Registry list failures are translated into clean command-level failures.
- DatasetCard create/update enforce parent StudyCard existence at the gateway
  boundary.
- ClaimCard create/update enforce parent StudyCard existence and optional
  referenced DatasetCard existence at the gateway boundary.
- StudyCard delete is blocked at the gateway boundary when dependent
  DatasetCard or ClaimCard records still exist.
- DatasetCard delete is blocked at the gateway boundary when dependent
  ClaimCard records still exist.
- ClaimCard delete is implemented directly at the gateway boundary when the
  target exists.
- StudyCard, DatasetCard, and ClaimCard serialization/deserialization use one
  YAML file per card at the canonical path.
- StudyCard, DatasetCard, and ClaimCard single-card writes use a temp-file plus
  replace atomic write flow, and full-replace update now adds snapshot-before-overwrite safety.
- Internal tests cover the StudyCard, DatasetCard, and ClaimCard runtime slices.
- Internal tests cover the public ingest, public show, and public list CLI
  paths for the three core card families, including single-file `--from-file` ingest for StudyCard, DatasetCard, and ClaimCard.
- Internal tests cover the public StudyCard, DatasetCard, and ClaimCard full-replace update
  CLI paths, including target/file mismatch and status/reference validation
  failures.
- No public restore, rollback, or history-browsing CLI exists for the internal
  update snapshot tree.
- `bind`, `extract`, `audit`, `review`, `run`, and `grade` remain skeleton-only.
- AVCP-derived governance assets remain in place as internal process
  scaffolding.

## Documented But Not Implemented

- The intended direction is a CLI-first, lightweight Python project with
  filesystem-oriented registry/persistence.
- Planned object families and future CLI growth beyond the current slice are
  documented at a placeholder level only.
- Batch and directory-based ingest remain absent even though single-file YAML ingest now exists for StudyCard, DatasetCard, and ClaimCard.
- Future execution-layer patterns may draw limited inspiration from
  CellVoyager, but no such layer is implemented here.

## Explicitly Deferred

- public search or filter for `StudyCard`, `DatasetCard`, or `ClaimCard`
- create or ingest locking for `StudyCard`, `DatasetCard`, or `ClaimCard`
- public StudyCard, DatasetCard, or ClaimCard update beyond file-based full replace
- force delete for `StudyCard`, `DatasetCard`, or `ClaimCard`
- cascade delete for `StudyCard`, `DatasetCard`, or `ClaimCard`
- delete by search or filter for `StudyCard`, `DatasetCard`, or `ClaimCard`
- restore, undo, trash, or archive semantics for public delete
- relationship expansion or reverse lookups in public reads
- pagination or query semantics for public discovery
- StudyCard patch, partial, or flag-based update
- DatasetCard patch, partial, or flag-based update
- ClaimCard patch, partial, or flag-based update
- batch or directory-based file update
- update by search or filter
- public restore, rollback, or history browsing for update snapshots
- public restore, rollback, or history browsing for delete operations
- batch or directory-based file ingest
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
  search/filter/update/force/cascade behavior before those contracts are
  intentionally designed.
