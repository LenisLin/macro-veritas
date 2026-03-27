# Public Delete CLI

## Purpose

This document is the source of truth for the first safe public delete surface.

This milestone adds conservative, by-id delete commands for `StudyCard`,
`DatasetCard`, and `ClaimCard` so users do not need to manually remove
registry files.

## Public Command Shapes

- `macro-veritas delete study --study-id <ID>`
- `macro-veritas delete dataset --dataset-id <ID>`
- `macro-veritas delete claim --claim-id <ID>`

These commands are by-id only.

Each command now acquires one exclusive target-card lock at the deterministic
`.locks/<family>/<id>.lock` path before dependency-check plus delete work
begins.

## Dependency-Blocking Rules

- `delete study --study-id <ID>` must fail when any `DatasetCard.study_id`
  equals `<ID>`.
- `delete study --study-id <ID>` must fail when any `ClaimCard.study_id`
  equals `<ID>`.
- `delete dataset --dataset-id <ID>` must fail when any
  `ClaimCard.dataset_ids` contains `<ID>`.
- `delete claim --claim-id <ID>` may delete directly when the target claim
  exists.

The gateway preserves the current fast target-existence check, then acquires
the target-card lock, re-checks target existence under that lock, and performs
dependency checks plus delete while that lock is held.

## Success Output

- Success writes one concise line to stdout.
- Success returns exit code `0`.
- Current success shape is `delete <family>: deleted <CardFamily> <ID>`.

## Failure Output

- Failure writes one concise line to stderr.
- Failure returns a non-zero exit code.
- Missing targets, dependency-blocked deletes, unsafe identifiers, and other
  registry failures all use this same failure style.
- Lock contention or lock-management failures surface as `registry_failure`
  with the precise lock message.
- Public delete commands do not emit stack traces as the intended user-facing
  surface.

## Non-Goals

- no force delete
- no cascade delete
- no bulk delete
- no delete by search or filter
- no restore or undo
- no trash or archive semantics
- no update or patch semantics
