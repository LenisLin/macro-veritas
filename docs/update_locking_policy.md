# Update Locking Policy

## Purpose

This document is the source of truth for the current update-only locking
milestone in the MacroVeritas registry runtime.

This milestone is intentionally narrow:

- it reduces the immediate clobbering risk for snapshot-then-replace updates
- it adds only local filesystem locking
- it preserves the existing public CLI surface

## Covered Operations

Single-card exclusive locking applies only to:

- `update study --study-id <ID> --from-file <path.yaml>`
- `update dataset --dataset-id <ID> --from-file <path.yaml>`
- `update claim --claim-id <ID> --from-file <path.yaml>`

Create, ingest, delete, show, and list are unchanged by this milestone.

## Lock Scope

The lock scope is one target card only.

- one update operation acquires one exclusive lock
- the lock covers only the targeted `StudyCard`, `DatasetCard`, or `ClaimCard`
- there is no cross-card lock graph or transaction bundle

## Lock Lifetime

The lock is held across the update mutation-critical section:

1. acquire the target-card lock
2. preserve the pre-update snapshot
3. atomically overwrite the live canonical YAML
4. release the lock after success or failure

The lock window starts before snapshot creation and ends only after the
overwrite path completes or fails.

## Lock Path And Naming Rule

The lock file path is deterministic and card-specific:

- `<registry_root>/.locks/studies/<study_id>.lock`
- `<registry_root>/.locks/datasets/<dataset_id>.lock`
- `<registry_root>/.locks/claims/<claim_id>.lock`

Rules:

- locking uses one advisory exclusive file lock on that deterministic path
- the lock file may remain on disk after release and be reused by later updates
- lock state is defined by the held advisory file lock, not by file presence alone

## Failure Rule

If the lock cannot be acquired, the update fails immediately and clearly.

- there is no silent retry loop
- there is no timeout/backoff workflow in this milestone
- if snapshot creation fails, the update fails and the lock is released during unwind
- if canonical overwrite fails, the update fails and the lock is released during unwind

## Non-Goals

This milestone does not add:

- create, ingest, delete, show, or list locking
- distributed locking
- multi-card transaction locking
- optimistic version counters
- force-unlock UX
