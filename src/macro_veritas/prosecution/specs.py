"""Static descriptors for the prosecution governance lane.

This module freezes the lane-level responsibilities and planned function names
for escalated review after routine audit escalation.

It does not implement prosecution workflows, case management, or automation.
Boundary docs: `docs/governance_spec.md`, `docs/module_map.md`,
`docs/audit_policy.md`, and `docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import (
    DescriptorSequence,
    InterfaceDescriptor,
    OfficeDescriptor,
)

_PROSECUTION_NAME = "prosecution"
_PROSECUTION_SCOPE = (
    "Freeze the escalated review lane for materially disputed, high-risk, or "
    "governance-sensitive cases after routine review escalation."
)
_RELATION_TO_AUDIT = (
    "Prosecution remains distinct from routine audit. Routine review asks "
    "whether a record is sufficiently documented for downstream use, while "
    "prosecution frames escalated cases that need structured dispute handling "
    "and a documented disposition recommendation."
)

_FUNCTIONAL_OFFICES: dict[str, OfficeDescriptor] = {
    "case_intake_lane": {
        "name": "case_intake_lane",
        "governance_label": "受案司 / Case Intake Lane",
        "purpose": "Accept only escalated cases and screen whether the prosecution lane is warranted.",
        "inputs": ("escalation packet", "linked audit record", "dispute summary"),
        "outputs": ("case-intake header", "screening note"),
        "core_functions": ("accept_escalated_case", "screen_material_dispute"),
        "deferred_items": (
            "automatic screening",
            "queue routing",
            "formal case intake workflow",
        ),
    },
    "case_brief_lane": {
        "name": "case_brief_lane",
        "governance_label": "案情司 / Case Brief Lane",
        "purpose": "Structure the affected artifacts, disputed points, and open response questions.",
        "inputs": ("case-intake header", "linked artifacts", "response questions"),
        "outputs": ("case-brief descriptor", "response-request note"),
        "core_functions": ("assemble_case_brief", "request_case_response"),
        "deferred_items": (
            "formal correspondence",
            "evidence grading",
            "external service integration",
        ),
    },
    "disposition_lane": {
        "name": "disposition_lane",
        "governance_label": "处置司 / Disposition Lane",
        "purpose": "Document a recommended resolution path after escalated review.",
        "inputs": ("case brief", "response materials", "decision rationale"),
        "outputs": ("disposition recommendation", "case-resolution header"),
        "core_functions": (
            "recommend_case_disposition",
            "record_case_resolution_header",
        ),
        "deferred_items": (
            "sanctions",
            "appeals",
            "case-management engine",
        ),
    },
}

_CORE_FUNCTIONS: dict[str, InterfaceDescriptor] = {
    "accept_escalated_case": {
        "name": "accept_escalated_case",
        "purpose": "Describe the intake boundary for a case that has already been escalated from routine review.",
        "inputs": ("escalation packet", "linked audit record", "dispute summary"),
        "outputs": ("case-intake header",),
        "non_goals": (
            "automatic escalation",
            "routine audit",
            "case management",
        ),
    },
    "screen_material_dispute": {
        "name": "screen_material_dispute",
        "purpose": "Describe whether an escalated dispute warrants prosecution-lane treatment.",
        "inputs": ("case-intake header", "dispute summary", "risk note"),
        "outputs": ("screening note",),
        "non_goals": (
            "evidence grading",
            "sanctions",
            "workflow automation",
        ),
    },
    "assemble_case_brief": {
        "name": "assemble_case_brief",
        "purpose": "Describe the structured brief for an escalated case.",
        "inputs": ("case-intake header", "linked artifacts", "open questions"),
        "outputs": ("case-brief descriptor",),
        "non_goals": (
            "formal case file management",
            "external correspondence",
            "scientific adjudication",
        ),
    },
    "request_case_response": {
        "name": "request_case_response",
        "purpose": "Describe the response materials that should be requested for an escalated case.",
        "inputs": ("case brief", "response questions", "linked artifacts"),
        "outputs": ("response-request note",),
        "non_goals": (
            "messaging systems",
            "workflow automation",
            "service integration",
        ),
    },
    "recommend_case_disposition": {
        "name": "recommend_case_disposition",
        "purpose": "Describe the recommended resolution path after escalated review.",
        "inputs": ("case brief", "response materials", "decision rationale"),
        "outputs": ("disposition recommendation",),
        "non_goals": (
            "sanctions",
            "automatic enforcement",
            "appeals workflow",
        ),
    },
    "record_case_resolution_header": {
        "name": "record_case_resolution_header",
        "purpose": "Describe the header that records a documented case resolution state.",
        "inputs": ("case brief", "disposition recommendation", "resolution note"),
        "outputs": ("case-resolution header",),
        "non_goals": (
            "case-management engine",
            "artifact mutation",
            "workflow automation",
        ),
    },
}

_DEFERRED_CAPABILITIES = (
    "automatic screening",
    "evidence grading logic",
    "sanctions",
    "case-management engine",
)

_NON_GOALS = (
    "routine audit operations",
    "automated escalation",
    "evidence grading logic",
    "sanctions",
    "formal case management",
    "orchestration runtime",
)


def prosecution_name() -> str:
    """Return the ASCII prosecution lane name used in code.

    Inputs:
        None.
    Outputs:
        The stable ASCII name for the prosecution specs module.
    Non-goals:
        This does not expose a runtime review lane.
    """

    return _PROSECUTION_NAME


def describe_prosecution_scope() -> str:
    """Describe the documented prosecution scope.

    Inputs:
        None.
    Outputs:
        A concise summary of the prosecution boundary.
    Non-goals:
        This does not create a case-management or decision engine.
    """

    return _PROSECUTION_SCOPE


def list_functional_offices() -> DescriptorSequence:
    """List the documented prosecution lanes.

    Inputs:
        None.
    Outputs:
        A tuple of ASCII lane names frozen for prosecution.
    Non-goals:
        This does not create lane packages or runtime handlers.
    """

    return tuple(_FUNCTIONAL_OFFICES)


def describe_functional_office(office_name: str) -> OfficeDescriptor | None:
    """Describe a documented prosecution lane.

    Inputs:
        `office_name`: ASCII lane name from the governance spec.
    Outputs:
        The lane descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not execute screening, briefing, or disposition behavior.
    """

    return _FUNCTIONAL_OFFICES.get(office_name)


def list_core_functions() -> DescriptorSequence:
    """List the planned prosecution core function names.

    Inputs:
        None.
    Outputs:
        A tuple of documented function names frozen for later work.
    Non-goals:
        This does not expose callable prosecution handlers.
    """

    return tuple(_CORE_FUNCTIONS)


def describe_core_function(function_name: str) -> InterfaceDescriptor | None:
    """Describe a planned prosecution function.

    Inputs:
        `function_name`: Planned function name from the governance spec.
    Outputs:
        The static interface descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not implement screening, case briefing, or disposition logic.
    """

    return _CORE_FUNCTIONS.get(function_name)


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred capabilities for the prosecution lane.

    Inputs:
        None.
    Outputs:
        A tuple of capabilities intentionally left unimplemented.
    Non-goals:
        This does not implement any deferred capability.
    """

    return _DEFERRED_CAPABILITIES


def describe_prosecution_domain() -> str:
    """Describe the documented prosecution-domain boundary.

    Inputs:
        None.
    Outputs:
        A short summary of the escalated review concept.
    Non-goals:
        This does not create a runtime review lane or decision engine.
    """

    return describe_prosecution_scope()


def describe_relation_to_audit() -> str:
    """Describe how prosecution relates to routine audit.

    Inputs:
        None.
    Outputs:
        A short description of the documented relationship to routine audit.
    Non-goals:
        This does not move records between lanes or enforce escalation rules.
    """

    return _RELATION_TO_AUDIT


def list_prosecution_non_goals() -> DescriptorSequence:
    """List documented prosecution non-goals for the current skeleton.

    Inputs:
        None.
    Outputs:
        A tuple of explicit non-goals drawn from the governance spec.
    Non-goals:
        This function only reports boundaries; it does not enforce them.
    """

    return _NON_GOALS


__all__ = [
    "describe_core_function",
    "describe_functional_office",
    "describe_prosecution_domain",
    "describe_prosecution_scope",
    "describe_relation_to_audit",
    "list_core_functions",
    "list_deferred_capabilities",
    "list_functional_offices",
    "list_prosecution_non_goals",
    "prosecution_name",
]
