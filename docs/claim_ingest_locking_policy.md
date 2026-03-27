# ClaimCard Ingest Locking Policy

## Purpose

This document is the source of truth for the current ClaimCard ingest-locking
milestone in the MacroVeritas registry runtime.

This milestone is intentionally narrow:

- it adds reference-aware locking for ClaimCard ingest only
- it reduces the immediate create-path race around StudyCard and DatasetCard
  reference validation plus duplicate-target collision for ClaimCard ingest
- it adds only local filesystem locking
- it preserves the existing public CLI and gateway signatures

## Covered Operations

Reference-aware locking applies only to:

- `ingest claim`
- `ingest claim --from-file <path.yaml>`

No other ingest path is changed by this milestone.

## Locks Acquired For ClaimCard Ingest

Each ClaimCard ingest acquires these existing local advisory locks:

- parent StudyCard lock:
  `<registry_root>/.locks/studies/<study_id>.lock`
- zero or more referenced DatasetCard locks:
  `<registry_root>/.locks/datasets/<dataset_id>.lock`
- target ClaimCard lock:
  `<registry_root>/.locks/claims/<claim_id>.lock`

Rules:

- locking reuses the same local advisory file-lock mechanism already used for
  DatasetCard ingest, update, and delete
- locking reuses the same deterministic `.locks/` directory layout and
  `<card_id>.lock` naming rule already used for update, delete, and
  DatasetCard ingest
- repeated dataset IDs do not produce repeated lock acquisition; the lock set
  is deduplicated by canonical lock path
- lock state is defined by the held advisory file lock, not by file presence
  alone

## Lock Order Rule

ClaimCard ingest computes the full lock set first, then acquires locks in one
deterministic order only:

1. derive the parent StudyCard lock path
2. derive each referenced DatasetCard lock path when `dataset_ids` is present
3. derive the target ClaimCard lock path
4. deduplicate the lock set by full lock path string
5. sort the full lock paths lexicographically
6. acquire locks in that sorted order

No caller-specific or payload-order lock ordering is allowed in this
milestone.

## Lock Lifetime

All ClaimCard ingest locks are held across the ClaimCard mutation-critical
section:

1. compute the full lock set
2. acquire all ClaimCard ingest locks in sorted order
3. validate the parent StudyCard reference under lock
4. validate referenced DatasetCard IDs under lock when present
5. check duplicate target state under lock
6. create the canonical ClaimCard YAML file
7. release all locks after success or failure

The lock window starts before reference validation and ends only after the
create path completes or fails.

## Failure Rule

If any ClaimCard ingest lock cannot be acquired, ClaimCard ingest fails
immediately and clearly.

- there is no silent retry loop
- there is no timeout/backoff workflow in this milestone
- parent-reference failure after lock acquisition still releases all locks
  during unwind
- dataset-reference failure after lock acquisition still releases all locks
  during unwind
- duplicate-target failure after lock acquisition still releases all locks
  during unwind
- create/write failure after lock acquisition still releases all locks during
  unwind

## Non-Goals

This milestone does not add:

- generalized ingest locking
- StudyCard ingest locking
- distributed locking
- multi-card transaction locking
- optimistic version counters
