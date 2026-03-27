from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from macro_veritas.cli import main
from macro_veritas.commands import ingest
from macro_veritas.registry.errors import UpdateLockError
from macro_veritas.registry.gateway import create_dataset_card, create_study_card
from macro_veritas.registry.layout import (
    claim_card_path,
    claim_lock_path,
    dataset_lock_path,
    study_lock_path,
)

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
        "created_from_note": "seeded for claim from-file test",
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


def _claim_ingest_data(
    claim_id: str = "claim-001",
    *,
    study_id: str = "study-001",
    dataset_ids: list[str] | None = None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "claim_id": claim_id,
        "study_id": study_id,
        "claim_text": f"Claim text for {claim_id}",
        "claim_type": "association",
        "provenance_pointer": "figure-2",
        "status": "captured",
        "review_readiness": "needs_scope",
        "created_from": "seeded in public claim from-file test",
        "claim_summary_handle": "claim-1",
    }
    if dataset_ids is not None:
        data["dataset_ids"] = dataset_ids
    return data


def _write_claim_ingest_file(path: Path, data: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _claim_from_file_command(
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
        "claim",
        "--from-file",
        str(ingest_path),
    ]
    if extra_args is not None:
        command.extend(extra_args)
    return command


def test_public_ingest_claim_from_file_succeeds_and_writes_canonical_claimcard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    _write_claim_ingest_file(
        ingest_path,
        _claim_ingest_data(dataset_ids=["dataset-001", "dataset-002"]),
    )
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))

    result = subprocess.run(
        _claim_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    canonical_path = claim_card_path(data_root.resolve() / "registry", "claim-001")
    claim_lock = claim_lock_path(data_root.resolve() / "registry", "claim-001")
    dataset_one_lock = dataset_lock_path(data_root.resolve() / "registry", "dataset-001")
    dataset_two_lock = dataset_lock_path(data_root.resolve() / "registry", "dataset-002")
    parent_lock = study_lock_path(data_root.resolve() / "registry", "study-001")

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ingest claim: created ClaimCard claim-001"
    assert claim_lock.is_file()
    assert dataset_one_lock.is_file()
    assert dataset_two_lock.is_file()
    assert parent_lock.is_file()
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
                "created_from_note: seeded in public claim from-file test",
                "dataset_ids:",
                "- dataset-001",
                "- dataset-002",
                "claim_summary_handle: claim-1",
                "",
            ]
        )
    )


def test_public_ingest_claim_from_file_missing_file_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        _claim_from_file_command(config_path, tmp_path / "missing-claim.yaml"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [invalid_payload]" in result.stderr
    assert "ClaimCard ingest file was not found" in result.stderr


def test_public_ingest_claim_from_file_malformed_yaml_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    ingest_path.write_text("claim_id: [claim-001\n", encoding="utf-8")

    result = subprocess.run(
        _claim_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [invalid_payload]" in result.stderr
    assert "ClaimCard ingest file is not valid YAML" in result.stderr


def test_public_ingest_claim_from_file_non_mapping_root_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    ingest_path.write_text(yaml.safe_dump(["claim-001"], sort_keys=False), encoding="utf-8")

    result = subprocess.run(
        _claim_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [invalid_payload]" in result.stderr
    assert "ClaimCard ingest file must decode to one mapping" in result.stderr


def test_public_ingest_claim_from_file_missing_required_keys_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    data = _claim_ingest_data()
    data.pop("claim_text")
    _write_claim_ingest_file(ingest_path, data)

    result = subprocess.run(
        _claim_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [invalid_payload]" in result.stderr
    assert "ClaimCard ingest file is missing required keys" in result.stderr
    assert "claim_text" in result.stderr


def test_public_ingest_claim_from_file_missing_parent_study_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    _write_claim_ingest_file(ingest_path, _claim_ingest_data())

    result = subprocess.run(
        _claim_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [missing_reference]" in result.stderr
    assert "parent StudyCard 'study-001'" in result.stderr


def test_public_ingest_claim_from_file_missing_dataset_fails_cleanly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    _write_claim_ingest_file(
        ingest_path,
        _claim_ingest_data(dataset_ids=["dataset-404"]),
    )
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    result = subprocess.run(
        _claim_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [missing_reference]" in result.stderr
    assert "dataset-404" in result.stderr


def test_public_ingest_claim_from_file_duplicate_create_fails_cleanly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    _write_claim_ingest_file(ingest_path, _claim_ingest_data())
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    first_result = subprocess.run(
        _claim_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _claim_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 1
    assert "ingest claim failed [duplicate_target]" in second_result.stderr
    assert "canonical ClaimCard already exists" in second_result.stderr


def test_public_ingest_claim_from_file_mixed_with_field_flags_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    _write_claim_ingest_file(ingest_path, _claim_ingest_data())

    result = subprocess.run(
        _claim_from_file_command(
            config_path,
            ingest_path,
            extra_args=["--claim-id", "claim-override"],
        ),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest claim failed [invalid_payload]" in result.stderr
    assert "ClaimCard --from-file cannot be combined with field flags" in result.stderr
    assert "--claim-id" in result.stderr


def test_public_ingest_claim_from_file_surfaces_lock_failure_clearly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "claim-input.yaml"
    _write_config(config_path, data_root)
    _write_claim_ingest_file(ingest_path, _claim_ingest_data())
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    create_study_card(_study_card())

    def _raise_lock_failure(card: object) -> object:
        raise UpdateLockError(
            "ClaimCard ingest could not acquire the exclusive ingest lock for 'claim-001'."
        )

    monkeypatch.setattr(ingest, "create_claim_card", _raise_lock_failure)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "claim",
            "--from-file",
            str(ingest_path),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest claim failed [registry_failure]" in captured.err
    assert "exclusive ingest lock" in captured.err
