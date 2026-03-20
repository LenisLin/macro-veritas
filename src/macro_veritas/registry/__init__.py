"""Registry skeleton modules for MacroVeritas.

This package holds static descriptor modules for registry object families,
their documentation-level boundaries, and the narrow StudyCard, DatasetCard,
and ClaimCard runtime helpers beneath the gateway.

It does not implement rich field schemas or a general validation framework.
Boundary docs: `docs/module_map.md`, `docs/registry_model.md`,
`docs/state_machine.md`, and `docs/data_contracts.md`.
"""

__all__ = [
    "claim",
    "claim_runtime",
    "dataset",
    "dataset_runtime",
    "specs",
    "study",
    "study_runtime",
]
