"""Internal skeleton for the reserved `grade` command family.

Owning domain: review-adjacent grading boundary, provisionally aligned with
Review Department / 刑部.
Non-goals: no evidence grading logic, no scoring engine, no public CLI wiring.
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

_FAMILY_NAME: CommandFamilyName = "grade"
_OWNING_MODULE = "macro_veritas.commands.grade"
_OWNING_DOMAIN = "Review-adjacent grading boundary / provisionally Review Department"
_PURPOSE = (
    "Stage a future evidence-judgment or claim-grading command family without "
    "locking grading runtime behavior."
)
_PRIMARY_INPUTS: DescriptorSequence = (
    "future command-normalized grading input",
    "claim reference",
    "linked dataset or bundle context",
    "judgment intent note",
)
_PRIMARY_OUTPUTS: DescriptorSequence = (
    "read-driven grading summary",
    "future evidence-judgment request",
)
_DEPENDENCY_CONTRACTS: DescriptorSequence = (
    "docs/payload_contracts.md",
    "docs/gateway_contracts.md",
    "docs/registry_io_boundary.md",
    "macro_veritas.governance.departments.review",
    "macro_veritas.registry.gateway",
)
_EXPECTED_GATEWAY_DEPENDENCIES: DescriptorSequence = (
    "get_claim_card",
    "get_dataset_card",
    "get_study_card",
)
_PAYLOAD_CONTRACTS: tuple[CommandPayloadDescriptor, ...] = (
    build_command_payload_descriptor(
        card_family="ClaimCard",
        payload_type="ClaimCardPayload",
        usage="read_only",
        gateway_reads=("get_claim_card",),
        gateway_mutations=(),
        notes=(
            "Grade reads ClaimCard context only in the MVP.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="DatasetCard",
        payload_type="DatasetCardPayload",
        usage="read_only",
        gateway_reads=("get_dataset_card",),
        gateway_mutations=(),
        notes=(
            "Grade reads DatasetCard context only in the MVP.",
        ),
    ),
    build_command_payload_descriptor(
        card_family="StudyCard",
        payload_type="StudyCardPayload",
        usage="read_only",
        gateway_reads=("get_study_card",),
        gateway_mutations=(),
        notes=(
            "Grade reads StudyCard context only in the MVP.",
        ),
    ),
)
_DEFERRED_CAPABILITIES: DescriptorSequence = (
    "public CLI exposure",
    "argument schema design",
    "evidence grading logic",
    "scoring engine",
    "report assembly runtime",
)
_NON_GOALS: DescriptorSequence = (
    "evidence grading logic",
    "scoring",
    "report assembly runtime",
    "gateway execution",
)


def family_name() -> CommandFamilyName:
    """Return the reserved command-family label for this module."""

    return _FAMILY_NAME


def describe_command_family() -> CommandDescriptor:
    """Return static metadata for the reserved internal `grade` family."""

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
    """Reserve the future parser-builder hook for the internal `grade` family.

    Inputs:
        `subparsers_or_parser`: future argparse subparsers or family parser.
    Outputs:
        `None` for this skeleton milestone.
    Non-goals:
        This placeholder does not register public CLI commands or flags.
    """

    del subparsers_or_parser
    return None


def handle_grade_command(args: object) -> object:
    """Reserve the future handler boundary for the internal `grade` family.

    Inputs:
        `args`: future raw parsed arguments for the reserved `grade` family.
    Outputs:
        Future handler result object; this skeleton currently raises.
    Non-goals:
        This placeholder does not normalize parser input, grade evidence, call
        the gateway, or mutate state.
    """

    del args
    raise command_handler_not_implemented(_FAMILY_NAME)


def list_expected_gateway_dependencies() -> DescriptorSequence:
    """List the planned registry-gateway operations this family is expected to use."""

    return _EXPECTED_GATEWAY_DEPENDENCIES


def describe_payload_contracts() -> tuple[CommandPayloadDescriptor, ...]:
    """Describe the frozen MVP payload families touched by `grade`."""

    return _PAYLOAD_CONTRACTS


def list_deferred_capabilities() -> DescriptorSequence:
    """List deferred `grade` capabilities beyond this skeleton milestone."""

    return _DEFERRED_CAPABILITIES


__all__ = [
    "build_parser",
    "describe_command_family",
    "describe_payload_contracts",
    "family_name",
    "handle_grade_command",
    "list_deferred_capabilities",
    "list_expected_gateway_dependencies",
]
