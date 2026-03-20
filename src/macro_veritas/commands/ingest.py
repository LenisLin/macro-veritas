"""Internal `ingest` command-family bridge for the first StudyCard runtime path.

Owning domain: Registry Department / 户部 intake boundary.
Implemented now:
- internal StudyCard ingest input normalization
- StudyCard payload preparation against the frozen payload contract
- StudyCard gateway planning + runtime create execution
- command-layer success/failure result translation

Deferred:
- public CLI wiring
- DatasetCard ingest runtime
- ClaimCard ingest runtime
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from macro_veritas.commands.common import (
    build_command_descriptor,
    build_command_payload_descriptor,
    build_command_result,
)
from macro_veritas.registry.errors import (
    CardAlreadyExistsError,
    RegistryError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.gateway import create_study_card, plan_create_study_card
from macro_veritas.shared.types import (
    CardFamilyName,
    CommandDescriptor,
    CommandErrorCategory,
    CommandExecutionResult,
    CommandFamilyName,
    CommandPayloadDescriptor,
    DescriptorSequence,
    StudyCardIngestInput,
    StudyCardPayload,
    StudyCardStatus,
    StudyScreeningDecision,
)

_FAMILY_NAME: CommandFamilyName = "ingest"
_OPERATION_NAME = "ingest"
_OWNING_MODULE = "macro_veritas.commands.ingest"
_OWNING_DOMAIN = "Registry Department / 户部"
_PURPOSE = (
    "Execute the first internal StudyCard ingest bridge while keeping "
    "DatasetCard and ClaimCard ingest non-runtime and non-public."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "internal StudyCard ingest input",
    "target card-family label",
    "full-card StudyCardPayload prepared from normalized intake input",
    "provenance note",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "StudyCard create-plan request prepared from the normalized payload",
    "StudyCard runtime create execution through the registry gateway",
    "internal command execution result mapping",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/payload_contracts.md",
    "docs/card_contracts.md",
    "docs/registry_io_boundary.md",
    "docs/gateway_contracts.md",
    "docs/ingest_studycard_runtime.md",
    "macro_veritas.governance.departments.registry",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "plan_create_study_card",
    "create_study_card",
    "plan_create_dataset_card",
    "plan_create_claim_card",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = (
    build_command_payload_descriptor(
        card_family="StudyCard",
        payload_type="StudyCardPayload",
        usage="prepare_create",
        gateway_reads=(),
        gateway_mutations=("plan_create_study_card", "create_study_card"),
        notes=(
            "Internal StudyCard ingest normalizes command-facing input before preparing a StudyCardPayload.",
            "The bridge calls plan_create_study_card before create_study_card.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="DatasetCard",
        payload_type="DatasetCardPayload",
        usage="prepare_create",
        gateway_reads=(),
        gateway_mutations=("plan_create_dataset_card",),
        notes=(
            "DatasetCard ingest remains skeleton-only in this milestone.",
            "Create planning accepts a full-card payload only.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="ClaimCard",
        payload_type="ClaimCardPayload",
        usage="prepare_create",
        gateway_reads=(),
        gateway_mutations=("plan_create_claim_card",),
        notes=(
            "ClaimCard ingest remains skeleton-only in this milestone.",
            "Create planning accepts a full-card payload only.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "public CLI exposure",
    "public parser flag design",
    "DatasetCard ingest runtime",
    "ClaimCard ingest runtime",
    "identifier allocation beyond caller-provided canonical IDs",
)
_NON_GOALS: DescriptorSequence = (
    "public CLI registration",
    "DatasetCard ingest execution",
    "ClaimCard ingest execution",
    "scientific logic",
    "evidence grading",
    "CellVoyager integration",
)
_CARD_FAMILY_LABELS: tuple[CardFamilyName, ...] = (
    "StudyCard",
    "DatasetCard",
    "ClaimCard",
)
_UNSAFE_STUDY_ID_MESSAGE_FRAGMENTS: tuple[str, ...] = (
    "must be a canonical identifier, not a path",
    "must not contain surrounding whitespace",
    "must not contain NUL bytes",
)


def family_name() -> CommandFamilyName:
    """Return the reserved command-family label for this module."""

    return _FAMILY_NAME


def describe_command_family() -> CommandDescriptor:
    """Return static metadata for the internal `ingest` family."""

    return build_command_descriptor(
        family_name=_FAMILY_NAME,
        owning_module=_OWNING_MODULE,
        owning_domain=_OWNING_DOMAIN,
        purpose=_PURPOSE,
        primary_inputs=_PRIMARY_INPUTS,
        primary_outputs=_PRIMARY_OUTPUTS,
        dependency_contracts=_DEPENDENCY_CONTRACTS,
        non_goals=_NON_GOALS,
    )


def build_parser(subparsers_or_parser: object) -> None:
    """Reserve the future parser-builder hook for the internal `ingest` family."""

    del subparsers_or_parser
    return None


def normalize_studycard_ingest_input(
    *,
    study_id: str,
    citation_handle: str,
    tumor_type: str | Sequence[str],
    therapy_scope: str | Sequence[str],
    relevance_scope: str | Sequence[str],
    screening_decision: StudyScreeningDecision,
    status: StudyCardStatus,
    created_from: str,
    screening_note: str | None = None,
    source_artifact: str | None = None,
) -> StudyCardIngestInput:
    """Normalize command-facing StudyCard ingest input into a small internal mapping."""

    normalized: StudyCardIngestInput = {
        "study_id": _require_command_string(study_id, field_name="study_id"),
        "citation_handle": _require_command_string(
            citation_handle,
            field_name="citation_handle",
        ),
        "tumor_types": _normalize_scope_input(tumor_type, field_name="tumor_type"),
        "therapy_scopes": _normalize_scope_input(
            therapy_scope,
            field_name="therapy_scope",
        ),
        "relevance_scopes": _normalize_scope_input(
            relevance_scope,
            field_name="relevance_scope",
        ),
        "screening_decision": _require_command_string(
            screening_decision,
            field_name="screening_decision",
        ),
        "status": _require_command_string(status, field_name="status"),
        "created_from": _require_command_string(
            created_from,
            field_name="created_from",
        ),
    }
    if screening_note is not None:
        normalized["screening_note"] = _require_command_string(
            screening_note,
            field_name="screening_note",
        )
    if source_artifact is not None:
        normalized["source_artifact"] = _require_command_string(
            source_artifact,
            field_name="source_artifact",
        )
    return normalized


def prepare_studycard_ingest_payload(command_input: StudyCardIngestInput) -> StudyCardPayload:
    """Prepare one `StudyCardPayload` from normalized internal ingest input."""

    payload: StudyCardPayload = {
        "study_id": command_input["study_id"],
        "citation_handle": command_input["citation_handle"],
        "tumor_scope_tags": list(command_input["tumor_types"]),
        "therapy_scope_tags": list(command_input["therapy_scopes"]),
        "relevance_scope_tags": list(command_input["relevance_scopes"]),
        "screening_decision": command_input["screening_decision"],
        "status": command_input["status"],
        "created_from_note": command_input["created_from"],
    }
    if "screening_note" in command_input:
        payload["screening_note"] = command_input["screening_note"]
    if "source_artifact" in command_input:
        payload["source_artifact_locator"] = command_input["source_artifact"]
    return payload


def translate_gateway_error(exc: Exception) -> tuple[CommandErrorCategory, str]:
    """Translate gateway/domain failures into the narrow command result semantics."""

    if isinstance(exc, CardAlreadyExistsError):
        return (
            "duplicate_target",
            "StudyCard ingest did not write because the canonical StudyCard already exists.",
        )
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            "StudyCard ingest rejected an unsupported registry operation or identifier.",
        )
    if isinstance(exc, RegistryError):
        if _looks_like_unsafe_study_id_error(exc):
            return (
                "unsupported_operation",
                "StudyCard ingest rejected an unsafe canonical study identifier.",
            )
        if _looks_like_invalid_payload_error(exc):
            return (
                "invalid_payload",
                f"StudyCard ingest rejected invalid StudyCard data: {exc}",
            )
        return (
            "registry_failure",
            "StudyCard ingest failed at the registry gateway boundary.",
        )
    return (
        "registry_failure",
        "StudyCard ingest failed before the registry gateway could complete.",
    )


def execute_studycard_ingest(
    *,
    study_id: str,
    citation_handle: str,
    tumor_type: str | Sequence[str],
    therapy_scope: str | Sequence[str],
    relevance_scope: str | Sequence[str],
    screening_decision: StudyScreeningDecision,
    status: StudyCardStatus,
    created_from: str,
    screening_note: str | None = None,
    source_artifact: str | None = None,
) -> CommandExecutionResult:
    """Execute the internal StudyCard ingest bridge through the real gateway path."""

    target_id = study_id if isinstance(study_id, str) else None
    try:
        command_input = normalize_studycard_ingest_input(
            study_id=study_id,
            citation_handle=citation_handle,
            tumor_type=tumor_type,
            therapy_scope=therapy_scope,
            relevance_scope=relevance_scope,
            screening_decision=screening_decision,
            status=status,
            created_from=created_from,
            screening_note=screening_note,
            source_artifact=source_artifact,
        )
        payload = prepare_studycard_ingest_payload(command_input)
        plan_create_study_card(payload)
        created = create_study_card(payload)
    except ValueError as exc:
        return _build_invalid_payload_result(target_id=target_id, message=str(exc))
    except RegistryError as exc:
        error_category, message = translate_gateway_error(exc)
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family="StudyCard",
            target_id=target_id,
            message=message,
            error_category=error_category,
        )
    except Exception:
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family="StudyCard",
            target_id=target_id,
            message="StudyCard ingest failed unexpectedly inside the internal command bridge.",
            error_category="registry_failure",
        )

    return build_command_result(
        ok=True,
        operation=_OPERATION_NAME,
        card_family="StudyCard",
        target_id=created["study_id"],
        message="StudyCard ingest created the canonical StudyCard record.",
    )


def handle_ingest_command(args: object) -> CommandExecutionResult:
    """Handle internal `ingest` dispatch without exposing any public CLI surface."""

    if not isinstance(args, Mapping):
        return _build_invalid_payload_result(
            target_id=None,
            message="handle_ingest_command expects a mapping-based internal input.",
        )

    raw_card_family = args.get("card_family")
    if raw_card_family is None:
        card_family: CardFamilyName = "StudyCard"
    elif raw_card_family in _CARD_FAMILY_LABELS:
        card_family = raw_card_family
    else:
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family="StudyCard",
            target_id=None,
            message=f"Unsupported internal ingest card family: {raw_card_family!r}.",
            error_category="unsupported_operation",
        )
    target_id = args.get("study_id") if isinstance(args.get("study_id"), str) else None
    if card_family != "StudyCard":
        return build_command_result(
            ok=False,
            operation=_OPERATION_NAME,
            card_family=card_family,
            target_id=target_id,
            message=f"Internal ingest runtime is implemented only for StudyCard, not {card_family}.",
            error_category="unsupported_operation",
        )

    try:
        return execute_studycard_ingest(
            study_id=_require_mapping_value(args, "study_id"),
            citation_handle=_require_mapping_value(args, "citation_handle"),
            tumor_type=_require_mapping_scope_value(args, "tumor_type"),
            therapy_scope=_require_mapping_scope_value(args, "therapy_scope"),
            relevance_scope=_require_mapping_scope_value(args, "relevance_scope"),
            screening_decision=_require_mapping_value(args, "screening_decision"),
            status=_require_mapping_value(args, "status"),
            created_from=_require_mapping_value(args, "created_from"),
            screening_note=_optional_mapping_string(args, "screening_note"),
            source_artifact=_optional_mapping_string(args, "source_artifact"),
        )
    except ValueError as exc:
        return _build_invalid_payload_result(target_id=target_id, message=str(exc))


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the registry-gateway operations this family uses or reserves."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Describe the frozen payload families touched by `ingest`."""

    return _PAYLOAD_CONTRACTS


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `ingest` capabilities beyond the StudyCard bridge."""

    return _DEFERRED_CAPABILITIES


def _build_invalid_payload_result(
    *,
    target_id: str | None,
    message: str,
) -> CommandExecutionResult:
    return build_command_result(
        ok=False,
        operation=_OPERATION_NAME,
        card_family="StudyCard",
        target_id=target_id,
        message=f"StudyCard ingest input is invalid: {message}",
        error_category="invalid_payload",
    )


def _looks_like_unsafe_study_id_error(exc: RegistryError) -> bool:
    message = str(exc)
    if "field 'study_id'" not in message and "lookup ID" not in message:
        return False
    return any(fragment in message for fragment in _UNSAFE_STUDY_ID_MESSAGE_FRAGMENTS)


def _looks_like_invalid_payload_error(exc: RegistryError) -> bool:
    message = str(exc)
    if "filesystem access" in message or "runtime translation" in message:
        return False
    return (
        message.startswith("StudyCard field '")
        or message.startswith("StudyCard payload ")
        or "missing required fields" in message
        or "unexpected fields" in message
    )


def _require_command_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Field '{field_name}' must be a string.")
    return value


def _normalize_scope_input(
    value: str | Sequence[str],
    *,
    field_name: str,
) -> list[str]:
    if isinstance(value, str):
        return [value]
    if not isinstance(value, (list, tuple)):
        raise ValueError(
            f"Field '{field_name}' must be a string or a list/tuple of strings."
        )
    normalized_items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(
                f"Field '{field_name}' must contain only strings when given as a sequence."
            )
        normalized_items.append(item)
    return normalized_items


def _require_mapping_value(args: Mapping[str, object], field_name: str) -> str:
    if field_name not in args:
        raise ValueError(f"Field '{field_name}' is required.")
    return _require_command_string(args[field_name], field_name=field_name)


def _require_mapping_scope_value(
    args: Mapping[str, object],
    field_name: str,
) -> str | Sequence[str]:
    if field_name not in args:
        raise ValueError(f"Field '{field_name}' is required.")
    value = args[field_name]
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return value
    raise ValueError(
        f"Field '{field_name}' must be a string or a list/tuple of strings."
    )


def _optional_mapping_string(
    args: Mapping[str, object],
    field_name: str,
) -> str | None:
    if field_name not in args or args[field_name] is None:
        return None
    return _require_command_string(args[field_name], field_name=field_name)


__all__ = [
    "build_parser",
    "describe_command_family",
    "describe_payload_contracts",
    "execute_studycard_ingest",
    "family_name",
    "handle_ingest_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
    "normalize_studycard_ingest_input",
    "prepare_studycard_ingest_payload",
    "translate_gateway_error",
]
