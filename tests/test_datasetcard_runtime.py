from __future__ import annotations

from pathlib import Path

import pytest

from macro_veritas.registry.errors import (
    BrokenReferenceError,
    CardAlreadyExistsError,
    CardNotFoundError,
    RegistryError,
)
from macro_veritas.registry.gateway import (
    create_dataset_card,
    create_study_card,
    dataset_card_exists,
    get_dataset_card,
    list_dataset_cards,
    plan_create_dataset_card,
    plan_update_dataset_card,
    update_dataset_card,
)
from macro_veritas.registry.layout import dataset_card_path


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


def _dataset_card(
    dataset_id: str = "dataset-001",
    *,
    study_id: str = "study-001",
    status: str = "identified",
    availability_status: str = "open",
    availability_note: str | None = None,
) -> dict[str, object]:
    card: dict[str, object] = {
        "dataset_id": dataset_id,
        "study_id": study_id,
        "source_locator": f"https://example.org/{dataset_id}",
        "availability_status": availability_status,
        "modality_scope_tags": ["rna-seq"],
        "cohort_summary": "adult cohort",
        "platform_summary": "Illumina",
        "status": status,
        "locator_confidence_note": "confirmed in supplement",
    }
    if availability_note is not None:
        card["availability_note"] = availability_note
    return card


@pytest.fixture
def configured_registry_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    return data_root.resolve() / "registry"


def test_create_then_get_dataset_card_round_trip(configured_registry_root: Path) -> None:
    create_study_card(_study_card())
    card = _dataset_card()

    created = create_dataset_card(card)
    loaded = get_dataset_card("dataset-001")

    assert created == loaded
    assert loaded["dataset_id"] == "dataset-001"


def test_dataset_card_exists_before_and_after_create(configured_registry_root: Path) -> None:
    assert dataset_card_exists("dataset-001") is False

    create_study_card(_study_card())
    create_dataset_card(_dataset_card())

    assert dataset_card_exists("dataset-001") is True


def test_list_dataset_cards_returns_created_cards(configured_registry_root: Path) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-002"))
    create_dataset_card(_dataset_card("dataset-001"))

    cards = list_dataset_cards()

    assert [card["dataset_id"] for card in cards] == ["dataset-001", "dataset-002"]


def test_create_duplicate_dataset_card_raises_domain_error(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card())

    with pytest.raises(CardAlreadyExistsError):
        create_dataset_card(_dataset_card())


def test_get_missing_dataset_card_raises_domain_error(configured_registry_root: Path) -> None:
    with pytest.raises(CardNotFoundError):
        get_dataset_card("dataset-001")


def test_plan_create_and_update_dataset_card_are_planning_only(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_plan = plan_create_dataset_card(_dataset_card())

    assert create_plan["plan_kind"] == "create"
    assert create_plan["execution_state"] == "planned_only"

    create_dataset_card(_dataset_card())
    update_plan = plan_update_dataset_card(_dataset_card(status="registered"))

    assert update_plan["plan_kind"] == "update"
    assert update_plan["execution_state"] == "planned_only"


def test_update_dataset_card_writes_replacement_content(configured_registry_root: Path) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card())

    update_dataset_card(
        _dataset_card(
            status="bound",
            availability_note="bound in processed workspace",
        )
    )
    loaded = get_dataset_card("dataset-001")

    assert loaded["status"] == "bound"
    assert loaded["availability_note"] == "bound in processed workspace"


def test_atomic_write_leaves_only_canonical_datasetcard_file(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card())
    update_dataset_card(_dataset_card(status="registered"))

    canonical_path = dataset_card_path(configured_registry_root, "dataset-001")

    assert canonical_path.is_file()
    assert sorted(path.name for path in canonical_path.parent.iterdir()) == ["dataset-001.yaml"]


def test_create_dataset_card_with_missing_study_raises_broken_reference(
    configured_registry_root: Path,
) -> None:
    with pytest.raises(BrokenReferenceError):
        create_dataset_card(_dataset_card())


def test_update_dataset_card_with_missing_study_raises_broken_reference(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card())

    with pytest.raises(BrokenReferenceError):
        update_dataset_card(_dataset_card(study_id="study-999"))


def test_malformed_yaml_raises_domain_level_registry_error(
    configured_registry_root: Path,
) -> None:
    canonical_path = dataset_card_path(configured_registry_root, "dataset-001")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text("dataset_id: [\n", encoding="utf-8")

    with pytest.raises(RegistryError):
        get_dataset_card("dataset-001")


def test_malformed_datasetcard_content_raises_domain_level_registry_error(
    configured_registry_root: Path,
) -> None:
    canonical_path = dataset_card_path(configured_registry_root, "dataset-001")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text(
        "\n".join(
            [
                "dataset_id: dataset-001",
                "study_id: study-001",
                "source_locator: https://example.org/dataset-001",
                "availability_status: open",
                "modality_scope_tags:",
                "  - rna-seq",
                "cohort_summary: adult cohort",
                "platform_summary: Illumina",
                "status: invalid-status",
                "locator_confidence_note: confirmed in supplement",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RegistryError):
        get_dataset_card("dataset-001")


def test_datasetcard_runtime_module_imports() -> None:
    from macro_veritas.registry import dataset_runtime

    assert dataset_runtime.__name__ == "macro_veritas.registry.dataset_runtime"
