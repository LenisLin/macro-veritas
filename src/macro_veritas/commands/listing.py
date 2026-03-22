"""`list` command-family bridge for the narrow public StudyCard, DatasetCard, and ClaimCard discovery paths.

Owning domain: Registry Department / 户部 discovery boundary.
Implemented now:
- thin public CLI adapter support for `list studies`
- thin public CLI adapter support for `list datasets`
- thin public CLI adapter support for `list claims`
- internal family-level list input normalization at the command boundary
- StudyCard, DatasetCard, and ClaimCard gateway list execution
- compact summary shaping for public discovery output
- command-layer success/failure translation for family-level listings

Deferred:
- search or filter behavior
- pagination
- relationship expansion or reverse lookups
- show expansion
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
from macro_veritas.registry.errors import RegistryError, UnsupportedRegistryOperationError
from macro_veritas.registry.gateway import (
    list_claim_cards,
    list_dataset_cards,
    list_study_cards,
)
from macro_veritas.shared.types import (
    CardFamilyName,
    ClaimCardSummary,
    CommandDescriptor,
    CommandErrorCategory,
    CommandExecutionResult,
    CommandFamilyName,
    CommandPayloadDescriptor,
    DatasetCardSummary,
    DescriptorSequence,
    GatewayListResult,
    ListCLIInput,
    ListSummaryResult,
    StudyCardSummary,
)

_FAMILY_NAME: CommandFamilyName = "list"
_OPERATION_NAME = "list"
_OWNING_MODULE = "macro_veritas.commands.listing"
_OWNING_DOMAIN = "Registry Department / 户部"
_PURPOSE = (
    "Execute the narrow public StudyCard, DatasetCard, and ClaimCard family-level "
    "listing bridges for discovery without widening into search, filter, pagination, "
    "or relationship traversal behavior."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "public by-family StudyCard, DatasetCard, or ClaimCard list CLI adapter input",
    "internal list command input carrying the target card-family label only",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "StudyCard, DatasetCard, or ClaimCard gateway family-list request",
    "stable compact summary entries on success or a narrow command failure result on error",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/card_contracts.md",
    "docs/gateway_contracts.md",
    "docs/cli_command_contracts.md",
    "docs/public_list_cli.md",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "list_study_cards",
    "list_dataset_cards",
    "list_claim_cards",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = (
    build_command_payload_descriptor(
        card_family="StudyCard",
        payload_type="StudyCardPayload",
        usage="read_only",
        gateway_reads=("list_study_cards",),
        gateway_mutations=(),
        notes=(
            "The list bridge returns compact StudyCard summaries only.",
            "The bridge does not expose full raw StudyCard payloads in list mode.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="DatasetCard",
        payload_type="DatasetCardPayload",
        usage="read_only",
        gateway_reads=("list_dataset_cards",),
        gateway_mutations=(),
        notes=(
            "The list bridge returns compact DatasetCard summaries only.",
            "The bridge does not expose full raw DatasetCard payloads in list mode.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="ClaimCard",
        payload_type="ClaimCardPayload",
        usage="read_only",
        gateway_reads=("list_claim_cards",),
        gateway_mutations=(),
        notes=(
            "The list bridge returns compact ClaimCard summaries only.",
            "The bridge does not expose long claim text bodies or other raw ClaimCard fields in list mode.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "search behavior",
    "filtering",
    "pagination",
    "relationship expansion",
    "reverse lookups",
    "show expansion",
    "update or delete semantics",
)
_NON_GOALS: DescriptorSequence = (
    "search, filter, or pagination behavior",
    "relationship expansion or reverse lookups",
    "show expansion",
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
    """Return static metadata for the `list` family."""

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
            "public `list studies`, `list datasets`, and `list claims` only; "
            "search/filter/update/delete semantics stay non-public"
        ),
    )


def build_parser(subparsers_or_parser: object) -> None:
    """Reserve the future parser-builder hook for the internal `list` family."""

    del subparsers_or_parser
    return None


def normalize_list_input(command_input: ListCLIInput) -> ListCLIInput:
    """Normalize public list CLI input into a small internal mapping."""

    try:
        card_family = command_input["card_family"]
    except KeyError as exc:
        raise ValueError(f"Field '{exc.args[0]}' is required.") from exc

    if card_family not in _CARD_FAMILY_LABELS:
        raise ValueError(f"Unsupported list card family: {card_family!r}.")

    return {
        "card_family": card_family,
    }


def execute_list_studies(
    command_input: ListCLIInput,
) -> tuple[ListSummaryResult | None, CommandExecutionResult | None]:
    """Execute StudyCard listing from normalized internal command input."""

    return _execute_list_input(
        command_input,
        card_family="StudyCard",
        reader=list_study_cards,
        summarizer=_summarize_study_cards,
    )


def execute_list_datasets(
    command_input: ListCLIInput,
) -> tuple[ListSummaryResult | None, CommandExecutionResult | None]:
    """Execute DatasetCard listing from normalized internal command input."""

    return _execute_list_input(
        command_input,
        card_family="DatasetCard",
        reader=list_dataset_cards,
        summarizer=_summarize_dataset_cards,
    )


def execute_list_claims(
    command_input: ListCLIInput,
) -> tuple[ListSummaryResult | None, CommandExecutionResult | None]:
    """Execute ClaimCard listing from normalized internal command input."""

    return _execute_list_input(
        command_input,
        card_family="ClaimCard",
        reader=list_claim_cards,
        summarizer=_summarize_claim_cards,
    )


def translate_gateway_error(
    exc: Exception,
    *,
    card_family: CardFamilyName,
) -> tuple[CommandErrorCategory, str]:
    """Translate gateway/domain failures into narrow list-command semantics."""

    display_name = card_family
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            f"requested {display_name} collection listing is unsupported by the registry gateway.",
        )
    if isinstance(exc, RegistryError):
        return (
            "registry_failure",
            f"could not list the requested {display_name} collection through the registry gateway.",
        )
    return (
        "registry_failure",
        f"failed before the registry gateway could complete the {display_name} listing.",
    )


def handle_list_command(args: object) -> ListSummaryResult | CommandExecutionResult:
    """Handle mapping-based internal `list` dispatch for StudyCard, DatasetCard, and ClaimCard."""

    if not isinstance(args, Mapping):
        return _build_invalid_payload_result(
            card_family="StudyCard",
            message="handle_list_command expects a mapping-based internal input.",
        )

    raw_card_family = args.get("card_family")
    if raw_card_family is None:
        return _build_invalid_payload_result(
            card_family="StudyCard",
            message="Field 'card_family' is required.",
        )
    if raw_card_family not in _CARD_FAMILY_LABELS:
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family="StudyCard",
            target_id=None,
            message=f"Unsupported internal list card family: {raw_card_family!r}.",
            error_category="unsupported_operation",
        )

    try:
        normalized_input = normalize_list_input(
            {
                "card_family": _require_mapping_value(args, "card_family"),
            }
        )
    except ValueError as exc:
        return _build_invalid_payload_result(
            card_family=raw_card_family,
            message=str(exc),
        )

    if raw_card_family == "StudyCard":
        summaries, error = execute_list_studies(normalized_input)
    elif raw_card_family == "DatasetCard":
        summaries, error = execute_list_datasets(normalized_input)
    else:
        summaries, error = execute_list_claims(normalized_input)

    return error if error is not None else summaries


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the registry-gateway operations this family uses or reserves."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Describe the frozen payload families touched by `list`."""

    return _PAYLOAD_CONTRACTS


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `list` capabilities beyond the public discovery bridges."""

    return _DEFERRED_CAPABILITIES


def _execute_list_input(
    command_input: ListCLIInput,
    *,
    card_family: CardFamilyName,
    reader: Callable[[], GatewayListResult],
    summarizer: Callable[[GatewayListResult], ListSummaryResult],
) -> tuple[ListSummaryResult | None, CommandExecutionResult | None]:
    try:
        if command_input["card_family"] != card_family:
            raise ValueError(
                f"List input card_family must be {card_family!r}, not {command_input['card_family']!r}."
            )
        summaries = summarizer(reader())
    except (KeyError, TypeError, ValueError) as exc:
        return None, _build_invalid_payload_result(
            card_family=card_family,
            message=str(exc),
        )
    except RegistryError as exc:
        error_category, message = translate_gateway_error(
            exc,
            card_family=card_family,
        )
        return None, build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family=card_family,
            target_id=None,
            message=message,
            error_category=error_category,
        )
    except Exception:
        return None, _build_unexpected_bridge_failure(card_family=card_family)

    return summaries, None


def _summarize_study_cards(cards: GatewayListResult) -> ListSummaryResult:
    summaries: list[StudyCardSummary] = []
    for card in cards:
        study_id = _require_summary_string(card, "study_id", card_family="StudyCard")
        summaries.append(
            {
                "study_id": study_id,
                "status": _require_summary_string(card, "status", card_family="StudyCard"),
                "citation_handle": _require_summary_string(
                    card,
                    "citation_handle",
                    card_family="StudyCard",
                ),
            }
        )
    return tuple(sorted(summaries, key=lambda item: item["study_id"]))


def _summarize_dataset_cards(cards: GatewayListResult) -> ListSummaryResult:
    summaries: list[DatasetCardSummary] = []
    for card in cards:
        dataset_id = _require_summary_string(card, "dataset_id", card_family="DatasetCard")
        summaries.append(
            {
                "dataset_id": dataset_id,
                "study_id": _require_summary_string(card, "study_id", card_family="DatasetCard"),
                "status": _require_summary_string(card, "status", card_family="DatasetCard"),
            }
        )
    return tuple(sorted(summaries, key=lambda item: item["dataset_id"]))


def _summarize_claim_cards(cards: GatewayListResult) -> ListSummaryResult:
    summaries: list[ClaimCardSummary] = []
    for card in cards:
        claim_id = _require_summary_string(card, "claim_id", card_family="ClaimCard")
        summaries.append(
            {
                "claim_id": claim_id,
                "study_id": _require_summary_string(card, "study_id", card_family="ClaimCard"),
                "status": _require_summary_string(card, "status", card_family="ClaimCard"),
                "claim_type": _require_summary_string(card, "claim_type", card_family="ClaimCard"),
            }
        )
    return tuple(sorted(summaries, key=lambda item: item["claim_id"]))


def _build_invalid_payload_result(
    *,
    card_family: CardFamilyName,
    message: str,
) -> CommandExecutionResult:
    return build_command_result(
        ok=False,
        operation=_OPERATION_NAME,
        card_family=card_family,
        target_id=None,
        message=f"{card_family} list input is invalid: {message}",
        error_category="invalid_payload",
    )


def _build_unexpected_bridge_failure(
    *,
    card_family: CardFamilyName,
) -> CommandExecutionResult:
    return build_command_result(
        ok=False,
        operation=_OPERATION_NAME,
        card_family=card_family,
        target_id=None,
        message=f"{card_family} list failed unexpectedly inside the internal command bridge.",
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


def _require_summary_string(
    card: Mapping[str, object],
    field_name: str,
    *,
    card_family: CardFamilyName,
) -> str:
    if field_name not in card:
        raise ValueError(f"{card_family} list summary field '{field_name}' is required.")
    value = card[field_name]
    if not isinstance(value, str):
        raise ValueError(f"{card_family} list summary field '{field_name}' must be a string.")
    return value


__all__ = [
    "build_parser",
    "describe_command_family",
    "describe_payload_contracts",
    "execute_list_claims",
    "execute_list_datasets",
    "execute_list_studies",
    "family_name",
    "handle_list_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
    "normalize_list_input",
    "translate_gateway_error",
]
