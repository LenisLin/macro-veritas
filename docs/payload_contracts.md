# Payload Contracts

## Purpose

This document is the source of truth for the first frozen command-to-gateway
payload and DTO contract.

- It freezes the payload shapes that internal command handlers are expected to
  prepare for the first slice.
- It freezes the DTO-like mapping shapes that future registry gateway
  read/list/plan functions are expected to accept or return.
- It does not imply parser implementation, runtime gateway execution,
  serialization, or validation behavior.

## Boundary Layers

The relevant boundary layers are intentionally distinct:

| Layer | Meaning | Freeze Status In This Milestone |
| --- | --- | --- |
| raw CLI argument layer | future `argparse` flags, options, and raw parsed objects | deferred |
| command-normalized input layer | internal command-family input after raw CLI parsing or equivalent caller input has been normalized into small family-specific values | frozen at the boundary-rule level, with one real path now implemented for internal StudyCard ingest |
| gateway payload / DTO layer | full-card payload mappings accepted by gateway create/update planning and bare card mappings returned by gateway reads | frozen here |
| stored card representation layer | canonical stored `StudyCard` / `DatasetCard` / `ClaimCard` field contract | frozen in [`docs/card_contracts.md`](card_contracts.md) |

Interpretation rules:

- This milestone freezes the middle two layers only.
- Raw `argparse` objects are not part of the gateway contract.
- Stored card fields remain governed by [`docs/card_contracts.md`](card_contracts.md).
- For the first slice, gateway create/update payloads intentionally use the
  same field sets as the stored card contracts, but they remain a separate
  interface boundary because they are command-to-gateway transfer objects.

## Shared Payload Rules

These rules apply to all first-slice payload families:

- Create and update planning use the same payload shape within a card family.
- Gateway-facing mutation planning accepts full-card payloads only.
- Partial patch payloads are out of contract for this MVP.
- Scalar IDs, notes, summaries, handles, and locators are plain strings.
- Tag collections and linked-card collections are sequences of strings.
- No payload family in this milestone includes parser-only artifacts,
  serializer-only metadata, validation reports, or runtime execution state.

## First-Slice Payload Families

### `StudyCard` create/update payload

Frozen gateway payload type name: `StudyCardPayload`

| Category | Frozen Contract |
| --- | --- |
| required keys | `study_id`, `citation_handle`, `tumor_scope_tags`, `therapy_scope_tags`, `relevance_scope_tags`, `screening_decision`, `status`, `created_from_note` |
| optional keys | `screening_note`, `source_artifact_locator` |
| full-card rule | yes; both create and update planning expect the complete `StudyCardPayload` |
| relationship pointer expectations | no outbound card pointer is required in this payload family; `study_id` is the anchor referenced by downstream cards |
| intentionally excluded | parser flag objects, citation parsing output, screening engine output, backlinks, patch fragments |

Expected value-shape notes:

- `tumor_scope_tags`, `therapy_scope_tags`, and `relevance_scope_tags` are
  sequences of strings.
- `screening_decision` stays within the first-slice vocabulary:
  `pending`, `include`, `exclude`.
- `status` stays within the first-slice lifecycle vocabulary frozen in
  [`docs/card_contracts.md`](card_contracts.md).
- The internal StudyCard ingest bridge now prepares this payload from the
  command-facing keys `study_id`, `citation_handle`, `tumor_type`,
  `therapy_scope`, `relevance_scope`, `screening_decision`, `status`,
  `created_from`, optional `screening_note`, and optional `source_artifact`.
- That bridge maps `tumor_type` / `therapy_scope` / `relevance_scope` to
  `tumor_scope_tags` / `therapy_scope_tags` / `relevance_scope_tags`, maps
  `created_from` to `created_from_note`, and maps `source_artifact` to
  `source_artifact_locator`.

### `DatasetCard` create/update payload

Frozen gateway payload type name: `DatasetCardPayload`

| Category | Frozen Contract |
| --- | --- |
| required keys | `dataset_id`, `study_id`, `source_locator`, `availability_status`, `modality_scope_tags`, `cohort_summary`, `platform_summary`, `status`, `locator_confidence_note` |
| optional keys | `accession_id`, `artifact_locator`, `availability_note` |
| full-card rule | yes; both create and update planning expect the complete `DatasetCardPayload` |
| relationship pointer expectations | `study_id` is required and points to `StudyCard.study_id`; no `ClaimCard` backlinks are carried in this payload family |
| intentionally excluded | parser flag objects, filesystem probes, artifact existence checks, locator-resolution output, patch fragments |

Expected value-shape notes:

- `modality_scope_tags` is a sequence of strings.
- `availability_status` stays within the first-slice vocabulary:
  `unknown`, `open`, `restricted`, `unavailable`.
- `status` stays within the first-slice lifecycle vocabulary frozen in
  [`docs/card_contracts.md`](card_contracts.md).

### `ClaimCard` create/update payload

Frozen gateway payload type name: `ClaimCardPayload`

| Category | Frozen Contract |
| --- | --- |
| required keys | `claim_id`, `study_id`, `claim_text`, `claim_type`, `provenance_pointer`, `status`, `review_readiness`, `created_from_note` |
| optional keys | `dataset_ids`, `claim_summary_handle` |
| full-card rule | yes; both create and update planning expect the complete `ClaimCardPayload` |
| relationship pointer expectations | `study_id` is required and points to `StudyCard.study_id`; `dataset_ids` is optional and, when present, contains one or more `DatasetCard.dataset_id` values |
| intentionally excluded | parser flag objects, extraction-engine output, grading fields, evidence judgments, patch fragments |

Expected value-shape notes:

- `dataset_ids` is a sequence of strings when present.
- `review_readiness` stays within the first-slice vocabulary:
  `needs_scope`, `reviewable`, `execution_candidate`.
- `status` stays within the first-slice lifecycle vocabulary frozen in
  [`docs/card_contracts.md`](card_contracts.md).

### Read and list DTO expectations

Read and list DTOs stay deliberately simple:

- `get_*` returns one bare card mapping shaped like the frozen card contract
  for that family.
- `list_*` returns a tuple of such bare card mappings for that family.
- `exists_*` returns bare `bool`.
- No read wrapper envelope is introduced in this milestone.

## Read Result Rule

The read result rule is frozen as follows:

- Gateway reads return bare card mappings shaped like the frozen card contract.
- Gateway list operations return tuples or other fixed sequences of those same
  card mappings.
- Gateway existence checks remain plain `bool`.
- Higher layers should consume those DTO-like mappings rather than raw storage
  or parser objects.

## Mutation Plan Rule

The minimum payload-to-plan relationship is frozen as follows:

- Commands prepare a full-card payload for one first-slice card family.
- Gateway `plan_create_*` and `plan_update_*` accept that full-card payload.
- Gateway `plan_create_*` and `plan_update_*` return a
  `MutationPlanDescriptor`.
- No mutation plan function accepts patch semantics in this milestone.
- No separate create schema and update schema is introduced because the first
  slice does not need a field difference between them.

## Command-Family Interpretation

This document does not freeze raw CLI flags. It does freeze what command
handlers are conceptually responsible for at the boundary:

- `ingest` prepares full-card create payloads for `StudyCard`,
  `DatasetCard`, or `ClaimCard`, and the internal StudyCard path now executes
  that payload through `plan_create_study_card(...)` followed by
  `create_study_card(...)`.
- `bind` may read a current card and then prepare a full-card replacement
  payload for update planning.
- `extract` may prepare a new or replacement `ClaimCardPayload` and may also
  prepare full replacement `StudyCardPayload` or `DatasetCardPayload` values
  when extraction follow-up refines those cards.
- `audit`, `review`, `run`, and `grade` remain read-oriented in the MVP slice;
  they consume gateway read/list DTOs but do not prepare first-slice mutation
  payloads.

## Non-Goals

This milestone does not add or imply:

- parser implementation
- raw CLI flag or option freeze
- serialization format enforcement beyond the already frozen card field
  contracts
- validation engine
- DTO conversion runtime
- patch-merging runtime
- scientific logic
- evidence grading
- registry IO
