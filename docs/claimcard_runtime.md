# ClaimCard Runtime

## Purpose

This document is the source of truth for the third narrow runtime slice in
MacroVeritas:

- file-backed registry gateway behavior for `ClaimCard`
- conservative YAML serialization and deserialization for one ClaimCard per file
- single-card atomic write behavior for ClaimCard create and update
- pre-update snapshot preservation for full-replace ClaimCard update
- single-card exclusive local-file locking for full-replace ClaimCard update
- gateway-level `StudyCard` and optional `DatasetCard` referential-integrity
  enforcement for ClaimCard create and update
- the public `macro_veritas ingest claim` and `macro_veritas update claim` CLI
  entry points as thin adapters over the existing ClaimCard command bridge and
  gateway path
- gateway translation of lower-level ClaimCard runtime failures into registry
  domain errors

This milestone stays intentionally narrow. It makes ClaimCard registry IO plus
create-only and full-replace public CLI intake real without implementing
scientific logic.

## Runtime-Real Now

The following gateway behavior is now runtime-real for `ClaimCard`:

- `get_claim_card(claim_id)`
- `claim_card_exists(claim_id)`
- `list_claim_cards()`
- `create_claim_card(card)`
- `update_claim_card(card)`

Planning-only behavior that now returns real mutation descriptors without
writing storage:

- `plan_create_claim_card(card)`
- `plan_update_claim_card(card)`

The public CLI entry points that now sit above that gateway/runtime slice are:

- `macro_veritas ingest claim`
- `macro_veritas update claim`

Interpretation:

- `get_claim_card`, `claim_card_exists`, and `list_claim_cards` read real files
- `create_claim_card` performs a real single-card write through the gateway
  only
- `update_claim_card` acquires the target-card lock, snapshots the exact prior
  YAML into the internal history tree while the lock is held, then performs the
  real single-card overwrite through the gateway only
- `plan_create_claim_card` and `plan_update_claim_card` validate input and
  direct references, then return planning descriptors without writing files
- `macro_veritas ingest claim` remains a thin adapter: CLI args are normalized
  into command input, then into `ClaimCardPayload`, then routed through
  `plan_create_claim_card(...)` and `create_claim_card(...)`
- `macro_veritas update claim` remains a thin adapter: the CLI target is
  normalized into command input, one complete canonical ClaimCard YAML mapping
  is loaded from file, `claim_id` target/file consistency is enforced, and then
  `plan_update_claim_card(...)` plus `update_claim_card(...)` are called

## Referential Integrity Rules

The implemented ClaimCard parent-reference rule is:

- the registry gateway must confirm that the referenced `StudyCard` canonical
  file exists before `create_claim_card` or `update_claim_card` proceeds

Canonical parent path rule:

- `ClaimCard.study_id -> <registry_root>/studies/<study_id>.yaml`

The implemented optional dataset-reference rule is:

- if `dataset_ids` is present and non-empty, the registry gateway must confirm
  that each referenced `DatasetCard` canonical file exists before
  `create_claim_card` or `update_claim_card` proceeds

Canonical dataset-reference path rule:

- each `dataset_id` in `ClaimCard.dataset_ids ->
  <registry_root>/datasets/<dataset_id>.yaml`

Current implementation notes:

- both direct checks happen at the gateway boundary, not in CLI code and not in
  the lower ClaimCard serializer/runtime helper
- missing parent `StudyCard` is translated to `BrokenReferenceError`
- missing referenced `DatasetCard` values are translated to
  `BrokenReferenceError`
- the same direct checks are also applied by `plan_create_claim_card` and
  `plan_update_claim_card`, but those functions still do not write storage
- the public CLI surfaces those failures as clean command-level
  `missing_reference` results rather than raw filesystem exceptions
- the public update file shape is the canonical stored ClaimCard shape, so
  update files use `created_from_note` rather than the ingest-file alias
  `created_from`

## Canonical ClaimCard Path Rule

The canonical ClaimCard storage path is:

`<registry_root>/claims/<claim_id>.yaml`

Rules:

- `registry_root` comes from the resolved project config
- one ClaimCard maps to one YAML file
- gateway/runtime code writes and reads only this canonical path
- lookup `claim_id` values must be a single identifier, not a path segment list
- stored file name must match the `claim_id` inside the YAML content

## Serialization Format

The runtime representation for `ClaimCard` is a single YAML mapping per file.

Rules:

- stored field names match the frozen `ClaimCard` field contract exactly
- no hidden metadata fields are injected
- allowed `status` values remain `captured`, `scoped`, `ready`, and `closed`
- allowed `review_readiness` values remain `needs_scope`, `reviewable`, and
  `execution_candidate`
- optional `dataset_ids` is serialized as a plain YAML list when present
- unexpected fields, missing required fields, wrong basic types, invalid
  `status`, invalid `review_readiness`, invalid `claim_id` / `study_id`,
  malformed `dataset_ids`, invalid dataset reference identifiers, or a
  mismatched canonical file name are treated as malformed ClaimCard content

## Snapshot And Atomic Write Rule

ClaimCard create uses a real single-card atomic write flow:

1. write the full YAML document to a temp file in the same directory as the
   final canonical file
2. flush and `fsync` the temp file
3. `os.replace(...)` the temp file onto the canonical path
4. `fsync` the parent directory after replacement

ClaimCard update adds one safety step before that overwrite:

1. acquire the exclusive target-card lock at
   `<registry_root>/.locks/claims/<claim_id>.lock`
2. read the current canonical ClaimCard file
3. copy the exact prior YAML bytes to
   `<registry_root>/history/claims/<claim_id>/<timestamp>.yaml`
4. only after snapshot success, perform the atomic canonical-file replacement
5. release the lock after overwrite success or failure

Scope limits:

- atomicity is for one canonical ClaimCard file at a time
- exclusive locking exists only for full-replace ClaimCard update
- create, show, list, and delete stay unlocked
- there is no multi-card transaction support
- there is no distributed locking, version counter, or force-unlock flow

## Error Translation Rule

Lower-level ClaimCard runtime failures are translated at the gateway boundary.

Implemented translations:

- missing canonical file on read or update -> `CardNotFoundError`
- duplicate ClaimCard create target -> `CardAlreadyExistsError`
- missing parent `StudyCard` on ClaimCard create or update ->
  `BrokenReferenceError`
- missing referenced `DatasetCard` values on ClaimCard create or update ->
  `BrokenReferenceError`
- malformed YAML or malformed ClaimCard content -> `RegistryError`
- update lock acquisition or release failure -> `UpdateLockError`
- snapshot creation failure before update overwrite -> `RegistryError`
- unsafe ClaimCard lookup ID passed to gateway read/existence functions ->
  `UnsupportedRegistryOperationError`
- other filesystem failures -> `RegistryError`

The public CLI translates those gateway/domain errors again into concise
command-level results such as `duplicate_target`, `missing_reference`,
`invalid_payload`, `unsupported_operation`, and `registry_failure`.

## Non-Goals

This milestone does not add:

- claim extraction engine or text-span parser
- scientific logic
- evidence grading
- multi-card transactions
- reverse indexes or manifests
- public ClaimCard patch commands
- restore or history-browsing commands for update snapshots
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
- CellVoyager integration
