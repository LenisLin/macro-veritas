# Update Snapshot Policy

## Purpose

This document is the source of truth for pre-update snapshot preservation in
the current MacroVeritas registry runtime.

This milestone is narrow:

- it adds snapshot-on-update safety only
- it applies only to the public full-replace update paths that already exist
- it now runs snapshot creation inside the single-card update lock window
- it does not add restore, history browsing, or diff behavior

## Covered Operations

Pre-update snapshots are taken only for:

- `update study --study-id <ID> --from-file <path.yaml>`
- `update dataset --dataset-id <ID> --from-file <path.yaml>`
- `update claim --claim-id <ID> --from-file <path.yaml>`

The create, ingest, show, list, and delete paths are unchanged by this
milestone.

## Lock Window

Pre-update snapshot creation now happens inside the same exclusive target-card
lock window used by update execution.

- the update lock is acquired before snapshot creation begins
- snapshot creation completes before the canonical overwrite starts
- the lock is released only after overwrite success or failure

## Snapshot Directory Layout

Snapshots live beneath the resolved registry root in an internal history tree:

- `<registry_root>/history/studies/<study_id>/<timestamp>.yaml`
- `<registry_root>/history/datasets/<dataset_id>/<timestamp>.yaml`
- `<registry_root>/history/claims/<claim_id>/<timestamp>.yaml`

Rules:

- the live canonical card paths remain `studies/`, `datasets/`, and `claims/`
- the history tree is internal-only and is not used by public `show` or `list`
- one update attempt may create at most one snapshot for the targeted card

## Snapshot Naming Rule

Each snapshot filename uses a UTC timestamp in this form:

`YYYYMMDDTHHMMSSffffffZ.yaml`

Rules:

- names are filesystem-safe ASCII
- names are append-only
- if a generated name already exists, the runtime retries with a fresh UTC
  timestamp rather than overwriting an existing snapshot

## Append-Only Rule

Snapshot preservation is append-only.

- existing snapshot files are never modified in place
- update execution writes a new snapshot file while the target-card lock is
  held and before replacing the live canonical card file
- this milestone does not add history cleanup or retention policy behavior

## Failure Rule

If snapshot creation fails, the update fails.

- the runtime must not continue to overwrite the live canonical card file after
  snapshot failure
- snapshot failure is surfaced through the existing registry failure path
- no raw stack trace is intended as the public failure surface

## Non-Goals

This milestone does not add:

- restore or rollback commands
- diff or history browsing commands
- snapshot deletion commands
- history CLI exposure
- patch, partial, or flag-based update semantics
