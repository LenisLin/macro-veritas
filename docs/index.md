# Documentation Index

## Purpose

This index is the navigation layer for the current MacroVeritas MVP documentation set. It is intended to help a new contributor or a new model session find the frozen position first, then the design-intent documents that describe the next implementation boundary.

## Start Here

Recommended first-pass reading order:

1. [`README.md`](../README.md) for repository identity, scope, and current freeze boundary.
2. [`docs/project_charter.md`](project_charter.md) for mission, domain scope, and project-level direction.
3. [`docs/state.md`](state.md) for the current snapshot of what exists now versus what is only documented.
4. [`docs/constraints.md`](constraints.md) for the locked boundaries that must not be crossed in this phase.
5. [`docs/decisions.md`](decisions.md) for the concrete architectural and governance decisions already made.
6. [`docs/architecture.md`](architecture.md) for the high-level repository shape, governance layer direction, and current component boundaries.
7. [`docs/governance_spec.md`](governance_spec.md) for the frozen A-header, department-office, and prosecution function descriptors.
8. [`docs/module_map.md`](module_map.md) for the conservative governance-to-code mapping used by the current package skeleton.
9. [`docs/registry_model.md`](registry_model.md) for planned object families and persistence forms.
10. [`docs/state_machine.md`](state_machine.md) for minimum lifecycle states.
11. [`docs/card_contracts.md`](card_contracts.md) for the field-level frozen contract of the first `StudyCard` / `DatasetCard` / `ClaimCard` slice.
12. [`docs/payload_contracts.md`](payload_contracts.md) for the frozen command-to-gateway payload and DTO shapes of the first card slice.
13. [`docs/registry_layout.md`](registry_layout.md) for the frozen filesystem placement, naming, and cross-reference conventions of that first card slice.
14. [`docs/registry_io_boundary.md`](registry_io_boundary.md) for the frozen future internal access boundary, integrity rule, mutation-safety rule, and registry error surface.
15. [`docs/gateway_contracts.md`](gateway_contracts.md) for the frozen gateway result, error, and mutation-plan communication contract.
16. [`docs/studycard_runtime.md`](studycard_runtime.md) for the real file-backed StudyCard runtime slice.
17. [`docs/datasetcard_runtime.md`](datasetcard_runtime.md) for the real file-backed DatasetCard runtime slice.
18. [`docs/claimcard_runtime.md`](claimcard_runtime.md) for the real file-backed ClaimCard runtime slice.
19. [`docs/ingest_studycard_runtime.md`](ingest_studycard_runtime.md) for the first real internal StudyCard command execution bridge.
20. [`docs/data_contracts.md`](data_contracts.md) for the high-level contract categories and the remaining non-frozen object families.
21. [`docs/api_specs.md`](api_specs.md) for the current CLI contract and the boundary between implemented public commands and reserved internal command families.
22. [`docs/cli_command_contracts.md`](cli_command_contracts.md) for the frozen internal command-family contracts and skeleton-module responsibilities.
23. [`docs/audit_policy.md`](audit_policy.md) for routine review policy and the distinction from future escalated review.

## Status Labels

- Defines current frozen position: treat as the current source of truth for the MVP freeze.
- Design intent / future-detail: useful for navigation and planned direction, but not an implementation claim.

## Governance

These documents define the current frozen position.

- [`README.md`](../README.md): top-level project entry point with scope, freeze boundaries, repository layout, and current CLI summary.
- [`docs/project_charter.md`](project_charter.md): states the project mission, literature focus, and high-level architectural direction.
- [`docs/state.md`](state.md): records the current project phase, what is implemented now, and what remains deferred.
- [`docs/constraints.md`](constraints.md): lists the locked constraints for the current milestone, including no FastAPI, no SQL, and no scientific implementation.
- [`docs/decisions.md`](decisions.md): captures the explicit decisions that fix identity, runtime surface, persistence direction, and other MVP boundaries.

## System Structure

These documents mix frozen-position context with design-intent detail.

- [`docs/architecture.md`](architecture.md): explains the current repository shape, component boundaries, and filesystem-oriented direction. Defines current frozen position.
- [`docs/governance_spec.md`](governance_spec.md): freezes A-header lanes, department offices, planned governance function names, and prosecution boundaries. Design intent / future-detail, but now the function-level source of truth.
- [`docs/module_map.md`](module_map.md): bridges governance labels to conservative package and module paths for the current skeletonization round. Design intent / future-detail.
- [`docs/registry_model.md`](registry_model.md): maps the MVP object families and their planned persistence forms. Design intent / future-detail.
- [`docs/state_machine.md`](state_machine.md): defines minimal object lifecycle states for the MVP registry layer. Design intent / future-detail.
- [`docs/registry_layout.md`](registry_layout.md): freezes the first-slice on-disk registry topology, naming, and cross-reference conventions without implying IO. Defines current frozen position for this slice.
- [`docs/payload_contracts.md`](payload_contracts.md): freezes the first-slice command-normalized-to-gateway payload and DTO boundary without implying parser or runtime implementation. Defines current frozen position for this slice.
- [`docs/registry_io_boundary.md`](registry_io_boundary.md): freezes the internal registry access boundary, integrity-enforcement point, mutation-safety rule, and error surface while distinguishing the implemented StudyCard, DatasetCard, and ClaimCard slices from deferred future work. Defines current frozen position for this slice.
- [`docs/gateway_contracts.md`](gateway_contracts.md): freezes the gateway-facing result shapes, error semantics, mutation-plan output contract, and full-replace update rule while documenting the current mixed implementation state. Defines current frozen position for this slice.
- [`docs/studycard_runtime.md`](studycard_runtime.md): defines the implemented StudyCard runtime slice, including canonical path usage, YAML storage, atomic writes, and error translation. Defines current implemented position for this slice.
- [`docs/datasetcard_runtime.md`](datasetcard_runtime.md): defines the implemented DatasetCard runtime slice, including canonical path usage, YAML storage, gateway-level StudyCard reference checks, atomic writes, and error translation. Defines current implemented position for this slice.
- [`docs/claimcard_runtime.md`](claimcard_runtime.md): defines the implemented ClaimCard runtime slice, including canonical path usage, YAML storage, gateway-level StudyCard and optional DatasetCard reference checks, atomic writes, and error translation. Defines current implemented position for this slice.
- [`docs/cli_command_contracts.md`](cli_command_contracts.md): freezes the reserved internal command-family contracts, family ownership, dependency boundaries, and skeleton style without making those commands public. Defines current frozen position for this slice.
- [`docs/ingest_studycard_runtime.md`](ingest_studycard_runtime.md): defines the first real internal command execution bridge for StudyCard ingest while keeping the public CLI unchanged. Defines current implemented position for this slice.

## Contracts And Audit

These documents describe the public CLI surface and the next layer of object and review contracts.

- [`docs/card_contracts.md`](card_contracts.md): freezes the first field-level card contracts for `StudyCard`, `DatasetCard`, and `ClaimCard`. Defines current frozen position for this slice.
- [`docs/payload_contracts.md`](payload_contracts.md): freezes the exact first-slice payload/DTO shapes exchanged between internal command handlers and future gateway operations. Defines current frozen position for this slice.
- [`docs/registry_layout.md`](registry_layout.md): freezes where those first-slice cards conceptually live on disk and how their IDs map to canonical file paths. Defines current frozen position for this slice.
- [`docs/registry_io_boundary.md`](registry_io_boundary.md): freezes who will own future registry access, where direct-reference checks belong, and what mutation-safety/error rules will apply. Defines current frozen position for this slice.
- [`docs/gateway_contracts.md`](gateway_contracts.md): freezes the precise language upper layers should consume from the gateway: success shapes, domain errors, mutation-plan outputs, and the full-replace rule. Defines current frozen position for this slice.
- [`docs/studycard_runtime.md`](studycard_runtime.md): records exactly what StudyCard registry behavior is runtime-real now and what remains deferred. Defines current implemented position for this slice.
- [`docs/datasetcard_runtime.md`](datasetcard_runtime.md): records exactly what DatasetCard registry behavior is runtime-real now and what remains deferred. Defines current implemented position for this slice.
- [`docs/claimcard_runtime.md`](claimcard_runtime.md): records exactly what ClaimCard registry behavior is runtime-real now and what remains deferred. Defines current implemented position for this slice.
- [`docs/ingest_studycard_runtime.md`](ingest_studycard_runtime.md): records exactly what internal StudyCard ingest command behavior is runtime-real now and what remains deferred. Defines current implemented position for this slice.
- [`docs/api_specs.md`](api_specs.md): documents the current CLI contract and clearly states that there is no web API in v0.1. Defines current implemented CLI surface and the reserved-not-public command boundary.
- [`docs/cli_command_contracts.md`](cli_command_contracts.md): freezes the internal command-family contracts for `ingest`, `bind`, `extract`, `audit`, `review`, `run`, and `grade`. Defines current frozen position for this slice.
- [`docs/data_contracts.md`](data_contracts.md): summarizes the minimum contract categories for planned object families and points to the first frozen card slice. Design intent / future-detail.
- [`docs/audit_policy.md`](audit_policy.md): defines the lightweight MVP audit posture, trigger points, and outcomes without implying an implemented audit engine. Design intent / future-detail.

## Process And Template Docs

These documents support repository discipline rather than end-user functionality.

- [`docs/avcp_guidelines.md`](avcp_guidelines.md): lightweight repo-memory and documentation-discipline guidance for non-trivial work.
- [`docs/dev_log.md`](dev_log.md): internal development notes and continuity aid; useful for context, but not a source of frozen product truth.

## Practical Reading Rule

If a question is about what is allowed now, read `state`, `constraints`, and `decisions` first. If a question is about how the next MVP layer is supposed to be organized, then read `architecture`, `governance_spec`, `module_map`, `registry_model`, `state_machine`, `card_contracts`, `payload_contracts`, `registry_layout`, `registry_io_boundary`, `gateway_contracts`, `studycard_runtime`, `datasetcard_runtime`, `claimcard_runtime`, `ingest_studycard_runtime`, `data_contracts`, `api_specs`, `cli_command_contracts`, and `audit_policy`.
