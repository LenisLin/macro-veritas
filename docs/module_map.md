# Module Map

## Purpose

This document bridges the governance freeze to the current package layout.

- [`docs/governance_spec.md`](governance_spec.md) is the function-level source of truth.
- [`docs/card_contracts.md`](card_contracts.md) is the field-level source of truth for the first frozen card slice.
- [`docs/payload_contracts.md`](payload_contracts.md) is the source of truth for the frozen command-to-gateway payload and DTO layer for the first slice.
- [`docs/registry_layout.md`](registry_layout.md) is the filesystem source of truth for first-slice registry placement and naming.
- [`docs/registry_io_boundary.md`](registry_io_boundary.md) is the source of truth for registry access and mutation boundaries.
- [`docs/gateway_contracts.md`](gateway_contracts.md) is the source of truth for gateway result, error, and mutation-plan communication contracts.
- [`docs/studycard_runtime.md`](studycard_runtime.md), [`docs/datasetcard_runtime.md`](datasetcard_runtime.md), and [`docs/claimcard_runtime.md`](claimcard_runtime.md) describe the implemented registry runtime slices.
- [`docs/cli_command_contracts.md`](cli_command_contracts.md) is the source of truth for reserved internal command-family contracts.
- [`docs/public_ingest_studycard_cli.md`](public_ingest_studycard_cli.md), [`docs/public_ingest_studycard_from_file.md`](public_ingest_studycard_from_file.md), [`docs/public_ingest_datasetcard_cli.md`](public_ingest_datasetcard_cli.md), [`docs/public_ingest_datasetcard_from_file.md`](public_ingest_datasetcard_from_file.md), [`docs/public_ingest_claimcard_cli.md`](public_ingest_claimcard_cli.md), [`docs/public_ingest_claimcard_from_file.md`](public_ingest_claimcard_from_file.md), [`docs/public_show_cli.md`](public_show_cli.md), [`docs/public_list_cli.md`](public_list_cli.md), and [`docs/public_delete_cli.md`](public_delete_cli.md) define the current public domain command surfaces.

## Stable Base To Preserve

The current freeze preserves the existing lightweight runtime base:

| Current Path | Current Role | Preserve Rule |
| --- | --- | --- |
| `src/macro_veritas/config.py` | Resolved project configuration and layout-path helper | Keep as the current runtime configuration base. |
| `src/macro_veritas/cli.py` | Lightweight `argparse` CLI scaffold plus the public `ingest study`, `ingest study --from-file`, `ingest dataset`, `ingest dataset --from-file`, `ingest claim`, `ingest claim --from-file`, `show study`, `show dataset`, `show claim`, `list studies`, `list datasets`, `list claims`, `delete study`, `delete dataset`, and `delete claim` adapters | Keep existing public commands intact while exposing only the narrow StudyCard, DatasetCard, and ClaimCard ingest/create, single-file YAML ingest, show-by-id, family-level discovery, and referentially-aware by-id delete paths. |
| `src/macro_veritas/__main__.py` | Module execution entrypoint | Preserve `python -m macro_veritas` support. |
| repo-root `macro_veritas/` bootstrap package | Checkout-time bootstrap namespace | Preserve unless the invocation model intentionally changes later. |
| current `status` / `show-config` / `init-layout` CLI scaffold | Honest implemented interface | Treat as stable implemented fact while governance descriptors grow around it. |

## Governance-To-Code Mapping

This mapping is the conservative module-level freeze for the current round.

| Governance Label | Code Path | Current Representation | Current Module Responsibility | Explicitly Deferred |
| --- | --- | --- | --- | --- |
| 核心决策层 / A-header | `macro_veritas.governance.a_header` | single module with static lane and function descriptors | Freeze mandate, contract, and oversight descriptor functions for future non-trivial work units. | Orchestration engine, dispatch, workflow execution, enforcement. |
| 吏部 / Personnel Department | `macro_veritas.governance.departments.personnel` | single department module with office-level descriptors | Freeze role vocabulary, assignment headers, and escalation coverage descriptors. | Authentication, permissions, staffing workflow, identity management. |
| 户部 / Registry Department | `macro_veritas.governance.departments.registry` | single department module with office-level descriptors | Freeze intake, locator-binding, and extraction-planning descriptors for registry-facing objects. | Registry IO, identifier allocation, validation, persistence workflow. |
| 礼部 / Standards Department | `macro_veritas.governance.departments.standards` | single department module with office-level descriptors | Freeze naming, contract-boundary, and exception-handling descriptors. | Automatic linting, rule enforcement, policy service. |
| 兵部 / Operations Department | `macro_veritas.governance.departments.operations` | single department module with office-level descriptors | Freeze method, reanalysis-planning, and artifact-manifest descriptors. | Scientific execution, orchestration runtime, notebook loop, CellVoyager integration. |
| 工部 / Infrastructure Department | `macro_veritas.governance.departments.infrastructure` | single department module with office-level descriptors | Freeze layout, config-boundary, and runtime-surface descriptors. | Deployment system, environment manager, storage backend, runtime automation. |
| 刑部 / Review Department | `macro_veritas.governance.departments.review` | single department module with office-level descriptors | Freeze routine audit intake, audit-record, and escalation-gate descriptors. | Audit engine, evidence grading engine, automated adjudication. |
| 检察院 / Prosecution | `macro_veritas.prosecution.specs` | single specs module with lane-level descriptors | Freeze escalated case intake, case-brief, and disposition descriptors. | Automated escalation, sanctions, case-management engine, enforcement. |

## Registry Layout And Access Boundary Modules

The filesystem layout freeze is documentation-led first and mirrored only by
helper modules.

| Code Path | Current Role | Explicit Boundary |
| --- | --- | --- |
| `src/macro_veritas/shared/types.py` | Lightweight descriptor aliases plus first-slice payload/DTO TypedDicts, including the public StudyCard/DatasetCard/ClaimCard ingest CLI adapters, the single-file StudyCard/DatasetCard/ClaimCard ingest file-input aliases, the public by-id show input boundary, the public family-level list input/summary boundary, and the public by-id delete input boundary | No validation engine, no runtime model classes, no general serializer framework |
| `src/macro_veritas/shared/naming.py` | Canonical first-slice subdirectory and filename helpers | No identifier validation, no filesystem access, no serialization |
| `src/macro_veritas/registry/layout.py` | Canonical first-slice relative paths plus StudyCard, DatasetCard, and ClaimCard directory/path helpers | Path/layout helper layer only; not a caller-facing IO API |
| `src/macro_veritas/registry/gateway.py` | Gateway contract descriptors plus the real StudyCard, DatasetCard, and ClaimCard runtime boundary | Real StudyCard, DatasetCard, and ClaimCard reads/listings/planning/create/update/delete with gateway-owned direct-reference and reverse-dependency checks |
| `src/macro_veritas/registry/study_runtime.py` | Internal StudyCard-only runtime helper layer beneath the gateway | YAML serialization, minimal validation, canonical path checks, and single-card atomic writes only |
| `src/macro_veritas/registry/dataset_runtime.py` | Internal DatasetCard-only runtime helper layer beneath the gateway | YAML serialization, minimal validation, canonical path checks, and single-card atomic writes only; direct StudyCard existence checks stay in the gateway |
| `src/macro_veritas/registry/claim_runtime.py` | Internal ClaimCard-only runtime helper layer beneath the gateway | YAML serialization, minimal validation, canonical path checks, and single-card atomic writes only; direct StudyCard and DatasetCard existence checks stay in the gateway |
| `src/macro_veritas/registry/errors.py` | Domain-level registry error taxonomy used by gateway contracts | No recovery engine, no exception routing framework |

## Internal Command Modules

The command layer stays conservative and thin.

| Code Path | Current Role | Explicit Boundary |
| --- | --- | --- |
| `src/macro_veritas/commands/common.py` | Shared command-contract style descriptors, runtime-boundary descriptors, narrow command-result helpers, and lightweight command metadata helpers | No standalone dispatch engine, no bypass around the registry gateway, no broad public command framework |
| `src/macro_veritas/commands/ingest.py` | `ingest` family module with the real StudyCard, DatasetCard, and ClaimCard execution bridges beneath the public CLI adapters, including the single-file YAML bridges used by `ingest study --from-file`, `ingest dataset --from-file`, and `ingest claim --from-file` | Real StudyCard/DatasetCard/ClaimCard normalization, single-file YAML mapping load + file-input normalization for all three core cards, payload preparation, plan/create gateway calls, and command result translation; update/patch ingest semantics remain deferred |
| `src/macro_veritas/commands/show.py` | `show` family module with the real StudyCard, DatasetCard, and ClaimCard by-id execution bridges beneath the public CLI adapters | Real by-id input normalization, direct `get_*_card` gateway calls, raw card return on success, and command-level failure translation; list/search/update/delete remain deferred |
| `src/macro_veritas/commands/listing.py` | `list` family module with the real StudyCard, DatasetCard, and ClaimCard family-level discovery bridges beneath the public CLI adapters | Real family-level input normalization, direct `list_*_cards` gateway calls, compact summary shaping, and command-level failure translation; search/filter/pagination/update/delete remain deferred |
| `src/macro_veritas/commands/delete.py` | `delete` family module with the real StudyCard, DatasetCard, and ClaimCard by-id execution bridges beneath the public CLI adapters | Real by-id input normalization, direct `delete_*_card` gateway calls, dependency-blocking failure translation, and conservative success/failure reporting; force/cascade/filter/update remain deferred |
| `src/macro_veritas/commands/bind.py` | Internal skeleton for the reserved `bind` family | Parser-builder + handler contract only; no filesystem checks, no public exposure |
| `src/macro_veritas/commands/extract.py` | Internal skeleton for the reserved `extract` family | Parser-builder + handler contract only; no parsing engine, no public exposure |
| `src/macro_veritas/commands/audit.py` | Internal skeleton for the reserved `audit` family | Parser-builder + handler contract only; no audit engine, no public exposure |
| `src/macro_veritas/commands/review.py` | Internal skeleton for the reserved `review` family | Parser-builder + handler contract only; no prosecution workflow, no public exposure |
| `src/macro_veritas/commands/run.py` | Internal skeleton for the reserved `run` family | Parser-builder + handler contract only; no scientific execution, no public exposure |
| `src/macro_veritas/commands/grade.py` | Internal skeleton for the reserved `grade` family | Parser-builder + handler contract only; no evidence grading logic, no public exposure |

## Boundary Rules For This Round

- Governance labels stay human-facing in docs.
- Code names stay ASCII and English.
- `macro_veritas.registry.gateway` remains the sole internal boundary for
  registry card retrieval and persistence.
- `macro_veritas.commands` remains the command-family layer between the public
  CLI surface and gateway/governance operations.
- `macro_veritas.shared.types` remains the code home of the minimal first-slice
  payload, DTO, and CLI-adapter TypedDicts.
- Higher command layers must normalize raw parser input before preparing gateway payloads.
- The only public domain commands in this round are `ingest study`,
  `ingest study --from-file`, `ingest dataset`, `ingest dataset --from-file`,
  `ingest claim`, `ingest claim --from-file`,
  `show study`, `show dataset`, `show claim`, `list studies`,
  `list datasets`, `list claims`, `delete study`, `delete dataset`,
  and `delete claim`.
- ClaimCard public update/patch ingest remains out of scope.
- File input remains single-file YAML only at `ingest study --from-file`, `ingest dataset --from-file`, and `ingest claim --from-file`.
- This round must not add FastAPI, SQL, notebook-centric workflow, evidence
  grading logic, or CellVoyager integration.
