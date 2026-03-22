from __future__ import annotations

from pathlib import Path

import pytest

from macro_veritas.commands import ingest
from macro_veritas.registry.errors import RegistryError
from macro_veritas.registry.layout import study_card_path


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


def _studycard_ingest_kwargs(
    study_id: str = "study-001",
    *,
    status: str = "draft",
) -> dict[str, object]:
    return {
        "study_id": study_id,
        "citation_handle": f"doi:{study_id}",
        "tumor_type": "glioma",
        "therapy_scope": "immunotherapy",
        "relevance_scope": "preclinical",
        "screening_decision": "include",
        "status": status,
        "created_from": "seeded in command test",
        "screening_note": "passed internal review",
        "source_artifact": "raw/studies/study-001.pdf",
    }


@pytest.fixture
def configured_registry_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    return data_root.resolve() / "registry"


def test_execute_studycard_ingest_writes_canonical_file_and_reports_success(
    configured_registry_root: Path,
) -> None:
    result = ingest.execute_studycard_ingest(**_studycard_ingest_kwargs())

    canonical_path = study_card_path(configured_registry_root, "study-001")

    assert canonical_path.is_file()
    assert canonical_path.read_text(encoding="utf-8") == (
        "\n".join(
            [
                "study_id: study-001",
                "citation_handle: doi:study-001",
                "tumor_scope_tags:",
                "- glioma",
                "therapy_scope_tags:",
                "- immunotherapy",
                "relevance_scope_tags:",
                "- preclinical",
                "screening_decision: include",
                "status: draft",
                "created_from_note: seeded in command test",
                "screening_note: passed internal review",
                "source_artifact_locator: raw/studies/study-001.pdf",
                "",
            ]
        )
    )
    assert result == {
        "ok": True,
        "operation": "ingest",
        "card_family": "StudyCard",
        "target_id": "study-001",
        "message": "StudyCard ingest created the canonical StudyCard record.",
    }


def test_duplicate_studycard_ingest_returns_translated_failure_result(
    configured_registry_root: Path,
) -> None:
    ingest.execute_studycard_ingest(**_studycard_ingest_kwargs())

    result = ingest.execute_studycard_ingest(**_studycard_ingest_kwargs())

    assert result == {
        "ok": False,
        "operation": "ingest",
        "card_family": "StudyCard",
        "target_id": "study-001",
        "message": (
            "StudyCard ingest did not write because the canonical StudyCard already exists."
        ),
        "error_category": "duplicate_target",
    }


def test_invalid_studycard_payload_returns_translated_failure_result(
    configured_registry_root: Path,
) -> None:
    result = ingest.execute_studycard_ingest(
        **_studycard_ingest_kwargs(status="invalid-status")
    )

    assert result["ok"] is False
    assert result["error_category"] == "invalid_payload"
    assert result["target_id"] == "study-001"
    assert "invalid StudyCard data" in result["message"]
    assert "status" in result["message"]


def test_unsafe_study_id_returns_translated_unsupported_result(
    configured_registry_root: Path,
) -> None:
    result = ingest.execute_studycard_ingest(
        **_studycard_ingest_kwargs(study_id="../study-001")
    )

    assert result == {
        "ok": False,
        "operation": "ingest",
        "card_family": "StudyCard",
        "target_id": "../study-001",
        "message": "StudyCard ingest rejected an unsafe canonical study identifier.",
        "error_category": "unsupported_operation",
    }


def test_registry_failure_is_translated_without_leaking_raw_contract(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise_registry_failure(card: object) -> object:
        raise RegistryError("simulated registry gateway failure")

    monkeypatch.setattr(ingest, "create_study_card", _raise_registry_failure)

    result = ingest.execute_studycard_ingest(**_studycard_ingest_kwargs())

    assert result == {
        "ok": False,
        "operation": "ingest",
        "card_family": "StudyCard",
        "target_id": "study-001",
        "message": "StudyCard ingest failed at the registry gateway boundary.",
        "error_category": "registry_failure",
    }

