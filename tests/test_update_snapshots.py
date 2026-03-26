from __future__ import annotations

from pathlib import Path

import pytest

from macro_veritas.registry import study_runtime
from macro_veritas.registry.errors import RegistryError
from macro_veritas.registry.gateway import (
    create_claim_card,
    create_dataset_card,
    create_study_card,
    get_claim_card,
    get_dataset_card,
    get_study_card,
    update_claim_card,
    update_dataset_card,
    update_study_card,
)
from macro_veritas.registry.layout import (
    claim_card_path,
    claim_history_dir,
    dataset_card_path,
    dataset_history_dir,
    study_card_path,
    study_history_dir,
)


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


def _study_card(
    study_id: str = "study-001",
    *,
    status: str = "registered",
    created_from_note: str = "seeded in test",
    screening_note: str | None = None,
) -> dict[str, object]:
    card: dict[str, object] = {
        "study_id": study_id,
        "citation_handle": f"doi:{study_id}",
        "tumor_scope_tags": ["glioma"],
        "therapy_scope_tags": ["immunotherapy"],
        "relevance_scope_tags": ["preclinical"],
        "screening_decision": "include",
        "status": status,
        "created_from_note": created_from_note,
    }
    if screening_note is not None:
        card["screening_note"] = screening_note
    return card


def _dataset_card(
    dataset_id: str = "dataset-001",
    *,
    study_id: str = "study-001",
    status: str = "identified",
    platform_summary: str = "Illumina",
) -> dict[str, object]:
    return {
        "dataset_id": dataset_id,
        "study_id": study_id,
        "source_locator": f"https://example.org/{dataset_id}",
        "availability_status": "open",
        "modality_scope_tags": ["rna-seq"],
        "cohort_summary": "adult cohort",
        "platform_summary": platform_summary,
        "status": status,
        "locator_confidence_note": "confirmed in supplement",
    }


def _claim_card(
    claim_id: str = "claim-001",
    *,
    study_id: str = "study-001",
    dataset_ids: list[str] | None = None,
    status: str = "captured",
    claim_text: str = "Claim text for claim-001",
) -> dict[str, object]:
    card: dict[str, object] = {
        "claim_id": claim_id,
        "study_id": study_id,
        "claim_text": claim_text,
        "claim_type": "association",
        "provenance_pointer": "figure-2",
        "status": status,
        "review_readiness": "needs_scope",
        "created_from_note": "seeded in test",
    }
    if dataset_ids is not None:
        card["dataset_ids"] = dataset_ids
    return card


@pytest.fixture
def configured_registry_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    return data_root.resolve() / "registry"


def test_update_study_creates_snapshot_with_prior_yaml_content(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    canonical_path = study_card_path(configured_registry_root, "study-001")
    prior_content = canonical_path.read_bytes()

    update_study_card(
        _study_card(
            status="closed",
            created_from_note="updated from replacement",
            screening_note="final screening note",
        )
    )

    snapshot_files = sorted(study_history_dir(configured_registry_root, "study-001").glob("*.yaml"))

    assert len(snapshot_files) == 1
    assert snapshot_files[0].read_bytes() == prior_content
    assert canonical_path.read_bytes() != prior_content
    assert get_study_card("study-001")["status"] == "closed"


def test_update_dataset_creates_snapshot_with_prior_yaml_content(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card())

    canonical_path = dataset_card_path(configured_registry_root, "dataset-001")
    prior_content = canonical_path.read_bytes()

    update_dataset_card(_dataset_card(status="bound", platform_summary="10x Genomics"))

    snapshot_files = sorted(
        dataset_history_dir(configured_registry_root, "dataset-001").glob("*.yaml")
    )

    assert len(snapshot_files) == 1
    assert snapshot_files[0].read_bytes() == prior_content
    assert canonical_path.read_bytes() != prior_content
    assert get_dataset_card("dataset-001")["status"] == "bound"


def test_update_claim_creates_snapshot_with_prior_yaml_content(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))
    create_claim_card(_claim_card(dataset_ids=["dataset-001"]))

    canonical_path = claim_card_path(configured_registry_root, "claim-001")
    prior_content = canonical_path.read_bytes()

    update_claim_card(
        _claim_card(
            dataset_ids=["dataset-001", "dataset-002"],
            status="ready",
            claim_text="Updated claim text",
        )
    )

    snapshot_files = sorted(claim_history_dir(configured_registry_root, "claim-001").glob("*.yaml"))

    assert len(snapshot_files) == 1
    assert snapshot_files[0].read_bytes() == prior_content
    assert canonical_path.read_bytes() != prior_content
    assert get_claim_card("claim-001")["status"] == "ready"


def test_repeated_updates_create_multiple_study_snapshots(configured_registry_root: Path) -> None:
    create_study_card(_study_card(status="draft", created_from_note="initial snapshot"))

    canonical_path = study_card_path(configured_registry_root, "study-001")
    original_content = canonical_path.read_bytes()

    update_study_card(_study_card(status="registered", created_from_note="first replacement"))
    first_replacement_content = canonical_path.read_bytes()

    update_study_card(
        _study_card(
            status="closed",
            created_from_note="second replacement",
            screening_note="final pass",
        )
    )

    snapshot_files = sorted(study_history_dir(configured_registry_root, "study-001").glob("*.yaml"))

    assert len(snapshot_files) == 2
    assert snapshot_files[0].read_bytes() == original_content
    assert snapshot_files[1].read_bytes() == first_replacement_content


def test_snapshot_failure_aborts_update_and_preserves_live_study_card(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())

    canonical_path = study_card_path(configured_registry_root, "study-001")
    prior_content = canonical_path.read_bytes()

    def _fail_snapshot(source_path: Path, destination_dir: Path) -> Path:
        raise OSError(
            f"simulated snapshot failure for {source_path.name} -> {destination_dir.name}"
        )

    monkeypatch.setattr(study_runtime, "preserve_pre_update_snapshot", _fail_snapshot)

    with pytest.raises(RegistryError):
        update_study_card(_study_card(status="closed", created_from_note="should not persist"))

    assert canonical_path.read_bytes() == prior_content
    assert not study_history_dir(configured_registry_root, "study-001").exists()

