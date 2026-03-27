# Public ClaimCard Ingest CLI

## Purpose

This document is the source of truth for the public `ClaimCard` ingest surface.

- It defines the public `ingest claim` command in both supported modes.
- It fixes the end-to-end ClaimCard create bridge: raw CLI input or one YAML mapping -> normalized ClaimCard ingest input -> `ClaimCardPayload` -> gateway create -> canonical YAML file write.
- It keeps the scope narrow: create-only ClaimCard ingest and nothing broader.

## Supported Public Modes

### Flag-Based Mode

```bash
macro-veritas ingest claim \
  --claim-id <ID> \
  --study-id <STUDY_ID> \
  --claim-text <TEXT> \
  --claim-type <TEXT> \
  --provenance-pointer <TEXT> \
  --status <captured|scoped|ready|closed> \
  --review-readiness <needs_scope|reviewable|execution_candidate> \
  --created-from <TEXT> \
  [--dataset-id <DATASET_ID>] \
  [--dataset-id <DATASET_ID> ...] \
  [--claim-summary-handle <TEXT>]
```

### File-Based Mode

```bash
macro-veritas ingest claim --from-file <path.yaml>
```

The detailed file contract for file-based mode is frozen at [`docs/public_ingest_claimcard_from_file.md`](public_ingest_claimcard_from_file.md).

## Flag-Based Required Arguments

- `--claim-id`
- `--study-id`
- `--claim-text`
- `--claim-type`
- `--provenance-pointer`
- `--status`
- `--review-readiness`
- `--created-from`

## Flag-Based Optional Arguments

- `--dataset-id` repeated zero or more times
- `--claim-summary-handle`

## File-Based Input Keys

The file-based path uses the existing ClaimCard ingest-input names:

- required: `claim_id`, `study_id`, `claim_text`, `claim_type`, `provenance_pointer`, `status`, `review_readiness`, `created_from`
- optional: `dataset_ids`, `claim_summary_handle`

The canonical stored ClaimCard still writes `created_from_note` after payload preparation.

## Mixed-Input Rule

- Exactly one ClaimCard ingest mode is allowed per invocation.
- `--from-file` cannot be combined with any ClaimCard field flags.
- Mixed usage fails cleanly as `ingest claim failed [invalid_payload]: ...` before gateway work.
- No precedence rule exists in this milestone.

## Create-Only Behavior

- Both modes are create-only.
- Both modes go through the same internal ClaimCard ingest bridge.
- Both modes prepare a ClaimCard create plan and then execute ClaimCard create through the registry gateway.
- Both modes now run under the same reference-aware ClaimCard ingest locking rule.
- If the target ClaimCard already exists, the command fails and does not update or replace the existing file.
- No patch mode or update mode exists in this milestone.

## Parent StudyCard Requirement

- `ClaimCard.study_id` must point to an existing canonical parent `StudyCard`.
- The existence check is enforced at the registry gateway boundary while the
  ClaimCard ingest lock set is held.
- A missing parent StudyCard is surfaced to the CLI as a clean `missing_reference` failure.

## Optional DatasetCard Reference Requirement

- `ClaimCard.dataset_ids` is optional.
- If one or more dataset IDs are provided, each referenced `DatasetCard` must already exist at its canonical path.
- These existence checks are enforced at the registry gateway boundary while
  the ClaimCard ingest lock set is held.
- Missing referenced DatasetCards are surfaced to the CLI as a clean `missing_reference` failure.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line confirming the create, for example `ingest claim: created ClaimCard claim-001`
- Side effect: one canonical YAML file is written to the configured registry
  root by the existing ClaimCard gateway/runtime layer after reference
  validation plus duplicate-target checks complete under the ClaimCard ingest
  lock set

## Failure Output Expectations

- Exit code: non-zero
- Output channel: standard error
- Output style: one concise command-level failure line
- Parser-level invalid choices still use standard `argparse` error output and exit non-zero.
- File and normalization failures are surfaced as `invalid_payload`.
- Gateway/domain failures are translated into the command result categories: `duplicate_target`, `missing_reference`, `invalid_payload`, `unsupported_operation`, and `registry_failure`.
- The intended user-facing surface is command-level messaging, not a raw filesystem traceback.

## Non-Goals

- ClaimCard update or patch ingest
- batch ingest
- directory scans or config-file-driven bulk ingest
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
