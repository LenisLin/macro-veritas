from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from macro_veritas.cli import main
from macro_veritas.commands import show
from macro_veritas.registry.errors import RegistryError

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
        "seeded for public show test",
        "--screening-note",
        "ready for public read",
        "--source-artifact",
        "raw/studies/study-001.pdf",
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


def _claim_ingest_command(
    config_path: Path,
    *,
    claim_id: str = "claim-001",
    study_id: str = "study-001",
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "ingest",
        "claim",
        "--claim-id",
        claim_id,
        "--study-id",
        study_id,
        "--claim-text",
        f"Claim text for {claim_id}",
        "--claim-type",
        "association",
        "--provenance-pointer",
        "figure-2",
        "--status",
        "captured",
        "--review-readiness",
        "needs_scope",
        "--created-from",
        "seeded for public show test",
        "--claim-summary-handle",
        "claim-1",
    ]


def _show_study_command(config_path: Path, study_id: str = "study-001") -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "show",
        "study",
        "--study-id",
        study_id,
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


def _show_claim_command(config_path: Path, claim_id: str = "claim-001") -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "show",
        "claim",
        "--claim-id",
        claim_id,
    ]


def test_public_show_study_cli_returns_json_card_by_id(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    ingest_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    show_result = subprocess.run(
        _show_study_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    expected = {
        "citation_handle": "doi:study-001",
        "created_from_note": "seeded for public show test",
        "relevance_scope_tags": ["preclinical"],
        "screening_decision": "include",
        "screening_note": "ready for public read",
        "source_artifact_locator": "raw/studies/study-001.pdf",
        "status": "registered",
        "study_id": "study-001",
        "therapy_scope_tags": ["immunotherapy"],
        "tumor_scope_tags": ["glioma"],
    }

    assert ingest_result.returncode == 0, ingest_result.stderr
    assert show_result.returncode == 0, show_result.stderr
    assert show_result.stdout == json.dumps(expected, indent=2, sort_keys=True) + "\n"
    assert show_result.stderr == ""


def test_public_show_dataset_cli_returns_json_card_by_id(tmp_path: Path) -> None:
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
    show_result = subprocess.run(
        _show_dataset_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    expected = {
        "accession_id": "GSE12345",
        "artifact_locator": "raw/datasets/dataset-001.h5ad",
        "availability_note": "open after registration",
        "availability_status": "open",
        "cohort_summary": "adult cohort",
        "dataset_id": "dataset-001",
        "locator_confidence_note": "confirmed in supplement",
        "modality_scope_tags": ["rna-seq"],
        "platform_summary": "Illumina",
        "source_locator": "https://example.org/dataset-001",
        "status": "identified",
        "study_id": "study-001",
    }

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert show_result.returncode == 0, show_result.stderr
    assert show_result.stdout == json.dumps(expected, indent=2, sort_keys=True) + "\n"
    assert show_result.stderr == ""


def test_public_show_claim_cli_returns_json_card_by_id(tmp_path: Path) -> None:
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
    claim_result = subprocess.run(
        _claim_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    show_result = subprocess.run(
        _show_claim_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    expected = {
        "claim_id": "claim-001",
        "claim_summary_handle": "claim-1",
        "claim_text": "Claim text for claim-001",
        "claim_type": "association",
        "created_from_note": "seeded for public show test",
        "provenance_pointer": "figure-2",
        "review_readiness": "needs_scope",
        "status": "captured",
        "study_id": "study-001",
    }

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert show_result.returncode == 0, show_result.stderr
    assert show_result.stdout == json.dumps(expected, indent=2, sort_keys=True) + "\n"
    assert show_result.stderr == ""


@pytest.mark.parametrize(
    ("command", "expected_prefix"),
    [
        ("study", "show study failed [missing_reference]: requested StudyCard 'study-404' was not found."),
        ("dataset", "show dataset failed [missing_reference]: requested DatasetCard 'dataset-404' was not found."),
        ("claim", "show claim failed [missing_reference]: requested ClaimCard 'claim-404' was not found."),
    ],
)
def test_public_show_cli_missing_cards_fail_cleanly(
    tmp_path: Path,
    command: str,
    expected_prefix: str,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    commands = {
        "study": _show_study_command(config_path, "study-404"),
        "dataset": _show_dataset_command(config_path, "dataset-404"),
        "claim": _show_claim_command(config_path, "claim-404"),
    }
    result = subprocess.run(
        commands[command],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.strip() == expected_prefix


def test_public_show_study_cli_translates_unsafe_identifier(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "show",
            "study",
            "--study-id",
            "../study-001",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "show study failed [unsupported_operation]" in captured.err
    assert "unsafe or unsupported canonical StudyCard identifier" in captured.err


def test_public_show_dataset_cli_translates_registry_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    def _raise_registry_failure(dataset_id: str) -> object:
        raise RegistryError(f"simulated registry gateway failure for {dataset_id}")

    monkeypatch.setattr(show, "get_dataset_card", _raise_registry_failure)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "show",
            "dataset",
            "--dataset-id",
            "dataset-001",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "show dataset failed [registry_failure]" in captured.err
    assert "could not read the requested DatasetCard through the registry gateway" in captured.err
