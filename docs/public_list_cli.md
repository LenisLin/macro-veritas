# Public List CLI

## Purpose

This milestone exposes the first public discovery CLI for the three core card
families.

The implemented path is:

- raw CLI args
- narrow typed family-level input
- gateway `list_*_cards` runtime call
- compact summary array returned as stable JSON

## Public Command Shapes

```text
macro-veritas list studies
macro-veritas list datasets
macro-veritas list claims
```

Equivalent module execution forms remain valid through `python -m macro_veritas`.

## Output Style

- Success: one JSON array to stdout, pretty-printed with stable key ordering.
- Failure: one concise human-readable line to stderr and a non-zero exit code.

## Summary Shapes

- `list studies`: `study_id`, `status`, `citation_handle`
- `list datasets`: `dataset_id`, `study_id`, `status`
- `list claims`: `claim_id`, `study_id`, `status`, `claim_type`

List output is for discovery only. It does not return full raw card payloads.

## Success Output Expectations

- The command reads exactly one card family through the registry gateway.
- The JSON array contains compact summary objects only.
- Ordering is normalized conservatively by canonical ID for stable discovery output.
- The command does not hydrate related `StudyCard`, `DatasetCard`, or `ClaimCard` records.

## Failure Output Expectations

- Registry failures become a clean command-level failure.
- Unsupported list operations become a clean command-level failure.
- Raw filesystem exceptions are not the intended user-facing surface.

## Non-Goals

- show expansion
- search, filter, or query behavior
- pagination
- relationship expansion or reverse lookups
- update or delete semantics
- scientific logic
- evidence grading
- CellVoyager integration
