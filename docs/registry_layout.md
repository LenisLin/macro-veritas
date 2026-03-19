# Registry Layout

## Purpose

This document freezes the on-disk registry conventions for the first core card
slice:

- `StudyCard`
- `DatasetCard`
- `ClaimCard`

It is the filesystem source of truth for where those cards conceptually live on
disk and how their identifiers map to canonical registry paths.

This freeze is structural only.

- It does not imply implemented file IO.
- It does not imply implemented serialization or deserialization.
- It does not imply an implemented index, manifest, or validation engine.

For planned access and mutation responsibility, see
[`docs/registry_io_boundary.md`](registry_io_boundary.md). This document freezes
canonical placement and naming only.

The configured registry root is still resolved from project configuration. This
document freezes the relative layout beneath that resolved registry root.

## Chosen Topology

The v0.1 primary registry topology is `entity-segregated roots`.

Why this is the MVP choice:

- It keeps one predictable root per card family.
- It matches the current frozen design, where `DatasetCard` and `ClaimCard`
  point directly to stable IDs rather than inheriting behavior from a study
  directory tree.
- It avoids coupling card location to parent-study nesting, which would make
  path stability weaker if linkage changes later.

Canonical top-level tree for the first slice:

```text
<data_root>/
  <registry_root>/
    studies/
      <study_id>.yaml
    datasets/
      <dataset_id>.yaml
    claims/
      <claim_id>.yaml
```

Notes:

- `<registry_root>` is the configured registry directory, defaulting to
  `registry/`.
- The subdirectories beneath the resolved registry root are fixed for this
  slice: `studies/`, `datasets/`, and `claims/`.

## First-Slice Card Placement

Each first-slice card uses one canonical file and one canonical family root.

| Card Family | Canonical Root / Subdirectory | Canonical Filename | One Card = One File | Expected Format Label |
| --- | --- | --- | --- | --- |
| `StudyCard` | `<registry_root>/studies/` | `<study_id>.yaml` | yes | YAML placeholder |
| `DatasetCard` | `<registry_root>/datasets/` | `<dataset_id>.yaml` | yes | YAML placeholder |
| `ClaimCard` | `<registry_root>/claims/` | `<claim_id>.yaml` | yes | YAML placeholder |

This freeze does not implement YAML handling. The format label only records the
intended human-readable file type for later IO work.

## State-Location Mapping Rule

The v0.1 state-location strategy is `static file location + internal status
field update`.

Global rule for this slice:

- Status changes do not move card files between directories.
- `StudyCard`, `DatasetCard`, and `ClaimCard` stay in their canonical family
  subdirectory for their entire lifetime.
- Lifecycle state is expressed by the card's internal `status` field, not by
  relocating the file on disk.

Why this is the MVP choice:

- Stable paths make cross-references simpler.
- Status changes remain ordinary metadata updates rather than filesystem move
  operations.
- This is the more conservative option for a docs-first slice with no runtime
  transition engine yet.

## Cross-Reference Resolution Rule

Cross-references are resolved conceptually by direct ID-to-path lookup using the
canonical family root and filename convention. No index engine is introduced in
this slice.

- `DatasetCard -> StudyCard`:
  resolve `DatasetCard.study_id` to `studies/<study_id>.yaml`
- `ClaimCard -> StudyCard`:
  resolve `ClaimCard.study_id` to `studies/<study_id>.yaml`
- `ClaimCard -> DatasetCard(s)`:
  resolve each `dataset_id` in `ClaimCard.dataset_ids` to
  `datasets/<dataset_id>.yaml`

MVP interpretation rules:

- References are direct outbound pointers only.
- `StudyCard` does not store dataset or claim backlink lists.
- `DatasetCard` does not store claim backlink lists.
- No separate manifest, search index, or resolver cache is part of this freeze.

## Naming Rules

Minimal naming conventions for the first slice:

- Directory names are lowercase ASCII plurals:
  `studies`, `datasets`, `claims`.
- Card filenames are the embedded identifier plus the canonical `.yaml`
  extension:
  `<study_id>.yaml`, `<dataset_id>.yaml`, `<claim_id>.yaml`.
- Identifiers are embedded in the filename stem, not in an additional nested
  study-specific directory structure.
- This slice does not introduce an escaping, slugification, or identifier
  normalization engine. The convention assumes the stored IDs are already in a
  form that can serve as a filename stem.

Reserved patterns for this slice:

- Names beginning with `_` are reserved for future support files or local
  metadata if such files are added later.
- Hidden dot-prefixed names are not canonical card paths.
- Temporary suffixes such as `.tmp` or `.bak` are non-canonical and outside
  this freeze.

## Responsibility Boundary

- `docs/registry_io_boundary.md` is the source of truth for future registry
  access and mutation responsibility.
- `macro_veritas.registry.layout` is a path/layout helper layer only.
- Planned card retrieval and persistence belong to
  `macro_veritas.registry.gateway`, not to CLI code, governance code, or raw
  layout traversal.

## Non-Goals

This document does not add or imply:

- file IO
- serializer or deserializer code
- index or manifest engine
- symlink strategy
- state-transition runtime
- referential-integrity enforcement runtime
