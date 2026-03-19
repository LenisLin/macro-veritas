"""Registry gateway for the first MacroVeritas runtime slice.

This module remains the sole internal boundary that higher layers should use to
retrieve or persist first-slice registry cards through frozen payload/DTO
shapes.

Implemented now:
- real file-backed runtime reads, existence checks, listings, create, and
  update for `StudyCard`
- planning descriptors for `StudyCard` create and update
- domain-level translation of lower-level StudyCard filesystem/YAML failures

Non-goals:
- no DatasetCard or ClaimCard runtime IO
- no CLI wiring
- no scientific logic, evidence grading, or CellVoyager integration

Boundary docs: `docs/registry_io_boundary.md`, `docs/gateway_contracts.md`,
`docs/payload_contracts.md`, and `docs/studycard_runtime.md`.
"""

from __future__ import annotations

from pathlib import Path

from macro_veritas.config import load_project_config
from macro_veritas.registry.errors import (
    CardAlreadyExistsError,
    CardNotFoundError,
    InvalidStateTransitionError,
    RegistryError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.specs import (
    describe_integrity_enforcement_policy,
    describe_registry_gateway_boundary,
    list_registry_error_categories,
)
from macro_veritas.registry.study_runtime import (
    StudyCardFormatError,
    StudyCardIdentifierError,
    StudyCardStateTransitionError,
    create_study_card as _runtime_create_study_card,
    ensure_study_card_update_allowed,
    list_study_cards as _runtime_list_study_cards,
    normalize_study_card_payload,
    read_study_card as _runtime_read_study_card,
    study_card_exists as _runtime_study_card_exists,
    update_study_card as _runtime_update_study_card,
)
from macro_veritas.shared.types import (
    CardFamilyName,
    ClaimCardPayload,
    DatasetCardPayload,
    GatewayOperationKind,
    GatewayResultDescriptor,
    MutationOperationKind,
    MutationPlanDescriptor,
    StudyCardPayload,
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
        "success_shape": "GatewayReadCard",
        "failure_channel": "raise RegistryError subclass",
        "notes": (
            "Returns one bare card mapping shaped like the frozen card contract.",
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
        "success_shape": "GatewayListResult",
        "failure_channel": "raise RegistryError subclass only for unsupported boundary use",
        "notes": (
            "Returns a bare tuple of card mappings shaped like the frozen card contract.",
            "An empty family listing is communicated as an empty tuple.",
        ),
    },
    "plan_create": {
        "operation_kind": "plan_create",
        "success_shape": "MutationPlanDescriptor",
        "failure_channel": "raise RegistryError subclass",
        "notes": (
            "Expects a full-card payload, not raw argparse objects or a patch.",
            "Returns an explicit mutation-plan descriptor without performing IO.",
        ),
    },
    "plan_update": {
        "operation_kind": "plan_update",
        "success_shape": "MutationPlanDescriptor",
        "failure_channel": "raise RegistryError subclass",
        "notes": (
            "Expects the complete replacement full-card payload, not a patch.",
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
        "This milestone implements runtime behavior for StudyCard only."
    )


def _registry_root() -> Path:
    return load_project_config().registry_dir


def _studycard_plan_descriptor(
    plan_kind: MutationOperationKind,
    study_id: str,
) -> MutationPlanDescriptor:
    integrity_checks_required: tuple[str, ...]
    if plan_kind == "create":
        integrity_checks_required = ("canonical StudyCard path must not already exist",)
    else:
        integrity_checks_required = (
            "canonical StudyCard path must already exist",
            "closed StudyCard status must not reopen to an active status",
        )

    return {
        "plan_kind": plan_kind,
        "card_family": "StudyCard",
        "target_id": study_id,
        "input_requirement": "full_card_payload",
        "integrity_checks_required": integrity_checks_required,
        "atomicity_expectation": "single-card atomic replace",
        "execution_state": "planned_only",
        "deferred_execution_note": (
            "Planning only. Runtime execution for StudyCard is available through "
            "create_study_card/update_study_card."
        ),
    }


def _translate_study_runtime_error(
    operation_name: str,
    exc: Exception,
) -> RegistryError:
    if isinstance(exc, StudyCardIdentifierError):
        return UnsupportedRegistryOperationError(str(exc))
    if isinstance(exc, FileNotFoundError):
        return CardNotFoundError(
            f"{operation_name} could not find the requested StudyCard at its canonical path."
        )
    if isinstance(exc, FileExistsError):
        return CardAlreadyExistsError(
            f"{operation_name} targeted a StudyCard that already exists at its canonical path."
        )
    if isinstance(exc, StudyCardStateTransitionError):
        return InvalidStateTransitionError(str(exc))
    if isinstance(exc, StudyCardFormatError):
        return RegistryError(str(exc))
    if isinstance(exc, OSError):
        return RegistryError(f"{operation_name} failed during StudyCard filesystem access: {exc}")
    return RegistryError(f"{operation_name} failed during StudyCard runtime translation: {exc}")


def describe_registry_gateway_role() -> dict[str, object]:
    """Describe the frozen role of the registry gateway boundary."""

    return {
        **describe_registry_gateway_boundary(),
        "boundary_status": "studycard-runtime-only",
        "communication_contract_doc": "docs/gateway_contracts.md",
        "payload_contract_doc": "docs/payload_contracts.md",
        "studycard_runtime_doc": "docs/studycard_runtime.md",
        "supported_card_families": list_supported_card_families(),
        "operation_families": _OPERATION_FAMILIES,
        "planned_error_categories": list_registry_error_categories(),
        "runtime_real_behavior": {
            "StudyCard": ("get", "exists", "list", "plan_create", "plan_update", "create", "update"),
            "DatasetCard": (),
            "ClaimCard": (),
        },
        "result_style": (
            "bare card reads shaped like the frozen card contract + bool exists "
            "+ tuple listings + explicit mutation-plan descriptor + StudyCard "
            "runtime create/update helpers + domain exceptions"
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
            "meaning": "base registry contract failure, including malformed StudyCard content and translated filesystem failures",
            "not_a_raw_os_exception": True,
        },
        "CardNotFoundError": {
            "semantic_layer": "gateway/domain",
            "meaning": "requested target card is absent for read, StudyCard update execution, or update planning",
            "applies_to": ("get_by_id", "plan_update", "update"),
            "not_a_raw_os_exception": True,
        },
        "CardAlreadyExistsError": {
            "semantic_layer": "gateway/domain",
            "meaning": "create planning or StudyCard create execution targets an already existing card",
            "applies_to": ("plan_create", "create"),
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
            "meaning": "requested StudyCard update conflicts with the frozen state policy",
            "applies_to": ("plan_update", "update"),
            "not_a_raw_os_exception": True,
        },
        "UnsupportedRegistryOperationError": {
            "semantic_layer": "gateway/domain",
            "meaning": "caller requested an operation or input style outside the frozen contract, including unsafe StudyCard lookup IDs",
            "applies_to": _OPERATION_FAMILIES,
            "not_a_raw_os_exception": True,
        },
    }


def describe_referential_integrity_policy() -> dict[str, object]:
    """Describe where direct referenced-card existence checks belong."""

    return describe_integrity_enforcement_policy()


def describe_atomic_write_policy() -> dict[str, str]:
    """Describe the single-card mutation-safety rule used by StudyCard runtime."""

    return {
        "policy": "single-card atomic replace",
        "write_shape": "write-temp-then-replace",
        "guarantee_scope": "one canonical card file per create or update operation",
        "implemented_for": "StudyCard only",
        "durability_steps": "fsync temp file before replace; fsync parent directory after replace",
        "multi_card_transaction_guarantee": "not planned in MVP",
        "concurrent_locking": "not implemented",
    }


def describe_mutation_plan_contract() -> dict[str, object]:
    """Describe the frozen mutation-planning result shape for gateway calls."""

    return {
        "output_type": "MutationPlanDescriptor",
        "required_fields": _MUTATION_PLAN_FIELDS,
        "input_requirement": "full_card_payload",
        "accepted_payload_types": (
            "StudyCardPayload",
            "DatasetCardPayload",
            "ClaimCardPayload",
        ),
        "execution_state": "planned_only",
        "atomicity_expectation": "single-card atomic replace",
        "deferred_execution_note": (
            "planning result only; StudyCard runtime execution lives in separate "
            "gateway helpers and no write occurs during planning"
        ),
    }


def describe_update_policy() -> dict[str, str | bool]:
    """Describe the frozen MVP update-input rule for the gateway."""

    return {
        "style": "full-card replace only",
        "patch_input_supported": False,
        "caller_obligation": "plan_update expects the complete replacement full-card payload",
        "why": (
            "Patch semantics are deferred until merge, validation, and serializer "
            "rules exist."
        ),
    }


def get_study_card(study_id: str) -> StudyCardPayload:
    """Read one StudyCard from its canonical YAML path by canonical ID.

    Inputs:
        `study_id`: canonical `StudyCard` identifier.
    Outputs:
        On success, the gateway returns one bare `StudyCardPayload`
        mapping shaped like the frozen stored-card contract.
    Expected domain errors:
        `CardNotFoundError` when the target card is absent.
    Non-goals:
        This does not read DatasetCard or ClaimCard files.
    """

    try:
        return _runtime_read_study_card(_registry_root(), study_id)
    except Exception as exc:
        raise _translate_study_runtime_error("get_study_card", exc) from exc


def get_dataset_card(dataset_id: str) -> DatasetCardPayload:
    """Planned gateway read for `DatasetCard` retrieval by canonical ID.

    Inputs:
        `dataset_id`: canonical `DatasetCard` identifier.
    Outputs:
        On success, the future gateway returns one bare `DatasetCardPayload`
        mapping shaped like the frozen stored-card contract.
    Expected domain errors:
        `CardNotFoundError` when the target card is absent.
    Non-goals:
        This placeholder does not read files, deserialize data, or validate fields.
    """

    raise _not_implemented("get_dataset_card")


def get_claim_card(claim_id: str) -> ClaimCardPayload:
    """Planned gateway read for `ClaimCard` retrieval by canonical ID.

    Inputs:
        `claim_id`: canonical `ClaimCard` identifier.
    Outputs:
        On success, the future gateway returns one bare `ClaimCardPayload`
        mapping shaped like the frozen stored-card contract.
    Expected domain errors:
        `CardNotFoundError` when the target card is absent.
    Non-goals:
        This placeholder does not read files, deserialize data, or validate fields.
    """

    raise _not_implemented("get_claim_card")


def study_card_exists(study_id: str) -> bool:
    """Check whether the canonical StudyCard YAML file exists.

    Inputs:
        `study_id`: canonical `StudyCard` identifier.
    Outputs:
        `True` if the target exists, otherwise `False`.
    Expected domain errors:
        Missing cards are communicated as `False`, not `CardNotFoundError`.
    Non-goals:
        This does not inspect DatasetCard or ClaimCard storage.
    """

    try:
        return _runtime_study_card_exists(_registry_root(), study_id)
    except Exception as exc:
        raise _translate_study_runtime_error("study_card_exists", exc) from exc


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


def list_study_cards() -> tuple[StudyCardPayload, ...]:
    """List StudyCards stored beneath the canonical StudyCard family directory.

    Inputs:
        None.
    Outputs:
        On success, the gateway returns `tuple[StudyCardPayload, ...]`.
        An empty family listing is an empty tuple.
    Expected domain errors:
        A malformed StudyCard file is translated to `RegistryError`.
    Non-goals:
        This does not traverse DatasetCard or ClaimCard directories.
    """

    try:
        return _runtime_list_study_cards(_registry_root())
    except Exception as exc:
        raise _translate_study_runtime_error("list_study_cards", exc) from exc


def list_dataset_cards() -> tuple[DatasetCardPayload, ...]:
    """Planned gateway listing operation for `DatasetCard` records.

    Inputs:
        None.
    Outputs:
        On success, the future gateway returns `tuple[DatasetCardPayload, ...]`.
        An empty family listing is an empty tuple.
    Expected domain errors:
        None for an empty family listing.
    Non-goals:
        This placeholder does not read files or freeze listing order semantics.
    """

    raise _not_implemented("list_dataset_cards")


def list_claim_cards() -> tuple[ClaimCardPayload, ...]:
    """Planned gateway listing operation for `ClaimCard` records.

    Inputs:
        None.
    Outputs:
        On success, the future gateway returns `tuple[ClaimCardPayload, ...]`.
        An empty family listing is an empty tuple.
    Expected domain errors:
        None for an empty family listing.
    Non-goals:
        This placeholder does not read files or freeze listing order semantics.
    """

    raise _not_implemented("list_claim_cards")


def plan_create_study_card(card: StudyCardPayload) -> MutationPlanDescriptor:
    """Return the StudyCard create planning descriptor without writing storage.

    Inputs:
        `card`: complete `StudyCardPayload` for the planned create operation.
    Outputs:
        On success, the gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardAlreadyExistsError` or `UnsupportedRegistryOperationError`.
    Non-goals:
        This does not perform a write.
    """

    try:
        normalized = normalize_study_card_payload(card)
        if _runtime_study_card_exists(_registry_root(), normalized["study_id"]):
            raise CardAlreadyExistsError(
                "plan_create_study_card targeted a StudyCard that already exists "
                "at its canonical path."
            )
        return _studycard_plan_descriptor("create", normalized["study_id"])
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_study_runtime_error("plan_create_study_card", exc) from exc


def plan_create_dataset_card(card: DatasetCardPayload) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `DatasetCard` create planning.

    Inputs:
        `card`: complete `DatasetCardPayload` for the planned create operation.
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


def plan_create_claim_card(card: ClaimCardPayload) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `ClaimCard` create planning.

    Inputs:
        `card`: complete `ClaimCardPayload` for the planned create operation.
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


def plan_update_study_card(card: StudyCardPayload) -> MutationPlanDescriptor:
    """Return the StudyCard update planning descriptor without writing storage.

    Inputs:
        `card`: complete replacement `StudyCardPayload`. Patch input is out of
        contract for this MVP freeze, and raw argparse objects are not accepted.
    Outputs:
        On success, the gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardNotFoundError`, `InvalidStateTransitionError`,
        or `UnsupportedRegistryOperationError`.
    Non-goals:
        This does not perform a write or merge patches.
    """

    try:
        normalized = normalize_study_card_payload(card)
        current_card = _runtime_read_study_card(_registry_root(), normalized["study_id"])
        ensure_study_card_update_allowed(current_card, normalized)
        return _studycard_plan_descriptor("update", normalized["study_id"])
    except Exception as exc:
        raise _translate_study_runtime_error("plan_update_study_card", exc) from exc


def create_study_card(card: StudyCardPayload) -> StudyCardPayload:
    """Create one StudyCard through the gateway's real runtime path."""

    try:
        return _runtime_create_study_card(_registry_root(), card)
    except Exception as exc:
        raise _translate_study_runtime_error("create_study_card", exc) from exc


def update_study_card(card: StudyCardPayload) -> StudyCardPayload:
    """Replace one StudyCard through the gateway's real runtime path."""

    try:
        return _runtime_update_study_card(_registry_root(), card)
    except Exception as exc:
        raise _translate_study_runtime_error("update_study_card", exc) from exc


def plan_update_dataset_card(card: DatasetCardPayload) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `DatasetCard` update planning.

    Inputs:
        `card`: complete replacement `DatasetCardPayload`. Patch input is out
        of contract for this MVP freeze, and raw argparse objects are not accepted.
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


def plan_update_claim_card(card: ClaimCardPayload) -> MutationPlanDescriptor:
    """Reserve the future gateway contract for `ClaimCard` update planning.

    Inputs:
        `card`: complete replacement `ClaimCardPayload`. Patch input is out of
        contract for this MVP freeze, and raw argparse objects are not accepted.
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
    "create_study_card",
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
    "update_study_card",
]
