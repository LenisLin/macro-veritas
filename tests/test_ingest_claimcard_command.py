from __future__ import annotations

from pathlib import Path

import pytest

from macro_veritas.commands import ingest
from macro_veritas.registry.gateway import create_dataset_card, create_study_card
from macro_veritas.registry.layout import claim_card_path


def _write_config(path: Path, data_root: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "project_name: MacroVeritas",
                "repo_name: macro-veritas",
                "package_name: macro_veritas",
                f"data_root: {data_root}",
                "registry_root: registry",
                "runs_root: runs",
                "reports_root: reports",
                "raw_root: raw",
                "processed_root: processed",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _study_card(study_id: str = "study-001") -> dict[str, object]:
    return {
        "study_id": study_id,
        "citation_handle": f"doi:{study_id}",
        "tumor_scope_tags": ["glioma"],
        "therapy_scope_tags": ["immunotherapy"],
        "relevance_scope_tags": ["preclinical"],
        "screening_decision": "include",
        "status": "registered",
        "created_from_note": "seeded in claim command test",
    }


def _dataset_card(dataset_id: str, *, study_id: str = "study-001") -> dict[str, object]:
    return {
        "dataset_id": dataset_id,
        "study_id": study_id,
        "source_locator": f"https://example.org/{dataset_id}",
        "availability_status": "open",
        "modality_scope_tags": ["rna-seq"],
        "cohort_summary": "adult cohort",
        "platform_summary": "Illumina",
        "status": "registered",
        "locator_confidence_note": "confirmed in supplement",
    }


def _claimcard_ingest_kwargs(
    claim_id: str = "claim-001",
    *,
    study_id: str = "study-001",
    status: str = "captured",
    review_readiness: str = "needs_scope",
    dataset_ids: list[str] | None = None,
) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "claim_id": claim_id,
        "study_id": study_id,
        "claim_text": f"Claim text for {claim_id}",
        "claim_type": "association",
        "provenance_pointer": "figure-2",
        "status": status,
        "review_readiness": review_readiness,
        "created_from": "seeded in claim command test",
        "claim_summary_handle": "claim-1",
    }
    if dataset_ids is not None:
        kwargs["dataset_ids"] = dataset_ids
    return kwargs


@pytest.fixture
def configured_registry_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    return data_root.resolve() / "registry"


def test_execute_claimcard_ingest_writes_canonical_file_and_reports_success(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))

    result = ingest.execute_claimcard_ingest(
        **_claimcard_ingest_kwargs(dataset_ids=["dataset-001"])
    )

    canonical_path = claim_card_path(configured_registry_root, "claim-001")

    assert canonical_path.is_file()
    assert canonical_path.read_text(encoding="utf-8") == (
        "\n".join(
            [
                "claim_id: claim-001",
                "study_id: study-001",
                "claim_text: Claim text for claim-001",
                "claim_type: association",
                "provenance_pointer: figure-2",
                "status: captured",
                "review_readiness: needs_scope",
                "created_from_note: seeded in claim command test",
                "dataset_ids:",
                "- dataset-001",
                "claim_summary_handle: claim-1",
                "",
            ]
        )
    )
    assert result == {
        "ok": True,
        "operation": "ingest",
        "card_family": "ClaimCard",
        "target_id": "claim-001",
        "message": "ClaimCard ingest created the canonical ClaimCard record.",
    }


def test_duplicate_claimcard_ingest_returns_translated_failure_result(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    ingest.execute_claimcard_ingest(**_claimcard_ingest_kwargs())

    result = ingest.execute_claimcard_ingest(**_claimcard_ingest_kwargs())

    assert result == {
        "ok": False,
        "operation": "ingest",
        "card_family": "ClaimCard",
        "target_id": "claim-001",
        "message": (
            "ClaimCard ingest did not write because the canonical ClaimCard already exists."
        ),
        "error_category": "duplicate_target",
    }


def test_missing_parent_study_returns_translated_failure_result(
    configured_registry_root: Path,
) -> None:
    result = ingest.execute_claimcard_ingest(**_claimcard_ingest_kwargs())

    assert result == {
        "ok": False,
        "operation": "ingest",
        "card_family": "ClaimCard",
        "target_id": "claim-001",
        "message": (
            "ClaimCard ingest requires the parent StudyCard 'study-001' to exist before create."
        ),
        "error_category": "missing_reference",
    }


def test_missing_referenced_dataset_returns_translated_failure_result(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    result = ingest.execute_claimcard_ingest(
        **_claimcard_ingest_kwargs(dataset_ids=["dataset-404"])
    )

    assert result == {
        "ok": False,
        "operation": "ingest",
        "card_family": "ClaimCard",
        "target_id": "claim-001",
        "message": (
            "ClaimCard ingest requires referenced DatasetCard(s) to exist before create: "
            "dataset-404."
        ),
        "error_category": "missing_reference",
    }


def test_invalid_claimcard_payload_returns_translated_failure_result(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    result = ingest.execute_claimcard_ingest(
        **_claimcard_ingest_kwargs(status="invalid-status")
    )

    assert result["ok"] is False
    assert result["error_category"] == "invalid_payload"
    assert result["target_id"] == "claim-001"
    assert "invalid ClaimCard data" in result["message"]
    assert "status" in result["message"]


def test_handle_ingest_command_supports_claimcard_mapping_input(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))

    result = ingest.handle_ingest_command(
        {
            "card_family": "ClaimCard",
            "claim_id": "claim-001",
            "study_id": "study-001",
            "claim_text": "Claim text for claim-001",
            "claim_type": "association",
            "provenance_pointer": "figure-2",
            "status": "captured",
            "review_readiness": "needs_scope",
            "created_from": "seeded in claim command test",
            "dataset_ids": ["dataset-001"],
            "claim_summary_handle": "claim-1",
        }
    )

    assert result == {
        "ok": True,
        "operation": "ingest",
        "card_family": "ClaimCard",
        "target_id": "claim-001",
        "message": "ClaimCard ingest created the canonical ClaimCard record.",
    }
