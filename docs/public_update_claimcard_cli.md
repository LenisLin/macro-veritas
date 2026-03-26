# Public ClaimCard Update CLI

## Purpose

This document is the source of truth for the ClaimCard public update CLI
milestone.

- It defines the public `update claim` surface.
- It fixes the narrow bridge: explicit target ID -> YAML file load -> full-card
  ClaimCard replacement -> gateway plan/update -> canonical YAML replace.
- It keeps scope narrow: ClaimCard only, file-only, full-replace only.

## Exact CLI Shape

The public command is:

```bash
macro-veritas update claim --claim-id <ID> --from-file <path.yaml>
```

The same path is also reachable as:

```bash
python -m macro_veritas update claim --claim-id <ID> --from-file <path.yaml>
```

## Full-Replace-Only Rule

- The YAML file must describe one complete replacement `ClaimCard`.
- Patch, merge, or partial-update semantics do not exist in this milestone.
- The file uses the canonical stored `ClaimCard` field names, not the
  create-ingest aliases used by `ingest claim --from-file`.

## Required YAML Keys

- `claim_id`
- `study_id`
- `claim_text`
- `claim_type`
- `provenance_pointer`
- `status`
- `review_readiness`
- `created_from_note`

## Optional YAML Keys

- `dataset_ids`
  - If provided, it must be a YAML sequence of strings.
- `claim_summary_handle`

If an optional key is provided, it must be a string.

## Target-Match Rule

- The CLI requires `--claim-id <ID>`.
- The YAML file must contain `claim_id`.
- The CLI target and file target must match exactly.
- A mismatch fails before gateway update execution and is surfaced as a clean
  `invalid_payload` CLI failure.

## Reference Re-Validation Rule

- The replacement file must still point to an existing parent `StudyCard`.
- Parent existence is re-checked at update time through the registry gateway.
- If `dataset_ids` is present and non-empty, each referenced `DatasetCard`
  must also exist at update time.
- Missing parent or dataset references are surfaced as clean
  `missing_reference` CLI failures.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line, for example `update claim: updated ClaimCard claim-001`

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
  - CLI `--claim-id` / file `claim_id` mismatch
  - missing target `ClaimCard`
  - missing parent `StudyCard`
  - missing referenced `DatasetCard` IDs
  - invalid payload
  - registry gateway failure

## Non-Goals

- patch or partial update
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
