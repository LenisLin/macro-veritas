"""Internal command-family skeleton modules for MacroVeritas.

This package holds reserved parser-builder and handler skeletons for future
command families without exposing them through the current public CLI.

It does not register commands, execute gateway operations, or perform file IO.
Boundary docs: `docs/cli_command_contracts.md`, `docs/module_map.md`, and
`docs/api_specs.md`.
"""

__all__ = [
    "audit",
    "bind",
    "common",
    "extract",
    "grade",
    "ingest",
    "review",
    "run",
]
