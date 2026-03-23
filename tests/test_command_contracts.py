from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import get_args

import pytest

from macro_veritas.commands import (
    audit,
    bind,
    common,
    delete,
    extract,
    grade,
    ingest,
    listing,
    review,
    run,
    show,
)
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
        "show",
        "list",
        "delete",
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
    assert get_args(shared_types.CommandErrorCategory) == (
        "duplicate_target",
        "dependency_exists",
        "missing_reference",
        "invalid_payload",
        "unsupported_operation",
        "registry_failure",
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
    assert shared_types.CommandExecutionResult.__required_keys__ == {
        "ok",
        "operation",
        "card_family",
        "target_id",
        "message",
    }
    assert shared_types.CommandExecutionResult.__optional_keys__ == {
        "error_category",
    }
    assert shared_types.StudyCardIngestInput.__required_keys__ == {
        "study_id",
        "citation_handle",
        "tumor_types",
        "therapy_scopes",
        "relevance_scopes",
        "screening_decision",
        "status",
        "created_from",
    }
    assert shared_types.StudyCardIngestInput.__optional_keys__ == {
        "screening_note",
        "source_artifact",
    }
    assert shared_types.StudyCardCLIInput.__required_keys__ == {
        "study_id",
        "citation_handle",
        "tumor_type",
        "therapy_scope",
        "relevance_scope",
        "screening_decision",
        "status",
        "created_from",
    }
    assert shared_types.StudyCardCLIInput.__optional_keys__ == {
        "screening_note",
        "source_artifact",
    }
    assert shared_types.DatasetCardIngestInput.__required_keys__ == {
        "dataset_id",
        "study_id",
        "source_locator",
        "availability_status",
        "modality_scopes",
        "cohort_summary",
        "platform_summary",
        "status",
        "locator_confidence_note",
    }
    assert shared_types.DatasetCardIngestInput.__optional_keys__ == {
        "accession_id",
        "artifact_locator",
        "availability_note",
    }
    assert shared_types.DatasetCardCLIInput.__required_keys__ == {
        "dataset_id",
        "study_id",
        "source_locator",
        "availability_status",
        "modality_scope",
        "cohort_summary",
        "platform_summary",
        "status",
        "locator_confidence_note",
    }
    assert shared_types.DatasetCardCLIInput.__optional_keys__ == {
        "accession_id",
        "artifact_locator",
        "availability_note",
    }
    assert shared_types.ClaimCardIngestInput.__required_keys__ == {
        "claim_id",
        "study_id",
        "claim_text",
        "claim_type",
        "provenance_pointer",
        "status",
        "review_readiness",
        "created_from",
    }
    assert shared_types.ClaimCardIngestInput.__optional_keys__ == {
        "dataset_ids",
        "claim_summary_handle",
    }
    assert shared_types.ClaimCardCLIInput.__required_keys__ == {
        "claim_id",
        "study_id",
        "claim_text",
        "claim_type",
        "provenance_pointer",
        "status",
        "review_readiness",
        "created_from",
    }
    assert shared_types.ClaimCardCLIInput.__optional_keys__ == {
        "dataset_ids",
        "claim_summary_handle",
    }


    assert shared_types.ShowCLIInput.__required_keys__ == {
        "card_family",
        "target_id",
    }
    assert shared_types.ShowCLIInput.__optional_keys__ == set()
    assert shared_types.ListCLIInput.__required_keys__ == {"card_family"}
    assert shared_types.ListCLIInput.__optional_keys__ == set()
    assert shared_types.DeleteCLIInput.__required_keys__ == {
        "card_family",
        "target_id",
    }
    assert shared_types.DeleteCLIInput.__optional_keys__ == set()
    assert shared_types.StudyCardSummary.__required_keys__ == {
        "study_id",
        "status",
        "citation_handle",
    }
    assert shared_types.DatasetCardSummary.__required_keys__ == {
        "dataset_id",
        "study_id",
        "status",
    }
    assert shared_types.ClaimCardSummary.__required_keys__ == {
        "claim_id",
        "study_id",
        "status",
        "claim_type",
    }


def test_common_command_style_descriptor_is_static() -> None:
    style = common.describe_command_contract_style()
    payload_style = common.describe_command_payload_contract_style()
    payload_boundary = common.describe_gateway_payload_boundary()
    runtime_boundary = common.describe_command_runtime_boundary()
    result_style = common.describe_command_result_style()

    assert style["module_layout"].startswith("one module per reserved command family")
    assert style["parser_builder_shape"] == "build_parser(subparsers_or_parser: object) -> None"
    assert "StudyCard, DatasetCard, and ClaimCard ingest/show/list/delete paths are runtime-real" in style["runtime_status"]
    assert style["public_exposure"] == (
        "public ingest study, ingest dataset, ingest claim, ingest claim --from-file, show study, show dataset, show claim, list studies, list datasets, list claims, delete study, delete dataset, and delete claim paths only; all other reserved families remain non-public"
    )
    assert payload_style["source_of_truth_doc"] == "docs/payload_contracts.md"
    assert "outside the frozen payload contract" in payload_style["raw_cli_argument_layer"]
    assert payload_boundary["gateway_consumes_argparse_objects"] is False
    assert payload_boundary["gateway_consumes_full_card_payloads_only"] is True
    assert payload_boundary["patch_payloads_supported"] is False
    assert runtime_boundary["source_of_truth_doc"] == "docs/cli_command_contracts.md"
    assert "ingest study" in runtime_boundary["public_cli_exposure"]
    assert "ingest dataset" in runtime_boundary["public_cli_exposure"]
    assert "ingest claim" in runtime_boundary["public_cli_exposure"]
    assert "ingest claim --from-file" in runtime_boundary["public_cli_exposure"]
    assert "show study" in runtime_boundary["public_cli_exposure"]
    assert "show dataset" in runtime_boundary["public_cli_exposure"]
    assert "show claim" in runtime_boundary["public_cli_exposure"]
    assert "list studies" in runtime_boundary["public_cli_exposure"]
    assert "list datasets" in runtime_boundary["public_cli_exposure"]
    assert "list claims" in runtime_boundary["public_cli_exposure"]
    assert "delete study" in runtime_boundary["public_cli_exposure"]
    assert "delete dataset" in runtime_boundary["public_cli_exposure"]
    assert "delete claim" in runtime_boundary["public_cli_exposure"]
    assert "public StudyCard CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public DatasetCard CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public ClaimCard CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public ClaimCard file-based CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public StudyCard show CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public DatasetCard show CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public ClaimCard show CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public StudyCard list CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public DatasetCard list CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public ClaimCard list CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public StudyCard delete CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public DatasetCard delete CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "public ClaimCard delete CLI adapter" in runtime_boundary["runtime_real_now"]
    assert "DatasetCard plan_create gateway call" in runtime_boundary["runtime_real_now"]
    assert "ClaimCard plan_create gateway call" in runtime_boundary["runtime_real_now"]
    assert "ClaimCard file-loaded ingest input" in runtime_boundary["runtime_real_now"]
    assert "StudyCard get-by-id gateway call" in runtime_boundary["runtime_real_now"]
    assert "DatasetCard get-by-id gateway call" in runtime_boundary["runtime_real_now"]
    assert "ClaimCard get-by-id gateway call" in runtime_boundary["runtime_real_now"]
    assert "StudyCard list-by-family gateway call" in runtime_boundary["runtime_real_now"]
    assert "DatasetCard list-by-family gateway call" in runtime_boundary["runtime_real_now"]
    assert "ClaimCard list-by-family gateway call" in runtime_boundary["runtime_real_now"]
    assert "StudyCard delete gateway call" in runtime_boundary["runtime_real_now"]
    assert "DatasetCard delete gateway call" in runtime_boundary["runtime_real_now"]
    assert "ClaimCard delete gateway call" in runtime_boundary["runtime_real_now"]
    assert "ClaimCard ingest" not in runtime_boundary["still_skeleton_only"]
    assert result_style["output_type"] == "CommandExecutionResult"
    assert result_style["failure_field"] == "error_category"
    assert "missing_reference" in result_style["supported_error_categories"]
    assert "dependency_exists" in result_style["supported_error_categories"]


def test_command_family_modules_export_static_metadata() -> None:
    modules = [ingest, show, listing, delete, bind, extract, audit, review, run, grade]

    for module in modules:
        family = module.family_name()
        descriptor = module.describe_command_family()

        assert descriptor["family_name"] == family
        if family == "list":
            assert descriptor["owning_module"].endswith(".listing")
        else:
            assert descriptor["owning_module"].endswith(f".{family}")
        assert descriptor["parser_builder"] == "build_parser"
        assert descriptor["handler"] == f"handle_{family}_command"
        if family == "ingest":
            assert descriptor["public_exposure"] == (
                "public `ingest study`, `ingest dataset`, `ingest claim`, and ClaimCard-only single-file YAML intake at `ingest claim --from-file`; update semantics stay non-public"
            )
        elif family == "show":
            assert descriptor["public_exposure"] == (
                "public `show study`, `show dataset`, and `show claim` only; list/search/update/delete semantics stay non-public"
            )
        elif family == "list":
            assert descriptor["public_exposure"] == (
                "public `list studies`, `list datasets`, and `list claims` only; search/filter/update/delete semantics stay non-public"
            )
        elif family == "delete":
            assert descriptor["public_exposure"] == (
                "public `delete study`, `delete dataset`, and `delete claim` only; force/cascade/filter/update semantics stay non-public"
            )
        else:
            assert descriptor["public_exposure"] == "reserved internal; not public CLI"
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
    ingest_result = ingest.handle_ingest_command(object())
    list_result = listing.handle_list_command(object())
    delete_result = delete.handle_delete_command(object())

    assert ingest_result == {
        "ok": False,
        "operation": "ingest",
        "card_family": "StudyCard",
        "target_id": None,
        "message": "StudyCard ingest input is invalid: handle_ingest_command expects a mapping-based internal input.",
        "error_category": "invalid_payload",
    }
    assert list_result == {
        "ok": False,
        "operation": "list",
        "card_family": "StudyCard",
        "target_id": None,
        "message": "StudyCard list input is invalid: handle_list_command expects a mapping-based internal input.",
        "error_category": "invalid_payload",
    }
    assert delete_result == {
        "ok": False,
        "operation": "delete",
        "card_family": "StudyCard",
        "target_id": None,
        "message": "StudyCard delete input is invalid: handle_delete_command expects a mapping-based internal input.",
        "error_category": "invalid_payload",
    }

    with pytest.raises(NotImplementedError, match="run family is reserved"):
        run.handle_run_command(object())


def test_public_cli_help_exposes_only_ingest_show_list_and_delete_families_beyond_scaffold_commands() -> None:
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
    assert "ingest" in result.stdout
    assert "show" in result.stdout
    assert "list" in result.stdout
    assert "delete" in result.stdout
    assert "bind" not in result.stdout
    assert "extract" not in result.stdout
    assert "audit" not in result.stdout
    assert "review" not in result.stdout
    assert "grade" not in result.stdout
