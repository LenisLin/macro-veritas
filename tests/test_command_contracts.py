from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import get_args

import pytest

from macro_veritas.commands import audit, bind, common, extract, grade, ingest, review, run
from macro_veritas.shared import types as shared_types

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_ROOT) if not existing else f"{SRC_ROOT}{os.pathsep}{existing}"
    return env


def test_shared_command_contract_types_are_frozen() -> None:
    assert get_args(shared_types.CommandFamilyName) == (
        "ingest",
        "bind",
        "extract",
        "audit",
        "review",
        "run",
        "grade",
    )
    assert get_args(shared_types.CommandPayloadUsage) == (
        "prepare_create",
        "prepare_update",
        "prepare_create_or_update",
        "read_only",
    )
    assert tuple(shared_types.CommandPayloadDescriptor.__annotations__.keys()) == (
        "card_family",
        "payload_type",
        "usage",
        "gateway_reads",
        "gateway_mutations",
        "notes",
    )
    assert tuple(shared_types.CommandDescriptor.__annotations__.keys()) == (
        "family_name",
        "owning_module",
        "owning_domain",
        "purpose",
        "primary_inputs",
        "primary_outputs",
        "dependency_contracts",
        "parser_builder",
        "handler",
        "public_exposure",
        "non_goals",
    )


def test_common_command_style_descriptor_is_static() -> None:
    style = common.describe_command_contract_style()
    payload_style = common.describe_command_payload_contract_style()
    payload_boundary = common.describe_gateway_payload_boundary()

    assert style["module_layout"].startswith("one module per reserved command family")
    assert style["parser_builder_shape"] == "build_parser(subparsers_or_parser: object) -> None"
    assert style["runtime_status"] == "internal skeleton only"
    assert style["public_exposure"] == "reserved but not part of the stable public CLI"
    assert payload_style["source_of_truth_doc"] == "docs/payload_contracts.md"
    assert payload_style["raw_cli_argument_layer"].startswith("deferred")
    assert payload_boundary["gateway_consumes_argparse_objects"] is False
    assert payload_boundary["gateway_consumes_full_card_payloads_only"] is True
    assert payload_boundary["patch_payloads_supported"] is False


def test_command_family_modules_export_static_metadata() -> None:
    modules = [ingest, bind, extract, audit, review, run, grade]

    for module in modules:
        family = module.family_name()
        descriptor = module.describe_command_family()

        assert descriptor["family_name"] == family
        assert descriptor["owning_module"].endswith(f".{family}")
        assert descriptor["parser_builder"] == "build_parser"
        assert descriptor["handler"] == f"handle_{family}_command"
        assert descriptor["public_exposure"] == "reserved internal skeleton; not public CLI"
        assert isinstance(module.list_expected_gateway_dependencies(), tuple)
        assert isinstance(module.describe_payload_contracts(), tuple)
        assert isinstance(module.list_deferred_capabilities(), tuple)
        assert module.build_parser(object()) is None

        for payload_descriptor in module.describe_payload_contracts():
            assert payload_descriptor["payload_type"].endswith("Payload")
            assert isinstance(payload_descriptor["gateway_reads"], tuple)
            assert isinstance(payload_descriptor["gateway_mutations"], tuple)
            assert isinstance(payload_descriptor["notes"], tuple)


def test_command_handlers_raise_precise_placeholders() -> None:
    with pytest.raises(NotImplementedError, match="`ingest` family is reserved"):
        ingest.handle_ingest_command(object())

    with pytest.raises(NotImplementedError, match="`run` family is reserved"):
        run.handle_run_command(object())


def test_public_cli_help_does_not_expose_reserved_command_families() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "status" in result.stdout
    assert "show-config" in result.stdout
    assert "init-layout" in result.stdout
    assert "ingest" not in result.stdout
    assert "bind" not in result.stdout
    assert "extract" not in result.stdout
    assert "audit" not in result.stdout
    assert "review" not in result.stdout
    assert "grade" not in result.stdout
