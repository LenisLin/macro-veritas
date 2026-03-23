# Public StudyCard Ingest CLI

## Purpose

This document is the source of truth for the public `StudyCard` ingest surface.

- It defines the public `ingest study` command in both supported modes.
- It fixes the end-to-end StudyCard create bridge: raw CLI input or one YAML mapping -> normalized StudyCard ingest input -> `StudyCardPayload` -> gateway create -> canonical YAML file write.
- It keeps the scope narrow: create-only StudyCard ingest and nothing broader.

## Supported Public Modes

### Flag-Based Mode

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

### File-Based Mode

```bash
macro-veritas ingest study --from-file <path.yaml>
```

The detailed file contract for file-based mode is frozen at [`docs/public_ingest_studycard_from_file.md`](public_ingest_studycard_from_file.md).

## Flag-Based Required Arguments

- `--study-id`
- `--citation-handle`
- `--tumor-type` at least once
- `--therapy-scope` at least once
- `--relevance-scope` at least once
- `--screening-decision`
- `--status`
- `--created-from`

## Flag-Based Optional Arguments

- `--screening-note`
- `--source-artifact`

## Mixed-Input Rule

- Exactly one StudyCard ingest mode is allowed per invocation.
- `--from-file` cannot be combined with any StudyCard field flags.
- Mixed usage fails cleanly as `ingest study failed [invalid_payload]: ...` before gateway work.
- No precedence rule exists in this milestone.

## Create-Only Behavior

- Both modes are create-only.
- Both modes go through the same internal StudyCard ingest bridge.
- Both modes prepare a StudyCard create plan and then execute StudyCard create through the registry gateway.
- If the target StudyCard already exists, the command fails and does not update or replace the existing file.
- No patch mode or update mode exists in this milestone.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line confirming the create, for example `ingest study: created StudyCard study-001`
- Side effect: one canonical YAML file is written to the configured registry root by the existing StudyCard gateway/runtime layer

## Failure Output Expectations

- Exit code: non-zero
- Output channel: standard error
- Output style: one concise command-level failure line
- Parser-level invalid choices still use standard `argparse` error output and exit non-zero.
- File and normalization failures are surfaced as `invalid_payload`.
- Gateway/domain failures are translated into the command result categories: `duplicate_target`, `invalid_payload`, `unsupported_operation`, and `registry_failure`.
- The intended user-facing surface is command-level messaging, not a raw filesystem traceback.

## Non-Goals

- StudyCard update or patch ingest
- batch ingest
- directory scans or config-file-driven bulk ingest
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
