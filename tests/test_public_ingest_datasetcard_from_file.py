from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from macro_veritas.cli import main
from macro_veritas.commands import ingest
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


def _study_card(study_id: str = "study-001") -> dict[str, object]:
    return {
        "study_id": study_id,
        "citation_handle": f"doi:{study_id}",
        "tumor_scope_tags": ["glioma"],
        "therapy_scope_tags": ["immunotherapy"],
        "relevance_scope_tags": ["preclinical"],
        "screening_decision": "include",
        "status": "registered",
        "created_from_note": "seeded for dataset from-file test",
    }


def _dataset_ingest_data(
    dataset_id: str = "dataset-001",
    *,
    study_id: str = "study-001",
) -> dict[str, object]:
    return {
        "dataset_id": dataset_id,
        "study_id": study_id,
        "status": "identified",
        "modality_scope": ["rna-seq"],
        "platform_summary": "Illumina",
        "cohort_summary": "adult cohort",
        "locator_confidence_note": "confirmed in supplement",
        "source_locator": f"https://example.org/{dataset_id}",
        "availability_status": "open",
        "accession_id": "GSE12345",
        "availability_note": "open after registration",
        "artifact_locator": "raw/datasets/dataset-001.h5ad",
    }


def _write_dataset_ingest_file(path: Path, data: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _dataset_from_file_command(
    config_path: Path,
    ingest_path: Path,
    extra_args: list[str] | None = None,
) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "ingest",
        "dataset",
        "--from-file",
        str(ingest_path),
    ]
    if extra_args is not None:
        command.extend(extra_args)
    return command


def test_public_ingest_dataset_from_file_succeeds_and_writes_canonical_datasetcard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "dataset-input.yaml"
    _write_config(config_path, data_root)
    _write_dataset_ingest_file(ingest_path, _dataset_ingest_data())
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    result = subprocess.run(
        _dataset_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    canonical_path = dataset_card_path(data_root.resolve() / "registry", "dataset-001")
    parent_lock = study_lock_path(data_root.resolve() / "registry", "study-001")
    target_lock = dataset_lock_path(data_root.resolve() / "registry", "dataset-001")

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


def test_public_ingest_dataset_from_file_missing_file_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        _dataset_from_file_command(config_path, tmp_path / "missing-dataset.yaml"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest dataset failed [invalid_payload]" in result.stderr
    assert "DatasetCard ingest file was not found" in result.stderr


def test_public_ingest_dataset_from_file_malformed_yaml_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "dataset-input.yaml"
    _write_config(config_path, data_root)
    ingest_path.write_text("dataset_id: [dataset-001\n", encoding="utf-8")

    result = subprocess.run(
        _dataset_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest dataset failed [invalid_payload]" in result.stderr
    assert "DatasetCard ingest file is not valid YAML" in result.stderr


def test_public_ingest_dataset_from_file_non_mapping_root_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "dataset-input.yaml"
    _write_config(config_path, data_root)
    ingest_path.write_text(yaml.safe_dump(["dataset-001"], sort_keys=False), encoding="utf-8")

    result = subprocess.run(
        _dataset_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest dataset failed [invalid_payload]" in result.stderr
    assert "DatasetCard ingest file must decode to one mapping" in result.stderr


def test_public_ingest_dataset_from_file_missing_required_keys_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "dataset-input.yaml"
    _write_config(config_path, data_root)
    data = _dataset_ingest_data()
    data.pop("modality_scope")
    _write_dataset_ingest_file(ingest_path, data)

    result = subprocess.run(
        _dataset_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest dataset failed [invalid_payload]" in result.stderr
    assert "DatasetCard ingest file is missing required keys" in result.stderr
    assert "modality_scope" in result.stderr


def test_public_ingest_dataset_from_file_missing_parent_study_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "dataset-input.yaml"
    _write_config(config_path, data_root)
    _write_dataset_ingest_file(ingest_path, _dataset_ingest_data())

    result = subprocess.run(
        _dataset_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest dataset failed [missing_reference]" in result.stderr
    assert "parent StudyCard 'study-001'" in result.stderr


def test_public_ingest_dataset_from_file_duplicate_create_fails_cleanly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "dataset-input.yaml"
    _write_config(config_path, data_root)
    _write_dataset_ingest_file(ingest_path, _dataset_ingest_data())
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    first_result = subprocess.run(
        _dataset_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _dataset_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 1
    assert "ingest dataset failed [duplicate_target]" in second_result.stderr
    assert "canonical DatasetCard already exists" in second_result.stderr


def test_public_ingest_dataset_from_file_mixed_with_field_flags_fails_before_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "dataset-input.yaml"
    _write_config(config_path, data_root)
    _write_dataset_ingest_file(ingest_path, _dataset_ingest_data())

    def _unexpected(*args: object, **kwargs: object) -> object:
        raise AssertionError("mixed-input dataset ingest should fail before execution")

    monkeypatch.setattr(ingest, "execute_datasetcard_ingest_from_file", _unexpected)
    monkeypatch.setattr(ingest, "execute_datasetcard_ingest_input", _unexpected)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "dataset",
            "--from-file",
            str(ingest_path),
            "--dataset-id",
            "dataset-override",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest dataset failed [invalid_payload]" in captured.err
    assert "DatasetCard --from-file cannot be combined with field flags" in captured.err
    assert "--dataset-id" in captured.err
