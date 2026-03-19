"""Shared helpers for internal command-family skeleton modules.

This module freezes the common style and metadata shape used by
`macro_veritas.commands.*`.

It does not dispatch commands, register parsers, or execute runtime behavior.
Boundary docs: `docs/cli_command_contracts.md`, `docs/payload_contracts.md`,
`docs/module_map.md`, and `docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    CardFamilyName,
    CommandDescriptor,
    CommandFamilyName,
    CommandPayloadDescriptor,
    CommandPayloadUsage,
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
_COMMAND_PAYLOAD_CONTRACT_STYLE: dict[str, object] = {
    "source_of_truth_doc": "docs/payload_contracts.md",
    "raw_cli_argument_layer": "deferred and intentionally outside the frozen payload contract",
    "command_normalized_input_layer": (
        "future handlers normalize raw CLI input into small internal command "
        "inputs before preparing gateway payloads"
    ),
    "gateway_payload_layer": (
        "handlers prepare full-card StudyCardPayload / DatasetCardPayload / "
        "ClaimCardPayload mappings for create or update planning"
    ),
    "stored_card_representation_layer": (
        "frozen separately by docs/card_contracts.md and returned by gateway "
        "reads as bare card mappings"
    ),
}
_GATEWAY_PAYLOAD_BOUNDARY: dict[str, str | bool] = {
    "source_of_truth_doc": "docs/payload_contracts.md",
    "gateway_consumes_argparse_objects": False,
    "gateway_consumes_full_card_payloads_only": True,
    "patch_payloads_supported": False,
    "read_result_shape": "bare card mapping shaped like the frozen card contract",
}


def describe_command_contract_style() -> dict[str, object]:
    """Describe the frozen shared style for internal command-family modules."""

    return _COMMAND_CONTRACT_STYLE


def describe_command_payload_contract_style() -> dict[str, object]:
    """Describe the shared payload-boundary style for command-family modules."""

    return _COMMAND_PAYLOAD_CONTRACT_STYLE


def describe_gateway_payload_boundary() -> dict[str, str | bool]:
    """Describe the frozen command-to-gateway payload boundary."""

    return _GATEWAY_PAYLOAD_BOUNDARY


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


def build_command_payload_descriptor(
    *,
    card_family: CardFamilyName,
    payload_type: str,
    usage: CommandPayloadUsage,
    gateway_reads: DescriptorSequence,
    gateway_mutations: DescriptorSequence,
    notes: DescriptorSequence,
) -> CommandPayloadDescriptor:
    """Build a static payload descriptor for one command-family/card touchpoint."""

    return {
        "card_family": card_family,
        "payload_type": payload_type,
        "usage": usage,
        "gateway_reads": gateway_reads,
        "gateway_mutations": gateway_mutations,
        "notes": notes,
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
    "build_command_payload_descriptor",
    "command_handler_not_implemented",
    "describe_command_contract_style",
    "describe_command_payload_contract_style",
    "describe_gateway_payload_boundary",
]
