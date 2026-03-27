# Ingest Locking Policy

## Purpose

This document is the source of truth for the current ingest-locking milestone
in the MacroVeritas registry runtime.

This milestone is intentionally narrow:

- it adds parent-aware locking for DatasetCard ingest only
- it reduces the immediate create-path race around parent validation and target
  collision for DatasetCard ingest
- it adds only local filesystem locking
- it preserves the existing public CLI and gateway signatures

## Covered Operations

Parent-aware locking applies only to:

- `ingest dataset`
- `ingest dataset --from-file <path.yaml>`

No other ingest path is changed by this milestone.

## Locks Acquired For DatasetCard Ingest

Each DatasetCard ingest acquires exactly two existing local advisory locks:

- parent StudyCard lock:
  `<registry_root>/.locks/studies/<study_id>.lock`
- target DatasetCard lock:
  `<registry_root>/.locks/datasets/<dataset_id>.lock`

Rules:

- locking reuses the same local advisory file-lock mechanism already used for
  update and delete
- locking reuses the same deterministic `.locks/` directory layout and
  `<card_id>.lock` naming rule already used for update and delete
- lock state is defined by the held advisory file lock, not by file presence
  alone

## Lock Order Rule

The lock order is fixed and must not vary by caller:

1. acquire the parent `StudyCard` lock
2. acquire the target `DatasetCard` lock

This fixed order is the only lock ordering used for DatasetCard ingest in this
milestone.

## Lock Lifetime

Both locks are held across the DatasetCard ingest mutation-critical section:

1. acquire the parent StudyCard lock
2. acquire the target DatasetCard lock
3. validate parent StudyCard existence under lock
4. check target DatasetCard duplicate/collision state under lock
5. create the canonical DatasetCard YAML file
6. release both locks after success or failure

The lock window starts before parent validation and ends only after the create
path completes or fails.

## Failure Rule

If either lock cannot be acquired, DatasetCard ingest fails immediately and
clearly.

- there is no silent retry loop
- there is no timeout/backoff workflow in this milestone
- parent validation failure after lock acquisition still releases both locks
  during unwind
- duplicate-target failure after lock acquisition still releases both locks
  during unwind
- create/write failure after lock acquisition still releases both locks during
  unwind

## Non-Goals

This milestone does not add:

- StudyCard ingest locking
- ClaimCard ingest locking
- distributed locking
- multi-card transaction locking
- optimistic version counters
