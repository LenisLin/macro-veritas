# Card Contracts

## Scope

This document is the field-level source of truth for the first frozen registry slice:

- `StudyCard`
- `DatasetCard`
- `ClaimCard`

The freeze in this document is intentionally narrow.

- It defines field names, minimal status vocabularies, and direct card-to-card pointers.
- It defines the stored card representation for this first slice.
- Gateway-facing payload and read/list DTO shapes live separately in
  [`docs/payload_contracts.md`](payload_contracts.md).
- StudyCard runtime file format and IO behavior now live in
  [`docs/studycard_runtime.md`](studycard_runtime.md).
- DatasetCard runtime file format and IO behavior now live in
  [`docs/datasetcard_runtime.md`](datasetcard_runtime.md).
- It does not define validation engines or scientific interpretation logic.
- Remaining card families stay conceptual in `docs/registry_model.md` and `docs/data_contracts.md`.

## Stored Card Contract Vs Payload Contract

This document freezes the canonical stored card field contract.

- [`docs/payload_contracts.md`](payload_contracts.md) freezes the
  command-to-gateway transfer shapes used for create/update planning and bare
  gateway reads.
- For the first slice, those payloads intentionally reuse the same field sets
  as the stored card contracts.
- The StudyCard and DatasetCard runtimes store those same field names directly
  as YAML mappings with no hidden metadata layer.
- They remain distinct boundary layers because command handlers should prepare
  gateway payloads, while storage concerns remain governed by the stored card
  contract and future registry IO boundary.

## `StudyCard`

### Purpose

Represent the canonical study or paper unit tracked by MacroVeritas so downstream cards can anchor to one stable study identity.

### Ownership / producer / primary consumer

- Producer: human curator or project lead during paper intake.
- Primary owner: registry-facing curator responsibility.
- Primary consumers: `DatasetCard`, `ClaimCard`, and later routine review.

### Persistence expectation

- Stored as a small YAML registry card at `studies/<study_id>.yaml` beneath the
  configured registry root.
- The first runtime slice now reads and writes this representation through the
  registry gateway only.

### Required fields

| Field | Meaning |
| --- | --- |
| `study_id` | Stable MacroVeritas identifier for the tracked study record. |
| `citation_handle` | Canonical citation handle for the paper or study source, such as DOI, PMID, or an internal citation key when no external handle is available. |
| `tumor_scope_tags` | Short tags describing the tumor or disease scope tracked for this study. |
| `therapy_scope_tags` | Short tags describing the therapy or intervention scope tracked for this study. |
| `relevance_scope_tags` | Short tags describing why the study is in scope for the project. |
| `screening_decision` | Intake decision label for inclusion tracking. Expected values for this slice: `pending`, `include`, `exclude`. |
| `status` | Study lifecycle status. Allowed values: `draft`, `registered`, `closed`. |
| `created_from_note` | Short provenance note describing how the study record was created or entered into the registry. |

### Optional fields

| Field | Meaning |
| --- | --- |
| `screening_note` | Human note explaining the current inclusion/exclusion position. |
| `source_artifact_locator` | Optional local or remote locator for a PDF, supplement, or intake artifact associated with the study source. |

### Required status field and allowed values

- Required field: `status`
- Allowed values:
  - `draft`: intake candidate exists, but the study record is still being screened or completed.
  - `registered`: study is in scope and has enough identity and provenance to anchor downstream cards.
  - `closed`: study record remains for traceability but is excluded, superseded, or intentionally retired.

### Required provenance/reference fields

- `citation_handle`
- `created_from_note`

Optional supporting reference field:

- `source_artifact_locator`

### Relationship pointers to other cards

- No outbound card pointer is required on `StudyCard` in this milestone.
- `StudyCard` is the anchor target referenced by:
  - `DatasetCard.study_id`
  - `ClaimCard.study_id`

### Explicit non-goals for this milestone

- No citation parsing or DOI resolution.
- No screening rule engine or automatic inclusion logic.
- No additional registry workflow logic beyond the narrow runtime slice
  documented separately in `docs/studycard_runtime.md`.
- No backlinks to `EvidenceCard` or `AuditRecord`.

## `DatasetCard`

### Purpose

Represent one dataset associated with a study together with the minimum locator and binding metadata needed for later registry planning.

### Ownership / producer / primary consumer

- Producer: human curator or analyst during dataset identification or binding.
- Primary owner: registry-facing curator or analyst.
- Primary consumers: later claim review, run planning, and routine review.

### Persistence expectation

- Stored as a small YAML registry card at `datasets/<dataset_id>.yaml` beneath
  the configured registry root.
- The current runtime reads and writes this representation through the registry
  gateway only.
- It may later reference paths under `raw/` or `processed/`, but this
  milestone does not implement those bindings.

### Required fields

| Field | Meaning |
| --- | --- |
| `dataset_id` | Stable MacroVeritas identifier for the dataset record. |
| `study_id` | Required pointer back to the owning `StudyCard`. |
| `source_locator` | Primary accession, URL, supplement reference, or equivalent locator used to find the dataset. |
| `availability_status` | Short access label for the dataset. Expected values for this slice: `unknown`, `open`, `restricted`, `unavailable`. |
| `modality_scope_tags` | Short tags describing the dataset modality or data-type scope. |
| `cohort_summary` | Minimal human-readable summary of the cohort represented by the dataset. |
| `platform_summary` | Minimal human-readable summary of platform, assay, or acquisition context. |
| `status` | Dataset lifecycle status. Allowed values: `identified`, `registered`, `bound`, `retired`. |
| `locator_confidence_note` | Short provenance note explaining how confident the project is that the locator or accession points to the intended dataset. |

### Optional fields

| Field | Meaning |
| --- | --- |
| `accession_id` | Separate accession identifier when it is useful to keep distinct from `source_locator`. |
| `artifact_locator` | Optional local project path or external locator for the bound artifact once one exists. |
| `availability_note` | Human note adding context about access conditions or binding limitations. |

### Required status field and allowed values

- Required field: `status`
- Allowed values:
  - `identified`: dataset is known, but the registry record is still incomplete.
  - `registered`: dataset has enough identity and provenance to be tracked.
  - `bound`: dataset has a concrete usable binding or artifact locator for project work.
  - `retired`: dataset remains for traceability but is no longer the preferred active binding.

### Required provenance/reference fields

- `study_id`
- `source_locator`
- `locator_confidence_note`

Optional supporting reference fields:

- `accession_id`
- `artifact_locator`

### Relationship pointers to other cards

- Required outbound pointer:
  - `study_id -> StudyCard.study_id`
- No `ClaimCard` backlinks are stored on `DatasetCard` in this milestone.

### Explicit non-goals for this milestone

- No dataset download logic or registry binding IO.
- No filesystem existence checks or locator resolution engine.
- No platform ontology or cohort schema beyond these summary fields.
- No links to `EvidenceCard` or `AuditRecord`.

## `ClaimCard`

### Purpose

Represent one scoped scientific claim candidate so later review or reanalysis planning can work from an explicit claim unit rather than free text notes.

### Ownership / producer / primary consumer

- Producer: human curator or reviewer during claim extraction.
- Primary owner: registry-facing curator or reviewer.
- Primary consumers: later review, reanalysis planning, and routine audit.

### Persistence expectation

- Planned as a small registry card under `registry/`.
- Current milestone freezes only the static field contract and direct pointers.

### Required fields

| Field | Meaning |
| --- | --- |
| `claim_id` | Stable MacroVeritas identifier for the claim record. |
| `study_id` | Required pointer back to the owning `StudyCard`. |
| `claim_text` | Human-readable claim text captured from the source study. |
| `claim_type` | Short category label describing the kind of claim being tracked. |
| `provenance_pointer` | Figure, table, supplement, or text-span pointer describing where the claim came from. |
| `status` | Claim lifecycle status. Allowed values: `captured`, `scoped`, `ready`, `closed`. |
| `review_readiness` | Minimal readiness label for later review or execution planning. Expected values for this slice: `needs_scope`, `reviewable`, `execution_candidate`. |
| `created_from_note` | Short provenance note describing how the claim record was created. |

### Optional fields

| Field | Meaning |
| --- | --- |
| `dataset_ids` | Zero, one, or many linked `DatasetCard` identifiers when a dataset connection is known. |
| `claim_summary_handle` | Optional normalized summary handle when later workflow wants a stable shorthand in addition to `claim_text`. |

### Required status field and allowed values

- Required field: `status`
- Allowed values:
  - `captured`: claim has been recorded, but scope or linkage is still incomplete.
  - `scoped`: study linkage and claim boundary are clear enough for review.
  - `ready`: claim has enough provenance and context to enter later binding or evaluation work.
  - `closed`: claim remains for traceability but has been deferred, superseded, or intentionally retired.

### Required provenance/reference fields

- `study_id`
- `provenance_pointer`
- `created_from_note`

Optional supporting reference field:

- `dataset_ids`

### Relationship pointers to other cards

- Required outbound pointer:
  - `study_id -> StudyCard.study_id`
- Optional outbound pointer:
  - `dataset_ids -> DatasetCard.dataset_id`

### Explicit non-goals for this milestone

- No claim extraction engine or text-span parser.
- No scientific truth evaluation or evidence grading logic.
- No enforcement that `dataset_ids` must already exist in a registry.
- No links to `EvidenceCard` or `AuditRecord`.
