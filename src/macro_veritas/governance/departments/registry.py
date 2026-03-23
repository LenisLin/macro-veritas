"""Static descriptors for the registry governance department.

This module freezes the office-level responsibilities and planned function
names for the registry-facing governance domain.

It does not implement registry IO, persistence, or validation logic.
Boundary docs: `docs/governance_spec.md`, `docs/module_map.md`,
`docs/registry_model.md`, and `docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    DescriptorSequence,
    InterfaceDescriptor,
    ObjectFamilyName,
    OfficeDescriptor,
    ReservedCLIFamilyName,
)

_DEPARTMENT_NAME = "registry"
_DEPARTMENT_SCOPE = (
    "Freeze intake, locator-binding, and extraction-planning interfaces for "
    "registry-facing objects without implementing registry IO."
)

_FUNCTIONAL_OFFICES: dict[str, OfficeDescriptor] = {
    "intake_office": {
        "name": "intake_office",
        "governance_label": "登籍司 / Intake Office",
        "purpose": "Define how primary registry objects enter documented project scope.",
        "inputs": (
            "source references",
            "provisional identifiers",
            "provenance notes",
        ),
        "outputs": (
            "StudyCard intake descriptor",
            "DatasetCard intake descriptor",
            "ClaimCard intake descriptor",
        ),
        "core_functions": (
            "register_study_intake",
            "register_dataset_intake",
            "register_claim_intake",
        ),
        "deferred_items": (
            "persistent identifiers",
            "file writes",
            "schema validation",
        ),
    },
    "locator_binding_office": {
        "name": "locator_binding_office",
        "governance_label": "定位司 / Locator Binding Office",
        "purpose": (
            "Define how registry objects will later be associated with "
            "filesystem locations and artifact bundles."
        ),
        "inputs": ("object identity", "locator or path reference", "binding provenance"),
        "outputs": ("locator-binding descriptor",),
        "core_functions": ("bind_dataset_locator", "bind_artifact_locator"),
        "deferred_items": (
            "existence checks",
            "path mutation",
            "storage backend logic",
        ),
    },
    "extraction_planning_office": {
        "name": "extraction_planning_office",
        "governance_label": "摘录司 / Extraction Planning Office",
        "purpose": "Frame planned extraction and metadata-capture tasks without executing them.",
        "inputs": (
            "curated source references",
            "target object-family label",
            "extraction intent",
        ),
        "outputs": ("extraction-task descriptor", "capture-scope note"),
        "core_functions": (
            "propose_claim_extraction_task",
            "propose_metadata_capture_task",
        ),
        "deferred_items": (
            "extraction logic",
            "automated parsing",
            "field-level schemas",
        ),
    },
}

_CORE_FUNCTIONS: dict[str, InterfaceDescriptor] = {
    "register_study_intake": {
        "name": "register_study_intake",
        "purpose": "Describe the planned intake boundary for a study record.",
        "inputs": ("source reference", "provisional identifier", "provenance note"),
        "outputs": ("StudyCard intake descriptor",),
        "non_goals": (
            "file writes",
            "identifier allocation",
            "schema validation",
        ),
    },
    "register_dataset_intake": {
        "name": "register_dataset_intake",
        "purpose": "Describe the planned intake boundary for a dataset record.",
        "inputs": ("source reference", "dataset label", "provenance note"),
        "outputs": ("DatasetCard intake descriptor",),
        "non_goals": (
            "registry mutation",
            "storage inspection",
            "validation logic",
        ),
    },
    "register_claim_intake": {
        "name": "register_claim_intake",
        "purpose": "Describe the planned intake boundary for a claim record.",
        "inputs": ("claim source reference", "claim scope note", "linked study or dataset context"),
        "outputs": ("ClaimCard intake descriptor",),
        "non_goals": (
            "claim extraction",
            "evidence grading",
            "registry writes",
        ),
    },
    "bind_dataset_locator": {
        "name": "bind_dataset_locator",
        "purpose": "Describe how a dataset record should later point to a concrete location.",
        "inputs": ("dataset identity", "locator or path reference", "binding provenance"),
        "outputs": ("dataset locator-binding descriptor",),
        "non_goals": (
            "filesystem checks",
            "path creation",
            "registry updates",
        ),
    },
    "bind_artifact_locator": {
        "name": "bind_artifact_locator",
        "purpose": "Describe how another governed artifact should later point to a concrete location.",
        "inputs": ("artifact identity", "locator or path reference", "binding provenance"),
        "outputs": ("artifact locator-binding descriptor",),
        "non_goals": (
            "artifact creation",
            "path mutation",
            "storage backend logic",
        ),
    },
    "propose_claim_extraction_task": {
        "name": "propose_claim_extraction_task",
        "purpose": "Describe a future claim-extraction task against curated sources.",
        "inputs": ("source reference", "target claim scope", "extraction intent"),
        "outputs": ("claim-extraction task descriptor",),
        "non_goals": (
            "text parsing",
            "NLP",
            "claim creation",
        ),
    },
    "propose_metadata_capture_task": {
        "name": "propose_metadata_capture_task",
        "purpose": "Describe a future metadata-capture task for registry-facing objects.",
        "inputs": ("source reference", "target object-family label", "capture scope"),
        "outputs": ("metadata-capture task descriptor",),
        "non_goals": (
            "schema completion",
            "registry writes",
            "automation",
        ),
    },
}

_OWNED_OBJECT_FAMILIES: tuple[ObjectFamilyName, ...] = (
    "StudyCard",
    "DatasetCard",
    "ClaimCard",
)

_EXPECTED_CLI_FAMILIES: tuple[ReservedCLIFamilyName, ...] = (
    "ingest",
    "show",
    "list",
    "delete",
    "bind",
    "extract",
)

_DEFERRED_CAPABILITIES = (
    "registry IO",
    "identifier allocation",
    "schema validation",
    "persistence workflow",
)


def department_name() -> str:
    """Return the ASCII department name used in code.

    Inputs:
        None.
    Outputs:
        The stable ASCII department name for this module.
    Non-goals:
        This does not expose a persistence namespace.
    """

    return _DEPARTMENT_NAME


def describe_department_scope() -> str:
    """Describe the documented scope of the registry department.

    Inputs:
        None.
    Outputs:
        A concise summary of the registry-facing documentation boundary.
    Non-goals:
        This does not write cards, scan directories, or enforce schemas.
    """

    return _DEPARTMENT_SCOPE


def list_functional_offices() -> DescriptorSequence:
    """List the documented registry offices.

    Inputs:
        None.
    Outputs:
        A tuple of ASCII office names frozen for this department.
    Non-goals:
        This does not create office packages or runtime handlers.
    """

    return tuple(_FUNCTIONAL_OFFICES)


def describe_functional_office(office_name: str) -> OfficeDescriptor | None:
    """Describe a documented registry office.

    Inputs:
        `office_name`: ASCII office name from the governance spec.
    Outputs:
        The office descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not execute intake, binding, or extraction behavior.
    """

    return _FUNCTIONAL_OFFICES.get(office_name)


def list_core_functions() -> DescriptorSequence:
    """List the planned registry core function names.

    Inputs:
        None.
    Outputs:
        A tuple of documented function names frozen for later work.
    Non-goals:
        This does not expose callable registry handlers.
    """

    return tuple(_CORE_FUNCTIONS)


def describe_core_function(function_name: str) -> InterfaceDescriptor | None:
    """Describe a planned registry function.

    Inputs:
        `function_name`: Planned function name from the governance spec.
    Outputs:
        The static interface descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not implement registry IO or card mutation.
    """

    return _CORE_FUNCTIONS.get(function_name)


def list_owned_object_families() -> tuple[ObjectFamilyName, ...]:
    """List object families governed by the registry department.

    Inputs:
        None.
    Outputs:
        A tuple of registry-facing object families owned by this department.
    Non-goals:
        This does not claim that persistence or lifecycle rules are implemented.
    """

    return _OWNED_OBJECT_FAMILIES


def list_expected_cli_families() -> tuple[ReservedCLIFamilyName, ...]:
    """List reserved CLI families associated with the registry department.

    Inputs:
        None.
    Outputs:
        A tuple of reserved registry-adjacent CLI family names.
    Non-goals:
        This does not register CLI parsers or new commands.
    """

    return _EXPECTED_CLI_FAMILIES


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred capabilities for the registry department.

    Inputs:
        None.
    Outputs:
        A tuple of capabilities intentionally left unimplemented.
    Non-goals:
        This does not perform IO or validation.
    """

    return _DEFERRED_CAPABILITIES


__all__ = [
    "department_name",
    "describe_core_function",
    "describe_department_scope",
    "describe_functional_office",
    "list_core_functions",
    "list_deferred_capabilities",
    "list_expected_cli_families",
    "list_functional_offices",
    "list_owned_object_families",
]
