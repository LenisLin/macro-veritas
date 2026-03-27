from __future__ import annotations

from typing import get_args, get_type_hints

import pytest

from macro_veritas.registry.errors import (
    BrokenReferenceError,
    CardAlreadyExistsError,
    CardNotFoundError,
    DependencyExistsError,
    InvalidStateTransitionError,
    RegistryError,
    UpdateLockError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.gateway import (
    claim_card_exists,
    create_claim_card,
    create_dataset_card,
    delete_claim_card,
    delete_dataset_card,
    delete_study_card,
    describe_atomic_write_policy,
    describe_gateway_error_semantics,
    describe_gateway_result_contract,
    describe_mutation_plan_contract,
    describe_referential_integrity_policy,
    describe_registry_gateway_role,
    describe_update_policy,
    get_claim_card,
    list_claim_cards,
    list_supported_card_families,
    plan_create_claim_card,
    plan_create_dataset_card,
    plan_create_study_card,
    plan_update_claim_card,
    plan_update_study_card,
    update_claim_card,
    update_dataset_card,
)
from macro_veritas.registry.layout import describe_layout_vs_gateway_boundary
from macro_veritas.registry.specs import (
    describe_integrity_enforcement_policy,
    describe_registry_gateway_boundary,
    list_registry_error_categories,
)
from macro_veritas.shared import types as shared_types


def test_shared_gateway_contract_types_are_frozen() -> None:
    assert get_args(shared_types.CardFamilyName) == (
        "StudyCard",
        "DatasetCard",
        "ClaimCard",
    )
    assert get_args(shared_types.GatewayReadMode) == (
        "get_by_id",
        "exists_by_id",
        "list_by_family",
    )
    assert get_args(shared_types.GatewayOperationKind) == (
        "get_by_id",
        "exists_by_id",
        "list_by_family",
        "plan_create",
        "plan_update",
    )
    assert get_args(shared_types.MutationOperationKind) == ("create", "update")
    assert tuple(shared_types.GatewayResultDescriptor.__annotations__.keys()) == (
        "operation_kind",
        "success_shape",
        "failure_channel",
        "notes",
    )
    assert tuple(shared_types.MutationPlanDescriptor.__annotations__.keys()) == (
        "plan_kind",
        "card_family",
        "target_id",
        "input_requirement",
        "integrity_checks_required",
        "atomicity_expectation",
        "execution_state",
        "deferred_execution_note",
    )


def test_registry_gateway_descriptors_match_frozen_boundary() -> None:
    boundary = describe_registry_gateway_boundary()
    gateway_role = describe_registry_gateway_role()
    result_contract = describe_gateway_result_contract()
    error_semantics = describe_gateway_error_semantics()
    mutation_plan_contract = describe_mutation_plan_contract()
    update_policy = describe_update_policy()
    integrity_policy = describe_referential_integrity_policy()
    atomic_policy = describe_atomic_write_policy()
    layout_boundary = describe_layout_vs_gateway_boundary()

    assert boundary["source_of_truth_doc"] == "docs/registry_io_boundary.md"
    assert "must not do raw path traversal" in boundary["cli_layer"]
    assert boundary["gateway_role"].startswith("sole internal boundary")
    assert boundary["current_runtime_scope"] == (
        "StudyCard, DatasetCard, and ClaimCard runtime are implemented"
    )

    assert list_supported_card_families() == (
        "StudyCard",
        "DatasetCard",
        "ClaimCard",
    )
    assert gateway_role["boundary_status"] == "studycard-datasetcard-claimcard-runtime"
    assert gateway_role["operation_families"] == (
        "get_by_id",
        "exists_by_id",
        "list_by_family",
        "plan_create",
        "plan_update",
    )
    assert gateway_role["communication_contract_doc"] == "docs/gateway_contracts.md"
    assert gateway_role["payload_contract_doc"] == "docs/payload_contracts.md"
    assert gateway_role["studycard_runtime_doc"] == "docs/studycard_runtime.md"
    assert gateway_role["datasetcard_runtime_doc"] == "docs/datasetcard_runtime.md"
    assert gateway_role["claimcard_runtime_doc"] == "docs/claimcard_runtime.md"
    assert gateway_role["runtime_real_behavior"]["StudyCard"] == (
        "get",
        "exists",
        "list",
        "plan_create",
        "plan_update",
        "create",
        "update",
        "delete",
    )
    assert gateway_role["runtime_real_behavior"]["DatasetCard"] == (
        "get",
        "exists",
        "list",
        "plan_create",
        "plan_update",
        "create",
        "update",
        "delete",
    )
    assert gateway_role["runtime_real_behavior"]["ClaimCard"] == (
        "get",
        "exists",
        "list",
        "plan_create",
        "plan_update",
        "create",
        "update",
        "delete",
    )
    assert result_contract["get_by_id"]["success_shape"] == "GatewayReadCard"
    assert result_contract["exists_by_id"]["success_shape"] == "bool"
    assert result_contract["list_by_family"]["success_shape"] == "GatewayListResult"
    assert result_contract["plan_update"]["success_shape"] == "MutationPlanDescriptor"
    assert error_semantics["CardNotFoundError"]["applies_to"] == (
        "get_by_id",
        "plan_update",
        "update",
        "delete",
    )
    assert error_semantics["BrokenReferenceError"]["applies_to"] == (
        "plan_create",
        "plan_update",
        "create",
        "update",
    )
    assert error_semantics["DependencyExistsError"]["applies_to"] == ("delete",)
    assert error_semantics["UpdateLockError"]["applies_to"] == ("update", "delete")
    assert error_semantics["UnsupportedRegistryOperationError"]["not_a_raw_os_exception"] is True
    assert mutation_plan_contract["output_type"] == "MutationPlanDescriptor"
    assert mutation_plan_contract["input_requirement"] == "full_card_payload"
    assert mutation_plan_contract["accepted_payload_types"] == (
        "StudyCardPayload",
        "DatasetCardPayload",
        "ClaimCardPayload",
    )
    assert mutation_plan_contract["execution_state"] == "planned_only"
    assert update_policy["style"] == "full-card replace only"
    assert update_policy["patch_input_supported"] is False

    assert integrity_policy == describe_integrity_enforcement_policy()
    assert integrity_policy["enforcement_point"] == "registry gateway"
    assert atomic_policy["write_shape"] == "write-temp-then-replace"
    assert atomic_policy["implemented_for"] == "StudyCard, DatasetCard, and ClaimCard"
    assert atomic_policy["multi_card_transaction_guarantee"] == "not planned in MVP"
    assert atomic_policy["concurrent_locking"] == "exclusive single-card update/delete lock only"

    assert layout_boundary["layout_is_access_api"] is False
    assert layout_boundary["cli_should_use_layout_as_io_layer"] is False


def test_registry_error_surface_is_small_and_explicit() -> None:
    assert list_registry_error_categories() == (
        "RegistryError",
        "CardNotFoundError",
        "CardAlreadyExistsError",
        "BrokenReferenceError",
        "DependencyExistsError",
        "InvalidStateTransitionError",
        "UpdateLockError",
        "UnsupportedRegistryOperationError",
    )

    assert issubclass(CardNotFoundError, RegistryError)
    assert issubclass(CardAlreadyExistsError, RegistryError)
    assert issubclass(BrokenReferenceError, RegistryError)
    assert issubclass(DependencyExistsError, RegistryError)
    assert issubclass(InvalidStateTransitionError, RegistryError)
    assert issubclass(UpdateLockError, RegistryError)
    assert issubclass(UnsupportedRegistryOperationError, RegistryError)

def test_gateway_signatures_reference_frozen_payload_types() -> None:
    claim_exists_hints = get_type_hints(claim_card_exists)
    create_claim_hints = get_type_hints(create_claim_card)
    get_claim_hints = get_type_hints(get_claim_card)
    plan_create_claim_hints = get_type_hints(plan_create_claim_card)
    plan_create_study_hints = get_type_hints(plan_create_study_card)
    plan_create_dataset_hints = get_type_hints(plan_create_dataset_card)
    list_claim_hints = get_type_hints(list_claim_cards)
    plan_update_study_hints = get_type_hints(plan_update_study_card)
    plan_update_claim_hints = get_type_hints(plan_update_claim_card)
    create_dataset_hints = get_type_hints(create_dataset_card)
    delete_claim_hints = get_type_hints(delete_claim_card)
    delete_dataset_hints = get_type_hints(delete_dataset_card)
    delete_study_hints = get_type_hints(delete_study_card)
    update_claim_hints = get_type_hints(update_claim_card)
    update_dataset_hints = get_type_hints(update_dataset_card)

    assert claim_exists_hints["return"] is bool
    assert create_claim_hints["card"] is shared_types.ClaimCardPayload
    assert create_claim_hints["return"] is shared_types.ClaimCardPayload
    assert get_claim_hints["return"] is shared_types.ClaimCardPayload
    assert plan_create_claim_hints["card"] is shared_types.ClaimCardPayload
    assert plan_create_claim_hints["return"] is shared_types.MutationPlanDescriptor
    assert plan_create_study_hints["card"] is shared_types.StudyCardPayload
    assert plan_create_study_hints["return"] is shared_types.MutationPlanDescriptor
    assert plan_create_dataset_hints["card"] is shared_types.DatasetCardPayload
    assert plan_create_dataset_hints["return"] is shared_types.MutationPlanDescriptor
    assert list_claim_hints["return"] == tuple[shared_types.ClaimCardPayload, ...]
    assert plan_update_study_hints["card"] is shared_types.StudyCardPayload
    assert plan_update_study_hints["return"] is shared_types.MutationPlanDescriptor
    assert plan_update_claim_hints["card"] is shared_types.ClaimCardPayload
    assert plan_update_claim_hints["return"] is shared_types.MutationPlanDescriptor
    assert create_dataset_hints["card"] is shared_types.DatasetCardPayload
    assert create_dataset_hints["return"] is shared_types.DatasetCardPayload
    assert delete_claim_hints["claim_id"] is str
    assert delete_claim_hints["return"] is type(None)
    assert delete_dataset_hints["dataset_id"] is str
    assert delete_dataset_hints["return"] is type(None)
    assert delete_study_hints["study_id"] is str
    assert delete_study_hints["return"] is type(None)
    assert update_claim_hints["card"] is shared_types.ClaimCardPayload
    assert update_claim_hints["return"] is shared_types.ClaimCardPayload
    assert update_dataset_hints["card"] is shared_types.DatasetCardPayload
    assert update_dataset_hints["return"] is shared_types.DatasetCardPayload
