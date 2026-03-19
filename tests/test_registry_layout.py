from __future__ import annotations

from pathlib import Path

from macro_veritas.config import load_project_config
from macro_veritas.registry.layout import (
    claim_card_relative_path,
    dataset_card_relative_path,
    describe_first_slice_layout,
    study_card_path,
    study_cards_dir,
    study_card_relative_path,
)
from macro_veritas.registry.specs import (
    describe_cross_reference_strategy,
    describe_registry_topology,
    describe_state_location_strategy,
    list_registry_roots,
)
from macro_veritas.shared.naming import (
    claim_card_filename,
    dataset_card_filename,
    registry_subdir_names,
    study_card_filename,
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


def test_first_slice_registry_naming_helpers() -> None:
    assert registry_subdir_names() == ("studies", "datasets", "claims")
    assert study_card_filename("study-001") == "study-001.yaml"
    assert dataset_card_filename("dataset-001") == "dataset-001.yaml"
    assert claim_card_filename("claim-001") == "claim-001.yaml"


def test_first_slice_registry_relative_paths() -> None:
    assert study_card_relative_path("study-001") == "studies/study-001.yaml"
    assert dataset_card_relative_path("dataset-001") == "datasets/dataset-001.yaml"
    assert claim_card_relative_path("claim-001") == "claims/claim-001.yaml"


def test_first_slice_layout_descriptors_match_frozen_mvp_choices() -> None:
    topology = describe_registry_topology()
    state_strategy = describe_state_location_strategy()
    cross_refs = describe_cross_reference_strategy()
    layout = describe_first_slice_layout()

    assert topology["primary_topology"] == "entity-segregated-roots"
    assert topology["one_card_per_file"] is True
    assert list_registry_roots() == ("studies", "datasets", "claims")

    assert state_strategy["strategy"] == "static-file-location + internal status field update"
    assert state_strategy["physical_move_on_status_change"] == "no"

    assert cross_refs["mode"] == "direct-id-to-canonical-path"
    assert cross_refs["DatasetCard.study_id"] == "studies/<study_id>.yaml"
    assert cross_refs["ClaimCard.study_id"] == "studies/<study_id>.yaml"
    assert cross_refs["ClaimCard.dataset_ids"] == (
        "datasets/<dataset_id>.yaml for each listed dataset_id"
    )

    assert layout["StudyCard"] == {
        "root_subdir": "studies",
        "filename_pattern": "<study_id>.yaml",
        "one_card_per_file": True,
        "format_label": "yaml",
    }
    assert layout["DatasetCard"]["root_subdir"] == "datasets"
    assert layout["ClaimCard"]["root_subdir"] == "claims"


def test_project_config_resolves_first_slice_registry_dirs(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    config = load_project_config(config_path)

    assert config.registry_subdir_path("studies") == data_root.resolve() / "registry" / "studies"
    assert config.first_slice_registry_dirs() == {
        "studies": data_root.resolve() / "registry" / "studies",
        "datasets": data_root.resolve() / "registry" / "datasets",
        "claims": data_root.resolve() / "registry" / "claims",
    }
    assert study_cards_dir(config.registry_dir) == data_root.resolve() / "registry" / "studies"
    assert study_card_path(config.registry_dir, "study-001") == (
        data_root.resolve() / "registry" / "studies" / "study-001.yaml"
    )
