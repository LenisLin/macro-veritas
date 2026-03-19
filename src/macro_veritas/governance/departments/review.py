"""Static descriptors for the routine review governance department.

This module freezes the office-level responsibilities and planned function
names for the routine audit and review lane.

It does not implement an audit engine, grading logic, or prosecution workflow.
Boundary docs: `docs/governance_spec.md`, `docs/module_map.md`,
`docs/audit_policy.md`, and `docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    DescriptorSequence,
    InterfaceDescriptor,
    ObjectFamilyName,
    OfficeDescriptor,
    ReservedCLIFamilyName,
)

_DEPARTMENT_NAME = "review"
_DEPARTMENT_SCOPE = (
    "Freeze the routine review and audit lane used for traceability, linkage, "
    "readiness, and escalation decisions without merging it into prosecution."
)

_FUNCTIONAL_OFFICES: dict[str, OfficeDescriptor] = {
    "audit_intake_office": {
        "name": "audit_intake_office",
        "governance_label": "受核司 / Audit Intake Office",
        "purpose": "Define the scope of a routine audit check at a high-value transition point.",
        "inputs": ("object or bundle reference", "stage transition", "traceability concerns"),
        "outputs": ("audit-check descriptor", "scope-confirmation note"),
        "core_functions": ("propose_audit_check", "confirm_audit_scope"),
        "deferred_items": (
            "automatic trigger evaluation",
            "review queue management",
            "audit scheduling",
        ),
    },
    "audit_record_office": {
        "name": "audit_record_office",
        "governance_label": "审记司 / Audit Record Office",
        "purpose": "Define the documented pass and return outcomes of routine audit.",
        "inputs": ("audit-check descriptor", "findings summary", "follow-up notes"),
        "outputs": ("AuditRecord header", "return note"),
        "core_functions": ("record_audit_pass", "record_audit_return"),
        "deferred_items": (
            "evidence grading",
            "scoring",
            "adjudication engine",
        ),
    },
    "escalation_gate_office": {
        "name": "escalation_gate_office",
        "governance_label": "移送司 / Escalation Gate Office",
        "purpose": (
            "Hand materially disputed or high-risk cases from routine review "
            "to prosecution without merging the two lanes."
        ),
        "inputs": ("audit record reference", "escalation rationale", "supporting context"),
        "outputs": ("escalation-packet descriptor", "prosecution handoff note"),
        "core_functions": ("escalate_review_case", "assemble_escalation_packet"),
        "deferred_items": (
            "automated escalation",
            "sanctions",
            "case tracking",
        ),
    },
}

_CORE_FUNCTIONS: dict[str, InterfaceDescriptor] = {
    "propose_audit_check": {
        "name": "propose_audit_check",
        "purpose": "Describe a planned routine audit check at a documented transition point.",
        "inputs": ("object or bundle reference", "stage transition", "traceability concerns"),
        "outputs": ("audit-check descriptor",),
        "non_goals": (
            "review execution",
            "scoring",
            "automated triggers",
        ),
    },
    "confirm_audit_scope": {
        "name": "confirm_audit_scope",
        "purpose": "Describe the boundaries and questions a routine audit should cover.",
        "inputs": ("audit-check descriptor", "scope statements", "linked docs"),
        "outputs": ("scope-confirmation note",),
        "non_goals": (
            "evidence grading",
            "scientific judgment",
            "case management",
        ),
    },
    "record_audit_pass": {
        "name": "record_audit_pass",
        "purpose": "Describe a routine audit pass outcome and its traceability basis.",
        "inputs": ("audit-check descriptor", "findings summary", "readiness note"),
        "outputs": ("AuditRecord pass header",),
        "non_goals": (
            "runtime audit execution",
            "grading logic",
            "artifact mutation",
        ),
    },
    "record_audit_return": {
        "name": "record_audit_return",
        "purpose": "Describe a routine audit return outcome and its required follow-up.",
        "inputs": ("audit-check descriptor", "findings summary", "required follow-up"),
        "outputs": ("AuditRecord return header",),
        "non_goals": (
            "issue remediation",
            "automatic reassignment",
            "case escalation",
        ),
    },
    "escalate_review_case": {
        "name": "escalate_review_case",
        "purpose": "Describe the handoff of a materially disputed or high-risk case to prosecution.",
        "inputs": ("audit record reference", "escalation rationale", "supporting context"),
        "outputs": ("prosecution handoff note",),
        "non_goals": (
            "automated escalation",
            "sanctions",
            "prosecution workflow",
        ),
    },
    "assemble_escalation_packet": {
        "name": "assemble_escalation_packet",
        "purpose": "Describe the materials that should accompany an escalated review case.",
        "inputs": ("audit record reference", "attached artifacts", "open questions"),
        "outputs": ("escalation-packet descriptor",),
        "non_goals": (
            "case management",
            "evidence grading",
            "workflow automation",
        ),
    },
}

_OWNED_OBJECT_FAMILIES: tuple[ObjectFamilyName, ...] = ("AuditRecord",)

_EXPECTED_CLI_FAMILIES: tuple[ReservedCLIFamilyName, ...] = ("audit",)

_DEFERRED_CAPABILITIES = (
    "audit engine",
    "adjudication system",
    "evidence grading engine",
)


def department_name() -> str:
    """Return the ASCII department name used in code.

    Inputs:
        None.
    Outputs:
        The stable ASCII department name for this module.
    Non-goals:
        This does not expose a review engine.
    """

    return _DEPARTMENT_NAME


def describe_department_scope() -> str:
    """Describe the documented scope of the review department.

    Inputs:
        None.
    Outputs:
        A concise summary of the routine review and audit boundary.
    Non-goals:
        This does not imply that escalated prosecution lives here.
    """

    return _DEPARTMENT_SCOPE


def list_functional_offices() -> DescriptorSequence:
    """List the documented review offices.

    Inputs:
        None.
    Outputs:
        A tuple of ASCII office names frozen for this department.
    Non-goals:
        This does not create office packages or runtime handlers.
    """

    return tuple(_FUNCTIONAL_OFFICES)


def describe_functional_office(office_name: str) -> OfficeDescriptor | None:
    """Describe a documented review office.

    Inputs:
        `office_name`: ASCII office name from the governance spec.
    Outputs:
        The office descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not execute audit or prosecution behavior.
    """

    return _FUNCTIONAL_OFFICES.get(office_name)


def list_core_functions() -> DescriptorSequence:
    """List the planned review core function names.

    Inputs:
        None.
    Outputs:
        A tuple of documented function names frozen for later work.
    Non-goals:
        This does not expose callable review handlers.
    """

    return tuple(_CORE_FUNCTIONS)


def describe_core_function(function_name: str) -> InterfaceDescriptor | None:
    """Describe a planned review function.

    Inputs:
        `function_name`: Planned function name from the governance spec.
    Outputs:
        The static interface descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not implement audit engines or prosecution workflows.
    """

    return _CORE_FUNCTIONS.get(function_name)


def list_owned_object_families() -> tuple[ObjectFamilyName, ...]:
    """List object families governed by the review department.

    Inputs:
        None.
    Outputs:
        A tuple of routine-review object families owned by this department.
    Non-goals:
        This does not assign ownership of all reviewable artifacts.
    """

    return _OWNED_OBJECT_FAMILIES


def list_expected_cli_families() -> tuple[ReservedCLIFamilyName, ...]:
    """List reserved CLI families associated with the review department.

    Inputs:
        None.
    Outputs:
        A tuple of reserved routine-review CLI family names.
    Non-goals:
        This does not register or expose commands.
    """

    return _EXPECTED_CLI_FAMILIES


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred capabilities for the review department.

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
