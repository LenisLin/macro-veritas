# Documentation Index

## Purpose

This index is the navigation layer for the current MacroVeritas MVP
documentation set. It is intended to help a new contributor or a new model
session find the frozen position first, then the design-intent documents that
still matter for the next implementation boundary.

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
15. [`docs/update_snapshot_policy.md`](update_snapshot_policy.md) for the internal pre-update snapshot safety rule.
16. [`docs/update_locking_policy.md`](update_locking_policy.md) for the single-card exclusive update-lock rule.
17. [`docs/delete_locking_policy.md`](delete_locking_policy.md) for the single-card exclusive delete-lock rule.
18. [`docs/ingest_locking_policy.md`](ingest_locking_policy.md) for the parent-aware DatasetCard ingest locking rule.
19. [`docs/claim_ingest_locking_policy.md`](claim_ingest_locking_policy.md) for the reference-aware ClaimCard ingest locking rule.
20. [`docs/gateway_contracts.md`](gateway_contracts.md) for the frozen gateway result, error, and mutation-plan communication contract.
21. [`docs/studycard_runtime.md`](studycard_runtime.md) for the real file-backed StudyCard runtime slice.
22. [`docs/datasetcard_runtime.md`](datasetcard_runtime.md) for the real file-backed DatasetCard runtime slice and the thin public CLI entry point.
23. [`docs/claimcard_runtime.md`](claimcard_runtime.md) for the real file-backed ClaimCard runtime slice.
24. [`docs/ingest_studycard_runtime.md`](ingest_studycard_runtime.md) for the first real StudyCard ingest runtime path.
25. [`docs/public_ingest_studycard_cli.md`](public_ingest_studycard_cli.md) for the first public StudyCard command surface.
26. [`docs/public_ingest_studycard_from_file.md`](public_ingest_studycard_from_file.md) for the public StudyCard single-file ingest surface.
27. [`docs/public_ingest_datasetcard_cli.md`](public_ingest_datasetcard_cli.md) for the public DatasetCard flag-based command surface.
28. [`docs/public_ingest_datasetcard_from_file.md`](public_ingest_datasetcard_from_file.md) for the public DatasetCard single-file ingest surface.
29. [`docs/public_update_studycard_cli.md`](public_update_studycard_cli.md) for the public StudyCard update surface.
30. [`docs/public_update_datasetcard_cli.md`](public_update_datasetcard_cli.md) for the public DatasetCard update surface.
31. [`docs/public_ingest_claimcard_cli.md`](public_ingest_claimcard_cli.md) for the public ClaimCard flag-based command surface.
32. [`docs/public_ingest_claimcard_from_file.md`](public_ingest_claimcard_from_file.md) for the public ClaimCard single-file ingest surface.
33. [`docs/public_update_claimcard_cli.md`](public_update_claimcard_cli.md) for the public ClaimCard update surface.
34. [`docs/public_show_cli.md`](public_show_cli.md) for the first public read-by-id command surface.
35. [`docs/public_list_cli.md`](public_list_cli.md) for the first public discovery command surface.
36. [`docs/public_delete_cli.md`](public_delete_cli.md) for the first public referentially-aware delete command surface.
37. [`docs/api_specs.md`](api_specs.md) for the current CLI contract and the boundary between implemented public commands and reserved internal command families.
38. [`docs/cli_command_contracts.md`](cli_command_contracts.md) for the frozen command-family contracts and module responsibilities.
39. [`docs/data_contracts.md`](data_contracts.md) for the high-level contract categories and the remaining non-frozen object families.
40. [`docs/audit_policy.md`](audit_policy.md) for routine review policy and the distinction from future escalated review.

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
- [`docs/governance_spec.md`](governance_spec.md): freezes A-header lanes, department offices, planned governance function names, and prosecution boundaries. Design intent / future-detail.
- [`docs/module_map.md`](module_map.md): bridges governance labels to conservative package and module paths for the current implementation state. Design intent / future-detail.
- [`docs/registry_model.md`](registry_model.md): maps the MVP object families and their planned persistence forms. Design intent / future-detail.
- [`docs/state_machine.md`](state_machine.md): defines minimal object lifecycle states for the MVP registry layer. Design intent / future-detail.
- [`docs/registry_layout.md`](registry_layout.md): freezes the first-slice on-disk registry topology, naming, and cross-reference conventions. Defines current frozen position for this slice.
- [`docs/payload_contracts.md`](payload_contracts.md): freezes the first-slice command-normalized-to-gateway payload and DTO boundary. Defines current frozen position for this slice.
- [`docs/registry_io_boundary.md`](registry_io_boundary.md): freezes the internal registry access boundary, integrity-enforcement point, mutation-safety rule, and error surface. Defines current frozen position for this slice.
- [`docs/update_snapshot_policy.md`](update_snapshot_policy.md): records the internal pre-update snapshot rule for public full-replace update. Defines current frozen position for this slice.
- [`docs/update_locking_policy.md`](update_locking_policy.md): records the single-card exclusive update-lock rule for public full-replace update. Defines current frozen position for this slice.
- [`docs/delete_locking_policy.md`](delete_locking_policy.md): records the single-card exclusive delete-lock rule for public by-id delete. Defines current frozen position for this slice.
- [`docs/ingest_locking_policy.md`](ingest_locking_policy.md): records the parent-aware DatasetCard ingest-locking rule for the current create-path milestone. Defines current frozen position for this slice.
- [`docs/claim_ingest_locking_policy.md`](claim_ingest_locking_policy.md): records the reference-aware ClaimCard ingest-locking rule for the current create-path milestone. Defines current frozen position for this slice.
- [`docs/gateway_contracts.md`](gateway_contracts.md): freezes the gateway-facing result shapes, error semantics, mutation-plan output contract, and full-replace update rule. Defines current frozen position for this slice.
- [`docs/studycard_runtime.md`](studycard_runtime.md): records the implemented StudyCard runtime slice. Defines current implemented position for this slice.
- [`docs/datasetcard_runtime.md`](datasetcard_runtime.md): records the implemented DatasetCard runtime slice plus the thin public DatasetCard CLI path. Defines current implemented position for this slice.
- [`docs/claimcard_runtime.md`](claimcard_runtime.md): records the implemented ClaimCard runtime slice. Defines current implemented position for this slice.
- [`docs/cli_command_contracts.md`](cli_command_contracts.md): freezes the command-family contracts while distinguishing the public `ingest study`, `ingest study --from-file`, `ingest dataset`, `ingest dataset --from-file`, `ingest claim`, `ingest claim --from-file`, `update study`, `update dataset`, `update claim`, `show study`, `show dataset`, `show claim`, `list studies`, `list datasets`, `list claims`, `delete study`, `delete dataset`, and `delete claim` paths from the still-internal families. Defines current frozen position for this slice.
- [`docs/ingest_studycard_runtime.md`](ingest_studycard_runtime.md): records the StudyCard ingest runtime beneath the public CLI adapter. Defines current implemented position for this slice.
- [`docs/public_ingest_studycard_cli.md`](public_ingest_studycard_cli.md): records the exact public `ingest study` surface. Defines current implemented position for this slice.
- [`docs/public_ingest_studycard_from_file.md`](public_ingest_studycard_from_file.md): records the exact public `ingest study --from-file` surface. Defines current implemented position for this slice.
- [`docs/public_update_studycard_cli.md`](public_update_studycard_cli.md): records the exact public `update study --study-id <ID> --from-file <path.yaml>` surface. Defines current implemented position for this slice.
- [`docs/public_ingest_datasetcard_cli.md`](public_ingest_datasetcard_cli.md): records the exact public `ingest dataset` surface. Defines current implemented position for this slice.
- [`docs/public_ingest_datasetcard_from_file.md`](public_ingest_datasetcard_from_file.md): records the exact public `ingest dataset --from-file` surface. Defines current implemented position for this slice.
- [`docs/public_update_datasetcard_cli.md`](public_update_datasetcard_cli.md): records the exact public `update dataset --dataset-id <ID> --from-file <path.yaml>` surface. Defines current implemented position for this slice.
- [`docs/public_ingest_claimcard_cli.md`](public_ingest_claimcard_cli.md): records the exact public `ingest claim` surface. Defines current implemented position for this slice.
- [`docs/public_ingest_claimcard_from_file.md`](public_ingest_claimcard_from_file.md): records the exact public `ingest claim --from-file` surface. Defines current implemented position for this slice.
- [`docs/public_update_claimcard_cli.md`](public_update_claimcard_cli.md): records the exact public `update claim --claim-id <ID> --from-file <path.yaml>` surface. Defines current implemented position for this slice.
- [`docs/public_show_cli.md`](public_show_cli.md): records the exact public `show study`, `show dataset`, and `show claim` surfaces. Defines current implemented position for this slice.
- [`docs/public_list_cli.md`](public_list_cli.md): records the exact public `list studies`, `list datasets`, and `list claims` surfaces. Defines current implemented position for this slice.
- [`docs/public_delete_cli.md`](public_delete_cli.md): records the exact public `delete study`, `delete dataset`, and `delete claim` surfaces. Defines current implemented position for this slice.

## Contracts And Audit

These documents describe the public CLI surface and the next layer of object and review contracts.

- [`docs/card_contracts.md`](card_contracts.md): freezes the first field-level card contracts for `StudyCard`, `DatasetCard`, and `ClaimCard`.
- [`docs/payload_contracts.md`](payload_contracts.md): freezes the exact first-slice payload/DTO shapes exchanged between internal command handlers and gateway operations.
- [`docs/registry_layout.md`](registry_layout.md): freezes where those first-slice cards conceptually live on disk and how their IDs map to canonical file paths.
- [`docs/registry_io_boundary.md`](registry_io_boundary.md): freezes who owns registry access, where direct-reference checks belong, and what mutation-safety/error rules apply.
- [`docs/update_snapshot_policy.md`](update_snapshot_policy.md): freezes the covered operations, layout, naming, append-only rule, and failure rule for pre-update snapshots.
- [`docs/update_locking_policy.md`](update_locking_policy.md): freezes the covered operations, deterministic lock paths, scope, lifetime, and failure rule for update-time locking.
- [`docs/delete_locking_policy.md`](delete_locking_policy.md): freezes the covered operations, deterministic lock paths, scope, lifetime, and failure rule for delete-time locking.
- [`docs/ingest_locking_policy.md`](ingest_locking_policy.md): freezes the covered operations, deterministic lock paths, scope, order, lifetime, and failure rule for parent-aware DatasetCard ingest locking.
- [`docs/claim_ingest_locking_policy.md`](claim_ingest_locking_policy.md): freezes the covered operations, deterministic lock paths, scope, order, lifetime, and failure rule for reference-aware ClaimCard ingest locking.
- [`docs/gateway_contracts.md`](gateway_contracts.md): freezes the precise language upper layers should consume from the gateway: success shapes, domain errors, mutation-plan outputs, and the full-replace rule.
- [`docs/studycard_runtime.md`](studycard_runtime.md): records exactly what StudyCard registry behavior is runtime-real now.
- [`docs/datasetcard_runtime.md`](datasetcard_runtime.md): records exactly what DatasetCard registry behavior is runtime-real now, including the public create and full-replace update CLI entry points.
- [`docs/claimcard_runtime.md`](claimcard_runtime.md): records exactly what ClaimCard registry behavior is runtime-real now.
- [`docs/ingest_studycard_runtime.md`](ingest_studycard_runtime.md): records exactly what StudyCard ingest runtime behavior is real now.
- [`docs/public_ingest_studycard_cli.md`](public_ingest_studycard_cli.md): records the exact public `ingest study` command shape, create-only behavior, and user-facing expectations.
- [`docs/public_ingest_studycard_from_file.md`](public_ingest_studycard_from_file.md): records the exact public `ingest study --from-file` command shape, YAML input rules, and user-facing expectations.
- [`docs/public_update_studycard_cli.md`](public_update_studycard_cli.md): records the exact public `update study --study-id <ID> --from-file <path.yaml>` command shape, canonical YAML rules, target-match requirement, and user-facing expectations.
- [`docs/public_ingest_datasetcard_cli.md`](public_ingest_datasetcard_cli.md): records the exact public `ingest dataset` command shape, create-only behavior, parent-StudyCard requirement, and user-facing expectations.
- [`docs/public_ingest_datasetcard_from_file.md`](public_ingest_datasetcard_from_file.md): records the exact public `ingest dataset --from-file` command shape, YAML input rules, parent-StudyCard requirement, and user-facing expectations.
- [`docs/public_update_datasetcard_cli.md`](public_update_datasetcard_cli.md): records the exact public `update dataset --dataset-id <ID> --from-file <path.yaml>` command shape, canonical YAML rules, target-match requirement, and user-facing expectations.
- [`docs/public_ingest_claimcard_cli.md`](public_ingest_claimcard_cli.md): records the exact public `ingest claim` command shape, create-only behavior, StudyCard and optional DatasetCard reference requirements, and user-facing expectations.
- [`docs/public_ingest_claimcard_from_file.md`](public_ingest_claimcard_from_file.md): records the exact public `ingest claim --from-file` command shape, YAML input rules, and user-facing expectations.
- [`docs/public_update_claimcard_cli.md`](public_update_claimcard_cli.md): records the exact public `update claim --claim-id <ID> --from-file <path.yaml>` command shape, canonical YAML rules, target-match requirement, and user-facing expectations.
- [`docs/public_show_cli.md`](public_show_cli.md): records the exact public `show study`, `show dataset`, and `show claim` command shapes, by-id behavior, and user-facing expectations.
- [`docs/public_list_cli.md`](public_list_cli.md): records the exact public `list studies`, `list datasets`, and `list claims` command shapes, compact-summary behavior, and user-facing expectations.
- [`docs/public_delete_cli.md`](public_delete_cli.md): records the exact public `delete study`, `delete dataset`, and `delete claim` command shapes, dependency-blocking behavior, and user-facing expectations.
- [`docs/api_specs.md`](api_specs.md): documents the current CLI contract and clearly states that there is no web API in v0.1.
- [`docs/cli_command_contracts.md`](cli_command_contracts.md): freezes the internal command-family contracts for `ingest`, `show`, `list`, `bind`, `extract`, `audit`, `review`, `run`, and `grade`.
- [`docs/data_contracts.md`](data_contracts.md): summarizes the minimum contract categories for planned object families and points to the first frozen card slice. Design intent / future-detail.
- [`docs/audit_policy.md`](audit_policy.md): defines the lightweight MVP audit posture, trigger points, and outcomes without implying an implemented audit engine. Design intent / future-detail.

## Process And Template Docs

These documents support repository discipline rather than end-user functionality.

- [`docs/avcp_guidelines.md`](avcp_guidelines.md): lightweight repo-memory and documentation-discipline guidance for non-trivial work.
- [`docs/dev_log.md`](dev_log.md): internal development notes and continuity aid; useful for context, but not a source of frozen product truth.

## Practical Reading Rule

If a question is about what is allowed now, read `state`, `constraints`, and
`decisions` first. If a question is about how the next MVP layer is organized,
then read `architecture`, `module_map`, `registry_model`, `state_machine`,
`card_contracts`, `payload_contracts`, `registry_layout`,
`registry_io_boundary`, `update_snapshot_policy`, `update_locking_policy`,
`delete_locking_policy`, `ingest_locking_policy`,
`claim_ingest_locking_policy`, `gateway_contracts`, `studycard_runtime`,
`datasetcard_runtime`, `claimcard_runtime`, `ingest_studycard_runtime`,
`public_ingest_studycard_cli`, `public_ingest_studycard_from_file`,
`public_update_studycard_cli`,
`public_ingest_datasetcard_cli`, `public_ingest_datasetcard_from_file`,
`public_update_datasetcard_cli`,
`public_ingest_claimcard_cli`, `public_ingest_claimcard_from_file`,
`public_update_claimcard_cli`, `public_show_cli`, `public_list_cli`,
`public_delete_cli`, `api_specs`,
`cli_command_contracts`, and `audit_policy`.
