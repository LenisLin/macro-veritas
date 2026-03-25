# DatasetCard Runtime

## Purpose

This document is the source of truth for the narrow DatasetCard runtime slice in
MacroVeritas.

- file-backed registry gateway behavior for `DatasetCard`
- conservative YAML serialization and deserialization for one DatasetCard per file
- single-card atomic write behavior for DatasetCard create and update
- gateway-level `StudyCard` referential-integrity enforcement for DatasetCard
  create and update
- thin public CLI exposure for `ingest dataset` create and `update dataset`
  full-replace update
- gateway translation of lower-level DatasetCard runtime failures into registry
  domain errors

This milestone stays intentionally narrow. It makes DatasetCard registry IO and
the public create/update CLI bridges runtime-real without widening the public
CLI any further.

## Runtime-Real Now

The following gateway behavior is runtime-real for `DatasetCard`:

- `get_dataset_card(dataset_id)`
- `dataset_card_exists(dataset_id)`
- `list_dataset_cards()`
- `create_dataset_card(card)`
- `update_dataset_card(card)`

Planning-only behavior that returns real mutation descriptors without writing
storage:

- `plan_create_dataset_card(card)`
- `plan_update_dataset_card(card)`

Interpretation:

- `get_dataset_card`, `dataset_card_exists`, and `list_dataset_cards` read real
  files.
- `create_dataset_card` and `update_dataset_card` perform real single-card
  writes through the gateway only.
- `plan_create_dataset_card` and `plan_update_dataset_card` validate input and
  return planning descriptors without writing files.

## Public CLI Entry Point

The public DatasetCard entry points are now real and intentionally thin:

1. `macro_veritas.cli` exposes `ingest dataset`
2. the CLI adapter converts parsed args into a small typed DatasetCard CLI mapping
3. `macro_veritas.commands.ingest.normalize_public_datasetcard_cli_input(...)`
   converts that mapping into normalized DatasetCard ingest input
4. `macro_veritas.commands.ingest.prepare_datasetcard_ingest_payload(...)`
   prepares one full-card `DatasetCardPayload`
5. `macro_veritas.commands.ingest.execute_datasetcard_ingest_input(...)` calls
   `plan_create_dataset_card(...)` and then `create_dataset_card(...)`
6. `macro_veritas.cli` also exposes `update dataset`
7. the update CLI adapter converts parsed args into a small typed DatasetCard
   update mapping
8. `macro_veritas.commands.update.load_datasetcard_update_file(...)` loads one
   complete replacement `DatasetCard` YAML mapping in canonical field shape
9. `macro_veritas.commands.update.execute_update_dataset(...)` verifies CLI
   target / file target consistency, then calls `plan_update_dataset_card(...)`
   and `update_dataset_card(...)`
10. the actual write remains owned by `macro_veritas.registry.gateway`

Scope limits:

- the public create path still exists at `ingest dataset` and `ingest dataset --from-file`
- the public update path exists only at `update dataset --dataset-id <ID> --from-file <path.yaml>`
- update is full-replace only; patch semantics do not exist
- public `StudyCard` and `ClaimCard` update do not exist
- raw `argparse.Namespace` objects are not part of the command-to-gateway boundary

## Referential Integrity Rule

The implemented DatasetCard parent-reference rule is:

- the registry gateway must confirm that the referenced `StudyCard` canonical
  file exists before `create_dataset_card` or `update_dataset_card` proceeds

Canonical parent path rule:

- `DatasetCard.study_id -> <registry_root>/studies/<study_id>.yaml`

Current implementation notes:

- the existence check happens at the gateway boundary, not in CLI code and not
  in the lower DatasetCard serializer/runtime helper
- missing parent `StudyCard` is translated to `BrokenReferenceError` at the
  gateway boundary
- the public CLI and command bridge translate that domain failure into a clean
  command-level `missing_reference` result
- the same direct check is also applied by `plan_create_dataset_card` and
  `plan_update_dataset_card`, but those functions still do not write storage

## Canonical DatasetCard Path Rule

The canonical DatasetCard storage path is:

`<registry_root>/datasets/<dataset_id>.yaml`

Rules:

- `registry_root` comes from the resolved project config
- one DatasetCard maps to one YAML file
- gateway/runtime code writes and reads only this canonical path
- lookup `dataset_id` values must be a single identifier, not a path segment
  list
- stored file name must match the `dataset_id` inside the YAML content

## Serialization Format

The runtime representation for `DatasetCard` is a single YAML mapping per file.

Rules:

- stored field names match the frozen `DatasetCard` field contract exactly
- no hidden metadata fields are injected
- allowed `status` values remain `identified`, `registered`, `bound`, and
  `retired`
- allowed `availability_status` values remain `unknown`, `open`, `restricted`,
  and `unavailable`
- required sequence fields are serialized as plain YAML lists
- unexpected fields, missing required fields, wrong basic types, invalid
  `status`, invalid `availability_status`, invalid `study_id` / `dataset_id`
  identifiers, or a mismatched canonical file name are treated as malformed
  DatasetCard content

## Atomic Write Rule

DatasetCard create and update use a real single-card atomic write flow:

1. write the full YAML document to a temp file in the same directory as the
   final canonical file
2. flush and `fsync` the temp file
3. `os.replace(...)` the temp file onto the canonical path
4. `fsync` the parent directory after replacement

Scope limits:

- atomicity is for one canonical DatasetCard file at a time
- there is no multi-card transaction support
- there is no locking or concurrent writer coordination

## Error Translation Rule

Lower-level DatasetCard runtime failures are translated at the gateway
boundary.

Implemented translations:

- missing canonical file on read or update -> `CardNotFoundError`
- duplicate DatasetCard create target -> `CardAlreadyExistsError`
- missing parent `StudyCard` on DatasetCard create or update ->
  `BrokenReferenceError`
- malformed YAML or malformed DatasetCard content -> `RegistryError`
- unsafe DatasetCard lookup ID passed to gateway read/existence functions ->
  `UnsupportedRegistryOperationError`
- other filesystem failures -> `RegistryError`

Public command-bridge translations for `ingest dataset`:

- duplicate create -> `duplicate_target`
- missing parent StudyCard -> `missing_reference`
- invalid DatasetCard data -> `invalid_payload`
- unsupported operation/identifier -> `unsupported_operation`
- other gateway/domain failures -> `registry_failure`

Public command-bridge translations for `update dataset`:

- missing target DatasetCard -> `missing_reference`
- missing parent StudyCard -> `missing_reference`
- invalid replacement file or invalid DatasetCard data -> `invalid_payload`
- unsupported operation/identifier -> `unsupported_operation`
- other gateway/domain failures -> `registry_failure`

## Non-Goals

This milestone does not add:

- StudyCard public update
- ClaimCard public update
- DatasetCard patch, merge, or partial-update commands
- scientific logic
- evidence grading
- multi-card transactions
- reverse indexes or manifests
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
- CellVoyager integration
