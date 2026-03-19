# Data Contracts

## Scope

This document defines the minimum contract categories for the planned MacroVeritas object families.

- `docs/card_contracts.md` is now the field-level source of truth for the first frozen card slice: `StudyCard`, `DatasetCard`, and `ClaimCard`.
- `docs/registry_layout.md` is now the persistence/location convention source of truth for the first frozen card slice.
- This document remains the higher-level contract summary for all object families.
- Validation rules, serialization details, and runtime enforcement remain deferred.

## Contract Categories

Each planned object family should eventually declare, at minimum:

- identity
- provenance
- status
- ownership / producer
- artifact location / persistence

## Planned Object Contract Summary

| Object Family | Identity | Provenance | Status | Ownership / Producer | Artifact Location / Persistence | Current Position |
| --- | --- | --- | --- | --- | --- | --- |
| `StudyCard` | Stable study identifier for the tracked paper or study unit | Source citation and intake origin | Study lifecycle state | Human curator or project lead | Canonical first-slice card at `<registry_root>/studies/<study_id>.yaml` | Field-frozen in the first core card slice. See `docs/card_contracts.md` and `docs/registry_layout.md`. |
| `DatasetCard` | Stable dataset identifier within the project registry | Study linkage, accession/source origin, and binding origin | Dataset lifecycle state | Human curator or analyst | Canonical first-slice card at `<registry_root>/datasets/<dataset_id>.yaml`, with later references to `raw/` or `processed/` paths | Field-frozen in the first core card slice. See `docs/card_contracts.md` and `docs/registry_layout.md`. |
| `ClaimCard` | Stable claim identifier scoped to a study | Claim capture source and supporting study linkage | Claim lifecycle state | Human curator or reviewer | Canonical first-slice card at `<registry_root>/claims/<claim_id>.yaml` | Field-frozen in the first core card slice. See `docs/card_contracts.md` and `docs/registry_layout.md`. |
| `MethodCard` | Stable method identifier and version label | Method origin, assumptions, and declared reanalysis context | Method status for active or superseded use | Analyst or method owner | Planned registry card under `registry/` | Documented design intent only |
| `ReanalysisBundle` | Stable bundle or run identifier | Input object references, method reference, and execution provenance | Bundle readiness or review state | Analyst or run owner | Planned directory artifact under `runs/` with a small manifest | Documented design intent only |
| `EvidenceCard` | Stable evidence identifier | Linked claim, dataset, and bundle/report provenance | Evidence review state | Analyst or reviewer | Planned registry card under `registry/` with links to supporting artifacts | Documented design intent only |
| `AuditRecord` | Stable audit identifier | Audited object references, reviewer identity, and audit context | Audit outcome state | Reviewer, auditor, or project lead | Planned registry card under `registry/` with optional notes/report links | Documented design intent only |

## Notes

- `registry/`, `runs/`, `reports/`, `raw/`, and `processed/` are current scaffold directories, not implemented business logic.
- The first field-level contract freeze covers only `StudyCard`, `DatasetCard`, and `ClaimCard`.
- The first filesystem placement and naming freeze for those cards lives in `docs/registry_layout.md`.
- `ReanalysisBundle` is the only planned object family whose primary persistence form is a directory artifact rather than a single card document.
- Lifecycle status meanings are intentionally kept high-level here and are described separately in `docs/state_machine.md`.

## Deferred

The following remain explicitly deferred to a later milestone:

- exact required fields for object families outside the first frozen card slice
- canonical file naming rules for object families outside the first frozen card slice
- validation rules
- runtime cross-object referential-integrity enforcement
- import/export formats beyond the current high-level persistence direction
