from __future__ import annotations

from pathlib import Path

import pytest

from macro_veritas.registry.errors import (
    CardAlreadyExistsError,
    CardNotFoundError,
    InvalidStateTransitionError,
    RegistryError,
)
from macro_veritas.registry.gateway import (
    create_study_card,
    get_study_card,
    list_study_cards,
    plan_create_study_card,
    plan_update_study_card,
    study_card_exists,
    update_study_card,
)
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


def _study_card(
    study_id: str = "study-001",
    *,
    status: str = "draft",
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
        "created_from_note": "seeded in test",
    }
    if screening_note is not None:
        card["screening_note"] = screening_note
    return card


@pytest.fixture
def configured_registry_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    return data_root.resolve() / "registry"


def test_create_then_get_study_card_round_trip(configured_registry_root: Path) -> None:
    card = _study_card()

    created = create_study_card(card)
    loaded = get_study_card("study-001")

    assert created == loaded
    assert loaded["study_id"] == "study-001"


def test_study_card_exists_before_and_after_create(configured_registry_root: Path) -> None:
    assert study_card_exists("study-001") is False

    create_study_card(_study_card())

    assert study_card_exists("study-001") is True


def test_list_study_cards_returns_created_cards(configured_registry_root: Path) -> None:
    create_study_card(_study_card("study-002"))
    create_study_card(_study_card("study-001"))

    cards = list_study_cards()

    assert [card["study_id"] for card in cards] == ["study-001", "study-002"]


def test_create_duplicate_study_card_raises_domain_error(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    with pytest.raises(CardAlreadyExistsError):
        create_study_card(_study_card())


def test_get_missing_study_card_raises_domain_error(configured_registry_root: Path) -> None:
    with pytest.raises(CardNotFoundError):
        get_study_card("study-001")


def test_plan_create_and_update_study_card_are_planning_only(
    configured_registry_root: Path,
) -> None:
    create_plan = plan_create_study_card(_study_card())

    assert create_plan["plan_kind"] == "create"
    assert create_plan["execution_state"] == "planned_only"

    create_study_card(_study_card())
    update_plan = plan_update_study_card(_study_card(status="registered"))

    assert update_plan["plan_kind"] == "update"
    assert update_plan["execution_state"] == "planned_only"


def test_update_study_card_writes_replacement_content(configured_registry_root: Path) -> None:
    create_study_card(_study_card())

    update_study_card(_study_card(status="registered", screening_note="promoted"))
    loaded = get_study_card("study-001")

    assert loaded["status"] == "registered"
    assert loaded["screening_note"] == "promoted"


def test_atomic_write_leaves_only_canonical_studycard_file(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    update_study_card(_study_card(status="registered"))

    canonical_path = study_card_path(configured_registry_root, "study-001")

    assert canonical_path.is_file()
    assert sorted(path.name for path in canonical_path.parent.iterdir()) == ["study-001.yaml"]


def test_malformed_yaml_raises_domain_level_registry_error(
    configured_registry_root: Path,
) -> None:
    canonical_path = study_card_path(configured_registry_root, "study-001")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text("study_id: [\n", encoding="utf-8")

    with pytest.raises(RegistryError):
        get_study_card("study-001")


def test_malformed_studycard_content_raises_domain_level_registry_error(
    configured_registry_root: Path,
) -> None:
    canonical_path = study_card_path(configured_registry_root, "study-001")
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text(
        "\n".join(
            [
                "study_id: study-001",
                "citation_handle: doi:study-001",
                "tumor_scope_tags:",
                "  - glioma",
                "therapy_scope_tags:",
                "  - immunotherapy",
                "relevance_scope_tags:",
                "  - preclinical",
                "screening_decision: include",
                "status: invalid-status",
                "created_from_note: seeded in test",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(RegistryError):
        get_study_card("study-001")


def test_update_rejects_reopening_closed_studycard(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card(status="closed"))

    with pytest.raises(InvalidStateTransitionError):
        update_study_card(_study_card(status="registered"))


def test_studycard_runtime_module_imports() -> None:
    from macro_veritas.registry import study_runtime

    assert study_runtime.__name__ == "macro_veritas.registry.study_runtime"
