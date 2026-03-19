"""Internal skeleton for the reserved `ingest` command family.

Owning domain: Registry Department / 户部 intake boundary.
Non-goals: no registry writes, no identifier allocation, no public CLI wiring.
Relevant docs: `docs/cli_command_contracts.md`, `docs/payload_contracts.md`,
`docs/card_contracts.md`, `docs/gateway_contracts.md`, and `docs/api_specs.md`.
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

_FAMILY_NAME: CommandFamilyName = "ingest"
_OWNING_MODULE = "macro_veritas.commands.ingest"
_OWNING_DOMAIN = "Registry Department / 户部"
_PURPOSE = (
    "Stage intake of StudyCard, DatasetCard, or ClaimCard material into the "
    "registry boundary without performing runtime mutation."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "future command-normalized intake input",
    "target card-family label",
    "full-card gateway payload for StudyCard, DatasetCard, or ClaimCard create planning",
    "provenance note",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "future gateway create-plan request prepared from a full-card payload",
    "CLI-facing intake summary",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/payload_contracts.md",
    "docs/card_contracts.md",
    "docs/registry_io_boundary.md",
    "docs/gateway_contracts.md",
    "macro_veritas.governance.departments.registry",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "plan_create_study_card",
    "plan_create_dataset_card",
    "plan_create_claim_card",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = (
    build_command_payload_descriptor(
        card_family="StudyCard",
        payload_type="StudyCardPayload",
        usage="prepare_create",
        gateway_reads=(),
        gateway_mutations=("plan_create_study_card",),
        notes=(
            "Future handlers normalize raw CLI intake input before preparing a StudyCardPayload.",
            "Create planning accepts a full-card payload only.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="DatasetCard",
        payload_type="DatasetCardPayload",
        usage="prepare_create",
        gateway_reads=(),
        gateway_mutations=("plan_create_dataset_card",),
        notes=(
            "Future handlers normalize raw CLI intake input before preparing a DatasetCardPayload.",
            "Create planning accepts a full-card payload only.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="ClaimCard",
        payload_type="ClaimCardPayload",
        usage="prepare_create",
        gateway_reads=(),
        gateway_mutations=("plan_create_claim_card",),
        notes=(
            "Future handlers normalize raw CLI intake input before preparing a ClaimCardPayload.",
            "Create planning accepts a full-card payload only.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "public CLI exposure",
    "argument schema design",
    "identifier allocation",
    "registry writes",
    "serializer integration",
)
_NON_GOALS: DescriptorSequence = (
    "file IO",
    "gateway execution",
    "identifier allocation",
    "schema validation",
)


def family_name() -> CommandFamilyName:
    """Return the reserved command-family label for this module."""

    return _FAMILY_NAME


def describe_command_family() -> CommandDescriptor:
    """Return static metadata for the reserved internal `ingest` family."""

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
    """Reserve the future parser-builder hook for the internal `ingest` family.

    Inputs:
        `subparsers_or_parser`: future argparse subparsers or family parser.
    Outputs:
        `None` for this skeleton milestone.
    Non-goals:
        This placeholder does not register public CLI commands or flags.
    """

    del subparsers_or_parser
    return None


def handle_ingest_command(args: object) -> object:
    """Reserve the future handler boundary for the internal `ingest` family.

    Inputs:
        `args`: future raw parsed arguments for the reserved `ingest` family.
    Outputs:
        Future handler result object; this skeleton currently raises.
    Non-goals:
        This placeholder does not normalize parser input, call the gateway,
        write files, or mutate state.
    """

    del args
    raise command_handler_not_implemented(_FAMILY_NAME)


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the planned registry-gateway operations this family is expected to use."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Describe the frozen MVP payload families touched by `ingest`."""

    return _PAYLOAD_CONTRACTS


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `ingest` capabilities beyond this skeleton milestone."""

    return _DEFERRED_CAPABILITIES


__all__ = [
    "build_parser",
    "describe_command_family",
    "describe_payload_contracts",
    "family_name",
    "handle_ingest_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
]
