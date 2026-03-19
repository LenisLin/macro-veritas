"""Registry skeleton modules for MacroVeritas.

This package holds static descriptor modules for registry object families,
their documentation-level boundaries, and the first narrow StudyCard runtime
helpers beneath the gateway.

It does not implement DatasetCard or ClaimCard runtime IO, rich field schemas,
or a general validation framework.
Boundary docs: `docs/module_map.md`, `docs/registry_model.md`,
`docs/state_machine.md`, and `docs/data_contracts.md`.
"""

__all__ = ["claim", "dataset", "specs", "study", "study_runtime"]
