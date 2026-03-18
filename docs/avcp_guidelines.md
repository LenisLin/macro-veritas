# AVCP Guidelines

MacroVeritas keeps AVCP-style repo-memory practices from the source template, but this file is now a lightweight process guide rather than a description of implemented agentic infrastructure.

## 1. Required Read Set

Before non-trivial changes, review:

- `docs/state.md`
- `docs/constraints.md`
- `docs/decisions.md`
- `docs/api_specs.md`
- `docs/data_contracts.md`
- `docs/architecture.md`

## 2. Documentation Discipline

- Update docs before or alongside interface changes.
- Distinguish implemented behavior from placeholders and future work.
- Keep claims tied to checked files, commands, or outputs.

## 3. Current Scope Discipline

- This milestone allows scaffold, packaging, config, and filesystem-layout work only.
- Do not invent scientific capabilities, evidence grading logic, or agent orchestration.
- Do not introduce a web service, SQL database, or notebook-first workflow without an explicit decision update.

## 4. Future Script Governance

Future non-trivial scripts should carry a concise header describing purpose, inputs, outputs, and contract references so the repository remains auditable as it grows.
