"""`update` command-family bridge for narrow public full-replace update paths.

Owning domain: Registry Department / 户部 mutation boundary.
Implemented now:
- thin public CLI adapter support for `update study`
- thin public CLI adapter support for `update dataset`
- thin public CLI adapter support for `update claim`
- internal StudyCard update input normalization at the command boundary
- internal DatasetCard update input normalization at the command boundary
- internal ClaimCard update input normalization at the command boundary
- single-file YAML load for one complete replacement StudyCard
- single-file YAML load for one complete replacement DatasetCard
- single-file YAML load for one complete replacement ClaimCard
- CLI target-ID and file `study_id` consistency check
- CLI target-ID and file `dataset_id` consistency check
- CLI target-ID and file `claim_id` consistency check
- StudyCard gateway planning + runtime update execution
- DatasetCard gateway planning + runtime update execution
- ClaimCard gateway planning + runtime update execution
- command-layer success/failure translation for conservative full-replace update

Deferred:
- patch or partial-update semantics
- field-flag update input
- batch update
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import yaml

from macro_veritas.commands.common import (
    build_command_descriptor,
    build_command_payload_descriptor,
    build_command_result,
)
from macro_veritas.registry.claim_runtime import (
    ClaimCardFormatError,
    normalize_claim_card_payload,
)
from macro_veritas.registry.dataset_runtime import (
    DatasetCardFormatError,
    normalize_dataset_card_payload,
)
from macro_veritas.registry.errors import (
    BrokenReferenceError,
    CardNotFoundError,
    InvalidStateTransitionError,
    RegistryError,
    UpdateLockError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.gateway import (
    plan_update_claim_card,
    plan_update_dataset_card,
    plan_update_study_card,
    update_claim_card,
    update_dataset_card,
    update_study_card,
)
from macro_veritas.registry.study_runtime import (
    StudyCardFormatError,
    normalize_study_card_payload,
)
from macro_veritas.shared.types import (
    CardFamilyName,
    ClaimCardPayload,
    ClaimCardUpdateInput,
    CommandDescriptor,
    CommandErrorCategory,
    CommandExecutionResult,
    CommandFamilyName,
    CommandPayloadDescriptor,
    DatasetCardPayload,
    DatasetCardUpdateInput,
    DescriptorSequence,
    StudyCardPayload,
    StudyCardUpdateInput,
)

_FAMILY_NAME: CommandFamilyName = "update"
_OPERATION_NAME = "update"
_OWNING_MODULE = "macro_veritas.commands.update"
_OWNING_DOMAIN = "Registry Department / 户部"
_PURPOSE = (
    "Execute the narrow public StudyCard, DatasetCard, and ClaimCard "
    "full-replace update bridges from one YAML file while keeping patch "
    "semantics and broader update surfaces deferred."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "public StudyCard by-id update CLI adapter input",
    "public DatasetCard by-id update CLI adapter input",
    "public ClaimCard by-id update CLI adapter input",
    "single-file YAML mapping input carrying one complete replacement StudyCard or DatasetCard or ClaimCard",
    "internal StudyCard or DatasetCard or ClaimCard update command input carrying canonical target ID plus file path",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "StudyCard or DatasetCard or ClaimCard update-plan request prepared from one complete replacement payload",
    "StudyCard or DatasetCard or ClaimCard runtime replace execution through the registry gateway",
    "internal command execution result mapping",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/gateway_contracts.md",
    "docs/cli_command_contracts.md",
    "docs/studycard_runtime.md",
    "docs/datasetcard_runtime.md",
    "docs/claimcard_runtime.md",
    "docs/public_update_studycard_cli.md",
    "docs/public_update_datasetcard_cli.md",
    "docs/public_update_claimcard_cli.md",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "plan_update_study_card",
    "update_study_card",
    "plan_update_dataset_card",
    "update_dataset_card",
    "plan_update_claim_card",
    "update_claim_card",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = (
    build_command_payload_descriptor(
        card_family="StudyCard",
        payload_type="StudyCardPayload",
        usage="prepare_update",
        gateway_reads=(),
        gateway_mutations=("plan_update_study_card", "update_study_card"),
        notes=(
            "The update bridge accepts one complete replacement StudyCard only.",
            "The bridge calls plan_update_study_card before update_study_card.",
        ),
    ),
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
    build_command_payload_descriptor(
        card_family="ClaimCard",
        payload_type="ClaimCardPayload",
        usage="prepare_update",
        gateway_reads=(),
        gateway_mutations=("plan_update_claim_card", "update_claim_card"),
        notes=(
            "The update bridge accepts one complete replacement ClaimCard only.",
            "The bridge calls plan_update_claim_card before update_claim_card.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "patch or merge semantics",
    "field-flag update input",
    "batch update",
    "update by search or filter",
)
_NON_GOALS: DescriptorSequence = (
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
            "public `update study --study-id <ID> --from-file <path.yaml>` and "
            "`update dataset --dataset-id <ID> --from-file <path.yaml>` and "
            "`update claim --claim-id <ID> --from-file <path.yaml>` only; "
            "patch semantics stay non-public"
        ),
    )


def build_parser(subparsers_or_parser: object) -> None:
    """Reserve the future parser-builder hook for the internal `update` family."""

    del subparsers_or_parser
    return None


def normalize_studycard_update_input(
    command_input: StudyCardUpdateInput,
) -> StudyCardUpdateInput:
    """Normalize the public StudyCard update CLI input into a small mapping."""

    try:
        study_id = command_input["study_id"]
        from_file = command_input["from_file"]
    except KeyError as exc:
        raise ValueError(f"Field '{exc.args[0]}' is required.") from exc

    normalized_study_id = _require_command_string(study_id, field_name="study_id")
    normalized_from_file = _require_command_string(from_file, field_name="from_file")
    if not normalized_study_id.strip():
        raise ValueError("Field 'study_id' must not be empty.")
    if not normalized_from_file.strip():
        raise ValueError("Field 'from_file' must not be empty.")

    return {
        "study_id": normalized_study_id,
        "from_file": normalized_from_file,
    }


def normalize_datasetcard_update_input(
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


def normalize_claimcard_update_input(
    command_input: ClaimCardUpdateInput,
) -> ClaimCardUpdateInput:
    """Normalize the public ClaimCard update CLI input into a small mapping."""

    try:
        claim_id = command_input["claim_id"]
        from_file = command_input["from_file"]
    except KeyError as exc:
        raise ValueError(f"Field '{exc.args[0]}' is required.") from exc

    normalized_claim_id = _require_command_string(claim_id, field_name="claim_id")
    normalized_from_file = _require_command_string(from_file, field_name="from_file")
    if not normalized_claim_id.strip():
        raise ValueError("Field 'claim_id' must not be empty.")
    if not normalized_from_file.strip():
        raise ValueError("Field 'from_file' must not be empty.")

    return {
        "claim_id": normalized_claim_id,
        "from_file": normalized_from_file,
    }


def normalize_update_input(
    command_input: DatasetCardUpdateInput,
) -> DatasetCardUpdateInput:
    """Backward-compatible alias for DatasetCard update normalization."""

    return normalize_datasetcard_update_input(command_input)


def load_studycard_update_file(path: str | Path) -> StudyCardPayload:
    """Load one complete replacement StudyCard payload from a YAML file."""

    raw_input = _load_update_file_mapping(path, card_family="StudyCard")
    try:
        return normalize_study_card_payload(raw_input)
    except StudyCardFormatError as exc:
        raise ValueError(
            "StudyCard update file must describe one complete valid StudyCard: "
            f"{exc}"
        ) from exc


def load_datasetcard_update_file(path: str | Path) -> DatasetCardPayload:
    """Load one complete replacement DatasetCard payload from a YAML file."""

    raw_input = _load_update_file_mapping(path, card_family="DatasetCard")
    try:
        return normalize_dataset_card_payload(raw_input)
    except DatasetCardFormatError as exc:
        raise ValueError(
            "DatasetCard update file must describe one complete valid DatasetCard: "
            f"{exc}"
        ) from exc


def load_claimcard_update_file(path: str | Path) -> ClaimCardPayload:
    """Load one complete replacement ClaimCard payload from a YAML file."""

    raw_input = _load_update_file_mapping(path, card_family="ClaimCard")
    try:
        return normalize_claim_card_payload(raw_input)
    except ClaimCardFormatError as exc:
        raise ValueError(
            "ClaimCard update file must describe one complete valid ClaimCard: "
            f"{exc}"
        ) from exc


def execute_update_study(
    command_input: StudyCardUpdateInput,
) -> CommandExecutionResult:
    """Execute StudyCard full-replace update from normalized command input."""

    target_id = command_input.get("study_id")
    try:
        replacement_card = load_studycard_update_file(command_input["from_file"])
        if replacement_card["study_id"] != command_input["study_id"]:
            raise ValueError(
                "CLI --study-id must match file study_id: "
                f"{command_input['study_id']} != {replacement_card['study_id']}."
            )
        plan_update_study_card(replacement_card)
        updated = update_study_card(replacement_card)
    except (KeyError, TypeError, ValueError) as exc:
        return _build_invalid_payload_result(
            card_family="StudyCard",
            target_id=target_id,
            message=str(exc),
        )
    except RegistryError as exc:
        error_category, message = translate_gateway_error(
            exc,
            card_family="StudyCard",
            target_id=target_id,
        )
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family="StudyCard",
            target_id=target_id,
            message=message,
            error_category=error_category,
        )
    except Exception:
        return _build_unexpected_bridge_failure(
            card_family="StudyCard",
            target_id=target_id,
        )

    return build_command_result(
        ok=True,
        operation=_OPERATION_NAME,
        card_family="StudyCard",
        target_id=updated["study_id"],
        message="StudyCard update replaced the canonical StudyCard record.",
    )


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
        return _build_invalid_payload_result(
            card_family="DatasetCard",
            target_id=target_id,
            message=str(exc),
        )
    except RegistryError as exc:
        error_category, message = translate_gateway_error(
            exc,
            card_family="DatasetCard",
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
        return _build_unexpected_bridge_failure(
            card_family="DatasetCard",
            target_id=target_id,
        )

    return build_command_result(
        ok=True,
        operation=_OPERATION_NAME,
        card_family="DatasetCard",
        target_id=updated["dataset_id"],
        message="DatasetCard update replaced the canonical DatasetCard record.",
    )


def execute_update_claim(
    command_input: ClaimCardUpdateInput,
) -> CommandExecutionResult:
    """Execute ClaimCard full-replace update from normalized command input."""

    target_id = command_input.get("claim_id")
    parent_study_id: str | None = None
    referenced_dataset_ids: tuple[str, ...] | None = None
    try:
        replacement_card = load_claimcard_update_file(command_input["from_file"])
        parent_study_id = replacement_card["study_id"]
        dataset_ids = replacement_card.get("dataset_ids")
        if dataset_ids:
            referenced_dataset_ids = tuple(dataset_ids)
        if replacement_card["claim_id"] != command_input["claim_id"]:
            raise ValueError(
                "CLI --claim-id must match file claim_id: "
                f"{command_input['claim_id']} != {replacement_card['claim_id']}."
            )
        plan_update_claim_card(replacement_card)
        updated = update_claim_card(replacement_card)
    except (KeyError, TypeError, ValueError) as exc:
        return _build_invalid_payload_result(
            card_family="ClaimCard",
            target_id=target_id,
            message=str(exc),
        )
    except RegistryError as exc:
        error_category, message = translate_gateway_error(
            exc,
            card_family="ClaimCard",
            target_id=target_id,
            parent_study_id=parent_study_id,
            referenced_dataset_ids=referenced_dataset_ids,
        )
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family="ClaimCard",
            target_id=target_id,
            message=message,
            error_category=error_category,
        )
    except Exception:
        return _build_unexpected_bridge_failure(
            card_family="ClaimCard",
            target_id=target_id,
        )

    return build_command_result(
        ok=True,
        operation=_OPERATION_NAME,
        card_family="ClaimCard",
        target_id=updated["claim_id"],
        message="ClaimCard update replaced the canonical ClaimCard record.",
    )


def translate_gateway_error(
    exc: Exception,
    *,
    card_family: CardFamilyName,
    target_id: str | None,
    parent_study_id: str | None = None,
    referenced_dataset_ids: Sequence[str] | None = None,
) -> tuple[CommandErrorCategory, str]:
    """Translate gateway/domain failures into narrow update-command semantics."""

    if card_family == "StudyCard":
        return _translate_studycard_gateway_error(exc, target_id=target_id)
    if card_family == "DatasetCard":
        return _translate_datasetcard_gateway_error(
            exc,
            target_id=target_id,
            parent_study_id=parent_study_id,
        )
    if card_family == "ClaimCard":
        return _translate_claimcard_gateway_error(
            exc,
            target_id=target_id,
            parent_study_id=parent_study_id,
            referenced_dataset_ids=referenced_dataset_ids,
        )
    raise ValueError(f"Unsupported card_family for gateway-error translation: {card_family!r}.")


def handle_update_command(args: object) -> CommandExecutionResult:
    """Handle mapping-based internal `update` dispatch for DatasetCard only."""

    if not isinstance(args, Mapping):
        return _build_invalid_payload_result(
            card_family="DatasetCard",
            target_id=None,
            message="handle_update_command expects a mapping-based internal input.",
        )

    target_id = args.get("dataset_id") if isinstance(args.get("dataset_id"), str) else None
    try:
        normalized_input = normalize_datasetcard_update_input(
            {
                "dataset_id": _require_mapping_value(args, "dataset_id"),
                "from_file": _require_mapping_value(args, "from_file"),
            }
        )
    except ValueError as exc:
        return _build_invalid_payload_result(
            card_family="DatasetCard",
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


def _translate_studycard_gateway_error(
    exc: Exception,
    *,
    target_id: str | None,
) -> tuple[CommandErrorCategory, str]:
    if isinstance(exc, CardNotFoundError):
        if target_id is None:
            return ("missing_reference", "requested StudyCard was not found.")
        return (
            "missing_reference",
            f"requested StudyCard '{target_id}' was not found.",
        )
    if isinstance(exc, InvalidStateTransitionError):
        return (
            "invalid_payload",
            f"StudyCard update rejected invalid StudyCard state: {exc}",
        )
    if isinstance(exc, UpdateLockError):
        return ("registry_failure", str(exc))
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            "StudyCard update rejected an unsupported registry operation or identifier.",
        )
    if isinstance(exc, RegistryError):
        if _looks_like_invalid_study_payload_error(exc):
            return (
                "invalid_payload",
                f"StudyCard update rejected invalid StudyCard data: {exc}",
            )
        return (
            "registry_failure",
            "StudyCard update failed at the registry gateway boundary.",
        )
    return (
        "registry_failure",
        "StudyCard update failed before the registry gateway could complete.",
    )


def _translate_datasetcard_gateway_error(
    exc: Exception,
    *,
    target_id: str | None,
    parent_study_id: str | None,
) -> tuple[CommandErrorCategory, str]:
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
    if isinstance(exc, UpdateLockError):
        return ("registry_failure", str(exc))
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


def _translate_claimcard_gateway_error(
    exc: Exception,
    *,
    target_id: str | None,
    parent_study_id: str | None,
    referenced_dataset_ids: Sequence[str] | None,
) -> tuple[CommandErrorCategory, str]:
    if isinstance(exc, CardNotFoundError):
        if target_id is None:
            return ("missing_reference", "requested ClaimCard was not found.")
        return (
            "missing_reference",
            f"requested ClaimCard '{target_id}' was not found.",
        )
    if isinstance(exc, BrokenReferenceError):
        missing_dataset_ids = _extract_missing_dataset_reference_ids(exc)
        if missing_dataset_ids is not None:
            missing_display = ", ".join(missing_dataset_ids)
            if not missing_display and referenced_dataset_ids is not None:
                missing_display = ", ".join(referenced_dataset_ids)
            if missing_display:
                return (
                    "missing_reference",
                    "ClaimCard update requires referenced DatasetCard(s) to exist before replace: "
                    f"{missing_display}.",
                )
            return (
                "missing_reference",
                "ClaimCard update requires referenced DatasetCard(s) to exist before replace.",
            )
        if parent_study_id is None:
            return (
                "missing_reference",
                "ClaimCard update requires the parent StudyCard to exist before replace.",
            )
        return (
            "missing_reference",
            "ClaimCard update requires the parent StudyCard "
            f"'{parent_study_id}' to exist before replace.",
        )
    if isinstance(exc, UpdateLockError):
        return ("registry_failure", str(exc))
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            "ClaimCard update rejected an unsupported registry operation or identifier.",
        )
    if isinstance(exc, RegistryError):
        if _looks_like_invalid_claim_payload_error(exc):
            return (
                "invalid_payload",
                f"ClaimCard update rejected invalid ClaimCard data: {exc}",
            )
        return (
            "registry_failure",
            "ClaimCard update failed at the registry gateway boundary.",
        )
    return (
        "registry_failure",
        "ClaimCard update failed before the registry gateway could complete.",
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
        message=f"{card_family} update input is invalid: {message}",
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
        message=f"{card_family} update failed unexpectedly inside the internal command bridge.",
        error_category="registry_failure",
    )


def _load_update_file_mapping(
    path: str | Path,
    *,
    card_family: CardFamilyName,
) -> dict[str, object]:
    input_path = Path(path)
    try:
        document = input_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"{card_family} update file was not found: {input_path}.") from exc
    except OSError as exc:
        raise ValueError(f"{card_family} update file could not be read: {input_path}.") from exc

    try:
        parsed = yaml.safe_load(document)
    except yaml.YAMLError as exc:
        raise ValueError(f"{card_family} update file is not valid YAML: {input_path}.") from exc

    if not isinstance(parsed, Mapping):
        raise ValueError(f"{card_family} update file must decode to one mapping: {input_path}.")

    raw_input = dict(parsed)
    non_string_keys = [key for key in raw_input if not isinstance(key, str)]
    if non_string_keys:
        raise ValueError(f"{card_family} update file keys must be strings.")

    return raw_input


def _looks_like_invalid_study_payload_error(exc: RegistryError) -> bool:
    message = str(exc)
    if "filesystem access" in message or "runtime translation" in message:
        return False
    return (
        message.startswith("StudyCard field '")
        or message.startswith("StudyCard payload ")
        or "missing required fields" in message
        or "unexpected fields" in message
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


def _looks_like_invalid_claim_payload_error(exc: RegistryError) -> bool:
    message = str(exc)
    if "filesystem access" in message or "runtime translation" in message:
        return False
    return (
        message.startswith("ClaimCard field '")
        or message.startswith("ClaimCard payload ")
        or "missing required fields" in message
        or "unexpected fields" in message
    )


def _extract_missing_dataset_reference_ids(
    exc: BrokenReferenceError,
) -> tuple[str, ...] | None:
    message = str(exc)
    marker = "DatasetCard(s)"
    if marker not in message:
        return None
    split_marker = "canonical paths: "
    if split_marker not in message:
        return ()
    trailing = message.split(split_marker, 1)[1].rstrip(".")
    values = [value.strip() for value in trailing.split(",") if value.strip()]
    return tuple(values)


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
    "execute_update_claim",
    "execute_update_study",
    "execute_update_dataset",
    "family_name",
    "handle_update_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
    "load_claimcard_update_file",
    "load_studycard_update_file",
    "load_datasetcard_update_file",
    "normalize_claimcard_update_input",
    "normalize_datasetcard_update_input",
    "normalize_studycard_update_input",
    "normalize_update_input",
    "translate_gateway_error",
]
