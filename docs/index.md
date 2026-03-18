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
- [`docs/registry_model.md`](registry_model.md): maps the MVP object families and their planned persistence forms. Design intent / future-detail.
- [`docs/state_machine.md`](state_machine.md): defines minimal object lifecycle states for the MVP registry layer. Design intent / future-detail.

## Contracts And Audit

These documents describe the public CLI surface and the next layer of object and review contracts.

- [`docs/api_specs.md`](api_specs.md): documents the current CLI contract and clearly states that there is no web API in v0.1. Defines current implemented CLI surface, plus future placeholders.
- [`docs/data_contracts.md`](data_contracts.md): summarizes the minimum contract categories for planned object families without locking field-level schemas. Design intent / future-detail.
- [`docs/audit_policy.md`](audit_policy.md): defines the lightweight MVP audit posture, trigger points, and outcomes without implying an implemented audit engine. Design intent / future-detail.

## Process And Template Docs

These documents support repository discipline rather than end-user functionality.

- [`docs/avcp_guidelines.md`](avcp_guidelines.md): lightweight repo-memory and documentation-discipline guidance for non-trivial work.
- [`docs/dev_log.md`](dev_log.md): internal development notes and continuity aid; useful for context, but not a source of frozen product truth.

## Practical Reading Rule

If a question is about what is allowed now, read `state`, `constraints`, and `decisions` first. If a question is about how the next MVP layer is supposed to be organized, then read `architecture`, `registry_model`, `state_machine`, `data_contracts`, `api_specs`, and `audit_policy`.
