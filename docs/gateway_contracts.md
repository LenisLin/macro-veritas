# Gateway Contracts

## Purpose

This document freezes the gateway communication contract for future registry
access.

- It defines the success/result shapes for gateway operations.
- It defines the domain-level error semantics for gateway failures.
- It defines the mutation-planning output contract for create and update flows.
- It freezes the update style as full-card replace only for the MVP planning
  boundary.

This document does not imply implemented runtime behavior.

- No gateway execution is implemented.
- No registry IO is implemented.
- No serializer or deserializer is implemented.
- No parser or validator is implemented.

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

Planned operation results:

| Operation Family | Planned Input | Success Result Shape | Failure Communication |
| --- | --- | --- | --- |
| `get` / `read` by ID | canonical card ID | bare `CardMapping` | raise domain error |
| `exists` | canonical card ID | bare `bool` | missing card is `False`, not a not-found error |
| `list` by family | no additional input on family-specific function | bare `tuple[CardMapping, ...]` | raise domain error only for unsupported boundary use |
| `plan_create` | full-card mapping | `MutationPlanDescriptor` | raise domain error |
| `plan_update` | full-card mapping | `MutationPlanDescriptor` | raise domain error |

Interpretation notes:

- `get_*` returns exactly one bare card mapping on success.
- `exists_*` returns `True` or `False`; absence is not exceptional.
- `list_*` returns a bare tuple of card mappings; an empty family listing is an
  empty tuple.
- `plan_*` returns a planning descriptor only; it does not mutate storage.

## Error Semantics

Gateway errors are domain-level contract semantics, not raw OS exceptions.
Future lower-level filesystem or serializer failures must not cross the gateway
boundary as raw implementation errors.

Planned error categories:

- `RegistryError`: base gateway/domain failure category
- `CardNotFoundError`: the requested target card is absent for read or update
  planning
- `CardAlreadyExistsError`: a create plan targets a card that already exists
- `BrokenReferenceError`: a create or update plan refers to a missing linked
  card that the gateway owns as a direct reference check
- `InvalidStateTransitionError`: the requested change conflicts with the frozen
  lifecycle or transition policy
- `UnsupportedRegistryOperationError`: the caller asks for an operation or
  input style outside the frozen gateway contract

Communication rule:

- These names define the contract surface seen by CLI and governance callers.
- They do not claim any raw storage/runtime implementation strategy.
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
- `plan_update` expects the complete replacement card mapping.
- No patch-merging engine is part of this freeze.

The minimum `MutationPlanDescriptor` shape must describe:

| Field | Meaning |
| --- | --- |
| `plan_kind` | `create` or `update` |
| `card_family` | target card family |
| `target_id` | canonical target card identifier |
| `input_requirement` | always `full_card_mapping` in this MVP freeze |
| `integrity_checks_required` | direct reference or existence checks the gateway expects before execution |
| `atomicity_expectation` | single-card atomic replace expectation |
| `execution_state` | always `planned_only` in this milestone |
| `deferred_execution_note` | explicit reminder that no write happened |

Planning interpretation:

- `plan_create` and `plan_update` share the same plan result shape.
- The plan object is the success result for mutation planning.
- The plan object records intended execution semantics without performing IO.

## Success Vs Failure Communication Rule

At the contract level:

- Success is returned as the operation's native domain shape:
  `CardMapping`, `bool`, `tuple[CardMapping, ...]`, or
  `MutationPlanDescriptor`.
- Failure is communicated by raising a gateway/domain exception from the frozen
  registry error taxonomy.
- `exists` is the one special case where absence is returned as `False` rather
  than as `CardNotFoundError`.

## Non-Goals

This milestone does not add or imply:

- runtime gateway implementation
- registry IO
- serializer or deserializer implementation
- parser or validation engine
- patch-merging engine
- retry runtime
- concurrency or locking runtime
- transaction engine
