from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

from macro_veritas.cli import main
from macro_veritas.commands import ingest
from macro_veritas.registry.errors import (
    RegistryError,
    UnsupportedRegistryOperationError,
    UpdateLockError,
)
from macro_veritas.registry.gateway import create_study_card
from macro_veritas.registry.layout import dataset_card_path, dataset_lock_path, study_lock_path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"


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


def _subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_ROOT) if not existing else f"{SRC_ROOT}{os.pathsep}{existing}"
    return env


def _study_ingest_command(config_path: Path, study_id: str = "study-001") -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "ingest",
        "study",
        "--study-id",
        study_id,
        "--citation-handle",
        f"doi:{study_id}",
        "--tumor-type",
        "glioma",
        "--therapy-scope",
        "immunotherapy",
        "--relevance-scope",
        "preclinical",
        "--screening-decision",
        "include",
        "--status",
        "registered",
        "--created-from",
        "seeded for dataset ingest test",
    ]


def _dataset_ingest_command(
    config_path: Path,
    *,
    dataset_id: str = "dataset-001",
    study_id: str = "study-001",
    status: str = "identified",
    availability_status: str = "open",
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "ingest",
        "dataset",
        "--dataset-id",
        dataset_id,
        "--study-id",
        study_id,
        "--status",
        status,
        "--modality-scope",
        "rna-seq",
        "--platform-summary",
        "Illumina",
        "--cohort-summary",
        "adult cohort",
        "--locator-confidence-note",
        "confirmed in supplement",
        "--source-locator",
        f"https://example.org/{dataset_id}",
        "--availability-status",
        availability_status,
        "--accession-id",
        "GSE12345",
        "--availability-note",
        "open after registration",
        "--artifact-locator",
        "raw/datasets/dataset-001.h5ad",
    ]


def _study_card(study_id: str = "study-001") -> dict[str, object]:
    return {
        "study_id": study_id,
        "citation_handle": f"doi:{study_id}",
        "tumor_scope_tags": ["glioma"],
        "therapy_scope_tags": ["immunotherapy"],
        "relevance_scope_tags": ["preclinical"],
        "screening_decision": "include",
        "status": "registered",
        "created_from_note": "seeded for dataset ingest test",
    }


def test_public_ingest_dataset_cli_succeeds_and_writes_canonical_datasetcard(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    canonical_path = dataset_card_path(data_root.resolve() / "registry", "dataset-001")
    parent_lock = study_lock_path(data_root.resolve() / "registry", "study-001")
    target_lock = dataset_lock_path(data_root.resolve() / "registry", "dataset-001")

    assert study_result.returncode == 0, study_result.stderr
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ingest dataset: created DatasetCard dataset-001"
    assert parent_lock.is_file()
    assert target_lock.is_file()
    assert canonical_path.read_text(encoding="utf-8") == (
        "\n".join(
            [
                "dataset_id: dataset-001",
                "study_id: study-001",
                "source_locator: https://example.org/dataset-001",
                "availability_status: open",
                "modality_scope_tags:",
                "- rna-seq",
                "cohort_summary: adult cohort",
                "platform_summary: Illumina",
                "status: identified",
                "locator_confidence_note: confirmed in supplement",
                "accession_id: GSE12345",
                "artifact_locator: raw/datasets/dataset-001.h5ad",
                "availability_note: open after registration",
                "",
            ]
        )
    )


def test_public_ingest_dataset_cli_duplicate_create_returns_user_facing_failure(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    first_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 1
    assert "ingest dataset failed [duplicate_target]" in second_result.stderr
    assert "canonical DatasetCard already exists" in second_result.stderr


def test_public_ingest_dataset_cli_missing_parent_returns_clean_failure(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest dataset failed [missing_reference]" in result.stderr
    assert "parent StudyCard 'study-001'" in result.stderr


def test_public_ingest_dataset_cli_invalid_argument_set_exits_non_zero(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    command = _dataset_ingest_command(config_path, availability_status="invalid-status")

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode != 0
    assert "invalid choice" in result.stderr
    assert "--availability-status" in result.stderr


def test_public_ingest_dataset_cli_translates_registry_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    def _raise_registry_failure(card: object) -> object:
        raise RegistryError("simulated registry gateway failure")

    monkeypatch.setattr(ingest, "create_dataset_card", _raise_registry_failure)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "dataset",
            "--dataset-id",
            "dataset-001",
            "--study-id",
            "study-001",
            "--status",
            "identified",
            "--modality-scope",
            "rna-seq",
            "--platform-summary",
            "Illumina",
            "--cohort-summary",
            "adult cohort",
            "--locator-confidence-note",
            "confirmed in supplement",
            "--source-locator",
            "https://example.org/dataset-001",
            "--availability-status",
            "open",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest dataset failed [registry_failure]" in captured.err
    assert "registry gateway boundary" in captured.err


def test_public_ingest_dataset_cli_surfaces_lock_failure_clearly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    def _raise_lock_failure(card: object) -> object:
        raise UpdateLockError(
            "DatasetCard ingest could not acquire the exclusive ingest lock for 'dataset-001'."
        )

    monkeypatch.setattr(ingest, "create_dataset_card", _raise_lock_failure)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "dataset",
            "--dataset-id",
            "dataset-001",
            "--study-id",
            "study-001",
            "--status",
            "identified",
            "--modality-scope",
            "rna-seq",
            "--platform-summary",
            "Illumina",
            "--cohort-summary",
            "adult cohort",
            "--locator-confidence-note",
            "confirmed in supplement",
            "--source-locator",
            "https://example.org/dataset-001",
            "--availability-status",
            "open",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest dataset failed [registry_failure]" in captured.err
    assert "exclusive ingest lock" in captured.err


def test_public_ingest_dataset_cli_translates_unsupported_operation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    def _raise_unsupported(card: object) -> object:
        raise UnsupportedRegistryOperationError("simulated unsupported registry operation")

    monkeypatch.setattr(ingest, "plan_create_dataset_card", _raise_unsupported)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "dataset",
            "--dataset-id",
            "dataset-001",
            "--study-id",
            "study-001",
            "--status",
            "identified",
            "--modality-scope",
            "rna-seq",
            "--platform-summary",
            "Illumina",
            "--cohort-summary",
            "adult cohort",
            "--locator-confidence-note",
            "confirmed in supplement",
            "--source-locator",
            "https://example.org/dataset-001",
            "--availability-status",
            "open",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest dataset failed [unsupported_operation]" in captured.err
    assert "unsupported registry operation or identifier" in captured.err
