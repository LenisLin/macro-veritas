"""Static descriptors for the standards governance department.

This module freezes the office-level responsibilities and planned function
names for naming and contract-boundary governance.

It does not implement lint rules, policy enforcement, or schema governance.
Boundary docs: `docs/governance_spec.md`, `docs/module_map.md`,
and `docs/avcp_guidelines.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    DescriptorSequence,
    InterfaceDescriptor,
    ObjectFamilyName,
    OfficeDescriptor,
    ReservedCLIFamilyName,
)

_DEPARTMENT_NAME = "standards"
_DEPARTMENT_SCOPE = (
    "Freeze naming, contract-boundary, and documentation-discipline standards "
    "so later code layers have a stable contract language."
)

_FUNCTIONAL_OFFICES: dict[str, OfficeDescriptor] = {
    "naming_office": {
        "name": "naming_office",
        "governance_label": "名制司 / Naming Office",
        "purpose": (
            "Keep object-family names, CLI-family names, and descriptor labels "
            "consistent across docs and code."
        ),
        "inputs": ("candidate label", "naming context", "documentation reference"),
        "outputs": ("naming finding", "normalized label note"),
        "core_functions": ("validate_object_naming", "validate_cli_family_name"),
        "deferred_items": (
            "automatic linting",
            "code rewrites",
            "mass rename tooling",
        ),
    },
    "contract_boundary_office": {
        "name": "contract_boundary_office",
        "governance_label": "界约司 / Contract Boundary Office",
        "purpose": (
            "Check that declared inputs, outputs, references, and non-goals "
            "are explicit enough for later implementation work."
        ),
        "inputs": ("draft header", "boundary claims", "linked governance documents"),
        "outputs": ("boundary-validation note", "required-reference note"),
        "core_functions": (
            "validate_contract_boundary",
            "declare_required_references",
        ),
        "deferred_items": (
            "parser-based validation",
            "enforcement",
            "service-level policy",
        ),
    },
    "exception_office": {
        "name": "exception_office",
        "governance_label": "例外司 / Exception Office",
        "purpose": "Document controlled deviations and deferred rule coverage during the freeze.",
        "inputs": ("deviation statement", "rationale", "compensating references"),
        "outputs": ("exception note", "deferred-rule summary"),
        "core_functions": ("record_standard_exception", "summarize_deferred_rule"),
        "deferred_items": (
            "approvals workflow",
            "waiver service",
            "automatic exception tracking",
        ),
    },
}

_CORE_FUNCTIONS: dict[str, InterfaceDescriptor] = {
    "validate_object_naming": {
        "name": "validate_object_naming",
        "purpose": "Describe whether a proposed object-family label matches the frozen naming vocabulary.",
        "inputs": ("candidate object-family label", "naming context", "linked docs"),
        "outputs": ("naming finding",),
        "non_goals": (
            "automatic linting",
            "code rewrites",
            "schema validation",
        ),
    },
    "validate_cli_family_name": {
        "name": "validate_cli_family_name",
        "purpose": "Describe whether a proposed CLI-family label matches the frozen vocabulary.",
        "inputs": ("candidate CLI-family label", "command context", "linked docs"),
        "outputs": ("CLI naming finding",),
        "non_goals": (
            "parser registration",
            "command generation",
            "enforcement",
        ),
    },
    "validate_contract_boundary": {
        "name": "validate_contract_boundary",
        "purpose": "Describe whether a draft header states enough about inputs, outputs, and non-goals.",
        "inputs": ("draft header", "boundary claims", "linked governance documents"),
        "outputs": ("boundary-validation note",),
        "non_goals": (
            "runtime interface checks",
            "schema validation",
            "policy enforcement",
        ),
    },
    "declare_required_references": {
        "name": "declare_required_references",
        "purpose": "Describe which governance references a work unit should cite.",
        "inputs": ("work unit identifier", "boundary type", "reference candidates"),
        "outputs": ("required-reference note",),
        "non_goals": (
            "doc-link enforcement",
            "citation parsing",
            "lint services",
        ),
    },
    "record_standard_exception": {
        "name": "record_standard_exception",
        "purpose": "Describe a documented deviation from the preferred standard.",
        "inputs": ("deviation statement", "rationale", "compensating references"),
        "outputs": ("exception note",),
        "non_goals": (
            "waiver approval",
            "exception tracking automation",
            "runtime overrides",
        ),
    },
    "summarize_deferred_rule": {
        "name": "summarize_deferred_rule",
        "purpose": "Describe a rule that is intentionally deferred beyond the current freeze.",
        "inputs": ("rule topic", "reason for deferral", "linked constraints"),
        "outputs": ("deferred-rule summary",),
        "non_goals": (
            "future implementation",
            "enforcement",
            "workflow automation",
        ),
    },
}

_DEFERRED_CAPABILITIES = (
    "automatic rule enforcement",
    "lint engine",
    "policy service",
)


def department_name() -> str:
    """Return the ASCII department name used in code.

    Inputs:
        None.
    Outputs:
        The stable ASCII department name for this module.
    Non-goals:
        This does not declare a global policy engine.
    """

    return _DEPARTMENT_NAME


def describe_department_scope() -> str:
    """Describe the documented scope of the standards department.

    Inputs:
        None.
    Outputs:
        A concise summary of the department's standards role.
    Non-goals:
        This does not lint code, docs, or interfaces automatically.
    """

    return _DEPARTMENT_SCOPE


def list_functional_offices() -> DescriptorSequence:
    """List the documented standards offices.

    Inputs:
        None.
    Outputs:
        A tuple of ASCII office names frozen for this department.
    Non-goals:
        This does not create office packages or runtime handlers.
    """

    return tuple(_FUNCTIONAL_OFFICES)


def describe_functional_office(office_name: str) -> OfficeDescriptor | None:
    """Describe a documented standards office.

    Inputs:
        `office_name`: ASCII office name from the governance spec.
    Outputs:
        The office descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not execute linting or policy logic.
    """

    return _FUNCTIONAL_OFFICES.get(office_name)


def list_core_functions() -> DescriptorSequence:
    """List the planned standards core function names.

    Inputs:
        None.
    Outputs:
        A tuple of documented function names frozen for later work.
    Non-goals:
        This does not expose callable standards handlers.
    """

    return tuple(_CORE_FUNCTIONS)


def describe_core_function(function_name: str) -> InterfaceDescriptor | None:
    """Describe a planned standards function.

    Inputs:
        `function_name`: Planned function name from the governance spec.
    Outputs:
        The static interface descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not implement linting, policy, or validation services.
    """

    return _CORE_FUNCTIONS.get(function_name)


def list_owned_object_families() -> tuple[ObjectFamilyName, ...]:
    """List object families owned by the standards department.

    Inputs:
        None.
    Outputs:
        An empty tuple because this department governs standards, not objects.
    Non-goals:
        This does not claim registry or review ownership.
    """

    return ()


def list_expected_cli_families() -> tuple[ReservedCLIFamilyName, ...]:
    """List reserved CLI families associated with the standards department.

    Inputs:
        None.
    Outputs:
        An empty tuple because no standards-facing CLI family is frozen.
    Non-goals:
        This does not reserve hidden CLI behavior.
    """

    return ()


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred capabilities for the standards department.

    Inputs:
        None.
    Outputs:
        A tuple of capabilities intentionally left unimplemented.
    Non-goals:
        This does not implement any enforcement mechanism.
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
