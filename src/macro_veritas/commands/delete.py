"""`delete` command-family bridge for the first safe public delete paths.

Owning domain: Registry Department / 户部 mutation boundary.
Implemented now:
- thin public CLI adapter support for `delete study`
- thin public CLI adapter support for `delete dataset`
- thin public CLI adapter support for `delete claim`
- internal by-id delete input normalization at the command boundary
- StudyCard, DatasetCard, and ClaimCard gateway delete execution
- command-layer success/failure translation for conservative delete behavior

Deferred:
- force delete
- cascade delete
- delete by search or filter
- restore or trash semantics
- update or patch semantics
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from macro_veritas.commands.common import build_command_descriptor, build_command_result
from macro_veritas.registry.errors import (
    CardNotFoundError,
    DependencyExistsError,
    RegistryError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.gateway import (
    delete_claim_card,
    delete_dataset_card,
    delete_study_card,
)
from macro_veritas.shared.types import (
    CardFamilyName,
    CommandDescriptor,
    CommandErrorCategory,
    CommandExecutionResult,
    CommandFamilyName,
    CommandPayloadDescriptor,
    DeleteCLIInput,
    DescriptorSequence,
)

_FAMILY_NAME: CommandFamilyName = "delete"
_OPERATION_NAME = "delete"
_OWNING_MODULE = "macro_veritas.commands.delete"
_OWNING_DOMAIN = "Registry Department / 户部"
_PURPOSE = (
    "Execute the first safe public StudyCard, DatasetCard, and ClaimCard by-id "
    "delete bridges while keeping force, cascade, and filter semantics deferred."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "public by-id StudyCard, DatasetCard, or ClaimCard delete CLI adapter input",
    "internal by-id delete command input carrying card-family label plus canonical target ID",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "StudyCard, DatasetCard, or ClaimCard gateway delete request",
    "narrow command execution result mapping with explicit dependency-blocking failures",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/registry_io_boundary.md",
    "docs/gateway_contracts.md",
    "docs/cli_command_contracts.md",
    "docs/public_delete_cli.md",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "delete_study_card",
    "delete_dataset_card",
    "delete_claim_card",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = ()
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "force delete",
    "cascade delete",
    "delete by search or filter",
    "restore or undo",
    "trash or archive semantics",
    "update or patch semantics",
)
_NON_GOALS: DescriptorSequence = (
    "force delete",
    "cascade delete",
    "delete by search or filter",
    "restore or undo",
    "trash or archive semantics",
    "scientific logic",
    "evidence grading",
    "CellVoyager integration",
)
_CARD_FAMILY_LABELS: tuple[CardFamilyName, ...] = (
    "StudyCard",
    "DatasetCard",
    "ClaimCard",
)


def family_name() -> CommandFamilyName:
    """Return the reserved command-family label for this module."""

    return _FAMILY_NAME


def describe_command_family() -> CommandDescriptor:
    """Return static metadata for the `delete` family."""

    return build_command_descriptor(
        family_name=_FAMILY_NAME,
        owning_module=_OWNING_MODULE,
        owning_domain=_OWNING_DOMAIN,
        purpose=_PURPOSE,
        primary_inputs=_PRIMARY_INPUTS,
        primary_outputs=_PRIMARY_OUTPUTS,
        dependency_contracts=_DEPENDENCY_CONTRACTS,
        non_goals=_NON_GOALS,
        public_exposure=(
            "public `delete study`, `delete dataset`, and `delete claim` only; "
            "force/cascade/filter/update semantics stay non-public"
        ),
    )


def build_parser(subparsers_or_parser: object) -> None:
    """Reserve the future parser-builder hook for the internal `delete` family."""

    del subparsers_or_parser
    return None


def normalize_delete_input(command_input: DeleteCLIInput) -> DeleteCLIInput:
    """Normalize public by-id delete CLI input into a small internal mapping."""

    try:
        card_family = command_input["card_family"]
        target_id = command_input["target_id"]
    except KeyError as exc:
        raise ValueError(f"Field '{exc.args[0]}' is required.") from exc

    if card_family not in _CARD_FAMILY_LABELS:
        raise ValueError(f"Unsupported delete card family: {card_family!r}.")

    return {
        "card_family": card_family,
        "target_id": _require_command_string(target_id, field_name="target_id"),
    }


def execute_delete_study(command_input: DeleteCLIInput) -> CommandExecutionResult:
    """Execute StudyCard delete from normalized internal command input."""

    return _execute_delete_input(
        command_input,
        card_family="StudyCard",
        deleter=delete_study_card,
    )


def execute_delete_dataset(command_input: DeleteCLIInput) -> CommandExecutionResult:
    """Execute DatasetCard delete from normalized internal command input."""

    return _execute_delete_input(
        command_input,
        card_family="DatasetCard",
        deleter=delete_dataset_card,
    )


def execute_delete_claim(command_input: DeleteCLIInput) -> CommandExecutionResult:
    """Execute ClaimCard delete from normalized internal command input."""

    return _execute_delete_input(
        command_input,
        card_family="ClaimCard",
        deleter=delete_claim_card,
    )


def translate_gateway_error(
    exc: Exception,
    *,
    card_family: CardFamilyName,
    target_id: str | None,
) -> tuple[CommandErrorCategory, str]:
    """Translate gateway/domain failures into narrow delete-command semantics."""

    display_name = card_family
    if isinstance(exc, CardNotFoundError):
        if target_id is None:
            return ("missing_reference", f"requested {display_name} was not found.")
        return (
            "missing_reference",
            f"requested {display_name} '{target_id}' was not found.",
        )
    if isinstance(exc, DependencyExistsError):
        return ("dependency_exists", str(exc))
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            f"rejected an unsafe or unsupported canonical {display_name} identifier.",
        )
    if isinstance(exc, RegistryError):
        return (
            "registry_failure",
            f"could not delete the requested {display_name} through the registry gateway.",
        )
    return (
        "registry_failure",
        f"failed before the registry gateway could complete the {display_name} delete.",
    )


def handle_delete_command(args: object) -> CommandExecutionResult:
    """Handle mapping-based internal `delete` dispatch for core card families."""

    if not isinstance(args, Mapping):
        return _build_invalid_payload_result(
            card_family="StudyCard",
            target_id=None,
            message="handle_delete_command expects a mapping-based internal input.",
        )

    raw_card_family = args.get("card_family")
    if raw_card_family is None:
        return _build_invalid_payload_result(
            card_family="StudyCard",
            target_id=None,
            message="Field 'card_family' is required.",
        )
    if raw_card_family not in _CARD_FAMILY_LABELS:
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family="StudyCard",
            target_id=None,
            message=f"Unsupported internal delete card family: {raw_card_family!r}.",
            error_category="unsupported_operation",
        )

    target_id = args.get("target_id") if isinstance(args.get("target_id"), str) else None
    try:
        normalized_input = normalize_delete_input(
            {
                "card_family": raw_card_family,
                "target_id": _require_mapping_value(args, "target_id"),
            }
        )
    except ValueError as exc:
        return _build_invalid_payload_result(
            card_family=raw_card_family,
            target_id=target_id,
            message=str(exc),
        )

    if raw_card_family == "StudyCard":
        return execute_delete_study(normalized_input)
    if raw_card_family == "DatasetCard":
        return execute_delete_dataset(normalized_input)
    return execute_delete_claim(normalized_input)


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the registry-gateway operations this family uses or reserves."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Describe the frozen payload families touched by `delete`."""

    return _PAYLOAD_CONTRACTS


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `delete` capabilities beyond the public by-id bridges."""

    return _DEFERRED_CAPABILITIES


def _execute_delete_input(
    command_input: DeleteCLIInput,
    *,
    card_family: CardFamilyName,
    deleter: Callable[[str], None],
) -> CommandExecutionResult:
    target_id = command_input.get("target_id") if isinstance(command_input.get("target_id"), str) else None
    try:
        if command_input["card_family"] != card_family:
            raise ValueError(
                f"Delete input card_family must be {card_family!r}, not {command_input['card_family']!r}."
            )
        deleter(command_input["target_id"])
    except (KeyError, TypeError, ValueError) as exc:
        return _build_invalid_payload_result(
            card_family=card_family,
            target_id=target_id,
            message=str(exc),
        )
    except RegistryError as exc:
        error_category, message = translate_gateway_error(
            exc,
            card_family=card_family,
            target_id=target_id,
        )
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family=card_family,
            target_id=target_id,
            message=message,
            error_category=error_category,
        )
    except Exception:
        return _build_unexpected_bridge_failure(
            card_family=card_family,
            target_id=target_id,
        )

    return build_command_result(
        ok=True,
        operation=_OPERATION_NAME,
        card_family=card_family,
        target_id=target_id,
        message=f"deleted {card_family} {target_id}",
    )


def _build_invalid_payload_result(
    *,
    card_family: CardFamilyName,
    target_id: str | None,
    message: str,
) -> CommandExecutionResult:
    return build_command_result(
        ok=False,
        operation=_OPERATION_NAME,
        card_family=card_family,
        target_id=target_id,
        message=f"{card_family} delete input is invalid: {message}",
        error_category="invalid_payload",
    )


def _build_unexpected_bridge_failure(
    *,
    card_family: CardFamilyName,
    target_id: str | None,
) -> CommandExecutionResult:
    return build_command_result(
        ok=False,
        operation=_OPERATION_NAME,
        card_family=card_family,
        target_id=target_id,
        message=f"{card_family} delete failed unexpectedly inside the internal command bridge.",
        error_category="registry_failure",
    )


def _require_command_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Field '{field_name}' must be a string.")
    return value


def _require_mapping_value(args: Mapping[str, object], field_name: str) -> str:
    if field_name not in args:
        raise ValueError(f"Field '{field_name}' is required.")
    return _require_command_string(args[field_name], field_name=field_name)


__all__ = [
    "build_parser",
    "describe_command_family",
    "describe_payload_contracts",
    "execute_delete_claim",
    "execute_delete_dataset",
    "execute_delete_study",
    "family_name",
    "handle_delete_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
    "normalize_delete_input",
    "translate_gateway_error",
]
