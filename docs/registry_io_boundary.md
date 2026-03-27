# Registry IO Boundary

## Purpose

This document freezes the internal access boundary for registry
operations.

- It defines the planned module boundary for reading and writing registry cards.
- It defines where direct referential-integrity checks are expected to happen.
- It defines the planned mutation-safety rule for future writes.
- It defines the current snapshot-before-overwrite safety rule for full-replace
  updates.
- It defines the current single-card exclusive update-lock rule for full-replace
  updates.
- It defines the current single-card exclusive delete-lock rule for by-id
  deletes.
- It defines the current parent-aware DatasetCard ingest-lock rule for the
  public create path.
- It defines the current reference-aware ClaimCard ingest-lock rule for the
  public create path.
- It defines the minimum planned error surface for registry access.
- `docs/gateway_contracts.md` defines the exact gateway communication contract
  for results, mutation-plan outputs, and domain-error semantics.

This document separates the frozen general boundary from the currently
implemented runtime slice.

- The general boundary remains frozen and conservative.
- `StudyCard` runtime reads, listings, existence checks, and single-card writes
  are implemented behind the gateway.
- `DatasetCard` runtime reads, listings, existence checks, and single-card
  writes are now implemented behind the gateway.
- `ClaimCard` runtime reads, listings, existence checks, and single-card writes
  are now implemented behind the gateway.
- `StudyCard`, `DatasetCard`, and `ClaimCard` delete execution are now
  implemented behind the gateway.

## Architectural Boundary

The intended split is conservative and layered.

| Layer | Planned Responsibility | Explicit Boundary |
| --- | --- | --- |
| CLI layer | Parse arguments, invoke package functions, and print results | Must not do raw path traversal or raw file access for registry cards |
| Governance / rule layer | Define policy, review rules, lifecycle intent, and higher-level workflow decisions | Must not do raw file access for registry cards |
| Registry gateway / repository boundary | Sole internal access boundary for retrieving and persisting `StudyCard`, `DatasetCard`, and `ClaimCard` | Current callers should use this boundary instead of touching layout helpers or files directly |
| Serialization layer | Convert between in-memory card mappings and on-disk representation | Implemented now for `StudyCard`, `DatasetCard`, and `ClaimCard` beneath the gateway; not called directly by CLI or governance |
| Filesystem layout layer | Freeze canonical relative paths, naming rules, and static placement conventions | Path helper layer only; not a read/write access API |

Planning rule:

- CLI must not do raw path traversal or raw file access.
- Governance must not do raw file access.
- The registry gateway is the only planned boundary for future card retrieval and persistence.
- Any future repository or serializer implementation sits behind that gateway boundary rather than alongside CLI or governance code.

## First-Slice Access Surface

The frozen first-slice access surface is limited to `StudyCard`,
`DatasetCard`, and `ClaimCard`.

Planned operation families:

- `get` / `read` by canonical card ID
- `exists` check by canonical card ID
- `list` by card family
- `plan create`
- `plan update`

Current execution helpers now also include by-id delete for `StudyCard`,
`DatasetCard`, and `ClaimCard`.

Current first-slice state:

- `StudyCard`: runtime-real `get`, `exists`, `list`, `plan create`,
  `plan update`, plus gateway-level `create`, `update`, and `delete`
  execution helpers
- `DatasetCard`: runtime-real `get`, `exists`, `list`, `plan create`,
  `plan update`, plus gateway-level `create`, `update`, and `delete`
  execution helpers
- `ClaimCard`: runtime-real `get`, `exists`, `list`, `plan create`,
  `plan update`, plus gateway-level `create`, `update`, and `delete`
  execution helpers

The boundary remains narrow even where runtime now exists.

- It does not introduce a broader repository abstraction.

The exact success/result shapes and mutation-plan payload contract are frozen in
[`docs/gateway_contracts.md`](gateway_contracts.md).

## Referential Integrity Enforcement Point

The conservative MVP rule is:

- Direct referenced-card existence checks belong at the registry gateway
  boundary for create and update operations.
- Reverse-dependency blocking checks belong at the registry gateway boundary
  before delete operations remove a canonical card file.

Planned direct-reference checks:

- `DatasetCard` create/update must confirm the referenced `StudyCard` exists.
- `ClaimCard` create/update must confirm the referenced `StudyCard` exists.
- `ClaimCard` create/update must confirm each referenced `DatasetCard` exists.
- `StudyCard` delete must block when any `DatasetCard` or `ClaimCard`
  depends on the target study.
- `DatasetCard` delete must block when any `ClaimCard` depends on the target
  dataset.

Implemented now:

- `DatasetCard` create now acquires the parent `StudyCard` lock and the target
  `DatasetCard` lock, then enforces parent `StudyCard` existence and duplicate
  target absence while both locks are held before the DatasetCard runtime
  helper writes storage.
- `DatasetCard` update still enforces parent `StudyCard` existence at the
  gateway boundary before the DatasetCard runtime helper writes storage.
- `DatasetCard` planning descriptors perform the same direct parent existence
  check without writing storage.
- `ClaimCard` create now acquires the parent `StudyCard` lock, any referenced
  `DatasetCard` locks, and the target `ClaimCard` lock, then enforces parent
  `StudyCard` existence, referenced `DatasetCard` existence, and duplicate
  target absence while those locks are held before the ClaimCard runtime
  helper writes storage.
- `ClaimCard` update still enforces parent `StudyCard` existence and
  referenced `DatasetCard` existence when `dataset_ids` is present and non-empty.
- `ClaimCard` planning descriptors perform the same direct checks without
  writing storage.
- `StudyCard` delete now scans existing `DatasetCard` and `ClaimCard` records
  before removal and raises a domain-level dependency-blocking error when
  dependents still exist.
- `DatasetCard` delete now scans existing `ClaimCard` records before removal
  and raises a domain-level dependency-blocking error when dependents still
  exist.
- `ClaimCard` delete now removes the canonical file directly when the target
  exists.

What remains above the gateway:

- Governance may still decide whether a proposed linkage is allowed by policy.
- Governance may still decide whether a transition or workflow step is acceptable.
- Those higher-level decisions do not replace gateway-level direct existence checks.

Why this is the chosen MVP boundary:

- It keeps raw registry access in one place.
- It prevents CLI and governance code from duplicating path traversal logic.
- It makes direct card-link integrity consistent across all future callers.

## Atomicity And Mutation Safety Strategy

The write rule remains intentionally narrow and is now implemented for
`StudyCard`, `DatasetCard`, and `ClaimCard`:

- Single-card create operations follow a write-temp-then-replace style atomic
  update principle for the canonical card file.
- Single-card DatasetCard create through the public ingest path now also
  acquires the parent `StudyCard` lock and the target `DatasetCard` lock
  before parent validation, duplicate-target checks, and create/write.
- Single-card ClaimCard create through the public ingest path now also
  acquires the parent `StudyCard` lock, any referenced `DatasetCard` locks,
  and the target `ClaimCard` lock before reference validation, duplicate-
  target checks, and create/write.
- Single-card full-replace update operations now acquire one exclusive
  target-card lock, preserve the exact prior canonical YAML in the internal
  history tree while that lock is held, then perform the atomic canonical-file
  replacement and release the lock.
- Single-card by-id delete operations now acquire one exclusive target-card
  lock, re-check target existence while that lock is held, perform reverse-
  dependency checks under that same lock when required, then delete the
  canonical card file and release the lock.

Implemented interpretation:

- The target of atomicity is one canonical card file at a time.
- Future writes should avoid in-place partial overwrite of the canonical file.
- A successful single-card update should appear as one completed lock
  acquisition, one completed snapshot creation, one completed replacement of
  the canonical card file, and one completed lock release.
- Snapshot history is internal-only beneath `<registry_root>/history/` and is
  not part of public read or list resolution.
- Mutation lock files live beneath `<registry_root>/.locks/` and are not part
  of public read or list resolution.

DatasetCard create execution order for the implemented public ingest path:

1. the gateway normalizes the DatasetCard payload and resolves the registry root
2. the gateway acquires the deterministic parent StudyCard ingest lock
3. the gateway acquires the deterministic target DatasetCard ingest lock
4. the gateway validates parent StudyCard existence under those locks
5. the gateway re-checks duplicate target state under those locks
6. the runtime atomically writes the canonical DatasetCard file
7. both locks are released after success or failure

ClaimCard create execution order for the implemented public ingest path:

1. the gateway normalizes the ClaimCard payload and resolves the registry root
2. the gateway derives the parent StudyCard, referenced DatasetCard, and target
   ClaimCard lock paths
3. the gateway sorts those full lock paths lexicographically and acquires them
   in that order
4. the gateway validates the StudyCard and DatasetCard references under those
   locks
5. the gateway re-checks duplicate target state under those locks
6. the runtime atomically writes the canonical ClaimCard file
7. all locks are released after success or failure

Update execution order for the implemented full-replace path:

1. gateway-owned direct reference checks complete before mutation
2. the gateway acquires the deterministic single-card update lock
3. the runtime preserves the pre-update snapshot
4. the runtime atomically overwrites the canonical card file
5. the lock is released after success or failure

Delete execution order for the implemented by-id path:

1. the gateway performs the normal fast target-existence check
2. the gateway acquires the deterministic single-card delete lock
3. the gateway re-checks target existence under that lock
4. the gateway performs reverse-dependency checks under that lock when required
5. the runtime removes the canonical card file
6. the lock is released after success or failure

Explicit limits:

- No multi-card transaction guarantee is planned yet.
- No cross-card commit bundle is planned yet.
- Single-card exclusive locking exists for full-replace update operations,
  by-id delete operations, parent-aware DatasetCard ingest, and
  reference-aware ClaimCard ingest only.
- StudyCard ingest, show, and list remain unlocked.
- No cross-card lock graph or distributed locking system is planned.
- No rollback engine is planned yet.
- No public restore or history-browsing CLI is planned yet.

## Error Surface

The minimum planned registry access error surface is conservative and small.

Gateway/domain categories:

- `RegistryError`: base registry access error
- `CardNotFoundError`: requested card does not exist
- `CardAlreadyExistsError`: create request targets an already existing card
- `BrokenReferenceError`: direct referenced card is missing
- `DependencyExistsError`: delete would leave dependent cards behind
- `InvalidStateTransitionError`: requested change conflicts with the frozen lifecycle/state policy
- `UpdateLockError`: the exclusive DatasetCard/ClaimCard ingest or
  update/delete lock could not be acquired or managed
- `UnsupportedRegistryOperationError`: requested registry action is outside the supported gateway contract

The runtime slice still uses a small error surface. Lower-level StudyCard,
DatasetCard, and ClaimCard filesystem/YAML failures are translated into this
domain layer at the gateway.

The exact gateway-facing meaning of those error categories is frozen in
[`docs/gateway_contracts.md`](gateway_contracts.md).

## Non-Goals

This milestone does not add or imply:

- transaction engine
- generalized create/show/list locking
- StudyCard ingest locking
- distributed locking system
- multi-card lock graph
- manifest or index engine
- broad parsing or validation engine
- scientific logic
- evidence grading
- CellVoyager integration
