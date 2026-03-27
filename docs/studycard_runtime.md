# StudyCard Runtime

## Purpose

This document is the source of truth for the implemented StudyCard runtime
slice in
MacroVeritas:

- file-backed registry gateway behavior for `StudyCard` only
- conservative YAML serialization and deserialization for one StudyCard per file
- single-card atomic write behavior for StudyCard create and update
- pre-update snapshot preservation for full-replace StudyCard update
- single-card exclusive local-file locking for full-replace StudyCard update
- gateway translation of lower-level StudyCard runtime failures into registry
  domain errors

This milestone is intentionally narrow. It proves the first runtime path
without introducing broader orchestration.

## Runtime-Real Now

The following gateway behavior is now runtime-real for `StudyCard`:

- `get_study_card(study_id)`
- `study_card_exists(study_id)`
- `list_study_cards()`
- `plan_create_study_card(card)`
- `plan_update_study_card(card)`
- `create_study_card(card)`
- `update_study_card(card)`

Interpretation:

- `get_study_card`, `study_card_exists`, and `list_study_cards` read real files.
- `plan_create_study_card` and `plan_update_study_card` validate StudyCard input
  and return planning descriptors without writing files.
- `create_study_card` performs a real single-card write through the gateway
  only.
- `update_study_card` acquires the target-card lock, snapshots the exact prior
  YAML into the internal history tree while the lock is held, then performs the
  real single-card overwrite through the gateway only.
- The public `ingest study` and `update study` CLI paths now reuse these
  gateway/runtime helpers through the command layer.

## Still Non-Runtime

The following remain outside this StudyCard runtime slice:

- `DatasetCard` runtime behavior, which is documented separately in
  [`docs/datasetcard_runtime.md`](datasetcard_runtime.md)
- all `ClaimCard` gateway reads, listings, existence checks, and mutations
- ClaimCard referential integrity
- CLI parsing and command-layer success/failure formatting

## Canonical StudyCard Path Rule

The canonical StudyCard storage path is:

`<registry_root>/studies/<study_id>.yaml`

Rules:

- `registry_root` comes from the resolved project config.
- one StudyCard maps to one YAML file
- gateway/runtime code writes and reads only this canonical path
- lookup `study_id` values must be a single identifier, not a path segment list
- stored file name must match the `study_id` inside the YAML content

## Serialization Format

The runtime representation for `StudyCard` is a single YAML mapping per file.

Rules:

- stored field names match the frozen `StudyCard` field contract exactly
- no hidden metadata fields are injected
- allowed `status` values remain `draft`, `registered`, and `closed`
- allowed `screening_decision` values remain `pending`, `include`, and `exclude`
- required sequence fields are serialized as plain YAML lists
- unexpected fields, missing required fields, wrong basic types, invalid status
  values, invalid screening decisions, or a mismatched canonical file name are
  treated as malformed StudyCard content

## Snapshot And Atomic Write Rule

StudyCard create uses a real single-card atomic write flow:

1. write the full YAML document to a temp file in the same directory as the
   final canonical file
2. flush and `fsync` the temp file
3. `os.replace(...)` the temp file onto the canonical path
4. `fsync` the parent directory after replacement

StudyCard update adds one safety step before that overwrite:

1. acquire the exclusive target-card lock at
   `<registry_root>/.locks/studies/<study_id>.lock`
2. read the current canonical StudyCard file
3. copy the exact prior YAML bytes to
   `<registry_root>/history/studies/<study_id>/<timestamp>.yaml`
4. only after snapshot success, perform the atomic canonical-file replacement
5. release the lock after overwrite success or failure

Scope limits:

- atomicity is for one canonical StudyCard file at a time
- exclusive locking exists only for full-replace StudyCard update
- create, show, list, and delete stay unlocked
- there is no multi-card transaction support
- there is no distributed locking, version counter, or force-unlock flow

## Error Translation Rule

Lower-level StudyCard runtime failures are translated at the gateway boundary.

Implemented translations:

- missing canonical file on read or update -> `CardNotFoundError`
- duplicate StudyCard create target -> `CardAlreadyExistsError`
- malformed YAML or malformed StudyCard content -> `RegistryError`
- attempt to reopen a `closed` StudyCard on update -> `InvalidStateTransitionError`
- update lock acquisition or release failure -> `UpdateLockError`
- snapshot creation failure before update overwrite -> `RegistryError`
- unsafe StudyCard lookup ID passed to gateway read/existence functions ->
  `UnsupportedRegistryOperationError`
- other filesystem failures -> `RegistryError`

## Non-Goals

This milestone does not add:

- ClaimCard runtime IO
- scientific logic
- evidence grading
- multi-card transactions
- manifest or index runtime
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
- CellVoyager integration
