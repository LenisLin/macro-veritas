"""Registry skeleton modules for MacroVeritas.

This package holds static descriptor modules for registry object families and
their documentation-level boundaries.

It does not implement registry IO, field schemas, or validation rules.
Boundary docs: `docs/module_map.md`, `docs/registry_model.md`,
`docs/state_machine.md`, and `docs/data_contracts.md`.
"""

__all__ = ["claim", "dataset", "specs", "study"]
