# Changelog

## Unreleased
- chore(init): convert AVCP template into MacroVeritas scaffold
- docs(mvp): establish the MVP documentation freeze across governance, architecture, registry/state/audit, and CLI contract docs; project remains docs-first with no scientific system implemented and CellVoyager reference-only

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
