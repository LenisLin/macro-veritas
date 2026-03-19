"""Shared helpers for internal command-family skeleton modules.

This module freezes the common style and metadata shape used by
`macro_veritas.commands.*`.

It does not dispatch commands, register parsers, or execute runtime behavior.
Boundary docs: `docs/cli_command_contracts.md`, `docs/module_map.md`, and
`docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    CommandDescriptor,
    CommandFamilyName,
    DescriptorSequence,
)

_COMMAND_CONTRACT_STYLE: dict[str, object] = {
    "module_layout": "one module per reserved command family beneath macro_veritas.commands",
    "parser_builder_shape": "build_parser(subparsers_or_parser: object) -> None",
    "handler_shape": "handle_<family>_command(args: object) -> object",
    "runtime_status": "internal skeleton only",
    "public_exposure": "reserved but not part of the stable public CLI",
    "file_io": "forbidden in this milestone",
    "silent_side_effects": "forbidden in this milestone",
}


def describe_command_contract_style() -> dict[str, object]:
    """Describe the frozen shared style for internal command-family modules."""

    return _COMMAND_CONTRACT_STYLE


def build_command_descriptor(
    *,
    family_name: CommandFamilyName,
    owning_module: str,
    owning_domain: str,
    purpose: str,
    primary_inputs: DescriptorSequence,
    primary_outputs: DescriptorSequence,
    dependency_contracts: DescriptorSequence,
    non_goals: DescriptorSequence,
) -> CommandDescriptor:
    """Build a static descriptor for one reserved internal command family."""

    return {
        "family_name": family_name,
        "owning_module": owning_module,
        "owning_domain": owning_domain,
        "purpose": purpose,
        "primary_inputs": primary_inputs,
        "primary_outputs": primary_outputs,
        "dependency_contracts": dependency_contracts,
        "parser_builder": "build_parser",
        "handler": f"handle_{family_name}_command",
        "public_exposure": "reserved internal skeleton; not public CLI",
        "non_goals": non_goals,
    }


def command_handler_not_implemented(family_name: CommandFamilyName) -> NotImplementedError:
    """Return the standard placeholder error for internal command handlers."""

    return NotImplementedError(
        f"handle_{family_name}_command is an internal command placeholder only. "
        f"The `{family_name}` family is reserved but not part of the public CLI, "
        "and no runtime execution is implemented."
    )


__all__ = [
    "build_command_descriptor",
    "command_handler_not_implemented",
    "describe_command_contract_style",
]
