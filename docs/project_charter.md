# Project Charter

## Definition

MacroVeritas is a claim-centered evidence grading and data-level verification project for literature in the melanoma, immune checkpoint inhibition, and macrophage domain.

## Project Mission

The project mission is to support disciplined, auditable development of a future system for evaluating claims and verifying data-level evidence in the melanoma + ICI + macrophage literature space.

## Scope For The Project

- claim-centered evidence grading
- data-level verification
- melanoma + ICI + macrophage literature focus
- auditable filesystem-oriented project structure

## Architecture Direction

- docs-first
- CLI-first
- filesystem-based registry and persistence
- lightweight Python implementation

## Reference Boundary

`reference/CellVoyager/` is retained only as a reference and possible execution-layer inspiration source. MacroVeritas is not being built as a CellVoyager fork, and CellVoyager is not the system backbone for v0.1.

## Explicit Boundary For This Milestone

This milestone is an MVP documentation freeze. It does not implement the scientific system itself. It only defines the package, config, docs, and minimal CLI needed for later stepwise development.
