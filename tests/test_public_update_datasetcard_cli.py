from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

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
        "seeded for public update test",
    ]


def _dataset_ingest_command(
    config_path: Path,
    *,
    dataset_id: str = "dataset-001",
    study_id: str = "study-001",
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
        f"https://example.org/{dataset_id}",
        "--availability-status",
        "open",
        "--accession-id",
        "GSE12345",
        "--availability-note",
        "open after registration",
        "--artifact-locator",
        "raw/datasets/dataset-001.h5ad",
    ]


def _show_dataset_command(config_path: Path, dataset_id: str = "dataset-001") -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "show",
        "dataset",
        "--dataset-id",
        dataset_id,
    ]


def _update_dataset_command(
    config_path: Path,
    update_path: Path,
    *,
    dataset_id: str = "dataset-001",
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "update",
        "dataset",
        "--dataset-id",
        dataset_id,
        "--from-file",
        str(update_path),
    ]


def _dataset_card(
    dataset_id: str = "dataset-001",
    *,
    study_id: str = "study-001",
    status: str = "identified",
    platform_summary: str = "Illumina",
    cohort_summary: str = "adult cohort",
    source_locator: str | None = None,
    availability_note: str = "open after registration",
    artifact_locator: str = "raw/datasets/dataset-001.h5ad",
) -> dict[str, object]:
    return {
        "dataset_id": dataset_id,
        "study_id": study_id,
        "source_locator": source_locator or f"https://example.org/{dataset_id}",
        "availability_status": "open",
        "modality_scope_tags": ["rna-seq"],
        "cohort_summary": cohort_summary,
        "platform_summary": platform_summary,
        "status": status,
        "locator_confidence_note": "confirmed in supplement",
        "accession_id": "GSE12345",
        "artifact_locator": artifact_locator,
        "availability_note": availability_note,
    }


def _write_update_file(path: Path, payload: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_public_update_dataset_from_file_succeeds_and_show_reflects_replacement(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "dataset-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(
        update_path,
        _dataset_card(
            status="bound",
            platform_summary="10x Genomics",
            cohort_summary="expanded validation cohort",
            source_locator="https://example.org/dataset-001-v2",
            availability_note="processed binding complete",
            artifact_locator="processed/datasets/dataset-001.h5ad",
        ),
    )

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_dataset_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    show_result = subprocess.run(
        _show_dataset_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    payload = json.loads(show_result.stdout)

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert update_result.returncode == 0, update_result.stderr
    assert update_result.stdout.strip() == "update dataset: updated DatasetCard dataset-001"
    assert update_result.stderr == ""
    assert show_result.returncode == 0, show_result.stderr
    assert payload["status"] == "bound"
    assert payload["platform_summary"] == "10x Genomics"
    assert payload["cohort_summary"] == "expanded validation cohort"
    assert payload["source_locator"] == "https://example.org/dataset-001-v2"
    assert payload["availability_note"] == "processed binding complete"
    assert payload["artifact_locator"] == "processed/datasets/dataset-001.h5ad"


def test_public_update_dataset_missing_target_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "dataset-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _dataset_card())

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_dataset_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update dataset failed [missing_reference]: requested DatasetCard 'dataset-001' was not found."
    )


def test_public_update_dataset_missing_parent_study_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "dataset-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _dataset_card(study_id="study-999"))

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_dataset_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update dataset failed [missing_reference]: DatasetCard update requires the parent StudyCard 'study-999' to exist before replace."
    )


def test_public_update_dataset_cli_and_file_target_mismatch_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "dataset-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _dataset_card(dataset_id="dataset-002"))

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_dataset_command(config_path, update_path, dataset_id="dataset-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update dataset failed [invalid_payload]: DatasetCard update input is invalid: CLI --dataset-id must match file dataset_id: dataset-001 != dataset-002."
    )


def test_public_update_dataset_missing_file_fails_cleanly(tmp_path: Path) -> None:
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
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_dataset_command(config_path, tmp_path / "missing-update.yaml"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update dataset failed [invalid_payload]" in update_result.stderr
    assert "DatasetCard update file was not found" in update_result.stderr


def test_public_update_dataset_malformed_yaml_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "dataset-update.yaml"
    _write_config(config_path, data_root)
    update_path.write_text("dataset_id: [dataset-001\n", encoding="utf-8")

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_dataset_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update dataset failed [invalid_payload]" in update_result.stderr
    assert "DatasetCard update file is not valid YAML" in update_result.stderr


def test_public_update_dataset_non_mapping_yaml_root_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "dataset-update.yaml"
    _write_config(config_path, data_root)
    update_path.write_text(yaml.safe_dump(["dataset-001"], sort_keys=False), encoding="utf-8")

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_dataset_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update dataset failed [invalid_payload]" in update_result.stderr
    assert "DatasetCard update file must decode to one mapping" in update_result.stderr


def test_public_update_dataset_missing_required_keys_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "dataset-update.yaml"
    _write_config(config_path, data_root)
    payload = _dataset_card()
    payload.pop("modality_scope_tags")
    _write_update_file(update_path, payload)

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_dataset_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update dataset failed [invalid_payload]" in update_result.stderr
    assert "DatasetCard payload is missing required fields: modality_scope_tags" in update_result.stderr
