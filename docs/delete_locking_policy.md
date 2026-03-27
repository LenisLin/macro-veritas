# Delete Locking Policy

## Purpose

This document is the source of truth for the current delete-locking milestone
in the MacroVeritas registry runtime.

This milestone is intentionally narrow:

- it reduces the immediate delete/update race on one target card
- it adds only local filesystem locking
- it preserves the existing public CLI surface

## Covered Operations

Single-card exclusive locking applies only to:

- `delete study --study-id <ID>`
- `delete dataset --dataset-id <ID>`
- `delete claim --claim-id <ID>`

## Lock Scope

The lock scope is one target card only.

- one delete operation acquires one exclusive lock
- the lock covers only the targeted `StudyCard`, `DatasetCard`, or `ClaimCard`
- there is no cross-card lock graph or transaction bundle

## Lock Lifetime

The lock is held across the delete critical section:

1. perform the normal fast target-existence check
2. acquire the target-card lock
3. re-check target existence under the lock
4. perform dependency checks under the lock when required
5. delete the canonical card file
6. release the lock after success or failure

The lock window starts before dependency-check or delete work begins and ends
only after the delete path completes or fails.

## Lock Path And Naming Rule

The lock file path is deterministic and card-specific:

- `<registry_root>/.locks/studies/<study_id>.lock`
- `<registry_root>/.locks/datasets/<dataset_id>.lock`
- `<registry_root>/.locks/claims/<claim_id>.lock`

Rules:

- locking uses one advisory exclusive file lock on that deterministic path
- the lock file may remain on disk after release and be reused by later mutations
- lock state is defined by the held advisory file lock, not by file presence alone

## Failure Rule

If the lock cannot be acquired, the delete fails immediately and clearly.

- there is no silent retry loop
- there is no timeout/backoff workflow in this milestone
- dependency-blocked deletes still fail with the existing dependency error
- delete failures after lock acquisition still release the lock during unwind

## Non-Goals

This milestone does not add:

- create or ingest locking
- show or list locking
- distributed locking
- multi-card transaction locking
- optimistic version counters
- force-unlock UX
