# Changelog

## Unreleased
- chore(init): convert AVCP template into MacroVeritas scaffold
- docs(mvp): establish the MVP documentation freeze across governance, architecture, registry/state/audit, and CLI contract docs; project remains docs-first with no scientific system implemented and CellVoyager reference-only

## v0.16.0 - 2026-03-27
- release: single-card exclusive locking now exists for StudyCard, DatasetCard, and ClaimCard full-replace update at `update study --study-id <ID> --from-file <path.yaml>`, `update dataset --dataset-id <ID> --from-file <path.yaml>`, and `update claim --claim-id <ID> --from-file <path.yaml>` and for `delete study --study-id <ID>`, `delete dataset --dataset-id <ID>`, and `delete claim --claim-id <ID>`; update lock spans snapshot plus overwrite; delete lock spans dependency-check plus delete; create/ingest locking remains absent; no patch semantics; release version chosen: v0.16.0

## v0.15.0 - 2026-03-27
- release: single-card exclusive locking now exists for StudyCard, DatasetCard, and ClaimCard full-replace update at `update study --study-id <ID> --from-file <path.yaml>`, `update dataset --dataset-id <ID> --from-file <path.yaml>`, and `update claim --claim-id <ID> --from-file <path.yaml>`; the lock is held across snapshot plus overwrite; pre-update snapshots remain in place; no create/delete/show/list locking; no patch semantics; release version chosen: v0.15.0

## v0.14.0 - 2026-03-26
- release: public full-replace update now exposed for StudyCard, DatasetCard, and ClaimCard at `update study --study-id <ID> --from-file <path.yaml>`, `update dataset --dataset-id <ID> --from-file <path.yaml>`, and `update claim --claim-id <ID> --from-file <path.yaml>`; update remains full-replace only with no patch semantics; pre-update snapshot preservation now exists for StudyCard, DatasetCard, and ClaimCard updates; release version chosen: v0.14.0

## v0.13.0 - 2026-03-25
- release: public DatasetCard update CLI exposed at `update dataset --dataset-id <ID> --from-file <path.yaml>`; DatasetCard-only, full-replace only, parent `StudyCard` is re-checked at update time, no `StudyCard` / `ClaimCard` update, no patch semantics; release version chosen: v0.13.0

## v0.12.0 - 2026-03-23
- release: file-based ingest parity exposed for StudyCard, DatasetCard, and ClaimCard; public CLI now supports `ingest study --from-file <path.yaml>`, `ingest dataset --from-file <path.yaml>`, and `ingest claim --from-file <path.yaml>`; flag-based ingest remains available; no batch ingest; no update/patch semantics; release version chosen: v0.12.0

## v0.11.0 - 2026-03-23
- release: public file-based ClaimCard ingest exposed; public CLI now supports `ingest claim --from-file <path.yaml>`; StudyCard and DatasetCard file-based ingest remain absent; no batch ingest; no update/patch semantics; release version chosen: v0.11.0

## v0.10.0 - 2026-03-23
- release: public referentially-aware delete CLI exposed for StudyCard, DatasetCard, and ClaimCard; dependency-blocking rules now enforce safe public removals; public ingest/show/list already exist; no public force/cascade/search/filter/update; release version chosen: v0.10.0

## v0.9.0 - 2026-03-22
- release: public list discovery CLI exposed for StudyCard, DatasetCard, and ClaimCard through flat family listing; public ingest triangle and show-by-id already exist; no public search/filter/update/delete; release version chosen: v0.9.0

## v0.8.0 - 2026-03-22
- release: public show-by-id CLI exposed for StudyCard, DatasetCard, and ClaimCard; public ingest triangle already available; public read capability is by id only; no public list/search/update/delete; release version chosen: v0.8.0

## v0.7.0 - 2026-03-21
- release: public DatasetCard ingest command exposed; CLI-to-runtime path is now real for DatasetCard create-only ingest; gateway-level StudyCard existence enforcement is surfaced through the public CLI; ClaimCard ingest remains non-public; release version chosen: v0.7.0

## v0.6.0 - 2026-03-20
- release: public StudyCard ingest command exposed; CLI-to-bridge path is now real for StudyCard create-only ingest; DatasetCard and ClaimCard ingest remain non-public; release version chosen: v0.6.0

## v0.5.0 - 2026-03-20
- release: internal StudyCard ingest bridge implemented; StudyCard command-layer payload normalization and result/error translation added; public CLI unchanged; DatasetCard and ClaimCard ingest remain skeleton-only; release version chosen: v0.5.0

## v0.4.0 - 2026-03-20
- release: ClaimCard runtime implemented; gateway enforces StudyCard existence for ClaimCard create/update and DatasetCard existence when `dataset_ids` are provided; public CLI unchanged; release version chosen: v0.4.0

## v0.3.0 - 2026-03-19
- release: DatasetCard runtime implemented with real YAML-backed persistence; gateway enforces StudyCard existence for DatasetCard create/update; ClaimCard remains contract-only; public CLI unchanged; release version chosen: v0.3.0

## v0.2.0 - 2026-03-19
- release: StudyCard runtime gateway implemented with YAML-backed StudyCard persistence and atomic single-card writes; DatasetCard and ClaimCard remain contract-only; public CLI unchanged

## v0.1.0 - 2026-03-19
- release: internal CLI command-family contracts frozen and internal command skeleton modules added; public CLI unchanged; no runtime IO, scientific logic, or CellVoyager integration added
