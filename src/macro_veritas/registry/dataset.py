"""Static `DatasetCard` contract metadata for MacroVeritas.

This module freezes field names, lifecycle states, and direct relationship
metadata for the first `DatasetCard` slice.

It does not read registry files, resolve real dataset locations, or enforce
schemas at runtime. Boundary docs: `docs/card_contracts.md`,
`docs/registry_model.md`, `docs/state_machine.md`, and
`docs/datasetcard_runtime.md`.
"""

from __future__ import annotations

from typing import Literal

from macro_veritas.shared.types import (
    CardFieldSequence,
    ContractCategoryName,
    DatasetAvailabilityStatus,
    DatasetCardStatus,
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
    "dataset_id",
    "study_id",
    "source_locator",
    "availability_status",
    "modality_scope_tags",
    "cohort_summary",
    "platform_summary",
    "status",
    "locator_confidence_note",
)
_OPTIONAL_FIELDS: CardFieldSequence = (
    "accession_id",
    "artifact_locator",
    "availability_note",
)
_ALLOWED_STATUSES: tuple[DatasetCardStatus, ...] = (
    "identified",
    "registered",
    "bound",
    "retired",
)
_ALLOWED_AVAILABILITY_STATUSES: tuple[DatasetAvailabilityStatus, ...] = (
    "unknown",
    "open",
    "restricted",
    "unavailable",
)
_RELATIONSHIP_POINTERS: RelationshipPointerMap = {
    "study_id": ("StudyCard.study_id",),
}


def object_family_name() -> Literal["DatasetCard"]:
    """Return the documented object-family name for this module.

    Inputs:
        None.
    Outputs:
        The canonical object-family label `DatasetCard`.
    Non-goals:
        This does not create a runtime model class.
    """

    return "DatasetCard"


def describe_object_purpose() -> str:
    """Describe the documented purpose of DatasetCard.

    Inputs:
        None.
    Outputs:
        A short description of why the object family exists.
    Non-goals:
        This does not define a binding workflow or file model.
    """

    return (
        "Represent a dataset associated with a study and its usable project "
        "binding so provenance and location tracking stay explicit."
    )


def contract_version() -> str:
    """Return the frozen contract version for the first card slice."""

    return _CONTRACT_VERSION


def required_fields() -> CardFieldSequence:
    """Return the required `DatasetCard` field names for the frozen slice."""

    return _REQUIRED_FIELDS


def optional_fields() -> CardFieldSequence:
    """Return the optional `DatasetCard` field names for the frozen slice."""

    return _OPTIONAL_FIELDS


def allowed_statuses() -> tuple[DatasetCardStatus, ...]:
    """Return the allowed lifecycle states for `DatasetCard`."""

    return _ALLOWED_STATUSES


def allowed_availability_statuses() -> tuple[DatasetAvailabilityStatus, ...]:
    """Return the allowed availability labels for `DatasetCard`."""

    return _ALLOWED_AVAILABILITY_STATUSES


def relationship_pointers() -> RelationshipPointerMap:
    """Return the direct relationship pointers documented for `DatasetCard`."""

    return _RELATIONSHIP_POINTERS


def list_minimum_contract_categories() -> tuple[ContractCategoryName, ...]:
    """Return the documented minimum contract categories for DatasetCard.

    Inputs:
        None.
    Outputs:
        A tuple of high-level contract categories from `docs/data_contracts.md`.
    Non-goals:
        This does not define required fields within those categories.
    """

    return _CONTRACT_CATEGORIES


def list_lifecycle_states() -> tuple[str, ...]:
    """Return the documented lifecycle states for DatasetCard.

    Inputs:
        None.
    Outputs:
        A tuple of state labels from `docs/state_machine.md`.
    Non-goals:
        This does not transition or validate states.
    """

    return allowed_statuses()


def describe_expected_persistence() -> str:
    """Describe the documented persistence direction for DatasetCard.

    Inputs:
        None.
    Outputs:
        A short description of the planned persistence form.
    Non-goals:
        This does not create files or resolve bindings.
    """

    return (
        "YAML registry card at datasets/<dataset_id>.yaml beneath the configured "
        "registry root."
    )


def storage_field_order() -> CardFieldSequence:
    """Return the canonical DatasetCard field order used for stored YAML."""

    return required_fields() + optional_fields()


__all__ = [
    "allowed_availability_statuses",
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
    "storage_field_order",
]
