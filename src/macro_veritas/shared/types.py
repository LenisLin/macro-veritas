"""Lightweight shared descriptor and payload types for the frozen MVP boundary.

These aliases and TypedDicts keep documentation-oriented signatures readable
across the governance, command, and registry modules while freezing the
first-slice payload contract between internal command handlers and the
registry gateway.

They do not define scientific schemas, validators, persistence models, or
broad serializer behavior. The implemented StudyCard, DatasetCard, and
ClaimCard runtime slices reuse these payload shapes directly.
Boundary docs:
docs/governance_spec.md, docs/module_map.md, docs/card_contracts.md,
docs/payload_contracts.md, docs/gateway_contracts.md,
docs/cli_command_contracts.md, and docs/constraints.md.
"""

from __future__ import annotations

from typing import Literal, Mapping, Sequence, TypeAlias, TypedDict

ContractCategoryName = Literal[
    "identity",
    "provenance",
    "status",
    "ownership / producer",
    "artifact location / persistence",
]

ObjectFamilyName = Literal[
    "StudyCard",
    "DatasetCard",
    "ClaimCard",
    "MethodCard",
    "ReanalysisBundle",
    "EvidenceCard",
    "AuditRecord",
]

CardFamilyName = Literal[
    "StudyCard",
    "DatasetCard",
    "ClaimCard",
]

AuditOutcomeName = Literal["pass", "return", "escalate"]

StudyCardStatus = Literal["draft", "registered", "closed"]
DatasetCardStatus = Literal["identified", "registered", "bound", "retired"]
ClaimCardStatus = Literal["captured", "scoped", "ready", "closed"]
StudyScreeningDecision = Literal["pending", "include", "exclude"]
DatasetAvailabilityStatus = Literal["unknown", "open", "restricted", "unavailable"]
ClaimReviewReadiness = Literal["needs_scope", "reviewable", "execution_candidate"]
CommandFamilyName = Literal[
    "ingest",
    "update",
    "show",
    "list",
    "delete",
    "bind",
    "extract",
    "audit",
    "review",
    "run",
    "grade",
]

ReservedCLIFamilyName = Literal[
    "ingest",
    "update",
    "show",
    "list",
    "delete",
    "bind",
    "extract",
    "audit",
    "review",
    "run",
    "grade",
]
CommandPayloadUsage = Literal[
    "prepare_create",
    "prepare_update",
    "prepare_create_or_update",
    "read_only",
]
CommandErrorCategory = Literal[
    "duplicate_target",
    "dependency_exists",
    "missing_reference",
    "invalid_payload",
    "unsupported_operation",
    "registry_failure",
]

DepartmentName = Literal[
    "personnel",
    "registry",
    "standards",
    "operations",
    "infrastructure",
    "review",
]

AHeaderLaneName = Literal["mandate", "contracts", "oversight"]
GatewayReadMode = Literal["get_by_id", "exists_by_id", "list_by_family"]
GatewayOperationKind = Literal[
    "get_by_id",
    "exists_by_id",
    "list_by_family",
    "plan_create",
    "plan_update",
]
MutationOperationKind = Literal["create", "update"]
MutationInputRequirement = Literal["full_card_payload"]
MutationExecutionState = Literal["planned_only"]

OfficeName: TypeAlias = str
FunctionName: TypeAlias = str
CardFieldName: TypeAlias = str
CardMapping: TypeAlias = Mapping[str, object]
CardSequence: TypeAlias = tuple[CardMapping, ...]
CardFieldSequence: TypeAlias = tuple[CardFieldName, ...]
DescriptorMap: TypeAlias = dict[str, str]
DescriptorSequence: TypeAlias = tuple[str, ...]
ResponsibilityMap: TypeAlias = dict[str, tuple[str, ...]]
RelationshipPointerMap: TypeAlias = dict[str, tuple[str, ...]]


class _StudyCardPayloadRequired(TypedDict):
    """Required keys for a first-slice StudyCard gateway payload."""

    study_id: str
    citation_handle: str
    tumor_scope_tags: Sequence[str]
    therapy_scope_tags: Sequence[str]
    relevance_scope_tags: Sequence[str]
    screening_decision: StudyScreeningDecision
    status: StudyCardStatus
    created_from_note: str


class StudyCardPayload(_StudyCardPayloadRequired, total=False):
    """Full-card StudyCard payload used by command-to-gateway boundaries."""

    screening_note: str
    source_artifact_locator: str


class _StudyCardIngestInputRequired(TypedDict):
    """Required keys for the internal StudyCard ingest command input."""

    study_id: str
    citation_handle: str
    tumor_types: Sequence[str]
    therapy_scopes: Sequence[str]
    relevance_scopes: Sequence[str]
    screening_decision: StudyScreeningDecision
    status: StudyCardStatus
    created_from: str


class StudyCardIngestInput(_StudyCardIngestInputRequired, total=False):
    """Normalized internal StudyCard ingest input before payload preparation."""

    screening_note: str
    source_artifact: str


StudyCardFileInput: TypeAlias = Mapping[str, object]


class _StudyCardCLIInputRequired(TypedDict):
    """Required fields for the public ingest study CLI adapter boundary."""

    study_id: str
    citation_handle: str
    tumor_type: Sequence[str]
    therapy_scope: Sequence[str]
    relevance_scope: Sequence[str]
    screening_decision: StudyScreeningDecision
    status: StudyCardStatus
    created_from: str


class StudyCardCLIInput(_StudyCardCLIInputRequired, total=False):
    """Typed mapping built from parsed CLI args before internal normalization."""

    screening_note: str
    source_artifact: str


class StudyCardUpdateInput(TypedDict):
    """Typed mapping built from parsed CLI args for public StudyCard update."""

    study_id: str
    from_file: str


class _DatasetCardPayloadRequired(TypedDict):
    """Required keys for a first-slice DatasetCard gateway payload."""

    dataset_id: str
    study_id: str
    source_locator: str
    availability_status: DatasetAvailabilityStatus
    modality_scope_tags: Sequence[str]
    cohort_summary: str
    platform_summary: str
    status: DatasetCardStatus
    locator_confidence_note: str


class DatasetCardPayload(_DatasetCardPayloadRequired, total=False):
    """Full-card DatasetCard payload used by command-to-gateway boundaries."""

    accession_id: str
    artifact_locator: str
    availability_note: str


class _DatasetCardIngestInputRequired(TypedDict):
    """Required keys for the internal DatasetCard ingest command input."""

    dataset_id: str
    study_id: str
    source_locator: str
    availability_status: DatasetAvailabilityStatus
    modality_scopes: Sequence[str]
    cohort_summary: str
    platform_summary: str
    status: DatasetCardStatus
    locator_confidence_note: str


class DatasetCardIngestInput(_DatasetCardIngestInputRequired, total=False):
    """Normalized internal DatasetCard ingest input before payload preparation."""

    accession_id: str
    artifact_locator: str
    availability_note: str


DatasetCardFileInput: TypeAlias = Mapping[str, object]


class _DatasetCardCLIInputRequired(TypedDict):
    """Required fields for the public ingest dataset CLI adapter boundary."""

    dataset_id: str
    study_id: str
    source_locator: str
    availability_status: DatasetAvailabilityStatus
    modality_scope: Sequence[str]
    cohort_summary: str
    platform_summary: str
    status: DatasetCardStatus
    locator_confidence_note: str


class DatasetCardCLIInput(_DatasetCardCLIInputRequired, total=False):
    """Typed mapping built from parsed CLI args before internal normalization."""

    accession_id: str
    artifact_locator: str
    availability_note: str


class DatasetCardUpdateInput(TypedDict):
    """Typed mapping built from parsed CLI args for public DatasetCard update."""

    dataset_id: str
    from_file: str


class _ClaimCardPayloadRequired(TypedDict):
    """Required keys for a first-slice ClaimCard gateway payload."""

    claim_id: str
    study_id: str
    claim_text: str
    claim_type: str
    provenance_pointer: str
    status: ClaimCardStatus
    review_readiness: ClaimReviewReadiness
    created_from_note: str


class ClaimCardPayload(_ClaimCardPayloadRequired, total=False):
    """Full-card ClaimCard payload used by command-to-gateway boundaries."""

    dataset_ids: Sequence[str]
    claim_summary_handle: str


class _ClaimCardIngestInputRequired(TypedDict):
    """Required keys for the internal ClaimCard ingest command input."""

    claim_id: str
    study_id: str
    claim_text: str
    claim_type: str
    provenance_pointer: str
    status: ClaimCardStatus
    review_readiness: ClaimReviewReadiness
    created_from: str


class ClaimCardIngestInput(_ClaimCardIngestInputRequired, total=False):
    """Normalized internal ClaimCard ingest input before payload preparation."""

    dataset_ids: Sequence[str]
    claim_summary_handle: str


ClaimCardFileInput: TypeAlias = Mapping[str, object]


class _ClaimCardCLIInputRequired(TypedDict):
    """Required fields for the public ingest claim CLI adapter boundary."""

    claim_id: str
    study_id: str
    claim_text: str
    claim_type: str
    provenance_pointer: str
    status: ClaimCardStatus
    review_readiness: ClaimReviewReadiness
    created_from: str


class ClaimCardCLIInput(_ClaimCardCLIInputRequired, total=False):
    """Typed mapping built from parsed CLI args before internal normalization."""

    dataset_ids: Sequence[str]
    claim_summary_handle: str


class ClaimCardUpdateInput(TypedDict):
    """Typed mapping built from parsed CLI args for public ClaimCard update."""

    claim_id: str
    from_file: str


class ShowCLIInput(TypedDict):
    """Typed mapping built from parsed CLI args for public by-id show commands."""

    card_family: CardFamilyName
    target_id: str


class ListCLIInput(TypedDict):
    """Typed mapping built from parsed CLI args for public family-level list commands."""

    card_family: CardFamilyName


class DeleteCLIInput(TypedDict):
    """Typed mapping built from parsed CLI args for public by-id delete commands."""

    card_family: CardFamilyName
    target_id: str


class StudyCardSummary(TypedDict):
    """Compact public discovery summary for one `StudyCard`."""

    study_id: str
    status: StudyCardStatus
    citation_handle: str


class DatasetCardSummary(TypedDict):
    """Compact public discovery summary for one `DatasetCard`."""

    dataset_id: str
    study_id: str
    status: DatasetCardStatus


class ClaimCardSummary(TypedDict):
    """Compact public discovery summary for one `ClaimCard`."""

    claim_id: str
    study_id: str
    status: ClaimCardStatus
    claim_type: str


ListSummaryEntry: TypeAlias = StudyCardSummary | DatasetCardSummary | ClaimCardSummary
ListSummaryResult: TypeAlias = tuple[ListSummaryEntry, ...]


GatewayCardPayload: TypeAlias = (
    StudyCardPayload | DatasetCardPayload | ClaimCardPayload
)
GatewayReadCard: TypeAlias = GatewayCardPayload
GatewayListResult: TypeAlias = tuple[GatewayReadCard, ...]


class GovernanceDescriptor(TypedDict):
    """Documentation-oriented descriptor for an A-header lane or domain."""

    name: str
    governance_label: str
    purpose: str
    inputs: DescriptorSequence
    outputs: DescriptorSequence
    core_functions: DescriptorSequence
    deferred_items: DescriptorSequence


class OfficeDescriptor(TypedDict):
    """Documentation-oriented descriptor for a department office or lane."""

    name: str
    governance_label: str
    purpose: str
    inputs: DescriptorSequence
    outputs: DescriptorSequence
    core_functions: DescriptorSequence
    deferred_items: DescriptorSequence


class InterfaceDescriptor(TypedDict):
    """Documentation-oriented descriptor for a planned core function."""

    name: str
    purpose: str
    inputs: DescriptorSequence
    outputs: DescriptorSequence
    non_goals: DescriptorSequence


class GatewayResultDescriptor(TypedDict):
    """Documentation-oriented descriptor for a frozen gateway result shape."""

    operation_kind: GatewayOperationKind
    success_shape: str
    failure_channel: str
    notes: DescriptorSequence


class MutationPlanDescriptor(TypedDict):
    """Documentation-oriented descriptor for a frozen mutation-planning result."""

    plan_kind: MutationOperationKind
    card_family: CardFamilyName
    target_id: str
    input_requirement: MutationInputRequirement
    integrity_checks_required: DescriptorSequence
    atomicity_expectation: str
    execution_state: MutationExecutionState
    deferred_execution_note: str


class CommandPayloadDescriptor(TypedDict):
    """Static descriptor for one command-family payload touchpoint."""

    card_family: CardFamilyName
    payload_type: str
    usage: CommandPayloadUsage
    gateway_reads: DescriptorSequence
    gateway_mutations: DescriptorSequence
    notes: DescriptorSequence


class CommandDescriptor(TypedDict):
    """Documentation-oriented descriptor for a reserved internal command family."""

    family_name: CommandFamilyName
    owning_module: str
    owning_domain: str
    purpose: str
    primary_inputs: DescriptorSequence
    primary_outputs: DescriptorSequence
    dependency_contracts: DescriptorSequence
    parser_builder: str
    handler: str
    public_exposure: str
    non_goals: DescriptorSequence


class _CommandExecutionResultRequired(TypedDict):
    """Required fields for a narrow internal command execution outcome."""

    ok: bool
    operation: str
    card_family: CardFamilyName
    target_id: str | None
    message: str


class CommandExecutionResult(_CommandExecutionResultRequired, total=False):
    """Internal command-layer success/failure envelope for runtime bridges."""

    error_category: CommandErrorCategory


__all__ = [
    "AHeaderLaneName",
    "AuditOutcomeName",
    "CardFamilyName",
    "CardMapping",
    "CardSequence",
    "CardFieldName",
    "CardFieldSequence",
    "ClaimCardCLIInput",
    "ClaimCardFileInput",
    "ClaimCardIngestInput",
    "ClaimCardPayload",
    "ClaimCardUpdateInput",
    "ClaimCardStatus",
    "ClaimReviewReadiness",
    "CommandDescriptor",
    "CommandErrorCategory",
    "CommandExecutionResult",
    "CommandFamilyName",
    "CommandPayloadDescriptor",
    "CommandPayloadUsage",
    "ContractCategoryName",
    "DatasetAvailabilityStatus",
    "DatasetCardCLIInput",
    "DatasetCardFileInput",
    "DatasetCardIngestInput",
    "DatasetCardPayload",
    "DatasetCardStatus",
    "DatasetCardUpdateInput",
    "DeleteCLIInput",
    "DepartmentName",
    "DescriptorMap",
    "DescriptorSequence",
    "FunctionName",
    "GatewayCardPayload",
    "GatewayListResult",
    "GatewayOperationKind",
    "GatewayReadCard",
    "GatewayReadMode",
    "GatewayResultDescriptor",
    "GovernanceDescriptor",
    "InterfaceDescriptor",
    "ListCLIInput",
    "ListSummaryEntry",
    "ListSummaryResult",
    "MutationExecutionState",
    "MutationInputRequirement",
    "MutationOperationKind",
    "MutationPlanDescriptor",
    "ObjectFamilyName",
    "OfficeDescriptor",
    "OfficeName",
    "RelationshipPointerMap",
    "ReservedCLIFamilyName",
    "ResponsibilityMap",
    "StudyCardSummary",
    "ShowCLIInput",
    "StudyCardCLIInput",
    "StudyCardFileInput",
    "StudyCardIngestInput",
    "StudyCardPayload",
    "StudyCardUpdateInput",
    "StudyScreeningDecision",
    "StudyCardStatus",
    "DatasetCardSummary",
    "ClaimCardSummary",
]
