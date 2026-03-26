# Public StudyCard Update CLI

## Purpose

This document is the source of truth for the StudyCard public update CLI
milestone.

- It defines the public `update study` surface.
- It fixes the narrow bridge: explicit target ID -> YAML file load -> full-card
  StudyCard replacement -> gateway plan/update -> canonical YAML replace.
- It keeps scope narrow: StudyCard only, file-only, full-replace only.

## Exact CLI Shape

The public command is:

```bash
macro-veritas update study --study-id <ID> --from-file <path.yaml>
```

The same path is also reachable as:

```bash
python -m macro_veritas update study --study-id <ID> --from-file <path.yaml>
```

## Full-Replace-Only Rule

- The YAML file must describe one complete replacement `StudyCard`.
- Patch, merge, or partial-update semantics do not exist in this milestone.
- The file uses the canonical stored `StudyCard` field names, not the
  create-ingest aliases used by `ingest study --from-file`.

## Required YAML Keys

- `study_id`
- `citation_handle`
- `tumor_scope_tags`
  - Must be a YAML sequence of strings.
- `therapy_scope_tags`
  - Must be a YAML sequence of strings.
- `relevance_scope_tags`
  - Must be a YAML sequence of strings.
- `screening_decision`
- `status`
- `created_from_note`

## Optional YAML Keys

- `screening_note`
- `source_artifact_locator`

If an optional key is provided, it must be a string.

## Target-Match Rule

- The CLI requires `--study-id <ID>`.
- The YAML file must contain `study_id`.
- The CLI target and file target must match exactly.
- A mismatch fails before gateway update execution and is surfaced as a clean
  `invalid_payload` CLI failure.

## Existing Status Rule

- The replacement file must still satisfy the existing StudyCard status model.
- In particular, a `closed` StudyCard cannot be updated back to an active
  status.
- A rejected state transition is surfaced as a clean `invalid_payload` CLI
  failure.

## Success Output Expectations

- Exit code: `0`
- Output channel: standard output
- Output style: one concise line, for example `update study: updated StudyCard study-001`

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
  - CLI `--study-id` / file `study_id` mismatch
  - invalid StudyCard state transition under the existing status rule
  - missing target `StudyCard`
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
