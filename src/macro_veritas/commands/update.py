"""`update` command-family bridge for the first public DatasetCard replace path.

Owning domain: Registry Department / 户部 mutation boundary.
Implemented now:
- thin public CLI adapter support for `update dataset`
- internal DatasetCard update input normalization at the command boundary
- single-file YAML load for one complete replacement DatasetCard
- CLI target-ID and file `dataset_id` consistency check
- DatasetCard gateway planning + runtime update execution
- command-layer success/failure translation for conservative full-replace update

Deferred:
- StudyCard update
- ClaimCard update
- patch or partial-update semantics
- field-flag update input
- batch update
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import yaml

from macro_veritas.commands.common import (
    build_command_descriptor,
    build_command_payload_descriptor,
    build_command_result,
)
from macro_veritas.registry.dataset_runtime import (
    DatasetCardFormatError,
    normalize_dataset_card_payload,
)
from macro_veritas.registry.errors import (
    BrokenReferenceError,
    CardNotFoundError,
    RegistryError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.gateway import (
    plan_update_dataset_card,
    update_dataset_card,
)
from macro_veritas.shared.types import (
    CardFamilyName,
    CommandDescriptor,
    CommandErrorCategory,
    CommandExecutionResult,
    CommandFamilyName,
    CommandPayloadDescriptor,
    DatasetCardPayload,
    DatasetCardUpdateInput,
    DescriptorSequence,
)

_FAMILY_NAME: CommandFamilyName = "update"
_OPERATION_NAME = "update"
_OWNING_MODULE = "macro_veritas.commands.update"
_OWNING_DOMAIN = "Registry Department / 户部"
_PURPOSE = (
    "Execute the first public DatasetCard full-replace update bridge from one "
    "YAML file while keeping patch semantics and other card families deferred."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "public DatasetCard by-id update CLI adapter input",
    "single-file YAML mapping input carrying one complete replacement DatasetCard",
    "internal DatasetCard update command input carrying canonical target ID plus file path",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "DatasetCard update-plan request prepared from one complete replacement payload",
    "DatasetCard runtime replace execution through the registry gateway",
    "internal command execution result mapping",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/gateway_contracts.md",
    "docs/cli_command_contracts.md",
    "docs/datasetcard_runtime.md",
    "docs/public_update_datasetcard_cli.md",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "plan_update_dataset_card",
    "update_dataset_card",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = (
    build_command_payload_descriptor(
        card_family="DatasetCard",
        payload_type="DatasetCardPayload",
        usage="prepare_update",
        gateway_reads=(),
        gateway_mutations=("plan_update_dataset_card", "update_dataset_card"),
        notes=(
            "The update bridge accepts one complete replacement DatasetCard only.",
            "The bridge calls plan_update_dataset_card before update_dataset_card.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "StudyCard update",
    "ClaimCard update",
    "patch or merge semantics",
    "field-flag update input",
    "batch update",
    "update by search or filter",
)
_NON_GOALS: DescriptorSequence = (
    "StudyCard update",
    "ClaimCard update",
    "patch or merge semantics",
    "field-flag update input",
    "batch update",
    "scientific logic",
    "evidence grading",
    "CellVoyager integration",
)


def family_name() -> CommandFamilyName:
    """Return the reserved command-family label for this module."""

    return _FAMILY_NAME


def describe_command_family() -> CommandDescriptor:
    """Return static metadata for the `update` family."""

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
            "public `update dataset --dataset-id <ID> --from-file <path.yaml>` only; "
            "StudyCard/ClaimCard/patch semantics stay non-public"
        ),
    )


def build_parser(subparsers_or_parser: object) -> None:
    """Reserve the future parser-builder hook for the internal `update` family."""

    del subparsers_or_parser
    return None


def normalize_update_input(
    command_input: DatasetCardUpdateInput,
) -> DatasetCardUpdateInput:
    """Normalize the public DatasetCard update CLI input into a small mapping."""

    try:
        dataset_id = command_input["dataset_id"]
        from_file = command_input["from_file"]
    except KeyError as exc:
        raise ValueError(f"Field '{exc.args[0]}' is required.") from exc

    normalized_dataset_id = _require_command_string(dataset_id, field_name="dataset_id")
    normalized_from_file = _require_command_string(from_file, field_name="from_file")
    if not normalized_dataset_id.strip():
        raise ValueError("Field 'dataset_id' must not be empty.")
    if not normalized_from_file.strip():
        raise ValueError("Field 'from_file' must not be empty.")

    return {
        "dataset_id": normalized_dataset_id,
        "from_file": normalized_from_file,
    }


def load_datasetcard_update_file(path: str | Path) -> DatasetCardPayload:
    """Load one complete replacement DatasetCard payload from a YAML file."""

    input_path = Path(path)
    try:
        document = input_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"DatasetCard update file was not found: {input_path}.") from exc
    except OSError as exc:
        raise ValueError(f"DatasetCard update file could not be read: {input_path}.") from exc

    try:
        parsed = yaml.safe_load(document)
    except yaml.YAMLError as exc:
        raise ValueError(f"DatasetCard update file is not valid YAML: {input_path}.") from exc

    if not isinstance(parsed, Mapping):
        raise ValueError(f"DatasetCard update file must decode to one mapping: {input_path}.")

    raw_input = dict(parsed)
    non_string_keys = [key for key in raw_input if not isinstance(key, str)]
    if non_string_keys:
        raise ValueError("DatasetCard update file keys must be strings.")

    try:
        return normalize_dataset_card_payload(raw_input)
    except DatasetCardFormatError as exc:
        raise ValueError(
            "DatasetCard update file must describe one complete valid DatasetCard: "
            f"{exc}"
        ) from exc


def execute_update_dataset(
    command_input: DatasetCardUpdateInput,
) -> CommandExecutionResult:
    """Execute DatasetCard full-replace update from normalized command input."""

    target_id = command_input.get("dataset_id")
    parent_study_id: str | None = None
    try:
        replacement_card = load_datasetcard_update_file(command_input["from_file"])
        parent_study_id = replacement_card["study_id"]
        if replacement_card["dataset_id"] != command_input["dataset_id"]:
            raise ValueError(
                "CLI --dataset-id must match file dataset_id: "
                f"{command_input['dataset_id']} != {replacement_card['dataset_id']}."
            )
        plan_update_dataset_card(replacement_card)
        updated = update_dataset_card(replacement_card)
    except (KeyError, TypeError, ValueError) as exc:
        return _build_invalid_payload_result(target_id=target_id, message=str(exc))
    except RegistryError as exc:
        error_category, message = translate_gateway_error(
            exc,
            target_id=target_id,
            parent_study_id=parent_study_id,
        )
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family="DatasetCard",
            target_id=target_id,
            message=message,
            error_category=error_category,
        )
    except Exception:
        return _build_unexpected_bridge_failure(target_id=target_id)

    return build_command_result(
        ok=True,
        operation=_OPERATION_NAME,
        card_family="DatasetCard",
        target_id=updated["dataset_id"],
        message="DatasetCard update replaced the canonical DatasetCard record.",
    )


def translate_gateway_error(
    exc: Exception,
    *,
    target_id: str | None,
    parent_study_id: str | None,
) -> tuple[CommandErrorCategory, str]:
    """Translate gateway/domain failures into narrow update-command semantics."""

    if isinstance(exc, CardNotFoundError):
        if target_id is None:
            return ("missing_reference", "requested DatasetCard was not found.")
        return (
            "missing_reference",
            f"requested DatasetCard '{target_id}' was not found.",
        )
    if isinstance(exc, BrokenReferenceError):
        if parent_study_id is None:
            return (
                "missing_reference",
                "DatasetCard update requires the parent StudyCard to exist before replace.",
            )
        return (
            "missing_reference",
            "DatasetCard update requires the parent StudyCard "
            f"'{parent_study_id}' to exist before replace.",
        )
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            "DatasetCard update rejected an unsupported registry operation or identifier.",
        )
    if isinstance(exc, RegistryError):
        if _looks_like_invalid_dataset_payload_error(exc):
            return (
                "invalid_payload",
                f"DatasetCard update rejected invalid DatasetCard data: {exc}",
            )
        return (
            "registry_failure",
            "DatasetCard update failed at the registry gateway boundary.",
        )
    return (
        "registry_failure",
        "DatasetCard update failed before the registry gateway could complete.",
    )


def handle_update_command(args: object) -> CommandExecutionResult:
    """Handle mapping-based internal `update` dispatch for DatasetCard only."""

    if not isinstance(args, Mapping):
        return _build_invalid_payload_result(
            target_id=None,
            message="handle_update_command expects a mapping-based internal input.",
        )

    target_id = args.get("dataset_id") if isinstance(args.get("dataset_id"), str) else None
    try:
        normalized_input = normalize_update_input(
            {
                "dataset_id": _require_mapping_value(args, "dataset_id"),
                "from_file": _require_mapping_value(args, "from_file"),
            }
        )
    except ValueError as exc:
        return _build_invalid_payload_result(
            target_id=target_id,
            message=str(exc),
        )

    return execute_update_dataset(normalized_input)


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Return the static payload-touchpoint descriptors for the `update` family."""

    return _PAYLOAD_CONTRACTS


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """Return the gateway operations that the `update` bridge expects."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def list_deferred_capabilities() -> DescriptorSequence:
    """Return explicitly deferred `update` capabilities."""

    return _DEFERRED_CAPABILITIES


def _build_invalid_payload_result(
    *,
    target_id: str | None,
    message: str,
) -> CommandExecutionResult:
    return build_command_result(
        ok=False,
        operation=_OPERATION_NAME,
        card_family="DatasetCard",
        target_id=target_id,
        message=f"DatasetCard update input is invalid: {message}",
        error_category="invalid_payload",
    )


def _build_unexpected_bridge_failure(
    *,
    target_id: str | None,
) -> CommandExecutionResult:
    return build_command_result(
        ok=False,
        operation=_OPERATION_NAME,
        card_family="DatasetCard",
        target_id=target_id,
        message="DatasetCard update failed unexpectedly inside the internal command bridge.",
        error_category="registry_failure",
    )


def _looks_like_invalid_dataset_payload_error(exc: RegistryError) -> bool:
    message = str(exc)
    if "filesystem access" in message or "runtime translation" in message:
        return False
    return (
        message.startswith("DatasetCard field '")
        or message.startswith("DatasetCard payload ")
        or "missing required fields" in message
        or "unexpected fields" in message
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
    "execute_update_dataset",
    "family_name",
    "handle_update_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
    "load_datasetcard_update_file",
    "normalize_update_input",
    "translate_gateway_error",
]
