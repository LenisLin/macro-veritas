from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
from typing import Iterable, Iterator

from .commands import delete as delete_command
from .commands import ingest as ingest_command
from .commands import listing as listing_command
from .commands import show as show_command
from .commands.common import format_command_result_for_cli
from .config import load_project_config
from .registry.claim import (
    allowed_review_readiness as allowed_claim_review_readiness,
)
from .registry.claim import allowed_statuses as allowed_claim_statuses
from .registry.dataset import (
    allowed_availability_statuses as allowed_dataset_availability_statuses,
)
from .registry.dataset import allowed_statuses as allowed_dataset_statuses
from .registry.study import allowed_screening_decisions
from .registry.study import allowed_statuses as allowed_study_statuses
from .shared.types import (
    ClaimCardCLIInput,
    CommandExecutionResult,
    DatasetCardCLIInput,
    DeleteCLIInput,
    ListCLIInput,
    ShowCLIInput,
    StudyCardCLIInput,
)

SCAFFOLD_STAGE = "Initialization / scaffold"

_CLAIMCARD_REQUIRED_FIELD_FLAGS: tuple[tuple[str, str], ...] = (
    ("claim_id", "--claim-id"),
    ("study_id", "--study-id"),
    ("claim_text", "--claim-text"),
    ("claim_type", "--claim-type"),
    ("provenance_pointer", "--provenance-pointer"),
    ("status", "--status"),
    ("review_readiness", "--review-readiness"),
    ("created_from", "--created-from"),
)
_CLAIMCARD_ALL_FIELD_FLAGS: tuple[tuple[str, str], ...] = (
    _CLAIMCARD_REQUIRED_FIELD_FLAGS
    + (("dataset_id", "--dataset-id"), ("claim_summary_handle", "--claim-summary-handle"))
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="macro_veritas",
        description="MacroVeritas scaffold CLI",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to project config file (default: config/project.yaml)",
    )
    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status", help="Show current scaffold status")
    status_parser.set_defaults(handler=_run_status)

    show_config_parser = subparsers.add_parser(
        "show-config",
        help="Print resolved configuration and derived layout paths",
    )
    show_config_parser.set_defaults(handler=_run_show_config)

    init_layout_parser = subparsers.add_parser(
        "init-layout",
        help="Create the placeholder filesystem layout under the configured data root",
    )
    init_layout_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be created without modifying the filesystem",
    )
    init_layout_parser.set_defaults(handler=_run_init_layout)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Create registry records through the public ingest paths",
    )
    ingest_subparsers = ingest_parser.add_subparsers(
        dest="ingest_command",
        required=True,
    )
    study_parser = ingest_subparsers.add_parser(
        "study",
        help="Create one StudyCard from explicit CLI fields",
    )
    _configure_study_ingest_parser(study_parser)
    study_parser.set_defaults(handler=_run_ingest_study)

    dataset_parser = ingest_subparsers.add_parser(
        "dataset",
        help="Create one DatasetCard from explicit CLI fields",
    )
    _configure_dataset_ingest_parser(dataset_parser)
    dataset_parser.set_defaults(handler=_run_ingest_dataset)

    claim_parser = ingest_subparsers.add_parser(
        "claim",
        help="Create one ClaimCard from explicit CLI fields or one YAML file",
    )
    _configure_claim_ingest_parser(claim_parser)
    claim_parser.set_defaults(handler=_run_ingest_claim)

    show_parser = subparsers.add_parser(
        "show",
        help="Read one registry card by canonical ID",
    )
    show_subparsers = show_parser.add_subparsers(
        dest="show_command",
        required=True,
    )
    show_study_parser = show_subparsers.add_parser(
        "study",
        help="Show one StudyCard by canonical ID",
    )
    show_study_parser.add_argument(
        "--study-id",
        required=True,
        help="Canonical StudyCard identifier",
    )
    show_study_parser.set_defaults(handler=_run_show_study)

    show_dataset_parser = show_subparsers.add_parser(
        "dataset",
        help="Show one DatasetCard by canonical ID",
    )
    show_dataset_parser.add_argument(
        "--dataset-id",
        required=True,
        help="Canonical DatasetCard identifier",
    )
    show_dataset_parser.set_defaults(handler=_run_show_dataset)

    show_claim_parser = show_subparsers.add_parser(
        "claim",
        help="Show one ClaimCard by canonical ID",
    )
    show_claim_parser.add_argument(
        "--claim-id",
        required=True,
        help="Canonical ClaimCard identifier",
    )
    show_claim_parser.set_defaults(handler=_run_show_claim)

    list_parser = subparsers.add_parser(
        "list",
        help="List compact registry summaries for discovery",
    )
    list_subparsers = list_parser.add_subparsers(
        dest="list_command",
        required=True,
    )
    list_studies_parser = list_subparsers.add_parser(
        "studies",
        help="List compact StudyCard summaries",
    )
    list_studies_parser.set_defaults(handler=_run_list_studies)

    list_datasets_parser = list_subparsers.add_parser(
        "datasets",
        help="List compact DatasetCard summaries",
    )
    list_datasets_parser.set_defaults(handler=_run_list_datasets)

    list_claims_parser = list_subparsers.add_parser(
        "claims",
        help="List compact ClaimCard summaries",
    )
    list_claims_parser.set_defaults(handler=_run_list_claims)

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete one registry card by canonical ID without force or cascade",
    )
    delete_subparsers = delete_parser.add_subparsers(
        dest="delete_command",
        required=True,
    )
    delete_study_parser = delete_subparsers.add_parser(
        "study",
        help="Delete one StudyCard by canonical ID when no dependent cards exist",
    )
    delete_study_parser.add_argument(
        "--study-id",
        required=True,
        help="Canonical StudyCard identifier",
    )
    delete_study_parser.set_defaults(handler=_run_delete_study)

    delete_dataset_parser = delete_subparsers.add_parser(
        "dataset",
        help="Delete one DatasetCard by canonical ID when no dependent claims exist",
    )
    delete_dataset_parser.add_argument(
        "--dataset-id",
        required=True,
        help="Canonical DatasetCard identifier",
    )
    delete_dataset_parser.set_defaults(handler=_run_delete_dataset)

    delete_claim_parser = delete_subparsers.add_parser(
        "claim",
        help="Delete one ClaimCard by canonical ID",
    )
    delete_claim_parser.add_argument(
        "--claim-id",
        required=True,
        help="Canonical ClaimCard identifier",
    )
    delete_claim_parser.set_defaults(handler=_run_delete_claim)

    return parser


def _describe_paths(paths: dict[str, Path]) -> list[str]:
    lines: list[str] = []
    for name, path in paths.items():
        state = "exists" if path.exists() else "missing"
        lines.append(f"{name}: {path} [{state}]")
    return lines


def _print_lines(lines: Iterable[str]) -> None:
    for line in lines:
        print(line)


def _configure_study_ingest_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--study-id", required=True, help="Canonical StudyCard identifier")
    parser.add_argument(
        "--citation-handle",
        required=True,
        help="Stable citation or accession handle for the study",
    )
    parser.add_argument(
        "--tumor-type",
        action="append",
        required=True,
        help="Repeatable tumor scope tag",
    )
    parser.add_argument(
        "--therapy-scope",
        action="append",
        required=True,
        help="Repeatable therapy scope tag",
    )
    parser.add_argument(
        "--relevance-scope",
        action="append",
        required=True,
        help="Repeatable relevance scope tag",
    )
    parser.add_argument(
        "--screening-decision",
        required=True,
        choices=allowed_screening_decisions(),
        help="StudyCard screening decision",
    )
    parser.add_argument(
        "--status",
        required=True,
        choices=allowed_study_statuses(),
        help="StudyCard lifecycle status",
    )
    parser.add_argument(
        "--created-from",
        required=True,
        help="Provenance note describing where this StudyCard came from",
    )
    parser.add_argument(
        "--screening-note",
        default=None,
        help="Optional screening note stored on the StudyCard",
    )
    parser.add_argument(
        "--source-artifact",
        default=None,
        help="Optional source artifact locator stored on the StudyCard",
    )


def _configure_dataset_ingest_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dataset-id", required=True, help="Canonical DatasetCard identifier")
    parser.add_argument(
        "--study-id",
        required=True,
        help="Canonical parent StudyCard identifier",
    )
    parser.add_argument(
        "--status",
        required=True,
        choices=allowed_dataset_statuses(),
        help="DatasetCard lifecycle status",
    )
    parser.add_argument(
        "--modality-scope",
        action="append",
        required=True,
        help="Repeatable modality scope tag",
    )
    parser.add_argument(
        "--platform-summary",
        required=True,
        help="Minimal human-readable platform or assay summary",
    )
    parser.add_argument(
        "--cohort-summary",
        required=True,
        help="Minimal human-readable cohort summary",
    )
    parser.add_argument(
        "--locator-confidence-note",
        required=True,
        help="Short provenance note explaining why the locator is trusted",
    )
    parser.add_argument(
        "--source-locator",
        required=True,
        help="Primary accession, URL, or supplement locator for the dataset",
    )
    parser.add_argument(
        "--availability-status",
        required=True,
        choices=allowed_dataset_availability_statuses(),
        help="Dataset access label",
    )
    parser.add_argument(
        "--accession-id",
        default=None,
        help="Optional separate accession identifier",
    )
    parser.add_argument(
        "--availability-note",
        default=None,
        help="Optional access-condition note",
    )
    parser.add_argument(
        "--artifact-locator",
        default=None,
        help="Optional bound artifact locator",
    )


def _configure_claim_ingest_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--from-file",
        default=None,
        type=Path,
        help=(
            "Load one ClaimCard ingest mapping from a YAML file; ClaimCard-only "
            "and not combinable with field flags"
        ),
    )
    parser.add_argument("--claim-id", help="Canonical ClaimCard identifier")
    parser.add_argument(
        "--study-id",
        help="Canonical parent StudyCard identifier",
    )
    parser.add_argument(
        "--claim-text",
        help="Human-readable claim text captured for the ClaimCard",
    )
    parser.add_argument(
        "--claim-type",
        help="Short category label describing the claim type",
    )
    parser.add_argument(
        "--provenance-pointer",
        help="Figure, table, supplement, or text-span pointer for the claim",
    )
    parser.add_argument(
        "--status",
        choices=allowed_claim_statuses(),
        help="ClaimCard lifecycle status",
    )
    parser.add_argument(
        "--review-readiness",
        choices=allowed_claim_review_readiness(),
        help="ClaimCard review readiness label",
    )
    parser.add_argument(
        "--created-from",
        help="Provenance note describing where this ClaimCard came from",
    )
    parser.add_argument(
        "--dataset-id",
        action="append",
        default=None,
        help="Repeatable referenced DatasetCard identifier",
    )
    parser.add_argument(
        "--claim-summary-handle",
        default=None,
        help="Optional normalized summary handle stored on the ClaimCard",
    )


def _build_studycard_cli_input(args: argparse.Namespace) -> StudyCardCLIInput:
    cli_input: StudyCardCLIInput = {
        "study_id": args.study_id,
        "citation_handle": args.citation_handle,
        "tumor_type": list(args.tumor_type),
        "therapy_scope": list(args.therapy_scope),
        "relevance_scope": list(args.relevance_scope),
        "screening_decision": args.screening_decision,
        "status": args.status,
        "created_from": args.created_from,
    }
    if args.screening_note is not None:
        cli_input["screening_note"] = args.screening_note
    if args.source_artifact is not None:
        cli_input["source_artifact"] = args.source_artifact
    return cli_input


def _build_datasetcard_cli_input(args: argparse.Namespace) -> DatasetCardCLIInput:
    cli_input: DatasetCardCLIInput = {
        "dataset_id": args.dataset_id,
        "study_id": args.study_id,
        "status": args.status,
        "modality_scope": list(args.modality_scope),
        "platform_summary": args.platform_summary,
        "cohort_summary": args.cohort_summary,
        "locator_confidence_note": args.locator_confidence_note,
        "source_locator": args.source_locator,
        "availability_status": args.availability_status,
    }
    if args.accession_id is not None:
        cli_input["accession_id"] = args.accession_id
    if args.availability_note is not None:
        cli_input["availability_note"] = args.availability_note
    if args.artifact_locator is not None:
        cli_input["artifact_locator"] = args.artifact_locator
    return cli_input


def _build_claimcard_cli_input(args: argparse.Namespace) -> ClaimCardCLIInput:
    cli_input: ClaimCardCLIInput = {
        "claim_id": args.claim_id,
        "study_id": args.study_id,
        "claim_text": args.claim_text,
        "claim_type": args.claim_type,
        "provenance_pointer": args.provenance_pointer,
        "status": args.status,
        "review_readiness": args.review_readiness,
        "created_from": args.created_from,
    }
    if args.dataset_id is not None:
        cli_input["dataset_ids"] = list(args.dataset_id)
    if args.claim_summary_handle is not None:
        cli_input["claim_summary_handle"] = args.claim_summary_handle
    return cli_input


def _claimcard_field_flag_values(args: argparse.Namespace) -> dict[str, object]:
    return {
        "claim_id": args.claim_id,
        "study_id": args.study_id,
        "claim_text": args.claim_text,
        "claim_type": args.claim_type,
        "provenance_pointer": args.provenance_pointer,
        "status": args.status,
        "review_readiness": args.review_readiness,
        "created_from": args.created_from,
        "dataset_id": args.dataset_id,
        "claim_summary_handle": args.claim_summary_handle,
    }


def _resolve_claimcard_ingest_mode(args: argparse.Namespace) -> str:
    field_values = _claimcard_field_flag_values(args)
    provided_field_flags = [
        option
        for field_name, option in _CLAIMCARD_ALL_FIELD_FLAGS
        if field_values[field_name] is not None
    ]
    if args.from_file is not None:
        if provided_field_flags:
            raise ValueError(
                "ClaimCard --from-file cannot be combined with field flags: "
                + ", ".join(provided_field_flags)
                + "."
            )
        return "from_file"

    missing_required_flags = [
        option
        for field_name, option in _CLAIMCARD_REQUIRED_FIELD_FLAGS
        if field_values[field_name] is None
    ]
    if missing_required_flags:
        raise ValueError(
            "ClaimCard flag-based ingest requires "
            + ", ".join(missing_required_flags)
            + " unless --from-file is used."
        )
    return "flags"


def _build_show_cli_input(*, card_family: str, target_id: str) -> ShowCLIInput:
    return {"card_family": card_family, "target_id": target_id}


def _build_list_cli_input(*, card_family: str) -> ListCLIInput:
    return {"card_family": card_family}


def _build_delete_cli_input(*, card_family: str, target_id: str) -> DeleteCLIInput:
    return {"card_family": card_family, "target_id": target_id}


@contextmanager
def _configured_runtime_environment(config_path: str | None) -> Iterator[None]:
    config = load_project_config(config_path)
    previous = os.environ.get("MACRO_VERITAS_CONFIG")
    os.environ["MACRO_VERITAS_CONFIG"] = str(config.config_path)
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("MACRO_VERITAS_CONFIG", None)
        else:
            os.environ["MACRO_VERITAS_CONFIG"] = previous


def _emit_command_result(result: CommandExecutionResult, *, command_path: str) -> int:
    message = format_command_result_for_cli(result, command_path=command_path)
    stream = sys.stdout if result["ok"] else sys.stderr
    print(message, file=stream)
    return 0 if result["ok"] else 1


def _emit_json_document(document: object) -> int:
    print(json.dumps(document, indent=2, sort_keys=True))
    return 0


def _run_status(args: argparse.Namespace) -> int:
    config = load_project_config(args.config)
    lines = [
        "MacroVeritas scaffold status",
        f"stage: {SCAFFOLD_STAGE}",
        f"config_path: {config.config_path}",
        f"project_name: {config.project_name}",
        f"repo_name: {config.repo_name}",
        f"package_name: {config.package_name}",
        f"data_root: {config.data_root}",
        "layout:",
        *_describe_paths(config.layout_paths()),
    ]
    _print_lines(lines)
    return 0


def _run_show_config(args: argparse.Namespace) -> int:
    config = load_project_config(args.config)
    print(json.dumps(config.to_display_dict(), indent=2, sort_keys=True))
    return 0


def _run_init_layout(args: argparse.Namespace) -> int:
    config = load_project_config(args.config)
    created: list[Path] = []
    existing: list[Path] = []
    would_create: list[Path] = []

    for path in config.layout_paths().values():
        if path.exists():
            existing.append(path)
            continue
        if args.dry_run:
            would_create.append(path)
            continue
        path.mkdir(parents=True, exist_ok=True)
        created.append(path)

    if args.dry_run:
        _print_lines(["Dry run only. No directories were created."])
        _print_lines(f"would_create: {path}" for path in would_create)
    else:
        _print_lines(f"created: {path}" for path in created)

    _print_lines(f"existing: {path}" for path in existing)
    return 0


def _run_ingest_study(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_studycard_cli_input(args)
        normalized_input = ingest_command.normalize_public_studycard_cli_input(cli_input)
        with _configured_runtime_environment(args.config):
            result = ingest_command.execute_studycard_ingest_input(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"ingest study failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    return _emit_command_result(result, command_path="ingest study")


def _run_ingest_dataset(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_datasetcard_cli_input(args)
        normalized_input = ingest_command.normalize_public_datasetcard_cli_input(cli_input)
        with _configured_runtime_environment(args.config):
            result = ingest_command.execute_datasetcard_ingest_input(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"ingest dataset failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    return _emit_command_result(result, command_path="ingest dataset")


def _run_ingest_claim(args: argparse.Namespace) -> int:
    try:
        mode = _resolve_claimcard_ingest_mode(args)
        with _configured_runtime_environment(args.config):
            if mode == "from_file":
                result = ingest_command.execute_claimcard_ingest_from_file(args.from_file)
            else:
                cli_input = _build_claimcard_cli_input(args)
                normalized_input = ingest_command.normalize_public_claimcard_cli_input(cli_input)
                result = ingest_command.execute_claimcard_ingest_input(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"ingest claim failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    return _emit_command_result(result, command_path="ingest claim")


def _run_show_study(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_show_cli_input(card_family="StudyCard", target_id=args.study_id)
        normalized_input = show_command.normalize_show_input(cli_input)
        with _configured_runtime_environment(args.config):
            card, error = show_command.execute_show_study(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"show study failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    if error is not None:
        return _emit_command_result(error, command_path="show study")
    return _emit_json_document(card)



def _run_show_dataset(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_show_cli_input(card_family="DatasetCard", target_id=args.dataset_id)
        normalized_input = show_command.normalize_show_input(cli_input)
        with _configured_runtime_environment(args.config):
            card, error = show_command.execute_show_dataset(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"show dataset failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    if error is not None:
        return _emit_command_result(error, command_path="show dataset")
    return _emit_json_document(card)



def _run_show_claim(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_show_cli_input(card_family="ClaimCard", target_id=args.claim_id)
        normalized_input = show_command.normalize_show_input(cli_input)
        with _configured_runtime_environment(args.config):
            card, error = show_command.execute_show_claim(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"show claim failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    if error is not None:
        return _emit_command_result(error, command_path="show claim")
    return _emit_json_document(card)


def _run_list_studies(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_list_cli_input(card_family="StudyCard")
        normalized_input = listing_command.normalize_list_input(cli_input)
        with _configured_runtime_environment(args.config):
            summaries, error = listing_command.execute_list_studies(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"list studies failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    if error is not None:
        return _emit_command_result(error, command_path="list studies")
    return _emit_json_document(summaries)



def _run_list_datasets(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_list_cli_input(card_family="DatasetCard")
        normalized_input = listing_command.normalize_list_input(cli_input)
        with _configured_runtime_environment(args.config):
            summaries, error = listing_command.execute_list_datasets(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"list datasets failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    if error is not None:
        return _emit_command_result(error, command_path="list datasets")
    return _emit_json_document(summaries)



def _run_list_claims(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_list_cli_input(card_family="ClaimCard")
        normalized_input = listing_command.normalize_list_input(cli_input)
        with _configured_runtime_environment(args.config):
            summaries, error = listing_command.execute_list_claims(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"list claims failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    if error is not None:
        return _emit_command_result(error, command_path="list claims")
    return _emit_json_document(summaries)


def _run_delete_study(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_delete_cli_input(card_family="StudyCard", target_id=args.study_id)
        normalized_input = delete_command.normalize_delete_input(cli_input)
        with _configured_runtime_environment(args.config):
            result = delete_command.execute_delete_study(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"delete study failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    return _emit_command_result(result, command_path="delete study")


def _run_delete_dataset(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_delete_cli_input(card_family="DatasetCard", target_id=args.dataset_id)
        normalized_input = delete_command.normalize_delete_input(cli_input)
        with _configured_runtime_environment(args.config):
            result = delete_command.execute_delete_dataset(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"delete dataset failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    return _emit_command_result(result, command_path="delete dataset")


def _run_delete_claim(args: argparse.Namespace) -> int:
    try:
        cli_input = _build_delete_cli_input(card_family="ClaimCard", target_id=args.claim_id)
        normalized_input = delete_command.normalize_delete_input(cli_input)
        with _configured_runtime_environment(args.config):
            result = delete_command.execute_delete_claim(normalized_input)
    except (FileNotFoundError, ValueError) as exc:
        print(
            f"delete claim failed [invalid_payload]: {exc}",
            file=sys.stderr,
        )
        return 1

    return _emit_command_result(result, command_path="delete claim")



def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "handler", None):
        parser.print_help()
        return 0

    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
