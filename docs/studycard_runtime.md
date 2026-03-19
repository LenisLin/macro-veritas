# StudyCard Runtime

## Purpose

This document is the source of truth for the first real runtime slice in
MacroVeritas:

- file-backed registry gateway behavior for `StudyCard` only
- conservative YAML serialization and deserialization for one StudyCard per file
- single-card atomic write behavior for StudyCard create and update
- gateway translation of lower-level StudyCard runtime failures into registry
  domain errors

This milestone is intentionally narrow. It proves the first runtime path
without expanding the public CLI or introducing broader orchestration.

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
- `create_study_card` and `update_study_card` perform real single-card writes
  through the gateway only.

## Still Non-Runtime

The following remain contract-only and do not perform runtime IO:

- all `DatasetCard` gateway reads, listings, existence checks, and mutations
- all `ClaimCard` gateway reads, listings, existence checks, and mutations
- cross-card referential integrity for `DatasetCard` and `ClaimCard`
- public CLI wiring for StudyCard create or update

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

## Atomic Write Rule

StudyCard create and update use a real single-card atomic write flow:

1. write the full YAML document to a temp file in the same directory as the
   final canonical file
2. flush and `fsync` the temp file
3. `os.replace(...)` the temp file onto the canonical path
4. `fsync` the parent directory after replacement

Scope limits:

- atomicity is for one canonical StudyCard file at a time
- there is no multi-card transaction support
- there is no locking or concurrent writer coordination

## Error Translation Rule

Lower-level StudyCard runtime failures are translated at the gateway boundary.

Implemented translations:

- missing canonical file on read or update -> `CardNotFoundError`
- duplicate StudyCard create target -> `CardAlreadyExistsError`
- malformed YAML or malformed StudyCard content -> `RegistryError`
- attempt to reopen a `closed` StudyCard on update -> `InvalidStateTransitionError`
- unsafe StudyCard lookup ID passed to gateway read/existence functions ->
  `UnsupportedRegistryOperationError`
- other filesystem failures -> `RegistryError`

## Non-Goals

This milestone does not add:

- DatasetCard runtime IO
- ClaimCard runtime IO
- scientific logic
- evidence grading
- multi-card transactions
- manifest or index runtime
- public CLI create/update commands
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
- CellVoyager integration
