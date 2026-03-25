"""Registry gateway for the first three MacroVeritas runtime slices.

This module remains the sole internal boundary that higher layers should use to
retrieve or persist first-slice registry cards through frozen payload/DTO
shapes.

Implemented now:
- real file-backed runtime reads, existence checks, listings, create, and
  update for `StudyCard`
- real file-backed runtime reads, existence checks, listings, create, and
  update for `DatasetCard`
- real file-backed runtime reads, existence checks, listings, create, and
  update for `ClaimCard`
- real file-backed runtime delete for `StudyCard`, `DatasetCard`, and
  `ClaimCard`
- planning descriptors for `StudyCard`, `DatasetCard`, and `ClaimCard` create
  and update
- gateway-level `StudyCard` referential-integrity checks for `DatasetCard`
  create and update
- gateway-level `StudyCard` and optional `DatasetCard` referential-integrity
  checks for `ClaimCard` create and update
- gateway-level reverse-dependency checks for `StudyCard` and `DatasetCard`
  delete
- domain-level translation of lower-level StudyCard/DatasetCard/ClaimCard
  filesystem/YAML failures
- internal StudyCard ingest bridge support through `plan_create_study_card`
  plus `create_study_card`
- internal DatasetCard update bridge support through `plan_update_dataset_card`
  plus `update_dataset_card`

Non-goals:
- no CLI wiring
- no scientific logic, evidence grading, or CellVoyager integration

Boundary docs: `docs/registry_io_boundary.md`, `docs/gateway_contracts.md`,
`docs/payload_contracts.md`, `docs/studycard_runtime.md`, and
`docs/datasetcard_runtime.md`, and `docs/claimcard_runtime.md`.
"""

from __future__ import annotations

from pathlib import Path

from macro_veritas.config import load_project_config
from macro_veritas.registry.claim_runtime import (
    ClaimCardFormatError,
    ClaimCardIdentifierError,
    claim_card_exists as _runtime_claim_card_exists,
    create_claim_card as _runtime_create_claim_card,
    delete_claim_card as _runtime_delete_claim_card,
    list_claim_cards as _runtime_list_claim_cards,
    normalize_claim_card_payload,
    read_claim_card as _runtime_read_claim_card,
    update_claim_card as _runtime_update_claim_card,
)
from macro_veritas.registry.dataset_runtime import (
    DatasetCardFormatError,
    DatasetCardIdentifierError,
    create_dataset_card as _runtime_create_dataset_card,
    dataset_card_exists as _runtime_dataset_card_exists,
    delete_dataset_card as _runtime_delete_dataset_card,
    list_dataset_cards as _runtime_list_dataset_cards,
    normalize_dataset_card_payload,
    read_dataset_card as _runtime_read_dataset_card,
    update_dataset_card as _runtime_update_dataset_card,
)
from macro_veritas.registry.errors import (
    BrokenReferenceError,
    CardAlreadyExistsError,
    CardNotFoundError,
    DependencyExistsError,
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
    delete_study_card as _runtime_delete_study_card,
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
        "failure_channel": (
            "missing card is False; unsupported boundary use raises RegistryError subclass"
        ),
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


def _datasetcard_plan_descriptor(
    plan_kind: MutationOperationKind,
    dataset_id: str,
) -> MutationPlanDescriptor:
    integrity_checks_required: tuple[str, ...]
    if plan_kind == "create":
        integrity_checks_required = (
            "referenced StudyCard canonical path must already exist",
            "canonical DatasetCard path must not already exist",
        )
    else:
        integrity_checks_required = (
            "referenced StudyCard canonical path must already exist",
            "canonical DatasetCard path must already exist",
        )

    return {
        "plan_kind": plan_kind,
        "card_family": "DatasetCard",
        "target_id": dataset_id,
        "input_requirement": "full_card_payload",
        "integrity_checks_required": integrity_checks_required,
        "atomicity_expectation": "single-card atomic replace",
        "execution_state": "planned_only",
        "deferred_execution_note": (
            "Planning only. Runtime execution for DatasetCard is available through "
            "create_dataset_card/update_dataset_card."
        ),
    }


def _claimcard_plan_descriptor(
    plan_kind: MutationOperationKind,
    claim_id: str,
) -> MutationPlanDescriptor:
    integrity_checks_required: tuple[str, ...]
    if plan_kind == "create":
        integrity_checks_required = (
            "referenced StudyCard canonical path must already exist",
            "referenced DatasetCard canonical paths must already exist when dataset_ids are present",
            "canonical ClaimCard path must not already exist",
        )
    else:
        integrity_checks_required = (
            "referenced StudyCard canonical path must already exist",
            "referenced DatasetCard canonical paths must already exist when dataset_ids are present",
            "canonical ClaimCard path must already exist",
        )

    return {
        "plan_kind": plan_kind,
        "card_family": "ClaimCard",
        "target_id": claim_id,
        "input_requirement": "full_card_payload",
        "integrity_checks_required": integrity_checks_required,
        "atomicity_expectation": "single-card atomic replace",
        "execution_state": "planned_only",
        "deferred_execution_note": (
            "Planning only. Runtime execution for ClaimCard is available through "
            "create_claim_card/update_claim_card."
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


def _translate_dataset_runtime_error(
    operation_name: str,
    exc: Exception,
) -> RegistryError:
    if isinstance(exc, DatasetCardIdentifierError):
        return UnsupportedRegistryOperationError(str(exc))
    if isinstance(exc, FileNotFoundError):
        return CardNotFoundError(
            f"{operation_name} could not find the requested DatasetCard at its canonical path."
        )
    if isinstance(exc, FileExistsError):
        return CardAlreadyExistsError(
            f"{operation_name} targeted a DatasetCard that already exists at its canonical path."
        )
    if isinstance(exc, DatasetCardFormatError):
        return RegistryError(str(exc))
    if isinstance(exc, OSError):
        return RegistryError(
            f"{operation_name} failed during DatasetCard filesystem access: {exc}"
        )
    return RegistryError(f"{operation_name} failed during DatasetCard runtime translation: {exc}")


def _translate_claim_runtime_error(
    operation_name: str,
    exc: Exception,
) -> RegistryError:
    if isinstance(exc, ClaimCardIdentifierError):
        return UnsupportedRegistryOperationError(str(exc))
    if isinstance(exc, FileNotFoundError):
        return CardNotFoundError(
            f"{operation_name} could not find the requested ClaimCard at its canonical path."
        )
    if isinstance(exc, FileExistsError):
        return CardAlreadyExistsError(
            f"{operation_name} targeted a ClaimCard that already exists at its canonical path."
        )
    if isinstance(exc, ClaimCardFormatError):
        return RegistryError(str(exc))
    if isinstance(exc, OSError):
        return RegistryError(f"{operation_name} failed during ClaimCard filesystem access: {exc}")
    return RegistryError(f"{operation_name} failed during ClaimCard runtime translation: {exc}")


def _require_study_reference_exists(
    operation_name: str,
    study_id: str,
    *,
    referencing_card_family: str,
) -> None:
    try:
        if not _runtime_study_card_exists(_registry_root(), study_id):
            raise BrokenReferenceError(
                f"{operation_name} requires the referenced StudyCard '{study_id}' for "
                f"{referencing_card_family} to exist at its canonical path."
            )
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_study_runtime_error(operation_name, exc) from exc


def _require_claim_dataset_references_exist(
    operation_name: str,
    dataset_ids: list[str],
) -> None:
    missing_dataset_ids: list[str] = []
    for dataset_id in dataset_ids:
        try:
            if not _runtime_dataset_card_exists(_registry_root(), dataset_id):
                if dataset_id not in missing_dataset_ids:
                    missing_dataset_ids.append(dataset_id)
        except RegistryError:
            raise
        except Exception as exc:
            raise _translate_dataset_runtime_error(operation_name, exc) from exc

    if missing_dataset_ids:
        missing_display = ", ".join(missing_dataset_ids)
        raise BrokenReferenceError(
            f"{operation_name} requires referenced DatasetCard(s) to exist at their "
            f"canonical paths: {missing_display}."
        )


def _require_claim_references_exist(
    operation_name: str,
    card: ClaimCardPayload,
) -> None:
    _require_study_reference_exists(
        operation_name,
        card["study_id"],
        referencing_card_family="ClaimCard",
    )
    dataset_ids = card.get("dataset_ids")
    if dataset_ids:
        _require_claim_dataset_references_exist(operation_name, list(dataset_ids))


def _require_delete_target_exists(
    *,
    exists: bool,
    operation_name: str,
    card_family: CardFamilyName,
) -> None:
    if exists:
        return
    raise CardNotFoundError(
        f"{operation_name} could not find the requested {card_family} at its canonical path."
    )


def _require_study_delete_allowed(study_id: str) -> None:
    dependent_dataset_ids = sorted(
        {
            card["dataset_id"]
            for card in list_dataset_cards()
            if card["study_id"] == study_id
        }
    )
    dependent_claim_ids = sorted(
        {
            card["claim_id"]
            for card in list_claim_cards()
            if card["study_id"] == study_id
        }
    )

    if not dependent_dataset_ids and not dependent_claim_ids:
        return

    reasons: list[str] = []
    if dependent_dataset_ids:
        reasons.append(
            "dependent DatasetCard(s) exist: " + ", ".join(dependent_dataset_ids)
        )
    if dependent_claim_ids:
        reasons.append(
            "dependent ClaimCard(s) exist: " + ", ".join(dependent_claim_ids)
        )

    raise DependencyExistsError(
        f"cannot delete StudyCard '{study_id}' because " + "; ".join(reasons) + "."
    )


def _require_dataset_delete_allowed(dataset_id: str) -> None:
    dependent_claim_ids = sorted(
        {
            card["claim_id"]
            for card in list_claim_cards()
            if dataset_id in card.get("dataset_ids", ())
        }
    )
    if not dependent_claim_ids:
        return

    raise DependencyExistsError(
        f"cannot delete DatasetCard '{dataset_id}' because dependent ClaimCard(s) exist: "
        + ", ".join(dependent_claim_ids)
        + "."
    )


def describe_registry_gateway_role() -> dict[str, object]:
    """Describe the frozen role of the registry gateway boundary."""

    return {
        **describe_registry_gateway_boundary(),
        "current_runtime_scope": (
            "StudyCard, DatasetCard, and ClaimCard runtime are implemented"
        ),
        "boundary_status": "studycard-datasetcard-claimcard-runtime",
        "communication_contract_doc": "docs/gateway_contracts.md",
        "payload_contract_doc": "docs/payload_contracts.md",
        "studycard_runtime_doc": "docs/studycard_runtime.md",
        "datasetcard_runtime_doc": "docs/datasetcard_runtime.md",
        "claimcard_runtime_doc": "docs/claimcard_runtime.md",
        "supported_card_families": list_supported_card_families(),
        "operation_families": _OPERATION_FAMILIES,
        "planned_error_categories": list_registry_error_categories(),
        "runtime_real_behavior": {
            "StudyCard": (
                "get",
                "exists",
                "list",
                "plan_create",
                "plan_update",
                "create",
                "update",
                "delete",
            ),
            "DatasetCard": (
                "get",
                "exists",
                "list",
                "plan_create",
                "plan_update",
                "create",
                "update",
                "delete",
            ),
            "ClaimCard": (
                "get",
                "exists",
                "list",
                "plan_create",
                "plan_update",
                "create",
                "update",
                "delete",
            ),
        },
        "result_style": (
            "bare card reads shaped like the frozen card contract + bool exists "
            "+ tuple listings + explicit mutation-plan descriptor + "
            "StudyCard/DatasetCard/ClaimCard runtime create/update/delete helpers + domain exceptions"
        ),
        "internal_command_bridges": {
            "StudyCard_ingest": (
                "macro_veritas.commands.ingest.execute_studycard_ingest -> "
                "plan_create_study_card -> create_study_card"
            ),
            "StudyCard_delete": (
                "macro_veritas.commands.delete.execute_delete_study -> "
                "delete_study_card"
            ),
            "DatasetCard_delete": (
                "macro_veritas.commands.delete.execute_delete_dataset -> "
                "delete_dataset_card"
            ),
            "DatasetCard_update": (
                "macro_veritas.commands.update.execute_update_dataset -> "
                "plan_update_dataset_card -> update_dataset_card"
            ),
            "ClaimCard_delete": (
                "macro_veritas.commands.delete.execute_delete_claim -> "
                "delete_claim_card"
            ),
        },
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
            "meaning": (
                "base registry contract failure, including malformed StudyCard or "
                "DatasetCard or ClaimCard content and translated filesystem failures"
            ),
            "not_a_raw_os_exception": True,
        },
        "CardNotFoundError": {
            "semantic_layer": "gateway/domain",
            "meaning": "requested target card is absent for read, update execution, or update planning",
            "applies_to": ("get_by_id", "plan_update", "update", "delete"),
            "not_a_raw_os_exception": True,
        },
        "CardAlreadyExistsError": {
            "semantic_layer": "gateway/domain",
            "meaning": "create planning or create execution targets an already existing card",
            "applies_to": ("plan_create", "create"),
            "not_a_raw_os_exception": True,
        },
        "BrokenReferenceError": {
            "semantic_layer": "gateway/domain",
            "meaning": "direct gateway-owned referenced-card existence check failed",
            "applies_to": ("plan_create", "plan_update", "create", "update"),
            "not_a_raw_os_exception": True,
        },
        "DependencyExistsError": {
            "semantic_layer": "gateway/domain",
            "meaning": "requested delete would leave dependent registry records behind",
            "applies_to": ("delete",),
            "not_a_raw_os_exception": True,
        },
        "InvalidStateTransitionError": {
            "semantic_layer": "gateway/domain",
            "meaning": (
                "requested StudyCard update conflicts with the frozen state policy"
            ),
            "applies_to": ("plan_update", "update"),
            "not_a_raw_os_exception": True,
        },
        "UnsupportedRegistryOperationError": {
            "semantic_layer": "gateway/domain",
            "meaning": (
                "caller requested an operation or input style outside the frozen contract, "
                "including unsafe StudyCard, DatasetCard, or ClaimCard lookup IDs"
            ),
            "applies_to": _OPERATION_FAMILIES + ("create", "update", "delete"),
            "not_a_raw_os_exception": True,
        },
    }


def describe_referential_integrity_policy() -> dict[str, object]:
    """Describe where direct referenced-card existence checks belong."""

    return describe_integrity_enforcement_policy()


def describe_atomic_write_policy() -> dict[str, str]:
    """Describe the single-card mutation-safety rule used by implemented runtimes."""

    return {
        "policy": "single-card atomic replace",
        "write_shape": "write-temp-then-replace",
        "guarantee_scope": "one canonical card file per create or update operation",
        "implemented_for": "StudyCard, DatasetCard, and ClaimCard",
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
            "planning result only; StudyCard, DatasetCard, and ClaimCard runtime "
            "execution lives in separate gateway helpers and no write occurs during planning"
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
    """Read one DatasetCard from its canonical YAML path by canonical ID.

    Inputs:
        `dataset_id`: canonical `DatasetCard` identifier.
    Outputs:
        On success, the gateway returns one bare `DatasetCardPayload`
        mapping shaped like the frozen stored-card contract.
    Expected domain errors:
        `CardNotFoundError` when the target card is absent.
    Non-goals:
        This does not read ClaimCard files.
    """

    try:
        return _runtime_read_dataset_card(_registry_root(), dataset_id)
    except Exception as exc:
        raise _translate_dataset_runtime_error("get_dataset_card", exc) from exc


def get_claim_card(claim_id: str) -> ClaimCardPayload:
    """Read one ClaimCard from its canonical YAML path by canonical ID.

    Inputs:
        `claim_id`: canonical `ClaimCard` identifier.
    Outputs:
        On success, the gateway returns one bare `ClaimCardPayload`
        mapping shaped like the frozen stored-card contract.
    Expected domain errors:
        `CardNotFoundError` when the target card is absent.
    Non-goals:
        This does not read StudyCard or DatasetCard files directly.
    """

    try:
        return _runtime_read_claim_card(_registry_root(), claim_id)
    except Exception as exc:
        raise _translate_claim_runtime_error("get_claim_card", exc) from exc


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
    """Check whether the canonical DatasetCard YAML file exists.

    Inputs:
        `dataset_id`: canonical `DatasetCard` identifier.
    Outputs:
        `True` if the target exists, otherwise `False`.
    Expected domain errors:
        Missing cards are communicated as `False`, not `CardNotFoundError`.
    Non-goals:
        This does not inspect ClaimCard storage.
    """

    try:
        return _runtime_dataset_card_exists(_registry_root(), dataset_id)
    except Exception as exc:
        raise _translate_dataset_runtime_error("dataset_card_exists", exc) from exc


def claim_card_exists(claim_id: str) -> bool:
    """Check whether the canonical ClaimCard YAML file exists.

    Inputs:
        `claim_id`: canonical `ClaimCard` identifier.
    Outputs:
        `True` if the target exists, otherwise `False`.
    Expected domain errors:
        Missing cards are communicated as `False`, not `CardNotFoundError`.
    Non-goals:
        This does not inspect StudyCard or DatasetCard storage.
    """

    try:
        return _runtime_claim_card_exists(_registry_root(), claim_id)
    except Exception as exc:
        raise _translate_claim_runtime_error("claim_card_exists", exc) from exc


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
    """List DatasetCards stored beneath the canonical DatasetCard family directory.

    Inputs:
        None.
    Outputs:
        On success, the gateway returns `tuple[DatasetCardPayload, ...]`.
        An empty family listing is an empty tuple.
    Expected domain errors:
        A malformed DatasetCard file is translated to `RegistryError`.
    Non-goals:
        This does not traverse ClaimCard directories.
    """

    try:
        return _runtime_list_dataset_cards(_registry_root())
    except Exception as exc:
        raise _translate_dataset_runtime_error("list_dataset_cards", exc) from exc


def list_claim_cards() -> tuple[ClaimCardPayload, ...]:
    """List ClaimCards stored beneath the canonical ClaimCard family directory.

    Inputs:
        None.
    Outputs:
        On success, the gateway returns `tuple[ClaimCardPayload, ...]`.
        An empty family listing is an empty tuple.
    Expected domain errors:
        A malformed ClaimCard file is translated to `RegistryError`.
    Non-goals:
        This does not traverse StudyCard or DatasetCard directories.
    """

    try:
        return _runtime_list_claim_cards(_registry_root())
    except Exception as exc:
        raise _translate_claim_runtime_error("list_claim_cards", exc) from exc


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
    """Return the DatasetCard create planning descriptor without writing storage.

    Inputs:
        `card`: complete `DatasetCardPayload` for the planned create operation.
    Outputs:
        On success, the gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardAlreadyExistsError`, `BrokenReferenceError`,
        or `UnsupportedRegistryOperationError`.
    Non-goals:
        This does not perform a write.
    """

    try:
        normalized = normalize_dataset_card_payload(card)
        _require_study_reference_exists(
            "plan_create_dataset_card",
            normalized["study_id"],
            referencing_card_family="DatasetCard",
        )
        if _runtime_dataset_card_exists(_registry_root(), normalized["dataset_id"]):
            raise CardAlreadyExistsError(
                "plan_create_dataset_card targeted a DatasetCard that already exists "
                "at its canonical path."
            )
        return _datasetcard_plan_descriptor("create", normalized["dataset_id"])
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_dataset_runtime_error("plan_create_dataset_card", exc) from exc


def plan_create_claim_card(card: ClaimCardPayload) -> MutationPlanDescriptor:
    """Return the ClaimCard create planning descriptor without writing storage.

    Inputs:
        `card`: complete `ClaimCardPayload` for the planned create operation.
    Outputs:
        On success, the gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardAlreadyExistsError`, `BrokenReferenceError`,
        or `UnsupportedRegistryOperationError`.
    Non-goals:
        This does not perform a write.
    """

    try:
        normalized = normalize_claim_card_payload(card)
        _require_claim_references_exist("plan_create_claim_card", normalized)
        if _runtime_claim_card_exists(_registry_root(), normalized["claim_id"]):
            raise CardAlreadyExistsError(
                "plan_create_claim_card targeted a ClaimCard that already exists "
                "at its canonical path."
            )
        return _claimcard_plan_descriptor("create", normalized["claim_id"])
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_claim_runtime_error("plan_create_claim_card", exc) from exc


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


def delete_study_card(study_id: str) -> None:
    """Delete one StudyCard through the gateway's real runtime path."""

    try:
        _require_delete_target_exists(
            exists=_runtime_study_card_exists(_registry_root(), study_id),
            operation_name="delete_study_card",
            card_family="StudyCard",
        )
        _require_study_delete_allowed(study_id)
        _runtime_delete_study_card(_registry_root(), study_id)
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_study_runtime_error("delete_study_card", exc) from exc


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


def create_dataset_card(card: DatasetCardPayload) -> DatasetCardPayload:
    """Create one DatasetCard through the gateway's real runtime path."""

    try:
        normalized = normalize_dataset_card_payload(card)
        _require_study_reference_exists(
            "create_dataset_card",
            normalized["study_id"],
            referencing_card_family="DatasetCard",
        )
        return _runtime_create_dataset_card(_registry_root(), normalized)
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_dataset_runtime_error("create_dataset_card", exc) from exc


def update_dataset_card(card: DatasetCardPayload) -> DatasetCardPayload:
    """Replace one DatasetCard through the gateway's real runtime path."""

    try:
        normalized = normalize_dataset_card_payload(card)
        _require_study_reference_exists(
            "update_dataset_card",
            normalized["study_id"],
            referencing_card_family="DatasetCard",
        )
        return _runtime_update_dataset_card(_registry_root(), normalized)
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_dataset_runtime_error("update_dataset_card", exc) from exc


def plan_update_dataset_card(card: DatasetCardPayload) -> MutationPlanDescriptor:
    """Return the DatasetCard update planning descriptor without writing storage.

    Inputs:
        `card`: complete replacement `DatasetCardPayload`. Patch input is out
        of contract for this MVP freeze, and raw argparse objects are not accepted.
    Outputs:
        On success, the gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardNotFoundError`, `BrokenReferenceError`,
        or `UnsupportedRegistryOperationError`.
    Non-goals:
        This does not perform a write or merge patches.
    """

    try:
        normalized = normalize_dataset_card_payload(card)
        _require_study_reference_exists(
            "plan_update_dataset_card",
            normalized["study_id"],
            referencing_card_family="DatasetCard",
        )
        _runtime_read_dataset_card(_registry_root(), normalized["dataset_id"])
        return _datasetcard_plan_descriptor("update", normalized["dataset_id"])
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_dataset_runtime_error("plan_update_dataset_card", exc) from exc


def delete_dataset_card(dataset_id: str) -> None:
    """Delete one DatasetCard through the gateway's real runtime path."""

    try:
        _require_delete_target_exists(
            exists=_runtime_dataset_card_exists(_registry_root(), dataset_id),
            operation_name="delete_dataset_card",
            card_family="DatasetCard",
        )
        _require_dataset_delete_allowed(dataset_id)
        _runtime_delete_dataset_card(_registry_root(), dataset_id)
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_dataset_runtime_error("delete_dataset_card", exc) from exc


def create_claim_card(card: ClaimCardPayload) -> ClaimCardPayload:
    """Create one ClaimCard through the gateway's real runtime path."""

    try:
        normalized = normalize_claim_card_payload(card)
        _require_claim_references_exist("create_claim_card", normalized)
        return _runtime_create_claim_card(_registry_root(), normalized)
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_claim_runtime_error("create_claim_card", exc) from exc


def update_claim_card(card: ClaimCardPayload) -> ClaimCardPayload:
    """Replace one ClaimCard through the gateway's real runtime path."""

    try:
        normalized = normalize_claim_card_payload(card)
        _require_claim_references_exist("update_claim_card", normalized)
        return _runtime_update_claim_card(_registry_root(), normalized)
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_claim_runtime_error("update_claim_card", exc) from exc


def plan_update_claim_card(card: ClaimCardPayload) -> MutationPlanDescriptor:
    """Return the ClaimCard update planning descriptor without writing storage.

    Inputs:
        `card`: complete replacement `ClaimCardPayload`. Patch input is out of
        contract for this MVP freeze, and raw argparse objects are not accepted.
    Outputs:
        On success, the gateway returns a `MutationPlanDescriptor`.
    Expected domain errors:
        `CardNotFoundError`, `BrokenReferenceError`,
        or `UnsupportedRegistryOperationError`.
    Non-goals:
        This does not perform a write or merge patches.
    """

    try:
        normalized = normalize_claim_card_payload(card)
        _require_claim_references_exist("plan_update_claim_card", normalized)
        _runtime_read_claim_card(_registry_root(), normalized["claim_id"])
        return _claimcard_plan_descriptor("update", normalized["claim_id"])
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_claim_runtime_error("plan_update_claim_card", exc) from exc


def delete_claim_card(claim_id: str) -> None:
    """Delete one ClaimCard through the gateway's real runtime path."""

    try:
        _require_delete_target_exists(
            exists=_runtime_claim_card_exists(_registry_root(), claim_id),
            operation_name="delete_claim_card",
            card_family="ClaimCard",
        )
        _runtime_delete_claim_card(_registry_root(), claim_id)
    except RegistryError:
        raise
    except Exception as exc:
        raise _translate_claim_runtime_error("delete_claim_card", exc) from exc


__all__ = [
    "claim_card_exists",
    "create_claim_card",
    "create_dataset_card",
    "create_study_card",
    "delete_claim_card",
    "delete_dataset_card",
    "delete_study_card",
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
    "update_claim_card",
    "update_dataset_card",
    "update_study_card",
]
