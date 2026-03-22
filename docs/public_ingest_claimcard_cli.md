# Public ClaimCard Ingest CLI

## Purpose

This document is the source of truth for the third real public domain command
in MacroVeritas.

- It defines the public `ClaimCard` ingest CLI surface.
- It fixes the third end-to-end public path:
  raw CLI args -> normalized ClaimCard ingest input -> `ClaimCardPayload` ->
  gateway create -> canonical YAML file write.
- It keeps the scope narrow: create-only `ClaimCard` ingest and nothing
  broader.

## Exact Command Shape

The public command is:

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

Notes:

- `--dataset-id` is repeatable.
- The CLI uses the frozen ClaimCard field names already documented in the
  repository where they differ from earlier preferred shorthand.
- No `--source-artifact` flag exists for ClaimCard in this milestone because
  that field is not part of the frozen ClaimCard contract.
- The same path is also reachable as
  `python -m macro_veritas ingest claim ...`.

## Required CLI Arguments

- `--claim-id`
- `--study-id`
- `--claim-text`
- `--claim-type`
- `--provenance-pointer`
- `--status`
- `--review-readiness`
- `--created-from`

## Optional CLI Arguments

- `--dataset-id` repeated zero or more times
- `--claim-summary-handle`

## Create-Only Behavior

- This command is create-only.
- It always prepares a create plan and then executes a create through the
  existing `ClaimCard` gateway path.
- If the target `ClaimCard` already exists, the command fails and does not
  update or replace the existing file.
- No patch mode or update mode exists in this milestone.

## Parent StudyCard Requirement

- `ClaimCard.study_id` must point to an existing canonical parent `StudyCard`.
- The existence check is enforced at the registry gateway boundary.
- A missing parent StudyCard is surfaced to the CLI as a clean command-level
  failure category: `missing_reference`.

## Optional DatasetCard Reference Requirement

- `ClaimCard.dataset_ids` is optional.
- If one or more `--dataset-id` flags are provided, each referenced
  `DatasetCard` must already exist at its canonical path.
- These existence checks are enforced at the registry gateway boundary.
- Missing referenced DatasetCards are surfaced to the CLI as a clean
  command-level failure category: `missing_reference`.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line confirming the create, for example
  `ingest claim: created ClaimCard claim-001`
- Side effect: one canonical YAML file is written to the configured registry
  root by the gateway/runtime layer

## Failure Output Expectations

- Exit code: non-zero
- Output channel: standard error
- Output style: one concise command-level failure line
- Parser-level malformed argument sets use standard `argparse` error output
  and exit non-zero.
- Domain/runtime failures are translated into the command result categories:
  `duplicate_target`, `missing_reference`, `invalid_payload`,
  `unsupported_operation`, and `registry_failure`.
- The intended user-facing surface is command-level messaging, not a raw
  filesystem traceback.

## Non-Goals

- `StudyCard` update or patch ingest
- `DatasetCard` update or patch ingest
- `ClaimCard` update or patch ingest
- config-file-driven ingest payloads
- `bind`, `extract`, `audit`, `review`, `run`, or `grade` public exposure
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
