# Decisions

## D001 — Project Identity
- Decision: `MacroVeritas` is the primary project identity; repository name = `macro-veritas`; package name = `macro_veritas`.
- Consequence: docs, config, packaging metadata, and imports must use the same identity.

## D002 — Current Phase
- Decision: the current step is an MVP documentation freeze, not feature development.
- Consequence: the milestone focuses on truthful documentation, packaging, and scaffold commands only.

## D003 — Runtime Surface
- Decision: v0.1 is CLI-first and lightweight Python, implemented with native Python and `argparse`.
- Consequence: no web API, FastAPI service, notebook-first architecture, or heavy application layer is introduced at this stage.

## D004 — Persistence Direction
- Decision: use a filesystem-based registry and run/report layout rooted at the configured project data directory.
- Consequence: registry and run artifacts will live under `/mnt/NAS_21T/ProjectData/MacroVeritas_Data`, not in SQL storage.

## D005 — Environment Philosophy
- Decision: conda is the intended development environment manager; Docker is for reproducibility only.
- Consequence: local workflows remain simple and file-oriented.

## D006 — Current Data Root
- Decision: set `data_root` to `/mnt/NAS_21T/ProjectData/MacroVeritas_Data` in committed configuration and docs.
- Consequence: the scaffold can safely initialize placeholder directories against the real external project data location.

## D007 — AVCP Governance Material
- Decision: AVCP-derived prompts, scripts, and process language are retained for governance and repository-memory scaffolding for now.
- Consequence: AVCP remains an internal operating aid, not the end-user identity of MacroVeritas.

## D008 — CellVoyager Boundary
- Decision: `reference/CellVoyager/` is reference-only and limited to possible future execution-layer inspiration.
- Consequence: MacroVeritas is not being developed as a CellVoyager fork, and CellVoyager code is not part of the current core architecture.

## D009 — Explicit v0.1 Exclusions
- Decision: no FastAPI, no SQL, no notebook-centric primary workflow, no scientific pipelines, no claim extraction, no evidence grading, no audit engine, and no real multi-agent implementation in v0.1.
- Consequence: future milestones must add those capabilities only if the constraints and architecture docs are explicitly revised.
