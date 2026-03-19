"""Static `ClaimCard` contract metadata for MacroVeritas.

This module freezes field names, lifecycle states, and direct relationship
metadata for the first `ClaimCard` slice.

It does not extract claims, grade evidence, or enforce schemas at runtime.
Boundary docs: `docs/card_contracts.md`, `docs/registry_model.md`,
and `docs/state_machine.md`.
"""

from __future__ import annotations

from typing import Literal

from macro_veritas.shared.types import (
    CardFieldSequence,
    ClaimCardStatus,
    ContractCategoryName,
    RelationshipPointerMap,
)

_CONTRACT_CATEGORIES: tuple[ContractCategoryName, ...] = (
    "identity",
    "provenance",
    "status",
    "ownership / producer",
    "artifact location / persistence",
)
_CONTRACT_VERSION = "2026-03-first-slice"
_REQUIRED_FIELDS: CardFieldSequence = (
    "claim_id",
    "study_id",
    "claim_text",
    "claim_type",
    "provenance_pointer",
    "status",
    "review_readiness",
    "created_from_note",
)
_OPTIONAL_FIELDS: CardFieldSequence = (
    "dataset_ids",
    "claim_summary_handle",
)
_ALLOWED_STATUSES: tuple[ClaimCardStatus, ...] = (
    "captured",
    "scoped",
    "ready",
    "closed",
)
_RELATIONSHIP_POINTERS: RelationshipPointerMap = {
    "study_id": ("StudyCard.study_id",),
    "dataset_ids": ("DatasetCard.dataset_id",),
}


def object_family_name() -> Literal["ClaimCard"]:
    """Return the documented object-family name for this module.

    Inputs:
        None.
    Outputs:
        The canonical object-family label `ClaimCard`.
    Non-goals:
        This does not create a runtime model class.
    """

    return "ClaimCard"


def describe_object_purpose() -> str:
    """Describe the documented purpose of ClaimCard.

    Inputs:
        None.
    Outputs:
        A short description of why the object family exists.
    Non-goals:
        This does not extract claims or infer scientific truth.
    """

    return (
        "Represent one scoped claim that the project may later examine so the "
        "system remains claim-centered and evaluation units stay explicit."
    )


def contract_version() -> str:
    """Return the frozen contract version for the first card slice."""

    return _CONTRACT_VERSION


def required_fields() -> CardFieldSequence:
    """Return the required `ClaimCard` field names for the frozen slice."""

    return _REQUIRED_FIELDS


def optional_fields() -> CardFieldSequence:
    """Return the optional `ClaimCard` field names for the frozen slice."""

    return _OPTIONAL_FIELDS


def allowed_statuses() -> tuple[ClaimCardStatus, ...]:
    """Return the allowed lifecycle states for `ClaimCard`."""

    return _ALLOWED_STATUSES


def relationship_pointers() -> RelationshipPointerMap:
    """Return the direct relationship pointers documented for `ClaimCard`."""

    return _RELATIONSHIP_POINTERS


def list_minimum_contract_categories() -> tuple[ContractCategoryName, ...]:
    """Return the documented minimum contract categories for ClaimCard.

    Inputs:
        None.
    Outputs:
        A tuple of high-level contract categories from `docs/data_contracts.md`.
    Non-goals:
        This does not define required fields within those categories.
    """

    return _CONTRACT_CATEGORIES


def list_lifecycle_states() -> tuple[str, ...]:
    """Return the documented lifecycle states for ClaimCard.

    Inputs:
        None.
    Outputs:
        A tuple of state labels from `docs/state_machine.md`.
    Non-goals:
        This does not transition or validate states.
    """

    return allowed_statuses()


def describe_expected_persistence() -> str:
    """Describe the documented persistence direction for ClaimCard.

    Inputs:
        None.
    Outputs:
        A short description of the planned persistence form.
    Non-goals:
        This does not create files or define a claim schema.
    """

    return "Planned YAML registry card under the registry/ area."


__all__ = [
    "allowed_statuses",
    "contract_version",
    "describe_expected_persistence",
    "describe_object_purpose",
    "list_lifecycle_states",
    "list_minimum_contract_categories",
    "object_family_name",
    "optional_fields",
    "relationship_pointers",
    "required_fields",
]
