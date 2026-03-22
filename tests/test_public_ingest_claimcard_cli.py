from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

from macro_veritas.cli import main
from macro_veritas.commands import ingest
from macro_veritas.registry.errors import RegistryError, UnsupportedRegistryOperationError
from macro_veritas.registry.gateway import create_dataset_card, create_study_card
from macro_veritas.registry.layout import claim_card_path

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
        "created_from_note": "seeded for claim ingest test",
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


def _claim_ingest_command(
    config_path: Path,
    *,
    claim_id: str = "claim-001",
    study_id: str = "study-001",
    status: str = "captured",
    review_readiness: str = "needs_scope",
    dataset_ids: list[str] | None = None,
) -> list[str]:
    command = [
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
        status,
        "--review-readiness",
        review_readiness,
        "--created-from",
        "seeded in public claim CLI test",
        "--claim-summary-handle",
        "claim-1",
    ]
    for dataset_id in dataset_ids or []:
        command.extend(["--dataset-id", dataset_id])
    return command


def test_public_ingest_claim_cli_succeeds_and_writes_canonical_claimcard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))

    result = subprocess.run(
        _claim_ingest_command(config_path, dataset_ids=["dataset-001", "dataset-002"]),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    canonical_path = claim_card_path(data_root.resolve() / "registry", "claim-001")

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ingest claim: created ClaimCard claim-001"
    assert canonical_path.read_text(encoding="utf-8") == (
        "\n".join(
            [
                "claim_id: claim-001",
                "study_id: study-001",
                "claim_text: Claim text for claim-001",
                "claim_type: association",
                "provenance_pointer: figure-2",
                "status: captured",
                "review_readiness: needs_scope",
                "created_from_note: seeded in public claim CLI test",
                "dataset_ids:",
                "- dataset-001",
                "- dataset-002",
                "claim_summary_handle: claim-1",
                "",
            ]
        )
    )


def test_public_ingest_claim_cli_duplicate_create_returns_user_facing_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    first_result = subprocess.run(
        _claim_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _claim_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 1
    assert "ingest claim failed [duplicate_target]" in second_result.stderr
    assert "canonical ClaimCard already exists" in second_result.stderr


def test_public_ingest_claim_cli_missing_parent_returns_clean_failure(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        _claim_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [missing_reference]" in result.stderr
    assert "parent StudyCard 'study-001'" in result.stderr


def test_public_ingest_claim_cli_missing_dataset_returns_clean_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    result = subprocess.run(
        _claim_ingest_command(config_path, dataset_ids=["dataset-404"]),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [missing_reference]" in result.stderr
    assert "dataset-404" in result.stderr


def test_public_ingest_claim_cli_invalid_argument_set_exits_non_zero(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    command = _claim_ingest_command(config_path, review_readiness="invalid-readiness")

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode != 0
    assert "invalid choice" in result.stderr
    assert "--review-readiness" in result.stderr


def test_public_ingest_claim_cli_translates_registry_failure(
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

    monkeypatch.setattr(ingest, "create_claim_card", _raise_registry_failure)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "claim",
            "--claim-id",
            "claim-001",
            "--study-id",
            "study-001",
            "--claim-text",
            "Claim text for claim-001",
            "--claim-type",
            "association",
            "--provenance-pointer",
            "figure-2",
            "--status",
            "captured",
            "--review-readiness",
            "needs_scope",
            "--created-from",
            "seeded in direct CLI test",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest claim failed [registry_failure]" in captured.err
    assert "registry gateway boundary" in captured.err


def test_public_ingest_claim_cli_translates_unsupported_operation(
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

    monkeypatch.setattr(ingest, "plan_create_claim_card", _raise_unsupported)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "claim",
            "--claim-id",
            "claim-001",
            "--study-id",
            "study-001",
            "--claim-text",
            "Claim text for claim-001",
            "--claim-type",
            "association",
            "--provenance-pointer",
            "figure-2",
            "--status",
            "captured",
            "--review-readiness",
            "needs_scope",
            "--created-from",
            "seeded in direct CLI test",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest claim failed [unsupported_operation]" in captured.err
    assert "unsupported registry operation or identifier" in captured.err
