from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
from typing import Iterable, Iterator

from .commands.common import format_command_result_for_cli
from .commands import ingest as ingest_command
from .config import load_project_config
from .registry.study import allowed_screening_decisions, allowed_statuses
from .shared.types import CommandExecutionResult, StudyCardCLIInput

SCAFFOLD_STAGE = "Initialization / scaffold"


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
        help="Create registry records through the first public ingest path",
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
        choices=allowed_statuses(),
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


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "handler", None):
        parser.print_help()
        return 0

    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
