from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from macro_veritas.cli import main
from macro_veritas.commands import listing
from macro_veritas.registry.errors import RegistryError, UnsupportedRegistryOperationError

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


def _study_ingest_command(config_path: Path, study_id: str) -> list[str]:
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
        f"seeded for {study_id}",
    ]


def _dataset_ingest_command(config_path: Path, dataset_id: str, study_id: str = "study-001") -> list[str]:
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
    ]


def _claim_ingest_command(config_path: Path, claim_id: str, study_id: str = "study-001") -> list[str]:
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
        f"seeded for {claim_id}",
        "--claim-summary-handle",
        f"summary-{claim_id}",
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


def _list_command(config_path: Path, collection: str) -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "list",
        collection,
    ]


def test_public_list_studies_cli_returns_compact_sorted_json_summaries(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    first_result = subprocess.run(
        _study_ingest_command(config_path, "study-002"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _study_ingest_command(config_path, "study-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    list_result = subprocess.run(
        _list_command(config_path, "studies"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    payload = json.loads(list_result.stdout)

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    assert list_result.returncode == 0, list_result.stderr
    assert list_result.stderr == ""
    assert payload == [
        {
            "citation_handle": "doi:study-001",
            "status": "registered",
            "study_id": "study-001",
        },
        {
            "citation_handle": "doi:study-002",
            "status": "registered",
            "study_id": "study-002",
        },
    ]
    assert all(set(item) == {"study_id", "status", "citation_handle"} for item in payload)
    assert "created_from_note" not in list_result.stdout
    assert "tumor_scope_tags" not in list_result.stdout


def test_public_list_datasets_cli_returns_compact_sorted_json_summaries(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(
        _study_ingest_command(config_path, "study-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    first_result = subprocess.run(
        _dataset_ingest_command(config_path, "dataset-002"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _dataset_ingest_command(config_path, "dataset-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    list_result = subprocess.run(
        _list_command(config_path, "datasets"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    payload = json.loads(list_result.stdout)

    assert study_result.returncode == 0, study_result.stderr
    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    assert list_result.returncode == 0, list_result.stderr
    assert list_result.stderr == ""
    assert payload == [
        {
            "dataset_id": "dataset-001",
            "status": "identified",
            "study_id": "study-001",
        },
        {
            "dataset_id": "dataset-002",
            "status": "identified",
            "study_id": "study-001",
        },
    ]
    assert all(set(item) == {"dataset_id", "study_id", "status"} for item in payload)
    assert "source_locator" not in list_result.stdout
    assert "modality_scope_tags" not in list_result.stdout


def test_public_list_claims_cli_returns_compact_sorted_json_summaries(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(
        _study_ingest_command(config_path, "study-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    first_result = subprocess.run(
        _claim_ingest_command(config_path, "claim-002"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _claim_ingest_command(config_path, "claim-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    list_result = subprocess.run(
        _list_command(config_path, "claims"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    payload = json.loads(list_result.stdout)

    assert study_result.returncode == 0, study_result.stderr
    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 0, second_result.stderr
    assert list_result.returncode == 0, list_result.stderr
    assert list_result.stderr == ""
    assert payload == [
        {
            "claim_id": "claim-001",
            "claim_type": "association",
            "status": "captured",
            "study_id": "study-001",
        },
        {
            "claim_id": "claim-002",
            "claim_type": "association",
            "status": "captured",
            "study_id": "study-001",
        },
    ]
    assert all(set(item) == {"claim_id", "study_id", "status", "claim_type"} for item in payload)
    assert "claim_text" not in list_result.stdout
    assert "provenance_pointer" not in list_result.stdout


def test_public_list_studies_cli_translates_registry_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    def _raise_registry_failure() -> object:
        raise RegistryError("simulated registry gateway failure")

    monkeypatch.setattr(listing, "list_study_cards", _raise_registry_failure)

    exit_code = main(["--config", str(config_path), "list", "studies"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "list studies failed [registry_failure]" in captured.err
    assert "could not list the requested StudyCard collection through the registry gateway" in captured.err


def test_public_list_claims_cli_translates_unsupported_operation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    def _raise_unsupported_operation() -> object:
        raise UnsupportedRegistryOperationError("simulated unsupported list")

    monkeypatch.setattr(listing, "list_claim_cards", _raise_unsupported_operation)

    exit_code = main(["--config", str(config_path), "list", "claims"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "list claims failed [unsupported_operation]" in captured.err
    assert "requested ClaimCard collection listing is unsupported by the registry gateway" in captured.err


def test_existing_public_commands_still_work_after_public_list_addition(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    status_result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "--config", str(config_path), "status"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    show_config_result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "--config", str(config_path), "show-config"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    init_layout_result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "--config", str(config_path), "init-layout"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    study_result = subprocess.run(
        _study_ingest_command(config_path, "study-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path, "dataset-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    claim_result = subprocess.run(
        _claim_ingest_command(config_path, "claim-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    show_study_result = subprocess.run(
        _show_study_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    show_dataset_result = subprocess.run(
        _show_dataset_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    show_claim_result = subprocess.run(
        _show_claim_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert status_result.returncode == 0, status_result.stderr
    assert show_config_result.returncode == 0, show_config_result.stderr
    assert init_layout_result.returncode == 0, init_layout_result.stderr
    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert show_study_result.returncode == 0, show_study_result.stderr
    assert show_dataset_result.returncode == 0, show_dataset_result.stderr
    assert show_claim_result.returncode == 0, show_claim_result.stderr
    assert "MacroVeritas scaffold status" in status_result.stdout
    assert '"project_name": "MacroVeritas"' in show_config_result.stdout
    assert json.loads(show_study_result.stdout)["study_id"] == "study-001"
    assert json.loads(show_dataset_result.stdout)["dataset_id"] == "dataset-001"
    assert json.loads(show_claim_result.stdout)["claim_id"] == "claim-001"
