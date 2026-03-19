"""Run-domain descriptor functions for MacroVeritas.

This module exposes static metadata about the documented run and reanalysis
domain.

It does not implement execution, manifests, or artifact generation.
Boundary docs: `docs/module_map.md`, `docs/registry_model.md`,
and `docs/constraints.md`.
"""

from __future__ import annotations

from macro_veritas.shared.types import ObjectFamilyName


def describe_run_domain() -> str:
    """Describe the documented run-domain boundary.

    Inputs:
        None.
    Outputs:
        A short summary of the run and reanalysis scope.
    Non-goals:
        This does not execute runs or manage runtime state.
    """

    return (
        "The run domain defines documentation-level boundaries around "
        "MethodCard and ReanalysisBundle without implementing scientific "
        "execution."
    )


def list_run_object_families() -> tuple[ObjectFamilyName, ...]:
    """List object families most closely aligned with the run domain.

    Inputs:
        None.
    Outputs:
        A tuple of documented run-domain object families.
    Non-goals:
        This does not assign ownership of all downstream review artifacts.
    """

    return ("MethodCard", "ReanalysisBundle")


def list_run_non_goals() -> tuple[str, ...]:
    """List documented run-domain non-goals for the current skeleton.

    Inputs:
        None.
    Outputs:
        A tuple of explicit non-goals drawn from the local docs.
    Non-goals:
        This function only reports boundaries; it does not enforce them.
    """

    return (
        "scientific pipelines",
        "notebook execution loop",
        "agent runtime",
        "CellVoyager integration",
    )


__all__ = [
    "describe_run_domain",
    "list_run_non_goals",
    "list_run_object_families",
]
