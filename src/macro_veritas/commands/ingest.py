"""`ingest` command-family bridge for the narrow public StudyCard, DatasetCard, and ClaimCard paths.

Owning domain: Registry Department / 户部 intake boundary.
Implemented now:
- thin public CLI adapter support for `ingest study`
- thin public CLI adapter support for `ingest dataset`
- thin public CLI adapter support for `ingest claim`
- internal StudyCard, DatasetCard, and ClaimCard ingest input normalization
- StudyCard, DatasetCard, and ClaimCard payload preparation against the frozen payload contract
- StudyCard, DatasetCard, and ClaimCard gateway planning + runtime create execution
- command-layer success/failure result translation

Deferred:
- StudyCard, DatasetCard, or ClaimCard update/patch ingest semantics
- broader ingest expansion beyond the narrow public create-only paths
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from macro_veritas.commands.common import (
    build_command_descriptor,
    build_command_payload_descriptor,
    build_command_result,
)
from macro_veritas.registry.errors import (
    BrokenReferenceError,
    CardAlreadyExistsError,
    RegistryError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.gateway import (
    create_claim_card,
    create_dataset_card,
    create_study_card,
    plan_create_claim_card,
    plan_create_dataset_card,
    plan_create_study_card,
)
from macro_veritas.shared.types import (
    CardFamilyName,
    ClaimCardCLIInput,
    ClaimCardIngestInput,
    ClaimCardPayload,
    ClaimCardStatus,
    ClaimReviewReadiness,
    CommandDescriptor,
    CommandErrorCategory,
    CommandExecutionResult,
    CommandFamilyName,
    CommandPayloadDescriptor,
    DatasetAvailabilityStatus,
    DatasetCardCLIInput,
    DatasetCardIngestInput,
    DatasetCardPayload,
    DatasetCardStatus,
    DescriptorSequence,
    StudyCardCLIInput,
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
    "Execute the narrow public StudyCard, DatasetCard, and ClaimCard ingest bridges "
    "while keeping update semantics deferred."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "public StudyCard CLI adapter input",
    "public DatasetCard CLI adapter input",
    "public ClaimCard CLI adapter input",
    "internal StudyCard, DatasetCard, or ClaimCard ingest input",
    "target card-family label",
    "full-card StudyCardPayload, DatasetCardPayload, or ClaimCardPayload prepared from normalized intake input",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "StudyCard, DatasetCard, or ClaimCard create-plan request prepared from the normalized payload",
    "StudyCard, DatasetCard, or ClaimCard runtime create execution through the registry gateway",
    "internal command execution result mapping",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/payload_contracts.md",
    "docs/card_contracts.md",
    "docs/registry_io_boundary.md",
    "docs/gateway_contracts.md",
    "docs/cli_command_contracts.md",
    "docs/ingest_studycard_runtime.md",
    "docs/datasetcard_runtime.md",
    "docs/claimcard_runtime.md",
    "docs/public_ingest_claimcard_cli.md",
    "macro_veritas.governance.departments.registry",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "plan_create_study_card",
    "create_study_card",
    "plan_create_dataset_card",
    "create_dataset_card",
    "plan_create_claim_card",
    "create_claim_card",
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
        gateway_mutations=("plan_create_dataset_card", "create_dataset_card"),
        notes=(
            "Internal DatasetCard ingest normalizes command-facing input before preparing a DatasetCardPayload.",
            "The bridge calls plan_create_dataset_card before create_dataset_card.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="ClaimCard",
        payload_type="ClaimCardPayload",
        usage="prepare_create",
        gateway_reads=(),
        gateway_mutations=("plan_create_claim_card", "create_claim_card"),
        notes=(
            "Internal ClaimCard ingest normalizes command-facing input before preparing a ClaimCardPayload.",
            "The bridge calls plan_create_claim_card before create_claim_card.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "StudyCard update or patch ingest semantics",
    "DatasetCard update or patch ingest semantics",
    "ClaimCard update or patch ingest semantics",
    "identifier allocation beyond caller-provided canonical IDs",
    "broader ingest surfaces such as file-driven batch input",
)
_NON_GOALS: DescriptorSequence = (
    "StudyCard update or patch ingest",
    "DatasetCard update or patch ingest",
    "ClaimCard update or patch ingest",
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
    """Return static metadata for the `ingest` family."""

    return build_command_descriptor(
        family_name=_FAMILY_NAME,
        owning_module=_OWNING_MODULE,
        owning_domain=_OWNING_DOMAIN,
        purpose=_PURPOSE,
        primary_inputs=_PRIMARY_INPUTS,
        primary_outputs=_PRIMARY_OUTPUTS,
        dependency_contracts=_DEPENDENCY_CONTRACTS,
        non_goals=_NON_GOALS,
        public_exposure="public `ingest study`, `ingest dataset`, and `ingest claim` only; update semantics stay non-public",
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


def normalize_datasetcard_ingest_input(
    *,
    dataset_id: str,
    study_id: str,
    status: DatasetCardStatus,
    modality_scope: str | Sequence[str],
    platform_summary: str,
    cohort_summary: str,
    locator_confidence_note: str,
    source_locator: str,
    availability_status: DatasetAvailabilityStatus,
    accession_id: str | None = None,
    availability_note: str | None = None,
    artifact_locator: str | None = None,
) -> DatasetCardIngestInput:
    """Normalize command-facing DatasetCard ingest input into a small internal mapping."""

    normalized: DatasetCardIngestInput = {
        "dataset_id": _require_command_string(dataset_id, field_name="dataset_id"),
        "study_id": _require_command_string(study_id, field_name="study_id"),
        "status": _require_command_string(status, field_name="status"),
        "modality_scopes": _normalize_scope_input(
            modality_scope,
            field_name="modality_scope",
        ),
        "platform_summary": _require_command_string(
            platform_summary,
            field_name="platform_summary",
        ),
        "cohort_summary": _require_command_string(
            cohort_summary,
            field_name="cohort_summary",
        ),
        "locator_confidence_note": _require_command_string(
            locator_confidence_note,
            field_name="locator_confidence_note",
        ),
        "source_locator": _require_command_string(
            source_locator,
            field_name="source_locator",
        ),
        "availability_status": _require_command_string(
            availability_status,
            field_name="availability_status",
        ),
    }
    if accession_id is not None:
        normalized["accession_id"] = _require_command_string(
            accession_id,
            field_name="accession_id",
        )
    if availability_note is not None:
        normalized["availability_note"] = _require_command_string(
            availability_note,
            field_name="availability_note",
        )
    if artifact_locator is not None:
        normalized["artifact_locator"] = _require_command_string(
            artifact_locator,
            field_name="artifact_locator",
        )
    return normalized


def normalize_claimcard_ingest_input(
    *,
    claim_id: str,
    study_id: str,
    claim_text: str,
    claim_type: str,
    provenance_pointer: str,
    status: ClaimCardStatus,
    review_readiness: ClaimReviewReadiness,
    created_from: str,
    dataset_ids: str | Sequence[str] | None = None,
    claim_summary_handle: str | None = None,
) -> ClaimCardIngestInput:
    """Normalize command-facing ClaimCard ingest input into a small internal mapping."""

    normalized: ClaimCardIngestInput = {
        "claim_id": _require_command_string(claim_id, field_name="claim_id"),
        "study_id": _require_command_string(study_id, field_name="study_id"),
        "claim_text": _require_command_string(claim_text, field_name="claim_text"),
        "claim_type": _require_command_string(claim_type, field_name="claim_type"),
        "provenance_pointer": _require_command_string(
            provenance_pointer,
            field_name="provenance_pointer",
        ),
        "status": _require_command_string(status, field_name="status"),
        "review_readiness": _require_command_string(
            review_readiness,
            field_name="review_readiness",
        ),
        "created_from": _require_command_string(
            created_from,
            field_name="created_from",
        ),
    }
    if dataset_ids is not None:
        normalized["dataset_ids"] = _normalize_scope_input(
            dataset_ids,
            field_name="dataset_ids",
        )
    if claim_summary_handle is not None:
        normalized["claim_summary_handle"] = _require_command_string(
            claim_summary_handle,
            field_name="claim_summary_handle",
        )
    return normalized


def normalize_public_studycard_cli_input(
    command_input: StudyCardCLIInput,
) -> StudyCardIngestInput:
    """Convert the public CLI StudyCard mapping into normalized ingest input."""

    return normalize_studycard_ingest_input(
        study_id=command_input["study_id"],
        citation_handle=command_input["citation_handle"],
        tumor_type=command_input["tumor_type"],
        therapy_scope=command_input["therapy_scope"],
        relevance_scope=command_input["relevance_scope"],
        screening_decision=command_input["screening_decision"],
        status=command_input["status"],
        created_from=command_input["created_from"],
        screening_note=command_input.get("screening_note"),
        source_artifact=command_input.get("source_artifact"),
    )


def normalize_public_datasetcard_cli_input(
    command_input: DatasetCardCLIInput,
) -> DatasetCardIngestInput:
    """Convert the public CLI DatasetCard mapping into normalized ingest input."""

    return normalize_datasetcard_ingest_input(
        dataset_id=command_input["dataset_id"],
        study_id=command_input["study_id"],
        status=command_input["status"],
        modality_scope=command_input["modality_scope"],
        platform_summary=command_input["platform_summary"],
        cohort_summary=command_input["cohort_summary"],
        locator_confidence_note=command_input["locator_confidence_note"],
        source_locator=command_input["source_locator"],
        availability_status=command_input["availability_status"],
        accession_id=command_input.get("accession_id"),
        availability_note=command_input.get("availability_note"),
        artifact_locator=command_input.get("artifact_locator"),
    )


def normalize_public_claimcard_cli_input(
    command_input: ClaimCardCLIInput,
) -> ClaimCardIngestInput:
    """Convert the public CLI ClaimCard mapping into normalized ingest input."""

    return normalize_claimcard_ingest_input(
        claim_id=command_input["claim_id"],
        study_id=command_input["study_id"],
        claim_text=command_input["claim_text"],
        claim_type=command_input["claim_type"],
        provenance_pointer=command_input["provenance_pointer"],
        status=command_input["status"],
        review_readiness=command_input["review_readiness"],
        created_from=command_input["created_from"],
        dataset_ids=command_input.get("dataset_ids"),
        claim_summary_handle=command_input.get("claim_summary_handle"),
    )


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


def prepare_datasetcard_ingest_payload(
    command_input: DatasetCardIngestInput,
) -> DatasetCardPayload:
    """Prepare one `DatasetCardPayload` from normalized internal ingest input."""

    payload: DatasetCardPayload = {
        "dataset_id": command_input["dataset_id"],
        "study_id": command_input["study_id"],
        "source_locator": command_input["source_locator"],
        "availability_status": command_input["availability_status"],
        "modality_scope_tags": list(command_input["modality_scopes"]),
        "cohort_summary": command_input["cohort_summary"],
        "platform_summary": command_input["platform_summary"],
        "status": command_input["status"],
        "locator_confidence_note": command_input["locator_confidence_note"],
    }
    if "accession_id" in command_input:
        payload["accession_id"] = command_input["accession_id"]
    if "artifact_locator" in command_input:
        payload["artifact_locator"] = command_input["artifact_locator"]
    if "availability_note" in command_input:
        payload["availability_note"] = command_input["availability_note"]
    return payload


def prepare_claimcard_ingest_payload(command_input: ClaimCardIngestInput) -> ClaimCardPayload:
    """Prepare one `ClaimCardPayload` from normalized internal ingest input."""

    payload: ClaimCardPayload = {
        "claim_id": command_input["claim_id"],
        "study_id": command_input["study_id"],
        "claim_text": command_input["claim_text"],
        "claim_type": command_input["claim_type"],
        "provenance_pointer": command_input["provenance_pointer"],
        "status": command_input["status"],
        "review_readiness": command_input["review_readiness"],
        "created_from_note": command_input["created_from"],
    }
    if "dataset_ids" in command_input:
        payload["dataset_ids"] = list(command_input["dataset_ids"])
    if "claim_summary_handle" in command_input:
        payload["claim_summary_handle"] = command_input["claim_summary_handle"]
    return payload


def translate_gateway_error(
    exc: Exception,
    *,
    card_family: CardFamilyName,
    parent_study_id: str | None = None,
    referenced_dataset_ids: Sequence[str] | None = None,
) -> tuple[CommandErrorCategory, str]:
    """Translate gateway/domain failures into the narrow command result semantics."""

    if card_family == "StudyCard":
        return _translate_studycard_gateway_error(exc)
    if card_family == "DatasetCard":
        return _translate_datasetcard_gateway_error(
            exc,
            parent_study_id=parent_study_id,
        )
    if card_family == "ClaimCard":
        return _translate_claimcard_gateway_error(
            exc,
            parent_study_id=parent_study_id,
            referenced_dataset_ids=referenced_dataset_ids,
        )
    raise ValueError(f"Unsupported card_family for gateway-error translation: {card_family!r}.")


def execute_studycard_ingest_input(
    command_input: StudyCardIngestInput,
) -> CommandExecutionResult:
    """Execute StudyCard ingest from normalized internal command input."""

    target_id = command_input.get("study_id")
    try:
        payload = prepare_studycard_ingest_payload(command_input)
        plan_create_study_card(payload)
        created = create_study_card(payload)
    except (KeyError, TypeError, ValueError) as exc:
        return _build_invalid_payload_result(
            card_family="StudyCard",
            target_id=target_id,
            message=str(exc),
        )
    except RegistryError as exc:
        error_category, message = translate_gateway_error(exc, card_family="StudyCard")
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
        target_id=created["study_id"],
        message="StudyCard ingest created the canonical StudyCard record.",
    )


def execute_datasetcard_ingest_input(
    command_input: DatasetCardIngestInput,
) -> CommandExecutionResult:
    """Execute DatasetCard ingest from normalized internal command input."""

    target_id = command_input.get("dataset_id")
    parent_study_id = command_input.get("study_id")
    try:
        payload = prepare_datasetcard_ingest_payload(command_input)
        plan_create_dataset_card(payload)
        created = create_dataset_card(payload)
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
        target_id=created["dataset_id"],
        message="DatasetCard ingest created the canonical DatasetCard record.",
    )


def execute_claimcard_ingest_input(
    command_input: ClaimCardIngestInput,
) -> CommandExecutionResult:
    """Execute ClaimCard ingest from normalized internal command input."""

    target_id = command_input.get("claim_id")
    parent_study_id = command_input.get("study_id")
    referenced_dataset_ids = command_input.get("dataset_ids")
    try:
        payload = prepare_claimcard_ingest_payload(command_input)
        plan_create_claim_card(payload)
        created = create_claim_card(payload)
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
        target_id=created["claim_id"],
        message="ClaimCard ingest created the canonical ClaimCard record.",
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
        normalized_input = normalize_studycard_ingest_input(
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
    except ValueError as exc:
        return _build_invalid_payload_result(
            card_family="StudyCard",
            target_id=target_id,
            message=str(exc),
        )
    return execute_studycard_ingest_input(normalized_input)


def execute_datasetcard_ingest(
    *,
    dataset_id: str,
    study_id: str,
    status: DatasetCardStatus,
    modality_scope: str | Sequence[str],
    platform_summary: str,
    cohort_summary: str,
    locator_confidence_note: str,
    source_locator: str,
    availability_status: DatasetAvailabilityStatus,
    accession_id: str | None = None,
    availability_note: str | None = None,
    artifact_locator: str | None = None,
) -> CommandExecutionResult:
    """Execute the internal DatasetCard ingest bridge through the real gateway path."""

    target_id = dataset_id if isinstance(dataset_id, str) else None
    try:
        normalized_input = normalize_datasetcard_ingest_input(
            dataset_id=dataset_id,
            study_id=study_id,
            status=status,
            modality_scope=modality_scope,
            platform_summary=platform_summary,
            cohort_summary=cohort_summary,
            locator_confidence_note=locator_confidence_note,
            source_locator=source_locator,
            availability_status=availability_status,
            accession_id=accession_id,
            availability_note=availability_note,
            artifact_locator=artifact_locator,
        )
    except ValueError as exc:
        return _build_invalid_payload_result(
            card_family="DatasetCard",
            target_id=target_id,
            message=str(exc),
        )
    return execute_datasetcard_ingest_input(normalized_input)


def execute_claimcard_ingest(
    *,
    claim_id: str,
    study_id: str,
    claim_text: str,
    claim_type: str,
    provenance_pointer: str,
    status: ClaimCardStatus,
    review_readiness: ClaimReviewReadiness,
    created_from: str,
    dataset_ids: str | Sequence[str] | None = None,
    claim_summary_handle: str | None = None,
) -> CommandExecutionResult:
    """Execute the internal ClaimCard ingest bridge through the real gateway path."""

    target_id = claim_id if isinstance(claim_id, str) else None
    try:
        normalized_input = normalize_claimcard_ingest_input(
            claim_id=claim_id,
            study_id=study_id,
            claim_text=claim_text,
            claim_type=claim_type,
            provenance_pointer=provenance_pointer,
            status=status,
            review_readiness=review_readiness,
            created_from=created_from,
            dataset_ids=dataset_ids,
            claim_summary_handle=claim_summary_handle,
        )
    except ValueError as exc:
        return _build_invalid_payload_result(
            card_family="ClaimCard",
            target_id=target_id,
            message=str(exc),
        )
    return execute_claimcard_ingest_input(normalized_input)


def handle_ingest_command(args: object) -> CommandExecutionResult:
    """Handle mapping-based internal `ingest` dispatch for StudyCard, DatasetCard, and ClaimCard."""

    if not isinstance(args, Mapping):
        return _build_invalid_payload_result(
            card_family="StudyCard",
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

    target_id = _mapping_target_id(args, card_family)
    if card_family == "StudyCard":
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
            return _build_invalid_payload_result(
                card_family="StudyCard",
                target_id=target_id,
                message=str(exc),
            )

    if card_family == "DatasetCard":
        try:
            return execute_datasetcard_ingest(
                dataset_id=_require_mapping_value(args, "dataset_id"),
                study_id=_require_mapping_value(args, "study_id"),
                status=_require_mapping_value(args, "status"),
                modality_scope=_require_mapping_scope_value(args, "modality_scope"),
                platform_summary=_require_mapping_value(args, "platform_summary"),
                cohort_summary=_require_mapping_value(args, "cohort_summary"),
                locator_confidence_note=_require_mapping_value(args, "locator_confidence_note"),
                source_locator=_require_mapping_value(args, "source_locator"),
                availability_status=_require_mapping_value(args, "availability_status"),
                accession_id=_optional_mapping_string(args, "accession_id"),
                availability_note=_optional_mapping_string(args, "availability_note"),
                artifact_locator=_optional_mapping_string(args, "artifact_locator"),
            )
        except ValueError as exc:
            return _build_invalid_payload_result(
                card_family="DatasetCard",
                target_id=target_id,
                message=str(exc),
            )

    if card_family == "ClaimCard":
        try:
            return execute_claimcard_ingest(
                claim_id=_require_mapping_value(args, "claim_id"),
                study_id=_require_mapping_value(args, "study_id"),
                claim_text=_require_mapping_value(args, "claim_text"),
                claim_type=_require_mapping_value(args, "claim_type"),
                provenance_pointer=_require_mapping_value(args, "provenance_pointer"),
                status=_require_mapping_value(args, "status"),
                review_readiness=_require_mapping_value(args, "review_readiness"),
                created_from=_require_mapping_value(args, "created_from"),
                dataset_ids=_optional_mapping_scope_value(args, "dataset_ids"),
                claim_summary_handle=_optional_mapping_string(args, "claim_summary_handle"),
            )
        except ValueError as exc:
            return _build_invalid_payload_result(
                card_family="ClaimCard",
                target_id=target_id,
                message=str(exc),
            )

    return build_command_result(
        ok=False,
        operation=_OPERATION_NAME,
        card_family=card_family,
        target_id=target_id,
        message=(
            "Internal ingest runtime is implemented only for StudyCard, DatasetCard, "
            f"and ClaimCard, not {card_family}."
        ),
        error_category="unsupported_operation",
    )


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the registry-gateway operations this family uses or reserves."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Describe the frozen payload families touched by `ingest`."""

    return _PAYLOAD_CONTRACTS


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `ingest` capabilities beyond the public Study/Dataset/Claim bridges."""

    return _DEFERRED_CAPABILITIES


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
        message=f"{card_family} ingest input is invalid: {message}",
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
        message=f"{card_family} ingest failed unexpectedly inside the internal command bridge.",
        error_category="registry_failure",
    )


def _translate_studycard_gateway_error(
    exc: Exception,
) -> tuple[CommandErrorCategory, str]:
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
        if _looks_like_invalid_study_payload_error(exc):
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


def _translate_datasetcard_gateway_error(
    exc: Exception,
    *,
    parent_study_id: str | None,
) -> tuple[CommandErrorCategory, str]:
    if isinstance(exc, CardAlreadyExistsError):
        return (
            "duplicate_target",
            "DatasetCard ingest did not write because the canonical DatasetCard already exists.",
        )
    if isinstance(exc, BrokenReferenceError):
        if parent_study_id is None:
            return (
                "missing_reference",
                "DatasetCard ingest requires the parent StudyCard to exist before create.",
            )
        return (
            "missing_reference",
            f"DatasetCard ingest requires the parent StudyCard '{parent_study_id}' to exist before create.",
        )
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            "DatasetCard ingest rejected an unsupported registry operation or identifier.",
        )
    if isinstance(exc, RegistryError):
        if _looks_like_invalid_dataset_payload_error(exc):
            return (
                "invalid_payload",
                f"DatasetCard ingest rejected invalid DatasetCard data: {exc}",
            )
        return (
            "registry_failure",
            "DatasetCard ingest failed at the registry gateway boundary.",
        )
    return (
        "registry_failure",
        "DatasetCard ingest failed before the registry gateway could complete.",
    )


def _translate_claimcard_gateway_error(
    exc: Exception,
    *,
    parent_study_id: str | None,
    referenced_dataset_ids: Sequence[str] | None,
) -> tuple[CommandErrorCategory, str]:
    if isinstance(exc, CardAlreadyExistsError):
        return (
            "duplicate_target",
            "ClaimCard ingest did not write because the canonical ClaimCard already exists.",
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
                    "ClaimCard ingest requires referenced DatasetCard(s) to exist before create: "
                    f"{missing_display}.",
                )
            return (
                "missing_reference",
                "ClaimCard ingest requires referenced DatasetCard(s) to exist before create.",
            )
        if parent_study_id is None:
            return (
                "missing_reference",
                "ClaimCard ingest requires the parent StudyCard to exist before create.",
            )
        return (
            "missing_reference",
            f"ClaimCard ingest requires the parent StudyCard '{parent_study_id}' to exist before create.",
        )
    if isinstance(exc, UnsupportedRegistryOperationError):
        return (
            "unsupported_operation",
            "ClaimCard ingest rejected an unsupported registry operation or identifier.",
        )
    if isinstance(exc, RegistryError):
        if _looks_like_invalid_claim_payload_error(exc):
            return (
                "invalid_payload",
                f"ClaimCard ingest rejected invalid ClaimCard data: {exc}",
            )
        return (
            "registry_failure",
            "ClaimCard ingest failed at the registry gateway boundary.",
        )
    return (
        "registry_failure",
        "ClaimCard ingest failed before the registry gateway could complete.",
    )


def _looks_like_unsafe_study_id_error(exc: RegistryError) -> bool:
    message = str(exc)
    if "field 'study_id'" not in message and "lookup ID" not in message:
        return False
    return any(fragment in message for fragment in _UNSAFE_STUDY_ID_MESSAGE_FRAGMENTS)


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


def _mapping_target_id(
    args: Mapping[str, object],
    card_family: CardFamilyName,
) -> str | None:
    field_name = {
        "StudyCard": "study_id",
        "DatasetCard": "dataset_id",
        "ClaimCard": "claim_id",
    }[card_family]
    value = args.get(field_name)
    return value if isinstance(value, str) else None


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


def _optional_mapping_scope_value(
    args: Mapping[str, object],
    field_name: str,
) -> str | Sequence[str] | None:
    if field_name not in args or args[field_name] is None:
        return None
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
    "execute_claimcard_ingest",
    "execute_claimcard_ingest_input",
    "execute_datasetcard_ingest",
    "execute_datasetcard_ingest_input",
    "execute_studycard_ingest",
    "execute_studycard_ingest_input",
    "family_name",
    "handle_ingest_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
    "normalize_claimcard_ingest_input",
    "normalize_datasetcard_ingest_input",
    "normalize_public_claimcard_cli_input",
    "normalize_public_datasetcard_cli_input",
    "normalize_public_studycard_cli_input",
    "normalize_studycard_ingest_input",
    "prepare_claimcard_ingest_payload",
    "prepare_datasetcard_ingest_payload",
    "prepare_studycard_ingest_payload",
    "translate_gateway_error",
]
