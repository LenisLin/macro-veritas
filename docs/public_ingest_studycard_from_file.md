# Public StudyCard From-File Ingest

## Purpose

This document is the source of truth for file-based `StudyCard` ingest.

- It defines the public `ingest study --from-file` path.
- It fixes the narrow bridge: file path -> YAML mapping load -> normalized StudyCard ingest input -> `StudyCardPayload` -> gateway create -> canonical YAML write.
- It keeps the scope narrow: single-file, create-only, YAML-mapping StudyCard ingest.

## Exact CLI Shape

The public command is:

```bash
macro-veritas ingest study --from-file <path.yaml>
```

The same path is also reachable as:

```bash
python -m macro_veritas ingest study --from-file <path.yaml>
```

## Input File Format

- Format: YAML only
- File shape: one mapping at the document root
- File count: one file only
- Input keys use the existing StudyCard ingest-input names, not the stored canonical YAML names
- In particular, the input file uses `created_from`; the stored canonical StudyCard still writes `created_from_note`
- This is distinct from `update study --study-id <ID> --from-file <path.yaml>`,
  which expects the canonical stored StudyCard field names

Example:

```yaml
study_id: study-001
citation_handle: doi:study-001
tumor_type:
  - glioma
therapy_scope:
  - immunotherapy
relevance_scope:
  - preclinical
screening_decision: include
status: draft
created_from: seeded in study file ingest
screening_note: passed CLI review
source_artifact: raw/studies/study-001.pdf
```

## Required YAML Keys

- `study_id`
- `citation_handle`
- `tumor_type`
  - Must be a YAML sequence of strings.
- `therapy_scope`
  - Must be a YAML sequence of strings.
- `relevance_scope`
  - Must be a YAML sequence of strings.
- `screening_decision`
- `status`
- `created_from`

## Optional YAML Keys

- `screening_note`
- `source_artifact`

If an optional key is provided, it must be a string.

## Mixed-Input Blocking Rule

- `--from-file` cannot be combined with StudyCard field flags.
- This includes required field flags such as `--study-id` and optional field flags such as `--screening-note`.
- Mixed usage fails at the command layer before gateway work.
- Mixed usage is surfaced as an `invalid_payload` CLI failure.
- There is no precedence rule in this milestone.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line, for example `ingest study: created StudyCard study-001`
- Side effect: the existing StudyCard create path writes one canonical YAML file beneath the configured registry root

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
  - duplicate StudyCard create
  - generic registry gateway failure

## Non-Goals

- batch ingest
- directory scans or config-driven file discovery
- update, replace, or patch semantics
- canonical stored-field StudyCard update input; that belongs to
  `update study --study-id <ID> --from-file <path.yaml>`
- JSON input mode as a public contract
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI, SQL, notebook workflow, plugin discovery, or orchestration runtime
