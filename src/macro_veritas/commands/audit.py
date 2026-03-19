"""Internal skeleton for the reserved `audit` command family.

Owning domain: Review Department / 刑部 routine audit lane.
Non-goals: no audit engine, no grading logic, no public CLI wiring.
Relevant docs: `docs/cli_command_contracts.md`, `docs/audit_policy.md`,
`docs/gateway_contracts.md`, and `docs/api_specs.md`.
"""

from __future__ import annotations

from macro_veritas.commands.common import (
    build_command_descriptor,
    command_handler_not_implemented,
)
from macro_veritas.shared.types import CommandDescriptor, CommandFamilyName, DescriptorSequence

_FAMILY_NAME: CommandFamilyName = "audit"
_OWNING_MODULE = "macro_veritas.commands.audit"
_OWNING_DOMAIN = "Review Department / 刑部"
_PURPOSE = (
    "Stage routine audit checks and routine audit outcome recording around "
    "reviewable objects without implementing adjudication."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "object or bundle reference",
    "audit scope note",
    "findings summary",
    "intended audit outcome label",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "audit action summary",
    "future audit-record planning request",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/audit_policy.md",
    "docs/registry_io_boundary.md",
    "docs/gateway_contracts.md",
    "macro_veritas.governance.departments.review",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "get_study_card",
    "get_dataset_card",
    "get_claim_card",
    "list_study_cards",
    "list_dataset_cards",
    "list_claim_cards",
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "public CLI exposure",
    "argument schema design",
    "audit execution",
    "audit record persistence",
    "automatic triggers",
)
_NON_GOALS: DescriptorSequence = (
    "audit engine",
    "adjudication runtime",
    "evidence grading",
    "gateway execution",
)


def family_name() -> CommandFamilyName:
    """Return the reserved command-family label for this module."""

    return _FAMILY_NAME


def describe_command_family() -> CommandDescriptor:
    """Return static metadata for the reserved internal `audit` family."""

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
    """Reserve the future parser-builder hook for the internal `audit` family.

    Inputs:
        `subparsers_or_parser`: future argparse subparsers or family parser.
    Outputs:
        `None` for this skeleton milestone.
    Non-goals:
        This placeholder does not register public CLI commands or flags.
    """

    del subparsers_or_parser
    return None


def handle_audit_command(args: object) -> object:
    """Reserve the future handler boundary for the internal `audit` family.

    Inputs:
        `args`: future parsed arguments for the reserved `audit` family.
    Outputs:
        Future handler result object; this skeleton currently raises.
    Non-goals:
        This placeholder does not execute audit logic, call the gateway, or mutate state.
    """

    del args
    raise command_handler_not_implemented(_FAMILY_NAME)


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the planned registry-gateway operations this family is expected to use."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `audit` capabilities beyond this skeleton milestone."""

    return _DEFERRED_CAPABILITIES


__all__ = [
    "build_parser",
    "describe_command_family",
    "family_name",
    "handle_audit_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
]
