# Public DatasetCard Ingest CLI

## Purpose

This document is the source of truth for the second real public domain command
in MacroVeritas.

- It defines the public `DatasetCard` ingest CLI surface.
- It fixes the second end-to-end public path:
  raw CLI args -> normalized DatasetCard ingest input -> `DatasetCardPayload`
  -> gateway create -> canonical YAML file write.
- It keeps the scope narrow: create-only `DatasetCard` ingest and nothing
  broader.

## Exact Command Shape

The public command is:

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

Notes:

- `--modality-scope` is repeatable because the frozen `DatasetCard` contract
  stores `modality_scope_tags` as a sequence.
- The CLI uses the actual frozen DatasetCard field names already documented in
  the repository where those differ from the earlier preferred shorthand.
- The same path is also reachable as
  `python -m macro_veritas ingest dataset ...`.

## Required CLI Arguments

- `--dataset-id`
- `--study-id`
- `--status`
- `--modality-scope` at least once
- `--platform-summary`
- `--cohort-summary`
- `--locator-confidence-note`
- `--source-locator`
- `--availability-status`

## Optional CLI Arguments

- `--accession-id`
- `--availability-note`
- `--artifact-locator`

## Create-Only Behavior

- This command is create-only.
- It always prepares a create plan and then executes a create through the
  existing `DatasetCard` gateway path.
- If the target `DatasetCard` already exists, the command fails and does not
  update or replace the existing file.
- No patch mode or update mode exists in this milestone.

## Parent StudyCard Requirement

- `DatasetCard.study_id` must point to an existing canonical parent
  `StudyCard`.
- The existence check is enforced at the registry gateway boundary.
- A missing parent StudyCard is surfaced to the CLI as a clean command-level
  failure category: `missing_reference`.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line confirming the create, for example
  `ingest dataset: created DatasetCard dataset-001`
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

- `ClaimCard` public ingest
- `StudyCard` update or patch ingest
- `DatasetCard` update or patch ingest
- config-file-driven ingest payloads
- `bind`, `extract`, `audit`, `review`, `run`, or `grade` public exposure
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
