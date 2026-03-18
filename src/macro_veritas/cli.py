from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from .config import load_project_config

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


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not getattr(args, "handler", None):
        parser.print_help()
        return 0

    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
