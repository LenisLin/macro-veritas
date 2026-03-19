"""A-header descriptor functions for the MacroVeritas governance layer.

This module exposes static metadata about the documented coordination standard
for future non-trivial modules, scripts, and CLI families.

It does not implement orchestration, dispatch, workflow control, or any agent
runtime. Boundary docs: `docs/governance_spec.md`, `docs/architecture.md`,
and `docs/module_map.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    AHeaderLaneName,
    DepartmentName,
    DescriptorMap,
    DescriptorSequence,
    GovernanceDescriptor,
    InterfaceDescriptor,
    ResponsibilityMap,
)

_A_HEADER_ROLE = (
    "A-header is the documentation-led coordination standard for future "
    "non-trivial modules, scripts, and CLI families so mandate, interface "
    "boundaries, and review coverage remain auditable."
)

_A_HEADER_LANES: dict[AHeaderLaneName, GovernanceDescriptor] = {
    "mandate": {
        "name": "mandate",
        "governance_label": "定旨线 / Mandate Lane",
        "purpose": (
            "Freeze why a work unit exists, what scope it covers, and what it "
            "explicitly will not do."
        ),
        "inputs": (
            "proposed work unit name",
            "linked governance references",
            "concise scope statement",
        ),
        "outputs": ("mandate header", "non-goal statement"),
        "core_functions": ("define_work_mandate", "declare_non_goals"),
        "deferred_items": (
            "automatic header generation",
            "orchestration hooks",
            "policy enforcement",
        ),
    },
    "contracts": {
        "name": "contracts",
        "governance_label": "定约线 / Contract Lane",
        "purpose": (
            "Freeze declared inputs, outputs, and governed artifact references "
            "before runtime logic exists."
        ),
        "inputs": (
            "documented input categories",
            "documented output categories",
            "object-family or CLI-family references",
        ),
        "outputs": ("interface-boundary descriptor", "artifact reference list"),
        "core_functions": (
            "declare_input_contract",
            "declare_output_contract",
            "link_governed_artifacts",
        ),
        "deferred_items": (
            "schema validation",
            "runtime contract checking",
            "dispatch wiring",
        ),
    },
    "oversight": {
        "name": "oversight",
        "governance_label": "定责线 / Oversight Lane",
        "purpose": (
            "Freeze ownership, review coverage, and escalation routing at the "
            "documentation level."
        ),
        "inputs": (
            "role labels",
            "review-lane requirements",
            "escalation triggers and department references",
        ),
        "outputs": ("governance-coverage header", "declared review route"),
        "core_functions": (
            "assign_governance_roles",
            "declare_review_route",
        ),
        "deferred_items": (
            "permissions",
            "assignment automation",
            "workflow routing",
        ),
    },
}

_A_HEADER_FUNCTIONS: dict[str, InterfaceDescriptor] = {
    "define_work_mandate": {
        "name": "define_work_mandate",
        "purpose": "Describe the intended mission and scope boundary of a work unit.",
        "inputs": (
            "work unit identifier",
            "scope statement",
            "linked governance references",
        ),
        "outputs": ("mandate descriptor",),
        "non_goals": (
            "runtime execution",
            "policy enforcement",
            "workflow scheduling",
        ),
    },
    "declare_non_goals": {
        "name": "declare_non_goals",
        "purpose": "Record the behaviors and claims that a work unit explicitly does not cover.",
        "inputs": ("work unit identifier", "excluded behavior statements"),
        "outputs": ("non-goal descriptor",),
        "non_goals": (
            "capability enforcement",
            "runtime blocking",
            "automatic compliance checks",
        ),
    },
    "declare_input_contract": {
        "name": "declare_input_contract",
        "purpose": "Describe the high-level inputs a future module or command expects.",
        "inputs": ("work unit identifier", "input categories", "linked object-family references"),
        "outputs": ("input-contract descriptor",),
        "non_goals": (
            "field-level schemas",
            "input parsing",
            "validation logic",
        ),
    },
    "declare_output_contract": {
        "name": "declare_output_contract",
        "purpose": "Describe the high-level outputs a future module or command is allowed to produce.",
        "inputs": ("work unit identifier", "output categories", "artifact intent"),
        "outputs": ("output-contract descriptor",),
        "non_goals": (
            "artifact creation",
            "filesystem writes",
            "serialization logic",
        ),
    },
    "link_governed_artifacts": {
        "name": "link_governed_artifacts",
        "purpose": "Link a work unit to the documented object families or reserved CLI families it governs.",
        "inputs": ("work unit identifier", "object-family references", "reserved CLI-family references"),
        "outputs": ("artifact-reference descriptor",),
        "non_goals": (
            "package import wiring",
            "runtime registration",
            "command exposure",
        ),
    },
    "assign_governance_roles": {
        "name": "assign_governance_roles",
        "purpose": "Describe the documented owner and reviewer roles for a work unit.",
        "inputs": ("work unit identifier", "owner role label", "reviewer role label"),
        "outputs": ("governance-role descriptor",),
        "non_goals": (
            "identity resolution",
            "permissions",
            "task assignment automation",
        ),
    },
    "declare_review_route": {
        "name": "declare_review_route",
        "purpose": "Describe the routine review lane and escalation path for a work unit.",
        "inputs": ("work unit identifier", "routine review lane", "escalation route"),
        "outputs": ("review-route descriptor",),
        "non_goals": (
            "routing automation",
            "case movement",
            "workflow enforcement",
        ),
    },
}

_GOVERNED_DEPARTMENTS: tuple[DepartmentName, ...] = (
    "personnel",
    "registry",
    "standards",
    "operations",
    "infrastructure",
    "review",
)

_GOVERNANCE_DOMAINS: tuple[str, ...] = (
    "macro_veritas.governance.a_header",
    "macro_veritas.governance.departments.personnel",
    "macro_veritas.governance.departments.registry",
    "macro_veritas.governance.departments.standards",
    "macro_veritas.governance.departments.operations",
    "macro_veritas.governance.departments.infrastructure",
    "macro_veritas.governance.departments.review",
    "macro_veritas.prosecution",
)


def describe_a_header_role() -> str:
    """Describe the documented A-header role.

    Inputs:
        None.
    Outputs:
        A concise description of the documented coordination role.
    Non-goals:
        This does not execute governance policy or route work across modules.
    """

    return _A_HEADER_ROLE


def list_a_header_lanes() -> tuple[AHeaderLaneName, ...]:
    """List the documented A-header lanes.

    Inputs:
        None.
    Outputs:
        A tuple of lane names in the current governance freeze.
    Non-goals:
        This does not create a runtime hierarchy or activate lane handlers.
    """

    return tuple(_A_HEADER_LANES)


def describe_a_header_lane(lane_name: str) -> GovernanceDescriptor | None:
    """Describe a documented A-header lane.

    Inputs:
        `lane_name`: ASCII lane name such as `mandate`, `contracts`, or `oversight`.
    Outputs:
        The static lane descriptor when the name is recognized, otherwise `None`.
    Non-goals:
        This does not validate headers or enforce the described lane behavior.
    """

    return _A_HEADER_LANES.get(lane_name)


def list_a_header_core_functions() -> DescriptorSequence:
    """List the planned A-header core function names.

    Inputs:
        None.
    Outputs:
        A tuple of documented function names frozen for later implementation rounds.
    Non-goals:
        This does not expose callable handlers beyond static descriptor lookup.
    """

    return tuple(_A_HEADER_FUNCTIONS)


def describe_a_header_function(function_name: str) -> InterfaceDescriptor | None:
    """Describe a planned A-header function.

    Inputs:
        `function_name`: Planned descriptor function name from the governance spec.
    Outputs:
        The static interface descriptor when the name is recognized, otherwise `None`.
    Non-goals:
        This does not implement the described function behavior.
    """

    return _A_HEADER_FUNCTIONS.get(function_name)


def list_governed_departments() -> tuple[DepartmentName, ...]:
    """List the departments governed beneath A-header.

    Inputs:
        None.
    Outputs:
        A tuple of ASCII department names used by the governance package.
    Non-goals:
        This does not import department modules dynamically or build an org chart.
    """

    return _GOVERNED_DEPARTMENTS


def describe_governance_layers() -> DescriptorMap:
    """Return a concise summary of the documented governance layers.

    Inputs:
        None.
    Outputs:
        A mapping from governance-layer label to documented responsibility.
    Non-goals:
        This does not define runtime hierarchy or workflow transitions.
    """

    return {
        "a_header": "Coordination standard for mandate, contract, and oversight headers.",
        "departments": "Office-level descriptor modules for routine governance responsibilities.",
        "routine_review": "Default audit lane for traceability and readiness review.",
        "prosecution": "Distinct escalated case lane after routine review escalation.",
    }


def list_governance_domains() -> tuple[str, ...]:
    """List the documented governance-domain import paths.

    Inputs:
        None.
    Outputs:
        A tuple of package or module paths that represent governance domains.
    Non-goals:
        This does not import or activate those domains dynamically.
    """

    return _GOVERNANCE_DOMAINS


def summarize_governance_responsibilities() -> ResponsibilityMap:
    """Summarize documented responsibilities across governance layers.

    Inputs:
        None.
    Outputs:
        A mapping from governance layer to concise responsibility statements.
    Non-goals:
        This does not allocate work at runtime or enforce ownership.
    """

    return {
        "a_header": (
            "Keep mandate, contract, and oversight boundaries explicit.",
            "Keep future modules and CLI families auditable before implementation.",
        ),
        "departments": (
            "Hold office-level descriptors inside conservative department modules.",
            "Avoid creating many empty governance subpackages too early.",
        ),
        "prosecution": (
            "Remain distinct from routine review.",
            "Consume escalated audit context rather than replace routine audit.",
        ),
    }


__all__ = [
    "describe_a_header_function",
    "describe_a_header_lane",
    "describe_a_header_role",
    "describe_governance_layers",
    "list_a_header_core_functions",
    "list_a_header_lanes",
    "list_governance_domains",
    "list_governed_departments",
    "summarize_governance_responsibilities",
]
