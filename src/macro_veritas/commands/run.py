"""Internal skeleton for the reserved `run` command family.

Owning domain: Operations Department / 兵部 run/bundle boundary.
Non-goals: no scientific execution, no orchestration runtime, no public CLI wiring.
Relevant docs: `docs/cli_command_contracts.md`, `docs/payload_contracts.md`,
`docs/gateway_contracts.md`, `docs/api_specs.md`, and `docs/constraints.md`.
"""

from __future__ import annotations

from macro_veritas.commands.common import (
    build_command_descriptor,
    build_command_payload_descriptor,
    command_handler_not_implemented,
)
from macro_veritas.shared.types import (
    CommandDescriptor,
    CommandFamilyName,
    CommandPayloadDescriptor,
    DescriptorSequence,
)

_FAMILY_NAME: CommandFamilyName = "run"
_OWNING_MODULE = "macro_veritas.commands.run"
_OWNING_DOMAIN = "Operations Department / 兵部"
_PURPOSE = (
    "Stage future run or bundle commands around declared inputs, methods, and "
    "outputs without implementing scientific execution."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "future command-normalized run input",
    "method or bundle reference",
    "linked input object references",
    "run intent note",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "read-driven run-scope summary",
    "future bundle-planning request",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/payload_contracts.md",
    "docs/gateway_contracts.md",
    "docs/registry_io_boundary.md",
    "macro_veritas.governance.departments.operations",
    "macro_veritas.runs.specs",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "get_study_card",
    "get_dataset_card",
    "get_claim_card",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = (
    build_command_payload_descriptor(
        card_family="StudyCard",
        payload_type="StudyCardPayload",
        usage="read_only",
        gateway_reads=("get_study_card",),
        gateway_mutations=(),
        notes=(
            "Run planning reads StudyCard context only in the MVP.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="DatasetCard",
        payload_type="DatasetCardPayload",
        usage="read_only",
        gateway_reads=("get_dataset_card",),
        gateway_mutations=(),
        notes=(
            "Run planning reads DatasetCard context only in the MVP.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="ClaimCard",
        payload_type="ClaimCardPayload",
        usage="read_only",
        gateway_reads=("get_claim_card",),
        gateway_mutations=(),
        notes=(
            "Run planning reads ClaimCard context only in the MVP.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "public CLI exposure",
    "argument schema design",
    "scientific execution",
    "bundle manifests",
    "orchestration runtime",
)
_NON_GOALS: DescriptorSequence = (
    "scientific execution",
    "bundle generation",
    "agent runtime",
    "CellVoyager integration",
)


def family_name() -> CommandFamilyName:
    """Return the reserved command-family label for this module."""

    return _FAMILY_NAME


def describe_command_family() -> CommandDescriptor:
    """Return static metadata for the reserved internal `run` family."""

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
    """Reserve the future parser-builder hook for the internal `run` family.

    Inputs:
        `subparsers_or_parser`: future argparse subparsers or family parser.
    Outputs:
        `None` for this skeleton milestone.
    Non-goals:
        This placeholder does not register public CLI commands or flags.
    """

    del subparsers_or_parser
    return None


def handle_run_command(args: object) -> object:
    """Reserve the future handler boundary for the internal `run` family.

    Inputs:
        `args`: future raw parsed arguments for the reserved `run` family.
    Outputs:
        Future handler result object; this skeleton currently raises.
    Non-goals:
        This placeholder does not normalize parser input, execute methods, call
        the gateway, or mutate state.
    """

    del args
    raise command_handler_not_implemented(_FAMILY_NAME)


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the planned registry-gateway operations this family is expected to use."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Describe the frozen MVP payload families touched by `run`."""

    return _PAYLOAD_CONTRACTS


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `run` capabilities beyond this skeleton milestone."""

    return _DEFERRED_CAPABILITIES


__all__ = [
    "build_parser",
    "describe_command_family",
    "describe_payload_contracts",
    "family_name",
    "handle_run_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
]
