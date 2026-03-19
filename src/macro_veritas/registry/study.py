"""Static `StudyCard` contract metadata for MacroVeritas.

This module freezes field names, lifecycle states, and direct relationship
metadata for the first `StudyCard` slice.

It does not read registry files, manage lifecycle transitions, or enforce
schemas at runtime. Boundary docs: `docs/card_contracts.md`,
`docs/registry_model.md`, and `docs/state_machine.md`.
"""

from __future__ import annotations

from typing import Literal

from macro_veritas.shared.types import (
    CardFieldSequence,
    ContractCategoryName,
    RelationshipPointerMap,
    StudyCardStatus,
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
    "study_id",
    "citation_handle",
    "tumor_scope_tags",
    "therapy_scope_tags",
    "relevance_scope_tags",
    "screening_decision",
    "status",
    "created_from_note",
)
_OPTIONAL_FIELDS: CardFieldSequence = (
    "screening_note",
    "source_artifact_locator",
)
_ALLOWED_STATUSES: tuple[StudyCardStatus, ...] = (
    "draft",
    "registered",
    "closed",
)
_RELATIONSHIP_POINTERS: RelationshipPointerMap = {
    "inbound_from": (
        "DatasetCard.study_id",
        "ClaimCard.study_id",
    ),
}


def object_family_name() -> Literal["StudyCard"]:
    """Return the documented object-family name for this module.

    Inputs:
        None.
    Outputs:
        The canonical object-family label `StudyCard`.
    Non-goals:
        This does not create a runtime model class.
    """

    return "StudyCard"


def describe_object_purpose() -> str:
    """Describe the documented purpose of StudyCard.

    Inputs:
        None.
    Outputs:
        A short description of why the object family exists.
    Non-goals:
        This does not define fields or persistence behavior beyond the docs.
    """

    return (
        "Represent the canonical study or paper unit tracked by the project so "
        "downstream work can refer to one stable study record."
    )


def contract_version() -> str:
    """Return the frozen contract version for the first card slice."""

    return _CONTRACT_VERSION


def required_fields() -> CardFieldSequence:
    """Return the required `StudyCard` field names for the frozen slice."""

    return _REQUIRED_FIELDS


def optional_fields() -> CardFieldSequence:
    """Return the optional `StudyCard` field names for the frozen slice."""

    return _OPTIONAL_FIELDS


def allowed_statuses() -> tuple[StudyCardStatus, ...]:
    """Return the allowed lifecycle states for `StudyCard`."""

    return _ALLOWED_STATUSES


def relationship_pointers() -> RelationshipPointerMap:
    """Return the direct relationship pointers documented for `StudyCard`."""

    return _RELATIONSHIP_POINTERS


def list_minimum_contract_categories() -> tuple[ContractCategoryName, ...]:
    """Return the documented minimum contract categories for StudyCard.

    Inputs:
        None.
    Outputs:
        A tuple of high-level contract categories from `docs/data_contracts.md`.
    Non-goals:
        This does not define required fields within those categories.
    """

    return _CONTRACT_CATEGORIES


def list_lifecycle_states() -> tuple[str, ...]:
    """Return the documented lifecycle states for StudyCard.

    Inputs:
        None.
    Outputs:
        A tuple of state labels from `docs/state_machine.md`.
    Non-goals:
        This does not transition or validate states.
    """

    return allowed_statuses()


def describe_expected_persistence() -> str:
    """Describe the documented persistence direction for StudyCard.

    Inputs:
        None.
    Outputs:
        A short description of the planned persistence form.
    Non-goals:
        This does not create files or naming rules.
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
