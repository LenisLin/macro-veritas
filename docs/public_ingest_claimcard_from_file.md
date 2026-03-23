# Public ClaimCard From-File Ingest

## Purpose

This document is the source of truth for file-based `ClaimCard` ingest.

- It defines the public `ingest claim --from-file` path.
- It fixes the narrow bridge: file path -> YAML mapping load -> normalized ClaimCard ingest input -> `ClaimCardPayload` -> gateway create -> canonical YAML write.
- It stays aligned with the StudyCard and DatasetCard file-ingest paths: single-file, create-only, YAML-mapping ingest only.

## Exact CLI Shape

The public command is:

```bash
macro-veritas ingest claim --from-file <path.yaml>
```

The same path is also reachable as:

```bash
python -m macro_veritas ingest claim --from-file <path.yaml>
```

## Input File Format

- Format: YAML only
- File shape: one mapping at the document root
- File count: one file only
- YAML is loaded safely and the root mapping keys must be strings
- Input keys use the existing ClaimCard ingest-input names, not the stored canonical YAML names
- In particular, the input file uses `created_from`; the stored canonical ClaimCard still writes `created_from_note`

Example:

```yaml
claim_id: claim-001
study_id: study-001
claim_text: Claim text for claim-001
claim_type: association
provenance_pointer: figure-2
status: captured
review_readiness: needs_scope
created_from: seeded in claim file ingest
claim_summary_handle: claim-1
dataset_ids:
  - dataset-001
  - dataset-002
```

## Required Keys

- `claim_id`
- `study_id`
- `claim_text`
- `claim_type`
- `provenance_pointer`
- `status`
- `review_readiness`
- `created_from`

## Optional Keys

- `dataset_ids`
  - If provided, it must be a YAML sequence of strings.
- `claim_summary_handle`
  - If provided, it must be a string.

## Mixed-Input Rule

- `--from-file` cannot be combined with ClaimCard field flags.
- This includes required field flags such as `--claim-id` and optional field flags such as `--dataset-id`.
- Mixed usage fails at the command layer before gateway work.
- Mixed usage is surfaced as an `invalid_payload` CLI failure.
- There is no precedence rule in this milestone.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line, for example `ingest claim: created ClaimCard claim-001`
- Side effect: the existing ClaimCard create path writes one canonical YAML file beneath the configured registry root

## Failure Output Expectations

- Exit code: non-zero
- Output channel: standard error
- Output style: one concise command-level failure line
- No raw stack trace is the intended public surface
- Expected clean failure classes include:
  - file not found
  - YAML parse failure
  - non-mapping YAML root
  - missing required keys
  - unsupported mixed `--from-file` plus field-flag usage
  - missing parent `StudyCard`
  - missing referenced `DatasetCard` IDs
  - duplicate ClaimCard create
  - generic registry gateway failure

## Non-Goals

- batch ingest
- directory scans or config-driven file discovery
- update, replace, or patch semantics
- JSON input mode as a public contract
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
