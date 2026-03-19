"""Static descriptors for the personnel governance department.

This module freezes the office-level responsibilities and planned function
names for the personnel domain.

It does not implement identity management, permissions, or staffing workflow.
Boundary docs: `docs/governance_spec.md`, `docs/module_map.md`,
and `docs/architecture.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    DescriptorSequence,
    InterfaceDescriptor,
    ObjectFamilyName,
    OfficeDescriptor,
    ReservedCLIFamilyName,
)

_DEPARTMENT_NAME = "personnel"
_DEPARTMENT_SCOPE = (
    "Freeze human-role vocabulary and responsibility coverage headers for "
    "governed work without implementing identity or authority systems."
)

_FUNCTIONAL_OFFICES: dict[str, OfficeDescriptor] = {
    "role_catalog": {
        "name": "role_catalog",
        "governance_label": "角色簿司 / Role Catalog Office",
        "purpose": (
            "Keep a small stable vocabulary for project roles such as lead, "
            "curator, analyst, reviewer, and auditor."
        ),
        "inputs": ("role label", "documentation context", "responsibility note"),
        "outputs": ("role-profile descriptor", "role-responsibility map"),
        "core_functions": ("define_role_profile", "map_role_responsibilities"),
        "deferred_items": ("directory services", "staffing records", "permissions"),
    },
    "assignment_headers": {
        "name": "assignment_headers",
        "governance_label": "署任司 / Assignment Header Office",
        "purpose": (
            "Describe the documented working owner and routine reviewer for a "
            "governed object or work packet."
        ),
        "inputs": ("artifact or task reference", "role-profile references", "stage note"),
        "outputs": ("ownership header", "review-coverage header"),
        "core_functions": ("assign_working_owner", "assign_review_owner"),
        "deferred_items": ("identity lookup", "workload balancing", "task routing"),
    },
    "escalation_coverage": {
        "name": "escalation_coverage",
        "governance_label": "升核司 / Escalation Coverage Office",
        "purpose": (
            "Document who sponsors escalation and how uncovered ownership gaps "
            "are recorded."
        ),
        "inputs": ("escalation context", "current owner labels", "gap note"),
        "outputs": ("escalation-sponsor descriptor", "coverage-gap note"),
        "core_functions": (
            "declare_escalation_sponsor",
            "record_coverage_gap",
        ),
        "deferred_items": (
            "staffing workflow",
            "notifications",
            "organizational policy enforcement",
        ),
    },
}

_CORE_FUNCTIONS: dict[str, InterfaceDescriptor] = {
    "define_role_profile": {
        "name": "define_role_profile",
        "purpose": "Describe a stable human role used in governance headers.",
        "inputs": ("role label", "scope note", "linked governance references"),
        "outputs": ("role-profile descriptor",),
        "non_goals": (
            "user accounts",
            "authentication",
            "permissions",
        ),
    },
    "map_role_responsibilities": {
        "name": "map_role_responsibilities",
        "purpose": "Describe the documented responsibilities attached to a role label.",
        "inputs": ("role profile", "responsibility statements"),
        "outputs": ("role-responsibility map",),
        "non_goals": (
            "staffing workflow",
            "enforcement",
            "org-chart management",
        ),
    },
    "assign_working_owner": {
        "name": "assign_working_owner",
        "purpose": "Describe the working owner for a governed artifact or work packet.",
        "inputs": ("artifact or task reference", "owner role label", "stage note"),
        "outputs": ("ownership header",),
        "non_goals": (
            "identity resolution",
            "task dispatch",
            "permissions",
        ),
    },
    "assign_review_owner": {
        "name": "assign_review_owner",
        "purpose": "Describe the routine reviewer for a governed artifact or work packet.",
        "inputs": ("artifact or task reference", "reviewer role label", "review context"),
        "outputs": ("review-coverage header",),
        "non_goals": (
            "review execution",
            "case management",
            "assignment automation",
        ),
    },
    "declare_escalation_sponsor": {
        "name": "declare_escalation_sponsor",
        "purpose": "Describe who sponsors escalation when a work unit crosses a higher-risk boundary.",
        "inputs": ("artifact or case reference", "sponsor role label", "escalation context"),
        "outputs": ("escalation-sponsor descriptor",),
        "non_goals": (
            "notifications",
            "workflow routing",
            "organizational approval logic",
        ),
    },
    "record_coverage_gap": {
        "name": "record_coverage_gap",
        "purpose": "Document where ownership or review coverage is still incomplete.",
        "inputs": ("artifact or task reference", "gap statement", "current known owners"),
        "outputs": ("coverage-gap note",),
        "non_goals": (
            "staffing decisions",
            "backfill assignment",
            "issue tracking automation",
        ),
    },
}

_DEFERRED_CAPABILITIES = (
    "authentication",
    "permissions",
    "staffing workflow",
    "identity management",
)


def department_name() -> str:
    """Return the ASCII department name used in code.

    Inputs:
        None.
    Outputs:
        The stable ASCII department name for this module.
    Non-goals:
        This does not encode a user directory or authority model.
    """

    return _DEPARTMENT_NAME


def describe_department_scope() -> str:
    """Describe the documented scope of the personnel department.

    Inputs:
        None.
    Outputs:
        A concise summary of the department's documentation-level scope.
    Non-goals:
        This does not assign permissions or resolve real human ownership.
    """

    return _DEPARTMENT_SCOPE


def list_functional_offices() -> DescriptorSequence:
    """List the documented personnel offices.

    Inputs:
        None.
    Outputs:
        A tuple of ASCII office names frozen for this department.
    Non-goals:
        This does not create office packages or runtime handlers.
    """

    return tuple(_FUNCTIONAL_OFFICES)


def describe_functional_office(office_name: str) -> OfficeDescriptor | None:
    """Describe a documented personnel office.

    Inputs:
        `office_name`: ASCII office name from the governance spec.
    Outputs:
        The office descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not execute office behavior or allocate human resources.
    """

    return _FUNCTIONAL_OFFICES.get(office_name)


def list_core_functions() -> DescriptorSequence:
    """List the planned personnel core function names.

    Inputs:
        None.
    Outputs:
        A tuple of documented function names frozen for later work.
    Non-goals:
        This does not expose callable runtime handlers.
    """

    return tuple(_CORE_FUNCTIONS)


def describe_core_function(function_name: str) -> InterfaceDescriptor | None:
    """Describe a planned personnel function.

    Inputs:
        `function_name`: Planned function name from the governance spec.
    Outputs:
        The static interface descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not implement staffing, permissions, or assignment logic.
    """

    return _CORE_FUNCTIONS.get(function_name)


def list_owned_object_families() -> tuple[ObjectFamilyName, ...]:
    """List object families owned by the personnel department.

    Inputs:
        None.
    Outputs:
        An empty tuple because this department governs roles, not object families.
    Non-goals:
        This does not claim registry or audit ownership.
    """

    return ()


def list_expected_cli_families() -> tuple[ReservedCLIFamilyName, ...]:
    """List reserved CLI families associated with the personnel department.

    Inputs:
        None.
    Outputs:
        An empty tuple because no personnel-facing CLI family is frozen.
    Non-goals:
        This does not reserve hidden commands.
    """

    return ()


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred capabilities for the personnel department.

    Inputs:
        None.
    Outputs:
        A tuple of capabilities intentionally left unimplemented.
    Non-goals:
        This does not implement any deferred capability.
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
