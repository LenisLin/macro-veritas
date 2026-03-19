"""Lightweight shared descriptor types for the governance and contract skeleton.

These aliases and TypedDicts exist to keep documentation-oriented descriptor
signatures readable across the governance, prosecution, and registry modules.

They do not define scientific schemas, validators, persistence models, or
runtime state. Boundary docs: `docs/governance_spec.md`,
`docs/module_map.md`, `docs/card_contracts.md`, `docs/gateway_contracts.md`,
`docs/cli_command_contracts.md`, and `docs/constraints.md`.
"""

from __future__ import annotations

from typing import Literal, Mapping, TypeAlias, TypedDict

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
MutationInputRequirement = Literal["full_card_mapping"]
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
    "ClaimCardStatus",
    "CommandDescriptor",
    "CommandFamilyName",
    "ContractCategoryName",
    "DatasetCardStatus",
    "DepartmentName",
    "DescriptorMap",
    "DescriptorSequence",
    "FunctionName",
    "GatewayOperationKind",
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
    "StudyCardStatus",
]
