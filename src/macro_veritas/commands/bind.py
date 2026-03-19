"""Internal skeleton for the reserved `bind` command family.

Owning domain: Registry Department / 户部 locator-binding boundary.
Non-goals: no filesystem checks, no path mutation, no public CLI wiring.
Relevant docs: `docs/cli_command_contracts.md`, `docs/registry_layout.md`,
`docs/gateway_contracts.md`, and `docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.commands.common import (
    build_command_descriptor,
    command_handler_not_implemented,
)
from macro_veritas.shared.types import CommandDescriptor, CommandFamilyName, DescriptorSequence

_FAMILY_NAME: CommandFamilyName = "bind"
_OWNING_MODULE = "macro_veritas.commands.bind"
_OWNING_DOMAIN = "Registry Department / 户部"
_PURPOSE = (
    "Stage locator-binding work for governed objects without touching raw "
    "filesystem paths or executing registry mutation."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "target object identity",
    "locator reference",
    "binding provenance note",
    "full replacement card mapping when update planning is needed",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "future gateway read or update-plan request",
    "binding summary",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/registry_layout.md",
    "docs/registry_io_boundary.md",
    "docs/gateway_contracts.md",
    "macro_veritas.governance.departments.registry",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "get_study_card",
    "get_dataset_card",
    "get_claim_card",
    "plan_update_study_card",
    "plan_update_dataset_card",
    "plan_update_claim_card",
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "public CLI exposure",
    "argument schema design",
    "filesystem checks",
    "registry writes",
    "serializer integration",
)
_NON_GOALS: DescriptorSequence = (
    "file IO",
    "raw path traversal",
    "gateway execution",
    "storage probing",
)


def family_name() -> CommandFamilyName:
    """Return the reserved command-family label for this module."""

    return _FAMILY_NAME


def describe_command_family() -> CommandDescriptor:
    """Return static metadata for the reserved internal `bind` family."""

    return build_command_descriptor(
        family_name=_FAMILY_NAME,
        owning_module=_OWNING_MODULE,
        owning_domain=_OWNING_DOMAIN,
        purpose=_PURPOSE,
        primary_inputs=_PRIMARY_INPUTS,
        primary_outputs=_PRIMARY_OUTPUTS,
        dependency_contracts=_DEPENDENCY_CONTRACTS,
        non_goals=_NON_GOALS,
    )


def build_parser(subparsers_or_parser: object) -> None:
    """Reserve the future parser-builder hook for the internal `bind` family.

    Inputs:
        `subparsers_or_parser`: future argparse subparsers or family parser.
    Outputs:
        `None` for this skeleton milestone.
    Non-goals:
        This placeholder does not register public CLI commands or flags.
    """

    del subparsers_or_parser
    return None


def handle_bind_command(args: object) -> object:
    """Reserve the future handler boundary for the internal `bind` family.

    Inputs:
        `args`: future parsed arguments for the reserved `bind` family.
    Outputs:
        Future handler result object; this skeleton currently raises.
    Non-goals:
        This placeholder does not call the gateway, inspect storage, or mutate state.
    """

    del args
    raise command_handler_not_implemented(_FAMILY_NAME)


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the planned registry-gateway operations this family is expected to use."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `bind` capabilities beyond this skeleton milestone."""

    return _DEFERRED_CAPABILITIES


__all__ = [
    "build_parser",
    "describe_command_family",
    "family_name",
    "handle_bind_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
]
