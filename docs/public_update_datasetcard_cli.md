# Public DatasetCard Update CLI

## Purpose

This document is the source of truth for the first public update CLI milestone.

- It defines the public `update dataset` surface.
- It fixes the narrow bridge: explicit target ID -> YAML file load -> full-card
  DatasetCard replacement -> gateway plan/update -> canonical YAML replace.
- It keeps scope narrow: DatasetCard only, file-only, full-replace only.

## Exact CLI Shape

The public command is:

```bash
macro-veritas update dataset --dataset-id <ID> --from-file <path.yaml>
```

The same path is also reachable as:

```bash
python -m macro_veritas update dataset --dataset-id <ID> --from-file <path.yaml>
```

## Full-Replace-Only Rule

- The YAML file must describe one complete replacement `DatasetCard`.
- Patch, merge, or partial-update semantics do not exist in this milestone.
- The file uses the canonical stored `DatasetCard` field names, not the
  create-ingest aliases used by `ingest dataset --from-file`.

## Required YAML Keys

- `dataset_id`
- `study_id`
- `source_locator`
- `availability_status`
- `modality_scope_tags`
  - Must be a YAML sequence of strings.
- `cohort_summary`
- `platform_summary`
- `status`
- `locator_confidence_note`

## Optional YAML Keys

- `accession_id`
- `artifact_locator`
- `availability_note`

If an optional key is provided, it must be a string.

## Target-Match Rule

- The CLI requires `--dataset-id <ID>`.
- The YAML file must contain `dataset_id`.
- The CLI target and file target must match exactly.
- A mismatch fails before gateway update execution and is surfaced as a clean
  `invalid_payload` CLI failure.

## Parent StudyCard Re-Validation Rule

- The replacement file must still point to an existing parent `StudyCard`.
- Parent existence is re-checked at update time through the registry gateway.
- A missing parent StudyCard is surfaced as a clean `missing_reference` CLI failure.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line, for example `update dataset: updated DatasetCard dataset-001`

## Failure Output Expectations

- Exit code: non-zero
- Output channel: standard error
- Output style: one concise command-level failure line
- No raw stack trace is the intended public surface
- Expected clean failure classes include:
  - file not found
  - YAML parse failure
  - non-mapping YAML root
  - missing required keys / incomplete full-card payload
  - CLI `--dataset-id` / file `dataset_id` mismatch
  - missing parent `StudyCard`
  - missing target `DatasetCard`
  - invalid payload
  - registry gateway failure

## Non-Goals

- patch or partial update
- StudyCard update
- ClaimCard update
- field-flag update input
- batch update
- update by filter or search
- force override
- optimistic locking or versioning
- manifest or index engines
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
