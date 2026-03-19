"""Routine audit-domain descriptor functions for MacroVeritas.

This module exposes static metadata about the documented routine review and
audit lane.

It does not implement audit execution, scoring, or grading behavior.
Boundary docs: `docs/audit_policy.md`, `docs/module_map.md`,
and `docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import AuditOutcomeName, ObjectFamilyName


def describe_audit_domain() -> str:
    """Describe the documented routine audit domain.

    Inputs:
        None.
    Outputs:
        A short summary of the routine review and traceability role.
    Non-goals:
        This does not execute reviews or decide outcomes dynamically.
    """

    return (
        "The audit domain is the lightweight routine review lane for "
        "traceability, provenance, linkage, and stage-readiness checks."
    )


def list_audit_outcomes() -> tuple[AuditOutcomeName, ...]:
    """Return the documented routine audit outcomes.

    Inputs:
        None.
    Outputs:
        A tuple of outcome labels from `docs/audit_policy.md`.
    Non-goals:
        This does not apply outcomes to objects.
    """

    return ("pass", "return", "escalate")


def describe_audit_trigger_points() -> dict[ObjectFamilyName, str]:
    """Describe the documented high-value audit trigger points.

    Inputs:
        None.
    Outputs:
        A mapping from object family to the documented trigger summary.
    Non-goals:
        This does not enforce those triggers or inspect lifecycle state.
    """

    return {
        "StudyCard": "When moving from draft to registered.",
        "DatasetCard": "When first bound to a usable project location.",
        "ClaimCard": "When marked ready for downstream work.",
        "ReanalysisBundle": "When assembled for review.",
        "EvidenceCard": "Before being treated as reportable project output.",
    }


def list_audit_non_implications() -> tuple[str, ...]:
    """List what audit failure does not mean in the current docs.

    Inputs:
        None.
    Outputs:
        A tuple of non-implications taken from `docs/audit_policy.md`.
    Non-goals:
        This does not interpret evidence or scientific truth.
    """

    return (
        "the paper is wrong",
        "the dataset is fraudulent",
        "the claim is scientifically false",
        "the analyst acted in bad faith",
        "the work can never proceed",
    )


__all__ = [
    "describe_audit_domain",
    "describe_audit_trigger_points",
    "list_audit_non_implications",
    "list_audit_outcomes",
]
