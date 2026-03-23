from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

from macro_veritas.cli import main
from macro_veritas.commands import delete as delete_command
from macro_veritas.registry.errors import RegistryError
from macro_veritas.registry.layout import claim_card_path, dataset_card_path, study_card_path

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
        "seeded for public delete test",
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
    ]


def _claim_ingest_command(
    config_path: Path,
    *,
    claim_id: str = "claim-001",
    study_id: str = "study-001",
    dataset_ids: tuple[str, ...] = (),
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
        "captured",
        "--review-readiness",
        "needs_scope",
        "--created-from",
        "seeded for public delete test",
    ]
    for dataset_id in dataset_ids:
        command.extend(["--dataset-id", dataset_id])
    return command


def _delete_study_command(config_path: Path, study_id: str = "study-001") -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "delete",
        "study",
        "--study-id",
        study_id,
    ]


def _delete_dataset_command(config_path: Path, dataset_id: str = "dataset-001") -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "delete",
        "dataset",
        "--dataset-id",
        dataset_id,
    ]


def _delete_claim_command(config_path: Path, claim_id: str = "claim-001") -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "delete",
        "claim",
        "--claim-id",
        claim_id,
    ]


def test_public_delete_claim_cli_succeeds_when_claim_exists(tmp_path: Path) -> None:
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
    delete_result = subprocess.run(
        _delete_claim_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    canonical_path = claim_card_path(data_root.resolve() / "registry", "claim-001")

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert delete_result.returncode == 0, delete_result.stderr
    assert delete_result.stdout.strip() == "delete claim: deleted ClaimCard claim-001"
    assert delete_result.stderr == ""
    assert not canonical_path.exists()


def test_public_delete_dataset_cli_is_blocked_when_claim_depends_on_it(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(_study_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    dataset_result = subprocess.run(_dataset_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    claim_result = subprocess.run(_claim_ingest_command(config_path, dataset_ids=("dataset-001",)), check=False, capture_output=True, text=True, env=_subprocess_env())
    delete_result = subprocess.run(_delete_dataset_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert delete_result.returncode == 1
    assert delete_result.stdout == ""
    assert delete_result.stderr.strip() == (
        "delete dataset failed [dependency_exists]: cannot delete DatasetCard 'dataset-001' because dependent ClaimCard(s) exist: claim-001."
    )


def test_public_delete_study_cli_is_blocked_when_dataset_depends_on_it(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(_study_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    dataset_result = subprocess.run(_dataset_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    delete_result = subprocess.run(_delete_study_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert delete_result.returncode == 1
    assert delete_result.stdout == ""
    assert delete_result.stderr.strip() == (
        "delete study failed [dependency_exists]: cannot delete StudyCard 'study-001' because dependent DatasetCard(s) exist: dataset-001."
    )


def test_public_delete_study_cli_is_blocked_when_claim_depends_on_it(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(_study_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    claim_result = subprocess.run(_claim_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    delete_result = subprocess.run(_delete_study_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert delete_result.returncode == 1
    assert delete_result.stdout == ""
    assert delete_result.stderr.strip() == (
        "delete study failed [dependency_exists]: cannot delete StudyCard 'study-001' because dependent ClaimCard(s) exist: claim-001."
    )


def test_public_delete_dataset_cli_succeeds_when_unreferenced(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(_study_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    dataset_result = subprocess.run(_dataset_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    delete_result = subprocess.run(_delete_dataset_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())

    canonical_path = dataset_card_path(data_root.resolve() / "registry", "dataset-001")

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert delete_result.returncode == 0, delete_result.stderr
    assert delete_result.stdout.strip() == "delete dataset: deleted DatasetCard dataset-001"
    assert delete_result.stderr == ""
    assert not canonical_path.exists()


def test_public_delete_study_cli_succeeds_when_unreferenced(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    study_result = subprocess.run(_study_ingest_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())
    delete_result = subprocess.run(_delete_study_command(config_path), check=False, capture_output=True, text=True, env=_subprocess_env())

    canonical_path = study_card_path(data_root.resolve() / "registry", "study-001")

    assert study_result.returncode == 0, study_result.stderr
    assert delete_result.returncode == 0, delete_result.stderr
    assert delete_result.stdout.strip() == "delete study: deleted StudyCard study-001"
    assert delete_result.stderr == ""
    assert not canonical_path.exists()


@pytest.mark.parametrize(
    ("command", "expected_message"),
    [
        (
            "study",
            "delete study failed [missing_reference]: requested StudyCard 'study-404' was not found.",
        ),
        (
            "dataset",
            "delete dataset failed [missing_reference]: requested DatasetCard 'dataset-404' was not found.",
        ),
        (
            "claim",
            "delete claim failed [missing_reference]: requested ClaimCard 'claim-404' was not found.",
        ),
    ],
)
def test_public_delete_cli_missing_targets_fail_cleanly(
    tmp_path: Path,
    command: str,
    expected_message: str,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    commands = {
        "study": _delete_study_command(config_path, "study-404"),
        "dataset": _delete_dataset_command(config_path, "dataset-404"),
        "claim": _delete_claim_command(config_path, "claim-404"),
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
    assert result.stderr.strip() == expected_message


def test_public_delete_claim_cli_translates_unsafe_identifier(
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
            "delete",
            "claim",
            "--claim-id",
            "../claim-001",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err.strip() == (
        "delete claim failed [unsupported_operation]: rejected an unsafe or unsupported canonical ClaimCard identifier."
    )


def test_public_delete_claim_cli_translates_registry_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    def _raise_registry_failure(claim_id: str) -> None:
        raise RegistryError(f"simulated registry gateway failure for {claim_id}")

    monkeypatch.setattr(delete_command, "delete_claim_card", _raise_registry_failure)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "delete",
            "claim",
            "--claim-id",
            "claim-001",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err.strip() == (
        "delete claim failed [registry_failure]: could not delete the requested ClaimCard through the registry gateway."
    )
