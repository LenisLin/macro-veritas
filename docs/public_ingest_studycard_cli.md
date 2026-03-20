# Public StudyCard Ingest CLI

## Purpose

This document is the source of truth for the first real public domain command
in MacroVeritas.

- It defines the public `StudyCard` ingest CLI surface.
- It fixes the first end-to-end public path:
  raw CLI args -> normalized StudyCard ingest input -> `StudyCardPayload` ->
  gateway create -> canonical YAML file write.
- It keeps the scope narrow: create-only `StudyCard` ingest and nothing else.

## Exact Command Shape

The public command is:

```bash
macro-veritas ingest study \
  --study-id <ID> \
  --citation-handle <TEXT> \
  --tumor-type <TEXT> \
  --therapy-scope <TEXT> \
  --relevance-scope <TEXT> \
  --screening-decision <pending|include|exclude> \
  --status <draft|registered|closed> \
  --created-from <TEXT> \
  [--screening-note <TEXT>] \
  [--source-artifact <TEXT>]
```

Notes:

- `--tumor-type`, `--therapy-scope`, and `--relevance-scope` are repeatable.
- `pending|include|exclude` follows the frozen first-slice `StudyCard`
  contract already defined in the repository.
- The same path is also reachable as
  `python -m macro_veritas ingest study ...`.

## Required CLI Arguments

- `--study-id`
- `--citation-handle`
- `--tumor-type` at least once
- `--therapy-scope` at least once
- `--relevance-scope` at least once
- `--screening-decision`
- `--status`
- `--created-from`

## Optional CLI Arguments

- `--screening-note`
- `--source-artifact`

## Create-Only Behavior

- This command is create-only.
- It always prepares a create plan and then executes a create through the
  existing `StudyCard` gateway path.
- If the target `StudyCard` already exists, the command fails and does not
  update or replace the existing file.
- No patch mode or update mode exists in this milestone.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line confirming the create, for example
  `ingest study: created StudyCard study-001`
- Side effect: one canonical YAML file is written to the configured registry
  root by the gateway/runtime layer

## Failure Output Expectations

- Exit code: non-zero
- Output channel: standard error
- Output style: one concise command-level failure line
- Parser-level malformed argument sets use standard `argparse` error output
  and exit non-zero.
- Domain/runtime failures are translated into the command result categories:
  `duplicate_target`, `invalid_payload`, `unsupported_operation`, and
  `registry_failure`.
- The intended user-facing surface is command-level messaging, not a raw
  filesystem traceback.

## Non-Goals

- `DatasetCard` public ingest
- `ClaimCard` public ingest
- `StudyCard` update or patch ingest
- config-file-driven ingest payloads
- `bind`, `extract`, `audit`, `review`, `run`, or `grade` public exposure
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
