from __future__ import annotations

from pathlib import Path

import pytest

from macro_veritas.registry.errors import (
    BrokenReferenceError,
    CardAlreadyExistsError,
    CardNotFoundError,
    RegistryError,
    UnsupportedRegistryOperationError,
)
from macro_veritas.registry.gateway import (
    claim_card_exists,
    create_claim_card,
    create_dataset_card,
    create_study_card,
    get_claim_card,
    list_claim_cards,
    plan_create_claim_card,
    plan_update_claim_card,
    update_claim_card,
)
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
        "created_from_note": "seeded in test",
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


def _claim_card(
    claim_id: str = "claim-001",
    *,
    study_id: str = "study-001",
    dataset_ids: list[str] | None = None,
    status: str = "captured",
    claim_summary_handle: str | None = None,
) -> dict[str, object]:
    card: dict[str, object] = {
        "claim_id": claim_id,
        "study_id": study_id,
        "claim_text": f"Claim text for {claim_id}",
        "claim_type": "association",
        "provenance_pointer": "figure-2",
        "status": status,
        "review_readiness": "needs_scope",
        "created_from_note": "seeded in test",
    }
    if dataset_ids is not None:
        card["dataset_ids"] = dataset_ids
    if claim_summary_handle is not None:
        card["claim_summary_handle"] = claim_summary_handle
    return card


@pytest.fixture
def configured_registry_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    return data_root.resolve() / "registry"


def test_create_then_get_claim_card_round_trip(configured_registry_root: Path) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    card = _claim_card(dataset_ids=["dataset-001"], claim_summary_handle="claim-1")

    created = create_claim_card(card)
    loaded = get_claim_card("claim-001")

    assert created == loaded
    assert loaded["dataset_ids"] == ["dataset-001"]
    assert loaded["claim_summary_handle"] == "claim-1"


def test_claim_card_exists_before_and_after_create(configured_registry_root: Path) -> None:
    assert claim_card_exists("claim-001") is False

    create_study_card(_study_card())
    create_claim_card(_claim_card())

    assert claim_card_exists("claim-001") is True


def test_list_claim_cards_returns_created_cards(configured_registry_root: Path) -> None:
    create_study_card(_study_card())
    create_claim_card(_claim_card("claim-002"))
    create_claim_card(_claim_card("claim-001"))

    cards = list_claim_cards()

    assert [card["claim_id"] for card in cards] == ["claim-001", "claim-002"]


def test_create_duplicate_claim_card_raises_domain_error(configured_registry_root: Path) -> None:
    create_study_card(_study_card())
    create_claim_card(_claim_card())

    with pytest.raises(CardAlreadyExistsError):
        create_claim_card(_claim_card())


def test_get_missing_claim_card_raises_domain_error(configured_registry_root: Path) -> None:
    with pytest.raises(CardNotFoundError):
        get_claim_card("claim-001")


def test_plan_create_and_update_claim_card_are_planning_only(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))

    create_plan = plan_create_claim_card(_claim_card(dataset_ids=["dataset-001"]))

    assert create_plan["plan_kind"] == "create"
    assert create_plan["execution_state"] == "planned_only"
    assert claim_card_exists("claim-001") is False

    create_claim_card(_claim_card(dataset_ids=["dataset-001"]))
    update_plan = plan_update_claim_card(
        _claim_card(dataset_ids=["dataset-001"], status="ready")
    )

    assert update_plan["plan_kind"] == "update"
    assert update_plan["execution_state"] == "planned_only"


def test_update_claim_card_writes_replacement_content(configured_registry_root: Path) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))
    create_claim_card(_claim_card(dataset_ids=["dataset-001"]))

    update_claim_card(
        _claim_card(
            dataset_ids=["dataset-001", "dataset-002"],
            status="ready",
            claim_summary_handle="claim-ready",
        )
    )
    loaded = get_claim_card("claim-001")

    assert loaded["status"] == "ready"
    assert loaded["dataset_ids"] == ["dataset-001", "dataset-002"]
    assert loaded["claim_summary_handle"] == "claim-ready"


def test_atomic_write_leaves_only_canonical_claimcard_file(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_claim_card(_claim_card())
    update_claim_card(_claim_card(status="scoped"))

    canonical_path = claim_card_path(configured_registry_root, "claim-001")

    assert canonical_path.is_file()
    assert sorted(path.name for path in canonical_path.parent.iterdir()) == ["claim-001.yaml"]


def test_create_claim_card_with_missing_study_raises_broken_reference(
    configured_registry_root: Path,
) -> None:
    with pytest.raises(BrokenReferenceError):
        create_claim_card(_claim_card())


def test_update_claim_card_with_missing_study_raises_broken_reference(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_claim_card(_claim_card())

    with pytest.raises(BrokenReferenceError):
        update_claim_card(_claim_card(study_id="study-999"))


def test_create_claim_card_with_missing_dataset_raises_broken_reference(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    with pytest.raises(BrokenReferenceError):
        create_claim_card(_claim_card(dataset_ids=["dataset-404"]))


def test_update_claim_card_with_missing_dataset_raises_broken_reference(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_claim_card(_claim_card(dataset_ids=["dataset-001"]))

    with pytest.raises(BrokenReferenceError):
        update_claim_card(_claim_card(dataset_ids=["dataset-001", "dataset-404"]))


def test_malformed_yaml_raises_domain_level_registry_error(
    configured_registry_root: Path,
) -> None:
    canonical_path = claim_card_path(configured_registry_root, "claim-001")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text("claim_id: [\n", encoding="utf-8")

    with pytest.raises(RegistryError):
        get_claim_card("claim-001")


def test_malformed_claimcard_content_raises_domain_level_registry_error(
    configured_registry_root: Path,
) -> None:
    canonical_path = claim_card_path(configured_registry_root, "claim-001")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text(
        "\n".join(
            [
                "claim_id: claim-001",
                "study_id: study-001",
                "claim_text: Claim text for claim-001",
                "claim_type: association",
                "provenance_pointer: figure-2",
                "status: captured",
                "review_readiness: needs_scope",
                "created_from_note: seeded in test",
                "dataset_ids: dataset-001",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RegistryError):
        get_claim_card("claim-001")


def test_dataset_ids_absent_is_allowed(configured_registry_root: Path) -> None:
    create_study_card(_study_card())

    created = create_claim_card(_claim_card())

    assert "dataset_ids" not in created
    assert "dataset_ids" not in get_claim_card("claim-001")


def test_dataset_ids_valid_list_is_preserved_round_trip(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))

    create_claim_card(_claim_card(dataset_ids=["dataset-001", "dataset-002"]))
    loaded = get_claim_card("claim-001")

    assert loaded["dataset_ids"] == ["dataset-001", "dataset-002"]


def test_unsafe_claim_lookup_id_raises_unsupported_registry_error(
    configured_registry_root: Path,
) -> None:
    with pytest.raises(UnsupportedRegistryOperationError):
        get_claim_card("../claim-001")


def test_claimcard_runtime_module_imports() -> None:
    from macro_veritas.registry import claim_runtime

    assert claim_runtime.__name__ == "macro_veritas.registry.claim_runtime"
