"""Interface skeleton for the future registry access boundary.

This module reserves the internal boundary that future code should use to
retrieve or persist first-slice registry cards.

Non-goals:
- no registry IO
- no serializer or deserializer implementation
- no filesystem mutation logic
- no validation or parsing engine

Boundary docs: `docs/registry_io_boundary.md` and `docs/gateway_contracts.md`.
"""

from __future__ import annotations

from macro_veritas.registry.specs import (
    describe_integrity_enforcement_policy,
    describe_registry_gateway_boundary,
    list_registry_error_categories,
)
from macro_veritas.shared.types import (
    CardFamilyName,
    CardMapping,
    CardSequence,
    GatewayOperationKind,
    GatewayResultDescriptor,
    MutationPlanDescriptor,
)

_SUPPORTED_CARD_FAMILIES: tuple[CardFamilyName, ...] = (
    "StudyCard",
    "DatasetCard",
    "ClaimCard",
)
_OPERATION_FAMILIES: tuple[GatewayOperationKind, ...] = (
    "get_by_id",
    "exists_by_id",
    "list_by_family",
    "plan_create",
    "plan_update",
)
_RESULT_CONTRACT: dict[GatewayOperationKind, GatewayResultDescriptor] = {
    "get_by_id": {
        "operation_kind": "get_by_id",
        "success_shape": "CardMapping",
        "failure_channel": "raise RegistryError subclass",
        "notes": (
            "Returns one bare card mapping on success.",
            "Absence is communicated as CardNotFoundError.",
        ),
    },
    "exists_by_id": {
        "operation_kind": "exists_by_id",
        "success_shape": "bool",
        "failure_channel": "missing card is False; unsupported boundary use raises RegistryError subclass",
        "notes": (
            "Absence is not exceptional for exists checks.",
            "This is the only first-slice gateway call where missing is not a domain error.",
        ),
    },
    "list_by_family": {
        "operation_kind": "list_by_family",
        "success_shape": "tuple[CardMapping, ...]",
        "failure_channel": "raise RegistryError subclass only for unsupported boundary use",
        "notes": (
            "Returns a bare tuple of card mappings.",
            "An empty family listing is communicated as an empty tuple.",
        ),
    },
    "plan_create": {
        "operation_kind": "plan_create",
        "success_shape": "MutationPlanDescriptor",
        "failure_channel": "raise RegistryError subclass",
        "notes": (
            "Expects a full card mapping, not a patch.",
            "Returns an explicit mutation-plan descriptor without performing IO.",
        ),
    },
    "plan_update": {
        "operation_kind": "plan_update",
        "success_shape": "MutationPlanDescriptor",
        "failure_channel": "raise RegistryError subclass",
        "notes": (
            "Expects the complete replacement card mapping, not a patch.",
            "Uses the same plan descriptor shape as create planning.",
        ),
    },
}
_MUTATION_PLAN_FIELDS: tuple[str, ...] = (
    "plan_kind",
    "card_family",
    "target_id",
    "input_requirement",
    "integrity_checks_required",
    "atomicity_expectation",
    "execution_state",
    "deferred_execution_note",
)


def _not_implemented(operation_name: str) -> NotImplementedError:
    return NotImplementedError(
        f"{operation_name} is a frozen registry gateway placeholder only. "
        "Registry IO, serialization, validation, and filesystem mutation are "
        "not implemented."
    )


def describe_registry_gateway_role() -> dict[str, object]:
    """Describe the frozen role of the registry gateway boundary."""

    return {
        **describe_registry_gateway_boundary(),
        "boundary_status": "interface-skeleton-only",
        "communication_contract_doc": "docs/gateway_contracts.md",
        "supported_card_families": list_supported_card_families(),
        "operation_families": _OPERATION_FAMILIES,
        "planned_error_categories": list_registry_error_categories(),
        "result_style": (
            "bare card reads + bool exists + tuple listings + explicit "
            "mutation-plan descriptor + domain exceptions"
        ),
    }


def list_supported_card_families() -> tuple[CardFamilyName, ...]:
    """Return the first-slice card families owned by this gateway contract."""

    return _SUPPORTED_CARD_FAMILIES


def describe_gateway_result_contract() -> dict[GatewayOperationKind, GatewayResultDescriptor]:
    """Describe the frozen success-result shapes for gateway operations."""

    return _RESULT_CONTRACT


def describe_gateway_error_semantics() -> dict[str, dict[str, object]]:
    """Describe the frozen domain-level meaning of gateway error categories."""

    return {
        "RegistryError": {
            "semantic_layer": "gateway/domain",
            "meaning": "base registry contract failure",
            "not_a_raw_os_exception": True,
        },
        "CardNotFoundError": {
            "semantic_layer": "gateway/domain",
            "meaning": "requested target card is absent for read or update planning",
            "applies_to": ("get_by_id", "plan_update"),
            "not_a_raw_os_exception": True,
        },
        "CardAlreadyExistsError": {
            "semantic_layer": "gateway/domain",
            "meaning": "create planning targets an already existing card",
            "applies_to": ("plan_create",),
            "not_a_raw_os_exception": True,
        },
        "BrokenReferenceError": {
            "semantic_layer": "gateway/domain",
            "meaning": "direct gateway-owned referenced-card existence check failed",
            "applies_to": ("plan_create", "plan_update"),
            "not_a_raw_os_exception": True,
        },
        "InvalidStateTransitionError": {
            "semantic_layer": "gateway/domain",
            "meaning": "requested change conflicts with the frozen state policy",
            "applies_to": ("plan_create", "plan_update"),
            "not_a_raw_os_exception": True,
        },
        "UnsupportedRegistryOperationError": {
            "semantic_layer": "gateway/domain",
            "meaning": "caller requested an operation or input style outside the frozen contract",
            "applies_to": _OPERATION_FAMILIES,
            "not_a_raw_os_exception": True,
        },
    }


def describe_referential_integrity_policy() -> dict[str, object]:
    """Describe where direct referenced-card existence checks belong."""

    return describe_integrity_enforcement_policy()


def describe_atomic_write_policy() -> dict[str, str]:
    """Describe the planned future single-card mutation-safety rule."""

    return {
        "policy": "single-card atomic replace",
        "write_shape": "write-temp-then-replace",
        "guarantee_scope": "one canonical card file per create or update operation",
        "multi_card_transaction_guarantee": "not planned in MVP",
        "concurrent_locking": "not implemented",
    }


def describe_mutation_plan_contract() -> dict[str, object]:
    """Describe the frozen mutation-planning result shape for gateway calls."""

    return {
        "output_type": "MutationPlanDescriptor",
        "required_fields": _MUTATION_PLAN_FIELDS,
        "input_requirement": "full_card_mapping",
        "execution_state": "planned_only",
        "atomicity_expectation": "single-card atomic replace",
        "deferred_execution_note": "planning result only; no IO or serializer work has occurred",
    }


def describe_update_policy() -> dict[str, str | bool]:
    """Describe the frozen MVP update-input rule for the gateway."""

    return {
        "style": "full-card replace only",
        "patch_input_supported": False,
        "caller_obligation": "plan_update expects the complete replacement card mapping",
        "why": (
            "Patch semantics are deferred until merge, validation, and serializer "
            "rules exist."
        ),
    }


def get_study_card(study_id: str) -> CardMapping:
    """Planned gateway read for `StudyCard` retrieval by canonical ID.

    Inputs:
        `study_id`: canonical `StudyCard` identifier.
    Outputs:
        On success, the future gateway returns one bare `CardMapping`.
    Expected domain errors:
        `CardNotFoundError` when the target card is absent.
    Non-goals:
        This placeholder does not read files, deserialize data, or validate fields.
    """

    raise _not_implemented("get_study_card")


def get_dataset_card(dataset_id: str) -> CardMapping:
    """Planned gateway read for `DatasetCard` retrieval by canonical ID.

    Inputs:
        `dataset_id`: canonical `DatasetCard` identifier.
    Outputs:
        On success, the future gateway returns one bare `CardMapping`.
    Expected domain errors:
        `CardNotFoundError` when the target card is absent.
    Non-goals:
        This placeholder does not read files, deserialize data, or validate fields.
    """

    raise _not_implemented("get_dataset_card")


def get_claim_card(claim_id: str) -> CardMapping:
    """Planned gateway read for `ClaimCard` retrieval by canonical ID.

    Inputs:
        `claim_id`: canonical `ClaimCard` identifier.
    Outputs:
        On success, the future gateway returns one bare `CardMapping`.
    Expected domain errors:
        `CardNotFoundError` when the target card is absent.
    Non-goals:
        This placeholder does not read files, deserialize data, or validate fields.
    """

    raise _not_implemented("get_claim_card")


def study_card_exists(study_id: str) -> bool:
    """Planned gateway existence check for `StudyCard` by canonical ID.

    Inputs:
        `study_id`: canonical `StudyCard` identifier.
    Outputs:
        `True` if the target exists, otherwise `False`.
    Expected domain errors:
        Missing cards are communicated as `False`, not `CardNotFoundError`.
    Non-goals:
        This placeholder does not inspect storage or perform raw path access.
    """

    raise _not_implemented("study_card_exists")


def dataset_card_exists(dataset_id: str) -> bool:
    """Planned gateway existence check for `DatasetCard` by canonical ID.

    Inputs:
        `dataset_id`: canonical `DatasetCard` identifier.
    Outputs:
        `True` if the target exists, otherwise `False`.
    Expected domain errors:
        Missing cards are communicated as `False`, not `CardNotFoundError`.
    Non-goals:
        This placeholder does not inspect storage or perform raw path access.
    """

    raise _not_implemented("dataset_card_exists")


def claim_card_exists(claim_id: str) -> bool:
    """Planned gateway existence check for `ClaimCard` by canonical ID.

    Inputs:
        `claim_id`: canonical `ClaimCard` identifier.
    Outputs:
        `True` if the target exists, otherwise `False`.
    Expected domain errors:
        Missing cards are communicated as `False`, not `CardNotFoundError`.
    Non-goals:
        This placeholder does not inspect storage or perform raw path access.
    """

    raise _not_implemented("claim_card_exists")


def list_study_cards() -> CardSequence:
    """Planned gateway listing operation for `StudyCard` records.

    Inputs:
        None.
    Outputs:
        On success, the future gateway returns `tuple[CardMapping, ...]`.
        An empty family listing is an empty tuple.
    Expected domain errors:
        None for an empty family listing.
    Non-goals:
        This placeholder does not read files or freeze listing order semantics.
    """

    raise _not_implemented("list_study_cards")


def list_dataset_cards() -> CardSequence:
    """Planned gateway listing operation for `DatasetCard` records.

    Inputs:
        None.
    Outputs:
        On success, the future gateway returns `tuple[CardMapping, ...]`.
        An empty family listing is an empty tuple.
    Expected domain errors:
        None for an empty family listing.
    Non-goals:
        This placeholder does not read files or freeze listing order semantics.
    """

    raise _not_implemented("list_dataset_cards")


def list_claim_cards() -> CardSequence:
    """Planned gateway listing operation for `ClaimCard` records.

    Inputs:
        None.
    Outputs:
        On success, the future gateway returns `tuple[CardMapping, ...]`.
        An empty family listing is an empty tuple.
    Expected domain errors:
        None for an empty family listing.
    Non-goals:
        This placeholder does not read files or freeze listing order semantics.
    """

    raise _not_implemented("list_claim_cards")


def plan_create_study_card(card: CardMapping) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `StudyCard` create planning.

    Inputs:
        `card`: complete `StudyCard` mapping for the planned create operation.
    Outputs:
        On success, the future gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardAlreadyExistsError`, `InvalidStateTransitionError`,
        or `UnsupportedRegistryOperationError`.
    Non-goals:
        This placeholder does not write files, allocate identifiers, or validate fields.
    """

    del card
    raise _not_implemented("plan_create_study_card")


def plan_create_dataset_card(card: CardMapping) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `DatasetCard` create planning.

    Inputs:
        `card`: complete `DatasetCard` mapping for the planned create operation.
    Outputs:
        On success, the future gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardAlreadyExistsError`, `BrokenReferenceError`,
        `InvalidStateTransitionError`, or `UnsupportedRegistryOperationError`.
    Non-goals:
        This placeholder does not write files, merge patches, or validate fields.
    """

    del card
    raise _not_implemented("plan_create_dataset_card")


def plan_create_claim_card(card: CardMapping) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `ClaimCard` create planning.

    Inputs:
        `card`: complete `ClaimCard` mapping for the planned create operation.
    Outputs:
        On success, the future gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardAlreadyExistsError`, `BrokenReferenceError`,
        `InvalidStateTransitionError`, or `UnsupportedRegistryOperationError`.
    Non-goals:
        This placeholder does not write files, merge patches, or validate fields.
    """

    del card
    raise _not_implemented("plan_create_claim_card")


def plan_update_study_card(card: CardMapping) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `StudyCard` update planning.

    Inputs:
        `card`: complete replacement `StudyCard` mapping. Patch input is out of
        contract for this MVP freeze.
    Outputs:
        On success, the future gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardNotFoundError`, `InvalidStateTransitionError`,
        or `UnsupportedRegistryOperationError`.
    Non-goals:
        This placeholder does not write files, merge patches, or validate fields.
    """

    del card
    raise _not_implemented("plan_update_study_card")


def plan_update_dataset_card(card: CardMapping) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `DatasetCard` update planning.

    Inputs:
        `card`: complete replacement `DatasetCard` mapping. Patch input is out
        of contract for this MVP freeze.
    Outputs:
        On success, the future gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardNotFoundError`, `BrokenReferenceError`,
        `InvalidStateTransitionError`, or `UnsupportedRegistryOperationError`.
    Non-goals:
        This placeholder does not write files, merge patches, or validate fields.
    """

    del card
    raise _not_implemented("plan_update_dataset_card")


def plan_update_claim_card(card: CardMapping) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `ClaimCard` update planning.

    Inputs:
        `card`: complete replacement `ClaimCard` mapping. Patch input is out of
        contract for this MVP freeze.
    Outputs:
        On success, the future gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardNotFoundError`, `BrokenReferenceError`,
        `InvalidStateTransitionError`, or `UnsupportedRegistryOperationError`.
    Non-goals:
        This placeholder does not write files, merge patches, or validate fields.
    """

    del card
    raise _not_implemented("plan_update_claim_card")


__all__ = [
    "claim_card_exists",
    "dataset_card_exists",
    "describe_atomic_write_policy",
    "describe_gateway_error_semantics",
    "describe_gateway_result_contract",
    "describe_mutation_plan_contract",
    "describe_referential_integrity_policy",
    "describe_registry_gateway_role",
    "describe_update_policy",
    "get_claim_card",
    "get_dataset_card",
    "get_study_card",
    "list_claim_cards",
    "list_dataset_cards",
    "list_study_cards",
    "list_supported_card_families",
    "plan_create_claim_card",
    "plan_create_dataset_card",
    "plan_create_study_card",
    "plan_update_claim_card",
    "plan_update_dataset_card",
    "plan_update_study_card",
    "study_card_exists",
]
