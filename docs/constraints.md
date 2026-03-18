# Constraints (Locked)

C1. This repository is docs-first. State, constraints, decisions, contracts, and architecture must remain current as the codebase evolves.
C2. v0.1 is CLI-first only. No FastAPI app, no web service layer, and no public web API are allowed in this phase.
C3. Persistence direction is filesystem-based under the configured data root. No SQL database, ORM, or schema migration system is allowed in v0.1.
C4. The primary workflow is not notebook-centric. Notebooks may appear later as adjunct artifacts, but not as the main operating path.
C5. The current step is an MVP documentation freeze, not feature development. No scientific pipeline implementation may be introduced in this step.
C6. No claim extraction, evidence grading logic, audit engine behavior, registry business logic, or real multi-agent implementation may be introduced in this phase.
C7. `reference/CellVoyager/` is reference-only. CellVoyager is not adopted as the primary MacroVeritas architecture.
C8. No integration of CellVoyager code is allowed during the current freeze phase.
C9. AVCP-derived assets are retained for internal governance and process scaffolding only. They do not define the end-user identity of MacroVeritas.
C10. The scaffold must not overclaim functionality. Commands may inspect configuration and initialize placeholder directories only.
C11. Runtime paths must come from committed configuration, with the current data root set to `/mnt/NAS_21T/ProjectData/MacroVeritas_Data`.
C12. Development environment management should assume conda first. Docker is reserved for reproducibility, not as the primary developer interface.
