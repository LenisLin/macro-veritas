# Registry IO Boundary

## Purpose

This document freezes the internal access boundary for registry
operations.

- It defines the planned module boundary for reading and writing registry cards.
- It defines where direct referential-integrity checks are expected to happen.
- It defines the planned mutation-safety rule for future writes.
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

- `DatasetCard` create/update enforce parent `StudyCard` existence at the
  gateway boundary before the DatasetCard runtime helper writes storage.
- `DatasetCard` planning descriptors perform the same direct parent existence
  check without writing storage.
- `ClaimCard` create/update enforce parent `StudyCard` existence and enforce
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

- Single-card create and update operations are expected to follow a write-temp-then-replace style atomic update principle for the canonical card file.

Implemented interpretation:

- The target of atomicity is one canonical card file at a time.
- Future writes should avoid in-place partial overwrite of the canonical file.
- A successful single-card mutation should appear as one completed replacement of the canonical card file.

Explicit limits:

- No multi-card transaction guarantee is planned yet.
- No cross-card commit bundle is planned yet.
- No concurrent locking system is planned yet.
- No rollback engine is planned yet.

## Error Surface

The minimum planned registry access error surface is conservative and small.

Gateway/domain categories:

- `RegistryError`: base registry access error
- `CardNotFoundError`: requested card does not exist
- `CardAlreadyExistsError`: create request targets an already existing card
- `BrokenReferenceError`: direct referenced card is missing
- `DependencyExistsError`: delete would leave dependent cards behind
- `InvalidStateTransitionError`: requested change conflicts with the frozen lifecycle/state policy
- `UnsupportedRegistryOperationError`: requested registry action is outside the supported gateway contract

The runtime slice still uses a small error surface. Lower-level StudyCard,
DatasetCard, and ClaimCard filesystem/YAML failures are translated into this
domain layer at the gateway.

The exact gateway-facing meaning of those error categories is frozen in
[`docs/gateway_contracts.md`](gateway_contracts.md).

## Non-Goals

This milestone does not add or imply:

- transaction engine
- concurrent locking system
- manifest or index engine
- broad parsing or validation engine
- scientific logic
- evidence grading
- CellVoyager integration
