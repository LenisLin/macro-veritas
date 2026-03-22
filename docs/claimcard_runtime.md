# ClaimCard Runtime

## Purpose

This document is the source of truth for the third narrow runtime slice in
MacroVeritas:

- file-backed registry gateway behavior for `ClaimCard`
- conservative YAML serialization and deserialization for one ClaimCard per file
- single-card atomic write behavior for ClaimCard create and update
- gateway-level `StudyCard` and optional `DatasetCard` referential-integrity
  enforcement for ClaimCard create and update
- the public create-only `macro_veritas ingest claim` CLI entry point as a thin
  adapter over the existing ClaimCard ingest bridge and gateway path
- gateway translation of lower-level ClaimCard runtime failures into registry
  domain errors

This milestone stays intentionally narrow. It makes ClaimCard registry IO and
create-only public CLI intake real without implementing scientific logic.

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

The public CLI entry point that now sits above that gateway/runtime slice is:

- `macro_veritas ingest claim`

Interpretation:

- `get_claim_card`, `claim_card_exists`, and `list_claim_cards` read real files
- `create_claim_card` and `update_claim_card` perform real single-card writes
  through the gateway only
- `plan_create_claim_card` and `plan_update_claim_card` validate input and
  direct references, then return planning descriptors without writing files
- `macro_veritas ingest claim` remains a thin adapter: CLI args are normalized
  into command input, then into `ClaimCardPayload`, then routed through
  `plan_create_claim_card(...)` and `create_claim_card(...)`

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

## Atomic Write Rule

ClaimCard create and update use a real single-card atomic write flow:

1. write the full YAML document to a temp file in the same directory as the
   final canonical file
2. flush and `fsync` the temp file
3. `os.replace(...)` the temp file onto the canonical path
4. `fsync` the parent directory after replacement

Scope limits:

- atomicity is for one canonical ClaimCard file at a time
- there is no multi-card transaction support
- there is no locking or concurrent writer coordination

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
- public ClaimCard update or patch commands
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
- CellVoyager integration
