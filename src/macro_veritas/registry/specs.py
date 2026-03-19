"""Registry-level descriptor functions for MacroVeritas.

This module exposes static metadata about documented registry object families,
their frozen first-slice layout, the planned gateway boundary, and the current
implementation boundary.

It does not implement persistence, lookup, or schema validation.
Boundary docs: `docs/module_map.md`, `docs/registry_layout.md`,
`docs/registry_io_boundary.md`, `docs/registry_model.md`, and
`docs/data_contracts.md`.
"""

from __future__ import annotations

from macro_veritas.registry.layout import describe_first_slice_layout
from macro_veritas.shared.naming import registry_subdir_names
from macro_veritas.shared.types import DescriptorSequence, ObjectFamilyName

_REGISTRY_OBJECT_FAMILIES: tuple[ObjectFamilyName, ...] = (
    "StudyCard",
    "DatasetCard",
    "ClaimCard",
    "MethodCard",
    "ReanalysisBundle",
    "EvidenceCard",
    "AuditRecord",
)
_PRIMARY_TOPOLOGY = "entity-segregated-roots"
_STATE_LOCATION_STRATEGY = "static-file-location + internal status field update"
_REGISTRY_ERROR_CATEGORIES: tuple[str, ...] = (
    "RegistryError",
    "CardNotFoundError",
    "CardAlreadyExistsError",
    "BrokenReferenceError",
    "InvalidStateTransitionError",
    "UnsupportedRegistryOperationError",
)


def list_registry_object_families() -> tuple[ObjectFamilyName, ...]:
    """Return the documented registry object families.

    Inputs:
        None.
    Outputs:
        A tuple of object families named in `docs/registry_model.md`.
    Non-goals:
        This does not create models or infer additional families.
    """

    return _REGISTRY_OBJECT_FAMILIES


def describe_registry_topology() -> dict[str, object]:
    """Describe the frozen primary registry topology for the first slice.

    Inputs:
        None.
    Outputs:
        A static metadata mapping for the chosen filesystem topology.
    Non-goals:
        This does not inspect the registry or allocate directories.
    """

    return {
        "primary_topology": _PRIMARY_TOPOLOGY,
        "registry_root_policy": (
            "Use the configured registry root beneath the project data root and "
            "place first-slice cards in family-specific subdirectories."
        ),
        "top_level_subdirectories": list_registry_roots(),
        "one_card_per_file": True,
        "why": (
            "Stable family roots keep paths predictable and avoid coupling card "
            "location to study-directory nesting."
        ),
    }


def list_registry_roots() -> tuple[str, ...]:
    """Return the canonical first-slice registry subdirectories.

    Inputs:
        None.
    Outputs:
        A tuple of subdirectory names beneath the resolved registry root.
    Non-goals:
        This does not create or inspect those directories.
    """

    return registry_subdir_names()


def describe_state_location_strategy() -> dict[str, str]:
    """Describe how lifecycle state relates to filesystem placement.

    Inputs:
        None.
    Outputs:
        A mapping that records the frozen v0.1 state-location policy.
    Non-goals:
        This does not move files or validate transition rules.
    """

    return {
        "strategy": _STATE_LOCATION_STRATEGY,
        "physical_move_on_status_change": "no",
        "rule": (
            "Card files remain in their canonical family subdirectory for their "
            "entire lifetime; status changes update only card fields."
        ),
        "why": (
            "Stable locations keep references simple and avoid turning lifecycle "
            "updates into filesystem operations."
        ),
    }


def describe_cross_reference_strategy() -> dict[str, str]:
    """Describe the frozen first-slice cross-reference resolution policy.

    Inputs:
        None.
    Outputs:
        A mapping that records the direct ID-based conceptual resolution rules.
    Non-goals:
        This does not implement a resolver, index, or manifest.
    """

    return {
        "mode": "direct-id-to-canonical-path",
        "DatasetCard.study_id": "studies/<study_id>.yaml",
        "ClaimCard.study_id": "studies/<study_id>.yaml",
        "ClaimCard.dataset_ids": "datasets/<dataset_id>.yaml for each listed dataset_id",
        "backlinks": "not stored",
        "index_engine": "not implemented",
    }


def describe_registry_gateway_boundary() -> dict[str, str]:
    """Describe the frozen future access boundary for registry operations.

    Inputs:
        None.
    Outputs:
        A static mapping that defines caller responsibilities around registry access.
    Non-goals:
        This does not implement a gateway, repository, serializer, or filesystem access.
    """

    return {
        "source_of_truth_doc": "docs/registry_io_boundary.md",
        "cli_layer": "must not do raw path traversal or raw file access for registry cards",
        "governance_layer": "must not do raw file access for registry cards",
        "gateway_role": (
            "sole planned internal boundary for StudyCard/DatasetCard/ClaimCard "
            "retrieval and persistence"
        ),
        "serialization_layer": "future internal dependency beneath the gateway only",
        "layout_layer": "static naming/path helper layer only",
    }


def list_registry_error_categories() -> tuple[str, ...]:
    """Return the frozen minimum planned registry error categories.

    Inputs:
        None.
    Outputs:
        A tuple of planned registry exception category names.
    Non-goals:
        This does not raise or route those exceptions.
    """

    return _REGISTRY_ERROR_CATEGORIES


def describe_integrity_enforcement_policy() -> dict[str, object]:
    """Describe the frozen referential-integrity rule for future registry access.

    Inputs:
        None.
    Outputs:
        A static mapping describing where direct reference existence checks belong.
    Non-goals:
        This does not validate cards or inspect the registry.
    """

    return {
        "enforcement_point": "registry gateway",
        "scope": "direct referenced-card existence checks for create and update operations",
        "DatasetCard": "must confirm referenced StudyCard exists",
        "ClaimCard": (
            "must confirm referenced StudyCard exists and each referenced "
            "DatasetCard exists"
        ),
        "governance_layer": (
            "may add higher-level policy checks but does not replace gateway-level "
            "existence enforcement"
        ),
    }


def describe_registry_persistence_forms() -> dict[ObjectFamilyName, str]:
    """Describe the documented persistence form for each object family.

    Inputs:
        None.
    Outputs:
        A mapping from object family to its documented persistence direction.
    Non-goals:
        This does not serialize objects or inspect the filesystem.
    """

    first_slice_layout = describe_first_slice_layout()

    return {
        "StudyCard": (
            "Planned YAML registry card at "
            f"{first_slice_layout['StudyCard']['root_subdir']}/<study_id>.yaml."
        ),
        "DatasetCard": (
            "Planned YAML registry card at "
            f"{first_slice_layout['DatasetCard']['root_subdir']}/<dataset_id>.yaml "
            "with raw/processed references."
        ),
        "ClaimCard": (
            "Planned YAML registry card at "
            f"{first_slice_layout['ClaimCard']['root_subdir']}/<claim_id>.yaml."
        ),
        "MethodCard": "Planned YAML registry card.",
        "ReanalysisBundle": "Planned directory artifact under runs/ with a small manifest.",
        "EvidenceCard": "Planned YAML registry card with supporting-artifact links.",
        "AuditRecord": "Planned YAML registry card with optional report links.",
    }


def describe_registry_boundaries() -> DescriptorSequence:
    """Summarize the current registry non-goals and constraints.

    Inputs:
        None.
    Outputs:
        A tuple of high-level boundary statements for the registry domain.
    Non-goals:
        This does not validate or enforce those boundaries.
    """

    return (
        "Registry objects are documented only; exact field schemas are deferred.",
        "First-slice filesystem placement is frozen by docs and static helpers only.",
        "Future registry card retrieval and persistence are reserved to macro_veritas.registry.gateway.",
        "No registry IO or object-store behavior is implemented.",
        "No validation framework or referential-integrity engine is implemented.",
    )


__all__ = [
    "describe_cross_reference_strategy",
    "describe_integrity_enforcement_policy",
    "describe_registry_gateway_boundary",
    "describe_registry_boundaries",
    "describe_registry_persistence_forms",
    "describe_registry_topology",
    "describe_state_location_strategy",
    "list_registry_error_categories",
    "list_registry_object_families",
    "list_registry_roots",
]
