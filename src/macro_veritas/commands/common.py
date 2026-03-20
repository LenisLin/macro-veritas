"""Shared helpers for internal command-family modules.

This module freezes the common style and metadata shape used by
`macro_veritas.commands.*`.

It does not dispatch broad public CLI command families or register parsers. It
does provide a small result envelope and formatting helper for the first real
StudyCard ingest bridge while keeping the rest of the command families
internal-only.
Boundary docs: `docs/cli_command_contracts.md`, `docs/payload_contracts.md`,
`docs/module_map.md`, `docs/ingest_studycard_runtime.md`, and
`docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    CardFamilyName,
    CommandDescriptor,
    CommandErrorCategory,
    CommandExecutionResult,
    CommandFamilyName,
    CommandPayloadDescriptor,
    CommandPayloadUsage,
    DescriptorSequence,
)

_COMMAND_CONTRACT_STYLE: dict[str, object] = {
    "module_layout": "one module per reserved command family beneath macro_veritas.commands",
    "parser_builder_shape": "build_parser(subparsers_or_parser: object) -> None",
    "handler_shape": "handle_<family>_command(args: object) -> object",
    "runtime_status": (
        "mixed; the StudyCard ingest path is runtime-real and all other "
        "per-family execution remains explicitly documented"
    ),
    "public_exposure": (
        "public ingest study path only; all other reserved families remain non-public"
    ),
    "file_io": "allowed only through the registry gateway for explicitly documented internal paths",
    "silent_side_effects": "forbidden",
}
_COMMAND_PAYLOAD_CONTRACT_STYLE: dict[str, object] = {
    "source_of_truth_doc": "docs/payload_contracts.md",
    "raw_cli_argument_layer": (
        "implemented at the CLI boundary but intentionally outside the frozen "
        "payload contract"
    ),
    "command_normalized_input_layer": (
        "handlers normalize raw CLI input into small internal command inputs "
        "before preparing gateway payloads"
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
_COMMAND_RUNTIME_BOUNDARY: dict[str, object] = {
    "source_of_truth_doc": "docs/ingest_studycard_runtime.md",
    "public_cli_exposure": (
        "public `ingest study` exists as a thin adapter over the internal "
        "StudyCard ingest bridge"
    ),
    "runtime_real_now": (
        "public StudyCard CLI adapter",
        "StudyCard-only command-normalized ingest input",
        "StudyCard payload preparation",
        "StudyCard plan_create gateway call",
        "StudyCard create gateway call",
        "command-layer success/failure result translation",
    ),
    "still_skeleton_only": (
        "DatasetCard ingest",
        "ClaimCard ingest",
        "bind",
        "extract",
        "audit",
        "review",
        "run",
        "grade",
    ),
}
_COMMAND_RESULT_STYLE: dict[str, object] = {
    "output_type": "CommandExecutionResult",
    "required_fields": ("ok", "operation", "card_family", "target_id", "message"),
    "failure_field": "error_category",
    "supported_error_categories": (
        "duplicate_target",
        "invalid_payload",
        "unsupported_operation",
        "registry_failure",
    ),
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


def describe_command_runtime_boundary() -> dict[str, object]:
    """Describe the implemented-vs-deferred runtime boundary for commands."""

    return _COMMAND_RUNTIME_BOUNDARY


def describe_command_result_style() -> dict[str, object]:
    """Describe the narrow internal command execution result envelope."""

    return _COMMAND_RESULT_STYLE


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
    public_exposure: str = "reserved internal; not public CLI",
) -> CommandDescriptor:
    """Build a static descriptor for one reserved command family."""

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
        "public_exposure": public_exposure,
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


def build_command_result(
    *,
    ok: bool,
    operation: str,
    card_family: CardFamilyName,
    target_id: str | None,
    message: str,
    error_category: CommandErrorCategory | None = None,
) -> CommandExecutionResult:
    """Build the narrow internal command result mapping used by runtime bridges."""

    if ok and error_category is not None:
        raise ValueError("Successful command results must not include an error_category.")
    if not ok and error_category is None:
        raise ValueError("Failed command results must include an error_category.")

    result: CommandExecutionResult = {
        "ok": ok,
        "operation": operation,
        "card_family": card_family,
        "target_id": target_id,
        "message": message,
    }
    if error_category is not None:
        result["error_category"] = error_category
    return result


def format_command_result_for_cli(
    result: CommandExecutionResult,
    *,
    command_path: str,
) -> str:
    """Format one command result as a single user-facing CLI line."""

    if result["ok"]:
        target_id = result["target_id"]
        if target_id is None:
            return f"{command_path}: ok"
        return f"{command_path}: created {result['card_family']} {target_id}"

    return (
        f"{command_path} failed [{result['error_category']}]: "
        f"{result['message']}"
    )


__all__ = [
    "build_command_descriptor",
    "build_command_result",
    "build_command_payload_descriptor",
    "command_handler_not_implemented",
    "describe_command_contract_style",
    "describe_command_payload_contract_style",
    "describe_command_result_style",
    "describe_command_runtime_boundary",
    "describe_gateway_payload_boundary",
    "format_command_result_for_cli",
]
