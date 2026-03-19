"""Static descriptors for the operations governance department.

This module freezes the office-level responsibilities and planned function
names for method and reanalysis planning.

It does not implement pipelines, notebook loops, or runtime execution.
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

_DEPARTMENT_NAME = "operations"
_DEPARTMENT_SCOPE = (
    "Freeze method and reanalysis-boundary descriptors so later execution "
    "layers can be added without changing the governance contract."
)

_FUNCTIONAL_OFFICES: dict[str, OfficeDescriptor] = {
    "method_scope_office": {
        "name": "method_scope_office",
        "governance_label": "方法司 / Method Scope Office",
        "purpose": "Define the documented context for a MethodCard and its expected inputs.",
        "inputs": ("method label", "assumptions", "planned input-family references"),
        "outputs": ("method-context descriptor", "input-contract note"),
        "core_functions": ("declare_method_context", "declare_method_inputs"),
        "deferred_items": (
            "algorithm implementation",
            "parameter validation",
            "method execution",
        ),
    },
    "reanalysis_planning_office": {
        "name": "reanalysis_planning_office",
        "governance_label": "复核司 / Reanalysis Planning Office",
        "purpose": "Frame reanalysis requests and bundle plans without running them.",
        "inputs": (
            "study, dataset, or claim references",
            "method context",
            "requested deliverables",
        ),
        "outputs": ("reanalysis-request descriptor", "ReanalysisBundle plan header"),
        "core_functions": ("plan_reanalysis_request", "assemble_bundle_plan"),
        "deferred_items": (
            "orchestration loops",
            "job scheduling",
            "notebook workflows",
        ),
    },
    "artifact_manifest_office": {
        "name": "artifact_manifest_office",
        "governance_label": "清单司 / Artifact Manifest Office",
        "purpose": "Describe expected run artifacts and declared outputs at the contract level.",
        "inputs": ("run-stage label", "artifact categories", "output intent"),
        "outputs": ("artifact-manifest descriptor", "output-contract note"),
        "core_functions": ("describe_run_artifacts", "describe_run_outputs"),
        "deferred_items": (
            "manifest generation",
            "pipeline writing",
            "runtime storage logic",
        ),
    },
}

_CORE_FUNCTIONS: dict[str, InterfaceDescriptor] = {
    "declare_method_context": {
        "name": "declare_method_context",
        "purpose": "Describe the high-level purpose and assumptions of a planned method.",
        "inputs": ("method label", "purpose note", "assumption statements"),
        "outputs": ("method-context descriptor",),
        "non_goals": (
            "algorithm implementation",
            "scientific execution",
            "parameter tuning",
        ),
    },
    "declare_method_inputs": {
        "name": "declare_method_inputs",
        "purpose": "Describe the object-family and artifact categories a planned method expects.",
        "inputs": ("method label", "input-family references", "artifact intent"),
        "outputs": ("method input-contract note",),
        "non_goals": (
            "schema validation",
            "data loading",
            "runtime checks",
        ),
    },
    "plan_reanalysis_request": {
        "name": "plan_reanalysis_request",
        "purpose": "Describe a future reanalysis request against governed inputs.",
        "inputs": ("study, dataset, or claim references", "method context", "requested deliverables"),
        "outputs": ("reanalysis-request descriptor",),
        "non_goals": (
            "job scheduling",
            "notebook execution",
            "scientific analysis",
        ),
    },
    "assemble_bundle_plan": {
        "name": "assemble_bundle_plan",
        "purpose": "Describe the intended contents of a future ReanalysisBundle.",
        "inputs": ("reanalysis request", "artifact categories", "reporting intent"),
        "outputs": ("ReanalysisBundle plan header",),
        "non_goals": (
            "artifact creation",
            "manifest generation",
            "filesystem writes",
        ),
    },
    "describe_run_artifacts": {
        "name": "describe_run_artifacts",
        "purpose": "Describe the categories of artifacts a future run should produce or consume.",
        "inputs": ("run-stage label", "artifact categories", "traceability intent"),
        "outputs": ("artifact-manifest descriptor",),
        "non_goals": (
            "manifest generation",
            "pipeline execution",
            "storage logic",
        ),
    },
    "describe_run_outputs": {
        "name": "describe_run_outputs",
        "purpose": "Describe the declared outputs and reporting boundary of a future run.",
        "inputs": ("run-stage label", "output categories", "reporting intent"),
        "outputs": ("output-contract note",),
        "non_goals": (
            "report generation",
            "scientific interpretation",
            "filesystem writes",
        ),
    },
}

_OWNED_OBJECT_FAMILIES: tuple[ObjectFamilyName, ...] = (
    "MethodCard",
    "ReanalysisBundle",
)

_EXPECTED_CLI_FAMILIES: tuple[ReservedCLIFamilyName, ...] = ("run",)

_DEFERRED_CAPABILITIES = (
    "scientific pipelines",
    "notebook execution loop",
    "agent runtime",
    "CellVoyager integration",
)


def department_name() -> str:
    """Return the ASCII department name used in code.

    Inputs:
        None.
    Outputs:
        The stable ASCII department name for this module.
    Non-goals:
        This does not create a run controller.
    """

    return _DEPARTMENT_NAME


def describe_department_scope() -> str:
    """Describe the documented scope of the operations department.

    Inputs:
        None.
    Outputs:
        A concise summary of the run-domain responsibility boundary.
    Non-goals:
        This does not execute scientific or agent workflows.
    """

    return _DEPARTMENT_SCOPE


def list_functional_offices() -> DescriptorSequence:
    """List the documented operations offices.

    Inputs:
        None.
    Outputs:
        A tuple of ASCII office names frozen for this department.
    Non-goals:
        This does not create office packages or runtime handlers.
    """

    return tuple(_FUNCTIONAL_OFFICES)


def describe_functional_office(office_name: str) -> OfficeDescriptor | None:
    """Describe a documented operations office.

    Inputs:
        `office_name`: ASCII office name from the governance spec.
    Outputs:
        The office descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not execute methods, runs, or orchestration.
    """

    return _FUNCTIONAL_OFFICES.get(office_name)


def list_core_functions() -> DescriptorSequence:
    """List the planned operations core function names.

    Inputs:
        None.
    Outputs:
        A tuple of documented function names frozen for later work.
    Non-goals:
        This does not expose callable run handlers.
    """

    return tuple(_CORE_FUNCTIONS)


def describe_core_function(function_name: str) -> InterfaceDescriptor | None:
    """Describe a planned operations function.

    Inputs:
        `function_name`: Planned function name from the governance spec.
    Outputs:
        The static interface descriptor when recognized, otherwise `None`.
    Non-goals:
        This does not implement pipelines or scientific logic.
    """

    return _CORE_FUNCTIONS.get(function_name)


def list_owned_object_families() -> tuple[ObjectFamilyName, ...]:
    """List object families governed by the operations department.

    Inputs:
        None.
    Outputs:
        A tuple of method and bundle object families owned by this department.
    Non-goals:
        This does not imply downstream evidence logic lives here.
    """

    return _OWNED_OBJECT_FAMILIES


def list_expected_cli_families() -> tuple[ReservedCLIFamilyName, ...]:
    """List reserved CLI families associated with the operations department.

    Inputs:
        None.
    Outputs:
        A tuple of reserved run-domain CLI family names.
    Non-goals:
        This does not register CLI commands.
    """

    return _EXPECTED_CLI_FAMILIES


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred capabilities for the operations department.

    Inputs:
        None.
    Outputs:
        A tuple of capabilities intentionally left unimplemented.
    Non-goals:
        This does not execute those capabilities.
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
