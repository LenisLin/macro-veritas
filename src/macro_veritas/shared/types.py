"""Lightweight shared descriptor and payload types for the frozen MVP boundary.

These aliases and TypedDicts keep documentation-oriented signatures readable
across the governance, command, and registry modules while freezing the
first-slice payload contract between internal command handlers and the
registry gateway.

They do not define scientific schemas, validators, persistence models, or
broad serializer behavior. The implemented StudyCard, DatasetCard, and
ClaimCard runtime slices reuse these payload shapes directly.
Boundary docs:
`docs/governance_spec.md`, `docs/module_map.md`, `docs/card_contracts.md`,
`docs/payload_contracts.md`, `docs/gateway_contracts.md`,
`docs/cli_command_contracts.md`, and `docs/constraints.md`.
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
    "bind",
    "extract",
    "audit",
    "review",
    "run",
    "grade",
]

ReservedCLIFamilyName = Literal[
    "ingest",
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
    """Required keys for a first-slice `StudyCard` gateway payload."""

    study_id: str
    citation_handle: str
    tumor_scope_tags: Sequence[str]
    therapy_scope_tags: Sequence[str]
    relevance_scope_tags: Sequence[str]
    screening_decision: StudyScreeningDecision
    status: StudyCardStatus
    created_from_note: str


class StudyCardPayload(_StudyCardPayloadRequired, total=False):
    """Full-card `StudyCard` payload used by command-to-gateway boundaries."""

    screening_note: str
    source_artifact_locator: str


class _DatasetCardPayloadRequired(TypedDict):
    """Required keys for a first-slice `DatasetCard` gateway payload."""

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
    """Full-card `DatasetCard` payload used by command-to-gateway boundaries."""

    accession_id: str
    artifact_locator: str
    availability_note: str


class _ClaimCardPayloadRequired(TypedDict):
    """Required keys for a first-slice `ClaimCard` gateway payload."""

    claim_id: str
    study_id: str
    claim_text: str
    claim_type: str
    provenance_pointer: str
    status: ClaimCardStatus
    review_readiness: ClaimReviewReadiness
    created_from_note: str


class ClaimCardPayload(_ClaimCardPayloadRequired, total=False):
    """Full-card `ClaimCard` payload used by command-to-gateway boundaries."""

    dataset_ids: Sequence[str]
    claim_summary_handle: str


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


__all__ = [
    "AHeaderLaneName",
    "AuditOutcomeName",
    "CardFamilyName",
    "CardMapping",
    "CardSequence",
    "CardFieldName",
    "CardFieldSequence",
    "ClaimCardPayload",
    "ClaimCardStatus",
    "ClaimReviewReadiness",
    "CommandDescriptor",
    "CommandFamilyName",
    "CommandPayloadDescriptor",
    "CommandPayloadUsage",
    "ContractCategoryName",
    "DatasetAvailabilityStatus",
    "DatasetCardPayload",
    "DatasetCardStatus",
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
    "StudyCardPayload",
    "StudyScreeningDecision",
    "StudyCardStatus",
]
