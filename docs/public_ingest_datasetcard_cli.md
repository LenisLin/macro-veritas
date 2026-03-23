# Public DatasetCard Ingest CLI

## Purpose

This document is the source of truth for the public `DatasetCard` ingest surface.

- It defines the public `ingest dataset` command in both supported modes.
- It fixes the end-to-end DatasetCard create bridge: raw CLI input or one YAML mapping -> normalized DatasetCard ingest input -> `DatasetCardPayload` -> gateway create -> canonical YAML file write.
- It keeps the scope narrow: create-only DatasetCard ingest and nothing broader.

## Supported Public Modes

### Flag-Based Mode

```bash
macro-veritas ingest dataset \
  --dataset-id <ID> \
  --study-id <STUDY_ID> \
  --status <identified|registered|bound|retired> \
  --modality-scope <TEXT> \
  --platform-summary <TEXT> \
  --cohort-summary <TEXT> \
  --locator-confidence-note <TEXT> \
  --source-locator <TEXT> \
  --availability-status <unknown|open|restricted|unavailable> \
  [--accession-id <TEXT>] \
  [--availability-note <TEXT>] \
  [--artifact-locator <TEXT>]
```

### File-Based Mode

```bash
macro-veritas ingest dataset --from-file <path.yaml>
```

The detailed file contract for file-based mode is frozen at [`docs/public_ingest_datasetcard_from_file.md`](public_ingest_datasetcard_from_file.md).

## Flag-Based Required Arguments

- `--dataset-id`
- `--study-id`
- `--status`
- `--modality-scope` at least once
- `--platform-summary`
- `--cohort-summary`
- `--locator-confidence-note`
- `--source-locator`
- `--availability-status`

## Flag-Based Optional Arguments

- `--accession-id`
- `--availability-note`
- `--artifact-locator`

## Mixed-Input Rule

- Exactly one DatasetCard ingest mode is allowed per invocation.
- `--from-file` cannot be combined with any DatasetCard field flags.
- Mixed usage fails cleanly as `ingest dataset failed [invalid_payload]: ...` before gateway work.
- No precedence rule exists in this milestone.

## Create-Only Behavior

- Both modes are create-only.
- Both modes go through the same internal DatasetCard ingest bridge.
- Both modes prepare a DatasetCard create plan and then execute DatasetCard create through the registry gateway.
- If the target DatasetCard already exists, the command fails and does not update or replace the existing file.
- No patch mode or update mode exists in this milestone.

## Parent StudyCard Requirement

- `DatasetCard.study_id` must point to an existing canonical parent `StudyCard`.
- The existence check is enforced at the registry gateway boundary.
- A missing parent StudyCard is surfaced to the CLI as a clean `missing_reference` failure.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line confirming the create, for example `ingest dataset: created DatasetCard dataset-001`
- Side effect: one canonical YAML file is written to the configured registry root by the existing DatasetCard gateway/runtime layer

## Failure Output Expectations

- Exit code: non-zero
- Output channel: standard error
- Output style: one concise command-level failure line
- Parser-level invalid choices still use standard `argparse` error output and exit non-zero.
- File and normalization failures are surfaced as `invalid_payload`.
- Gateway/domain failures are translated into the command result categories: `duplicate_target`, `missing_reference`, `invalid_payload`, `unsupported_operation`, and `registry_failure`.
- The intended user-facing surface is command-level messaging, not a raw filesystem traceback.

## Non-Goals

- DatasetCard update or patch ingest
- batch ingest
- directory scans or config-file-driven bulk ingest
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
