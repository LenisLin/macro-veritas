# Public Show CLI

## Purpose

This milestone exposes the first public read-by-id CLI for the three core card
families.

The implemented path is:

- raw CLI args
- narrow typed by-id input
- gateway `get_*_card` runtime call
- raw hydrated card mapping returned as stable JSON

## Public Command Shapes

```text
macro-veritas show study --study-id <ID>
macro-veritas show dataset --dataset-id <ID>
macro-veritas show claim --claim-id <ID>
```

Equivalent module execution forms remain valid through `python -m macro_veritas`.

## Required Arguments

- `show study` requires `--study-id`.
- `show dataset` requires `--dataset-id`.
- `show claim` requires `--claim-id`.

## Output Style

- Success: one JSON object to stdout, pretty-printed with stable key ordering.
- Failure: one concise human-readable line to stderr and a non-zero exit code.

## Success Output Expectations

- The command reads exactly one card by canonical ID.
- The JSON object is the raw hydrated card mapping returned by the gateway.
- The command does not expand related `StudyCard`, `DatasetCard`, or `ClaimCard`
  records.

## Failure Output Expectations

- Missing target card becomes a clean command-level failure.
- Unsafe or unsupported identifiers become a clean command-level failure.
- Registry read failures become a clean command-level failure.
- Raw filesystem exceptions are not the intended user-facing surface.

## Non-Goals

- list, search, or filter commands
- relationship expansion or reverse lookups
- update or delete semantics
- scientific logic
- evidence grading
- CellVoyager integration
