"""Internal command-family skeleton modules for MacroVeritas.

This package holds the narrow real `ingest`, `update`, `show`, `list`, and
`delete` bridges plus the remaining reserved parser-builder and handler
skeletons for future command families.

It does not register commands, execute gateway operations, or perform file IO
outside the documented bridge modules.
Boundary docs: `docs/cli_command_contracts.md`, `docs/module_map.md`, and
`docs/api_specs.md`.
"""

__all__ = [
    "audit",
    "bind",
    "common",
    "delete",
    "extract",
    "grade",
    "ingest",
    "listing",
    "show",
    "review",
    "run",
    "update",
]
