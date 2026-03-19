"""Static descriptors for the infrastructure governance department.

This module freezes the office-level responsibilities and planned function
names for filesystem-layout, configuration, and runtime-surface governance.

It does not implement deployment, storage backends, or environment automation.
Boundary docs: `docs/governance_spec.md`, `docs/module_map.md`,
and `docs/decisions.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    DescriptorSequence,
    InterfaceDescriptor,
    ObjectFamilyName,
    OfficeDescriptor,
    ReservedCLIFamilyName,
)

_DEPARTMENT_NAME = "infrastructure"
_DEPARTMENT_SCOPE = (
    "Freeze filesystem-layout, configuration-boundary, and runtime-surface "
    "descriptors that support the CLI-first scaffold."
)

_FUNCTIONAL_OFFICES: dict[str, OfficeDescriptor] = {
    "layout_contract_office": {
        "name": "layout_contract_office",
        "governance_label": "形制司 / Layout Contract Office",
        "purpose": (
            "Declare how storage areas and artifact-location families are "
            "described at the governance level."
        ),
        "inputs": ("layout segment", "object or run context", "storage intent"),
        "outputs": ("layout-contract descriptor", "reserved-location note"),
        "core_functions": (
            "declare_layout_contract",
            "reserve_artifact_location_family",
        ),
        "deferred_items": (
            "storage allocation",
            "backend management",
            "layout automation",
        ),
    },
    "config_boundary_office": {
        "name": "config_boundary_office",
        "governance_label": "配置司 / Config Boundary Office",
        "purpose": "Distinguish committed config inputs from derived path or runtime values.",
        "inputs": ("config key", "derived-path reference", "boundary question"),
        "outputs": ("config-boundary note", "config-input descriptor"),
        "core_functions": ("validate_config_boundary", "describe_config_inputs"),
        "deferred_items": (
            "schema migration",
            "environment management",
            "secrets handling",
        ),
    },
    "runtime_surface_office": {
        "name": "runtime_surface_office",
        "governance_label": "运行界面司 / Runtime Surface Office",
        "purpose": "Keep the allowed runtime surface conservative and explicit.",
        "inputs": ("command-surface label", "environment assumption", "constraint source"),
        "outputs": ("runtime-surface note", "constraint record"),
        "core_functions": ("declare_runtime_surface", "record_environment_constraint"),
        "deferred_items": (
            "deployment automation",
            "service provisioning",
            "orchestration runtime",
        ),
    },
}

_CORE_FUNCTIONS: dict[str, InterfaceDescriptor] = {
    "declare_layout_contract": {
        "name": "declare_layout_contract",
        "purpose": "Describe the intended filesystem layout boundary for a governed storage area.",
        "inputs": ("layout segment", "artifact family", "storage intent"),
        "outputs": ("layout-contract descriptor",),
        "non_goals": (
            "directory creation",
            "backend provisioning",
            "filesystem mutation",
        ),
    },
    "reserve_artifact_location_family": {
        "name": "reserve_artifact_location_family",
        "purpose": "Describe a reserved family of artifact locations without binding concrete paths.",
        "inputs": ("artifact family", "location intent", "traceability note"),
        "outputs": ("reserved-location note",),
        "non_goals": (
            "path creation",
            "path validation",
            "storage backend logic",
        ),
    },
    "validate_config_boundary": {
        "name": "validate_config_boundary",
        "purpose": "Describe whether a setting belongs in committed config or derived runtime state.",
        "inputs": ("config key", "derived-path reference", "boundary question"),
        "outputs": ("config-boundary note",),
        "non_goals": (
            "schema enforcement",
            "config migration",
            "environment mutation",
        ),
    },
    "describe_config_inputs": {
        "name": "describe_config_inputs",
        "purpose": "Describe which high-level inputs a future component depends on from project config.",
        "inputs": ("component label", "config keys", "derived path notes"),
        "outputs": ("config-input descriptor",),
        "non_goals": (
            "config loading",
            "runtime validation",
            "secrets management",
        ),
    },
    "declare_runtime_surface": {
        "name": "declare_runtime_surface",
        "purpose": "Describe the allowed runtime surface for a future component or command family.",
        "inputs": ("component or CLI-family label", "allowed surface", "constraint source"),
        "outputs": ("runtime-surface note",),
        "non_goals": (
            "service deployment",
            "command exposure",
            "runtime enforcement",
        ),
    },
    "record_environment_constraint": {
        "name": "record_environment_constraint",
        "purpose": "Describe a documented environment constraint that later code must preserve.",
        "inputs": ("constraint label", "environment assumption", "linked docs"),
        "outputs": ("constraint record",),
        "non_goals": (
            "environment provisioning",
            "runtime checks",
            "automation",
        ),
    },
}

_DEFERRED_CAPABILITIES = (
    "deployment system",
    "environment manager",
    "storage backend",
    "runtime automation layer",
)


def department_name() -> str:
    """Return the ASCII department name used in code.

    Inputs:
        None.
    Outputs:
        The stable ASCII department name for this module.
    Non-goals:
        This does not create infrastructure services.
    """

    return _DEPARTMENT_NAME


def describe_department_scope() -> str:
    """Describe the documented scope of the infrastructure department.

    Inputs:
        None.
    Outputs:
        A concise summary of the infrastructure-facing documentation scope.
    Non-goals:
        This does not allocate storage or mutate the configured layout.
    """

    return _DEPARTMENT_SCOPE


def list_functional_offices() -> DescriptorSequence:
    """List the documented infrastructure offices.

    Inputs:
        None.
    Outputs:
        A tuple of ASCII office names frozen for this department.
    Non-goals:
        This does not create office packages or runtime handlers.
    """

    return tuple(_FUNCTIONAL_OFFICES)


def describe_functional_office(office_name: str) -> OfficeDescriptor | None:
    """Describe a documented infrastructure office.

    Inputs:
        `office_name`: ASCII office name from the governance spec.
    Outputs:
        The office descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not execute filesystem or deployment behavior.
    """

    return _FUNCTIONAL_OFFICES.get(office_name)


def list_core_functions() -> DescriptorSequence:
    """List the planned infrastructure core function names.

    Inputs:
        None.
    Outputs:
        A tuple of documented function names frozen for later work.
    Non-goals:
        This does not expose callable infrastructure handlers.
    """

    return tuple(_CORE_FUNCTIONS)


def describe_core_function(function_name: str) -> InterfaceDescriptor | None:
    """Describe a planned infrastructure function.

    Inputs:
        `function_name`: Planned function name from the governance spec.
    Outputs:
        The static interface descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not implement deployment, storage, or runtime automation.
    """

    return _CORE_FUNCTIONS.get(function_name)


def list_owned_object_families() -> tuple[ObjectFamilyName, ...]:
    """List object families owned by the infrastructure department.

    Inputs:
        None.
    Outputs:
        An empty tuple because this department governs boundaries, not objects.
    Non-goals:
        This does not claim registry or run ownership.
    """

    return ()


def list_expected_cli_families() -> tuple[ReservedCLIFamilyName, ...]:
    """List reserved CLI families associated with the infrastructure department.

    Inputs:
        None.
    Outputs:
        An empty tuple because no infrastructure-facing CLI family is frozen.
    Non-goals:
        This does not expose internal maintenance commands.
    """

    return ()


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred capabilities for the infrastructure department.

    Inputs:
        None.
    Outputs:
        A tuple of capabilities intentionally left unimplemented.
    Non-goals:
        This does not implement any of them.
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
