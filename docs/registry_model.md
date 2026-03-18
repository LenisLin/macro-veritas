# Registry Model

## Scope

This document defines the minimum MVP object families for MacroVeritas. It is a high-level design document for a filesystem-oriented registry layer, not an implemented schema set.

## Object Families

| Object Family | Purpose | Produced By / Owner Role | Consumed By | Persistence Form | Current Status | Why It Exists |
| --- | --- | --- | --- | --- | --- | --- |
| `StudyCard` | Represent the canonical study or paper unit tracked by the project | Human curator or project lead | `DatasetCard`, `ClaimCard`, audit review | Planned YAML registry card | Documented only | Keeps the study identity stable so downstream work refers to one canonical record |
| `DatasetCard` | Represent a dataset associated with a study and its usable project binding | Human curator or analyst | `ClaimCard`, `ReanalysisBundle`, audit review | Planned YAML registry card with references to raw/processed filesystem locations | Documented only | Separates dataset provenance and location tracking from claim interpretation |
| `ClaimCard` | Represent one scoped claim that the project may later examine | Human curator or reviewer | `ReanalysisBundle`, `EvidenceCard`, audit review | Planned YAML registry card | Documented only | Keeps the project claim-centered and makes evaluation units explicit |
| `MethodCard` | Represent a declared reanalysis method or protocol choice | Analyst or method owner | `ReanalysisBundle`, audit review | Planned YAML registry card | Documented only | Prevents method assumptions from living only in scripts or informal notes |
| `ReanalysisBundle` | Represent one concrete bundle of run artifacts tied to defined inputs and a declared method | Analyst or run owner | `EvidenceCard`, `AuditRecord`, later reporting | Planned directory artifact under `runs/` with a small manifest document | Documented only | Preserves a reproducible boundary around one reanalysis attempt without requiring a database |
| `EvidenceCard` | Represent a reviewable evidence summary linked to claim, dataset, and bundle outputs | Analyst or reviewer | Audit review, later grading/report assembly | Planned YAML registry card with links to supporting artifacts | Documented only | Separates the summarized evidence statement from the underlying run files |
| `AuditRecord` | Represent an explicit review outcome on an object or bundle | Reviewer, auditor, or project lead | Governance review and future deeper audit lanes | Planned YAML registry card, optionally linked to notes under `reports/` | Documented only | Makes review decisions explicit and inspectable rather than implicit in conversation |

## Model Notes

- This model is intentionally card-and-bundle oriented rather than service-oriented.
- Card objects are planned as small human-reviewable registry documents.
- Bundle objects are planned as filesystem artifact directories with a lightweight manifest.
- Exact field schemas are intentionally deferred.
- No registry engine, object store, or validation framework is implemented yet.
