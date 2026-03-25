# Public DatasetCard From-File Ingest

## Purpose

This document is the source of truth for file-based `DatasetCard` ingest.

- It defines the public `ingest dataset --from-file` path.
- It fixes the narrow bridge: file path -> YAML mapping load -> normalized DatasetCard ingest input -> `DatasetCardPayload` -> gateway create -> canonical YAML write.
- It keeps the scope narrow: single-file, create-only, YAML-mapping DatasetCard ingest.
- It is distinct from `update dataset --dataset-id <ID> --from-file <path.yaml>`, which expects a complete canonical `DatasetCard` replacement file and performs update, not create.

## Exact CLI Shape

The public command is:

```bash
macro-veritas ingest dataset --from-file <path.yaml>
```

The same path is also reachable as:

```bash
python -m macro_veritas ingest dataset --from-file <path.yaml>
```

## Input File Format

- Format: YAML only
- File shape: one mapping at the document root
- File count: one file only
- Input keys use the existing DatasetCard ingest-input names, not the stored canonical YAML names
- In particular, this create path uses `modality_scope`; the update path uses the canonical stored field name `modality_scope_tags`

Example:

```yaml
dataset_id: dataset-001
study_id: study-001
status: identified
modality_scope:
  - rna-seq
platform_summary: Illumina
cohort_summary: adult cohort
locator_confidence_note: confirmed in supplement
source_locator: https://example.org/dataset-001
availability_status: open
accession_id: GSE12345
availability_note: open after registration
artifact_locator: raw/datasets/dataset-001.h5ad
```

## Required YAML Keys

- `dataset_id`
- `study_id`
- `status`
- `modality_scope`
  - Must be a YAML sequence of strings.
- `platform_summary`
- `cohort_summary`
- `locator_confidence_note`
- `source_locator`
- `availability_status`

## Optional YAML Keys

- `accession_id`
- `availability_note`
- `artifact_locator`

If an optional key is provided, it must be a string.

## Parent StudyCard Requirement

- `study_id` must point to an existing canonical parent `StudyCard`.
- The existence check is enforced at the registry gateway boundary.
- A missing parent StudyCard is surfaced to the CLI as a clean `missing_reference` failure.

## Mixed-Input Blocking Rule

- `--from-file` cannot be combined with DatasetCard field flags.
- This includes required field flags such as `--dataset-id` and optional field flags such as `--artifact-locator`.
- Mixed usage fails at the command layer before gateway work.
- Mixed usage is surfaced as an `invalid_payload` CLI failure.
- There is no precedence rule in this milestone.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line, for example `ingest dataset: created DatasetCard dataset-001`
- Side effect: the existing DatasetCard create path writes one canonical YAML file beneath the configured registry root

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
  - missing parent StudyCard
  - duplicate DatasetCard create
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
