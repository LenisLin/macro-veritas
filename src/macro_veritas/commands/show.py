"""`show` command-family bridge for the narrow public StudyCard, DatasetCard, and ClaimCard read paths.

Owning domain: Registry Department / 户部 read boundary.
Implemented now:
- thin public CLI adapter support for `show study`
- thin public CLI adapter support for `show dataset`
- thin public CLI adapter support for `show claim`
- internal by-id input normalization at the command boundary
- StudyCard, DatasetCard, and ClaimCard gateway get-by-id execution
- command-layer success/failure translation for one-card reads

Deferred:
- list, search, or filter behavior
- relationship expansion or reverse lookups
- update/delete semantics
- scientific logic or evidence grading
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from macro_veritas.commands.common import (
    build_command_descriptor,
    build_command_payload_descriptor,
    build_command_result,
)
from macro_veritas.registry.errors import (
    CardNotFoundError,
    RegistryError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.gateway import (
    get_claim_card,
    get_dataset_card,
    get_study_card,
)
from macro_veritas.shared.types import (
    CardFamilyName,
    CommandDescriptor,
    CommandErrorCategory,
    CommandExecutionResult,
    CommandFamilyName,
    CommandPayloadDescriptor,
    DescriptorSequence,
    GatewayReadCard,
    ShowCLIInput,
)

_FAMILY_NAME: CommandFamilyName = "show"
_OPERATION_NAME = "show"
_OWNING_MODULE = "macro_veritas.commands.show"
_OWNING_DOMAIN = "Registry Department / 户部"
_PURPOSE = (
    "Execute the narrow public StudyCard, DatasetCard, and ClaimCard by-id show "
    "bridges without widening into list, search, or relationship traversal behavior."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "public by-id StudyCard, DatasetCard, or ClaimCard CLI adapter input",
    "internal by-id command input carrying card-family label plus canonical target ID",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "StudyCard, DatasetCard, or ClaimCard gateway get-by-id request",
    "raw hydrated card mapping on success or a narrow command failure result on error",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/card_contracts.md",
    "docs/gateway_contracts.md",
    "docs/cli_command_contracts.md",
    "docs/public_show_cli.md",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "get_study_card",
    "get_dataset_card",
    "get_claim_card",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = (
    build_command_payload_descriptor(
        card_family="StudyCard",
        payload_type="StudyCardPayload",
        usage="read_only",
        gateway_reads=("get_study_card",),
        gateway_mutations=(),
        notes=(
            "The show bridge accepts one canonical StudyCard identifier only.",
            "The bridge returns the raw hydrated StudyCard mapping without expansion.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="DatasetCard",
        payload_type="DatasetCardPayload",
        usage="read_only",
        gateway_reads=("get_dataset_card",),
        gateway_mutations=(),
        notes=(
            "The show bridge accepts one canonical DatasetCard identifier only.",
            "The bridge returns the raw hydrated DatasetCard mapping without expansion.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="ClaimCard",
        payload_type="ClaimCardPayload",
        usage="read_only",
        gateway_reads=("get_claim_card",),
        gateway_mutations=(),
        notes=(
            "The show bridge accepts one canonical ClaimCard identifier only.",
            "The bridge returns the raw hydrated ClaimCard mapping without expansion.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "list or search behavior",
    "filtering",
    "relationship expansion",
    "reverse lookups",
    "update or delete semantics",
)
_NON_GOALS: DescriptorSequence = (
    "list, search, or filter commands",
    "relationship expansion or reverse lookups",
    "update/delete semantics",
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
    """Return static metadata for the `show` family."""

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
            "public `show study`, `show dataset`, and `show claim` only; "
            "list/search/update/delete semantics stay non-public"
        ),
    )


def build_parser(subparsers_or_parser: object) -> None:
    """Reserve the future parser-builder hook for the internal `show` family."""

    del subparsers_or_parser
    return None


def normalize_show_input(command_input: ShowCLIInput) -> ShowCLIInput:
    """Normalize public by-id CLI input into a small internal mapping."""

    try:
        card_family = command_input["card_family"]
        target_id = command_input["target_id"]
    except KeyError as exc:
        raise ValueError(f"Field '{exc.args[0]}' is required.") from exc

    if card_family not in _CARD_FAMILY_LABELS:
        raise ValueError(f"Unsupported show card family: {card_family!r}.")

    return {
        "card_family": card_family,
        "target_id": _require_command_string(target_id, field_name="target_id"),
    }


def execute_show_study(
    command_input: ShowCLIInput,
) -> tuple[GatewayReadCard | None, CommandExecutionResult | None]:
    """Execute StudyCard show from normalized internal command input."""

    return _execute_show_input(
        command_input,
        card_family="StudyCard",
        reader=get_study_card,
    )


def execute_show_dataset(
    command_input: ShowCLIInput,
) -> tuple[GatewayReadCard | None, CommandExecutionResult | None]:
    """Execute DatasetCard show from normalized internal command input."""

    return _execute_show_input(
        command_input,
        card_family="DatasetCard",
        reader=get_dataset_card,
    )


def execute_show_claim(
    command_input: ShowCLIInput,
) -> tuple[GatewayReadCard | None, CommandExecutionResult | None]:
    """Execute ClaimCard show from normalized internal command input."""

    return _execute_show_input(
        command_input,
        card_family="ClaimCard",
        reader=get_claim_card,
    )


def translate_gateway_error(
    exc: Exception,
    *,
    card_family: CardFamilyName,
    target_id: str | None,
) -> tuple[CommandErrorCategory, str]:
    """Translate gateway/domain failures into narrow show-command semantics."""

    display_name = card_family
    if isinstance(exc, CardNotFoundError):
        if target_id is None:
            return (
                "missing_reference",
                f"requested {display_name} was not found.",
            )
        return (
            "missing_reference",
            f"requested {display_name} '{target_id}' was not found.",
        )
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            f"rejected an unsafe or unsupported canonical {display_name} identifier.",
        )
    if isinstance(exc, RegistryError):
        return (
            "registry_failure",
            f"could not read the requested {display_name} through the registry gateway.",
        )
    return (
        "registry_failure",
        f"failed before the registry gateway could complete the {display_name} read.",
    )


def handle_show_command(args: object) -> GatewayReadCard | CommandExecutionResult:
    """Handle mapping-based internal `show` dispatch for StudyCard, DatasetCard, and ClaimCard."""

    if not isinstance(args, Mapping):
        return _build_invalid_payload_result(
            card_family="StudyCard",
            target_id=None,
            message="handle_show_command expects a mapping-based internal input.",
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
            message=f"Unsupported internal show card family: {raw_card_family!r}.",
            error_category="unsupported_operation",
        )

    target_id = args.get("target_id") if isinstance(args.get("target_id"), str) else None
    try:
        normalized_input = normalize_show_input(
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
        card, error = execute_show_study(normalized_input)
    elif raw_card_family == "DatasetCard":
        card, error = execute_show_dataset(normalized_input)
    else:
        card, error = execute_show_claim(normalized_input)

    return error if error is not None else card


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the registry-gateway operations this family uses or reserves."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Describe the frozen payload families touched by `show`."""

    return _PAYLOAD_CONTRACTS


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `show` capabilities beyond the public by-id bridges."""

    return _DEFERRED_CAPABILITIES


def _execute_show_input(
    command_input: ShowCLIInput,
    *,
    card_family: CardFamilyName,
    reader: Callable[[str], GatewayReadCard],
) -> tuple[GatewayReadCard | None, CommandExecutionResult | None]:
    target_id = command_input.get("target_id") if isinstance(command_input.get("target_id"), str) else None
    try:
        if command_input["card_family"] != card_family:
            raise ValueError(
                f"Show input card_family must be {card_family!r}, not {command_input['card_family']!r}."
            )
        card = reader(command_input["target_id"])
    except (KeyError, TypeError, ValueError) as exc:
        return None, _build_invalid_payload_result(
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
        return None, build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family=card_family,
            target_id=target_id,
            message=message,
            error_category=error_category,
        )
    except Exception:
        return None, _build_unexpected_bridge_failure(
            card_family=card_family,
            target_id=target_id,
        )

    return card, None


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
        message=f"{card_family} show input is invalid: {message}",
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
        message=f"{card_family} show failed unexpectedly inside the internal command bridge.",
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
    "execute_show_claim",
    "execute_show_dataset",
    "execute_show_study",
    "family_name",
    "handle_show_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
    "normalize_show_input",
    "translate_gateway_error",
]
