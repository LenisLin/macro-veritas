# Gateway Contracts

## Purpose

This document freezes the gateway communication contract for registry
access.

- It defines the success/result shapes for gateway operations.
- It defines the domain-level error semantics for gateway failures.
- It defines the mutation-planning output contract for create and update flows.
- It freezes the update style as full-card replace only for the MVP planning
  boundary.
- It relies on [`docs/payload_contracts.md`](payload_contracts.md) for the
  concrete first-slice payload and DTO shapes.

This document now describes a mixed implementation state.

- `StudyCard` read, exists, list, create, and update execution are runtime-real
  behind the gateway.
- `StudyCard` `plan_create` and `plan_update` return real planning descriptors
  without writing storage.
- `DatasetCard` read, exists, list, create, and update execution are now
  runtime-real behind the gateway.
- `DatasetCard` `plan_create` and `plan_update` return real planning
  descriptors without writing storage.
- `DatasetCard` create/update and planning enforce referenced `StudyCard`
  existence at the gateway boundary.
- `ClaimCard` read, exists, list, create, and update execution are now
  runtime-real behind the gateway.
- `ClaimCard` `plan_create` and `plan_update` return real planning descriptors
  without writing storage.
- `ClaimCard` create/update and planning enforce referenced `StudyCard`
  existence and referenced `DatasetCard` existence when `dataset_ids` is
  present.
- `StudyCard`, `DatasetCard`, and `ClaimCard` delete execution are now
  runtime-real behind the gateway.
- `StudyCard` and `DatasetCard` delete execution enforce reverse-dependency
  blocking before removal.
- An internal StudyCard ingest bridge now consumes the unchanged StudyCard
  gateway contract by calling `plan_create_study_card(...)` and then
  `create_study_card(...)`.

## Access Result Contract

The chosen MVP communication style is:

- bare domain result for reads
- domain exception for failures
- explicit mutation-plan descriptor for `plan_create` and `plan_update`

Why this is the chosen style:

- It keeps read calls simple for upper layers.
- It avoids wrapper-envelope complexity before runtime behavior exists.
- It keeps mutation planning explicit without pretending that execution already
  happens.

Gateway result contract:

| Operation Family | Planned Input | Success Result Shape | Failure Communication |
| --- | --- | --- | --- |
| `get` / `read` by ID | canonical card ID | bare card mapping shaped by [`docs/payload_contracts.md`](payload_contracts.md) and [`docs/card_contracts.md`](card_contracts.md) | raise domain error |
| `exists` | canonical card ID | bare `bool` | missing card is `False`, not a not-found error |
| `list` by family | no additional input on family-specific function | bare tuple of card mappings shaped by [`docs/payload_contracts.md`](payload_contracts.md) and [`docs/card_contracts.md`](card_contracts.md) | raise domain error only for unsupported boundary use |
| `plan_create` | full-card payload | `MutationPlanDescriptor` | raise domain error |
| `plan_update` | full-card payload | `MutationPlanDescriptor` | raise domain error |

Interpretation notes:

- `get_*` returns exactly one bare card mapping on success.
- `exists_*` returns `True` or `False`; absence is not exceptional.
- `list_*` returns a bare tuple of card mappings; an empty family listing is an
  empty tuple.
- These shapes are runtime-real today for `StudyCard`, `DatasetCard`, and
  `ClaimCard`.
- The concrete first-slice mapping shapes live in
  [`docs/payload_contracts.md`](payload_contracts.md).
- `plan_*` returns a planning descriptor only; it does not mutate storage.
- `create_study_card`, `update_study_card`, `delete_study_card`,
  `create_dataset_card`, `update_dataset_card`, `delete_dataset_card`,
  `create_claim_card`, `update_claim_card`, and `delete_claim_card` are
  separate execution helpers.
- The internal StudyCard ingest bridge uses this exact split: plan first, then
  create.

## Error Semantics

Gateway errors are domain-level contract semantics, not raw OS exceptions.
Future lower-level filesystem or serializer failures must not cross the gateway
boundary as raw implementation errors.

Gateway/domain error categories:

- `RegistryError`: base gateway/domain failure category
- `CardNotFoundError`: the requested target card is absent for read or update
  planning
- `CardAlreadyExistsError`: a create plan targets a card that already exists
- `BrokenReferenceError`: a create or update plan refers to a missing linked
  card that the gateway owns as a direct reference check
- `DependencyExistsError`: a delete request would leave dependent linked cards
  behind
- `InvalidStateTransitionError`: the requested change conflicts with the frozen
  lifecycle or transition policy
- `UnsupportedRegistryOperationError`: the caller asks for an operation or
  input style outside the frozen gateway contract

Communication rule:

- These names define the contract surface seen by CLI and governance callers.
- StudyCard, DatasetCard, and ClaimCard runtime translate raw storage and YAML
  failures into these names.
- They do not expose raw OS or serializer exception types as public contract
  surface.

## Mutation Planning Contract

The MVP update style is frozen as `full-card replace only`.

Why this is the chosen rule:

- Patch semantics would force merge rules before validators and serializers
  exist.
- Full-card replace makes caller responsibility explicit.
- The meaning of an update stays stable even while runtime execution is still
  deferred.

Patch rule:

- `plan_update` does not accept patch-style input.
- `plan_update` expects the complete replacement full-card payload.
- No patch-merging engine is part of this freeze.

The minimum `MutationPlanDescriptor` shape must describe:

| Field | Meaning |
| --- | --- |
| `plan_kind` | `create` or `update` |
| `card_family` | target card family |
| `target_id` | canonical target card identifier |
| `input_requirement` | always `full_card_payload` in this MVP freeze |
| `integrity_checks_required` | direct reference or existence checks the gateway expects before execution |
| `atomicity_expectation` | single-card atomic replace expectation |
| `execution_state` | always `planned_only` in this milestone |
| `deferred_execution_note` | explicit reminder that no write happened |

Planning interpretation:

- `plan_create` and `plan_update` share the same plan result shape.
- The plan object is the success result for mutation planning.
- The plan object records intended execution semantics without performing IO.
- The accepted payload families for the first slice are `StudyCardPayload`,
  `DatasetCardPayload`, and `ClaimCardPayload` from
  [`docs/payload_contracts.md`](payload_contracts.md).
- For `StudyCard`, the plan functions are separate from the runtime execution
  helpers and still do not write storage.
- The internal StudyCard ingest command bridge depends on that separation and
  does not change the gateway result or error contract.
- For `DatasetCard`, the plan functions are separate from the runtime execution
  helpers, still do not write storage, and do perform the direct parent
  `StudyCard` existence check.
- For `ClaimCard`, the plan functions are separate from the runtime execution
  helpers, still do not write storage, and do perform the direct parent
  `StudyCard` existence check plus optional `DatasetCard` existence checks when
  `dataset_ids` is present.

## Success Vs Failure Communication Rule

At the contract level:

- Success is returned as the operation's native domain shape:
  bare card mapping, `bool`, bare tuple of card mappings, or
  `MutationPlanDescriptor`.
- Failure is communicated by raising a gateway/domain exception from the frozen
  registry error taxonomy.
- `exists` is the one special case where absence is returned as `False` rather
  than as `CardNotFoundError`.

## Non-Goals

This milestone does not add or imply:

- broad parser or validation engine
- payload conversion runtime
- patch-merging engine
- retry runtime
- concurrency or locking runtime
- transaction engine
