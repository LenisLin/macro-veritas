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
        "seeded for public claim update test",
    ]


def _dataset_ingest_command(
    config_path: Path,
    *,
    dataset_id: str,
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
        "seeded for public claim update test",
        "--claim-summary-handle",
        "claim-1",
    ]
    for dataset_id in dataset_ids:
        command.extend(["--dataset-id", dataset_id])
    return command


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


def _update_claim_command(
    config_path: Path,
    update_path: Path,
    *,
    claim_id: str = "claim-001",
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "update",
        "claim",
        "--claim-id",
        claim_id,
        "--from-file",
        str(update_path),
    ]


def _claim_card(
    claim_id: str = "claim-001",
    *,
    study_id: str = "study-001",
    claim_text: str = "Updated ClaimCard text",
    provenance_pointer: str = "table-4",
    status: str = "ready",
    review_readiness: str = "execution_candidate",
    created_from_note: str = "updated from YAML replacement",
    dataset_ids: list[str] | None = None,
    claim_summary_handle: str = "claim-ready",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "claim_id": claim_id,
        "study_id": study_id,
        "claim_text": claim_text,
        "claim_type": "association",
        "provenance_pointer": provenance_pointer,
        "status": status,
        "review_readiness": review_readiness,
        "created_from_note": created_from_note,
        "claim_summary_handle": claim_summary_handle,
    }
    if dataset_ids is not None:
        payload["dataset_ids"] = dataset_ids
    return payload


def _write_update_file(path: Path, payload: dict[str, object] | list[object] | str) -> None:
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
        return
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_public_update_claim_from_file_succeeds_and_show_reflects_replacement(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "claim-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(
        update_path,
        _claim_card(
            claim_text="Updated claim text for claim-001",
            created_from_note="curation replacement from YAML",
            dataset_ids=["dataset-001", "dataset-002"],
        ),
    )

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_one_result = subprocess.run(
        _dataset_ingest_command(config_path, dataset_id="dataset-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_two_result = subprocess.run(
        _dataset_ingest_command(config_path, dataset_id="dataset-002"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    claim_result = subprocess.run(
        _claim_ingest_command(config_path, dataset_ids=("dataset-001",)),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_claim_command(config_path, update_path),
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

    payload = json.loads(show_result.stdout)

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_one_result.returncode == 0, dataset_one_result.stderr
    assert dataset_two_result.returncode == 0, dataset_two_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert update_result.returncode == 0, update_result.stderr
    assert update_result.stdout.strip() == "update claim: updated ClaimCard claim-001"
    assert update_result.stderr == ""
    assert show_result.returncode == 0, show_result.stderr
    assert payload["claim_text"] == "Updated claim text for claim-001"
    assert payload["provenance_pointer"] == "table-4"
    assert payload["status"] == "ready"
    assert payload["review_readiness"] == "execution_candidate"
    assert payload["created_from_note"] == "curation replacement from YAML"
    assert payload["dataset_ids"] == ["dataset-001", "dataset-002"]
    assert payload["claim_summary_handle"] == "claim-ready"


def test_public_update_claim_missing_target_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "claim-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _claim_card())

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_claim_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update claim failed [missing_reference]: requested ClaimCard 'claim-001' was not found."
    )


def test_public_update_claim_missing_parent_study_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "claim-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _claim_card(study_id="study-999"))

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
    update_result = subprocess.run(
        _update_claim_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update claim failed [missing_reference]: ClaimCard update requires the parent StudyCard 'study-999' to exist before replace."
    )


def test_public_update_claim_missing_dataset_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "claim-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _claim_card(dataset_ids=["dataset-001", "dataset-404"]))

    study_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        _dataset_ingest_command(config_path, dataset_id="dataset-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    claim_result = subprocess.run(
        _claim_ingest_command(config_path, dataset_ids=("dataset-001",)),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_claim_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update claim failed [missing_reference]: ClaimCard update requires referenced DatasetCard(s) to exist before replace: dataset-404."
    )


def test_public_update_claim_cli_and_file_target_mismatch_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "claim-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _claim_card(claim_id="claim-002"))

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
    update_result = subprocess.run(
        _update_claim_command(config_path, update_path, claim_id="claim-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update claim failed [invalid_payload]: "
        "ClaimCard update input is invalid: CLI --claim-id must match file claim_id: "
        "claim-001 != claim-002."
    )


def test_public_update_claim_missing_file_fails_cleanly(tmp_path: Path) -> None:
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
    update_result = subprocess.run(
        _update_claim_command(config_path, tmp_path / "missing-claim-update.yaml"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update claim failed [invalid_payload]" in update_result.stderr
    assert "ClaimCard update file was not found" in update_result.stderr


def test_public_update_claim_malformed_yaml_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "claim-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, "claim_id: [claim-001\n")

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
    update_result = subprocess.run(
        _update_claim_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update claim failed [invalid_payload]" in update_result.stderr
    assert "ClaimCard update file is not valid YAML" in update_result.stderr


def test_public_update_claim_non_mapping_yaml_root_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "claim-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, ["claim-001"])

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
    update_result = subprocess.run(
        _update_claim_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update claim failed [invalid_payload]" in update_result.stderr
    assert "ClaimCard update file must decode to one mapping" in update_result.stderr


def test_public_update_claim_missing_required_keys_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "claim-update.yaml"
    _write_config(config_path, data_root)
    payload = _claim_card()
    del payload["created_from_note"]
    _write_update_file(update_path, payload)

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
    update_result = subprocess.run(
        _update_claim_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert study_result.returncode == 0, study_result.stderr
    assert claim_result.returncode == 0, claim_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update claim failed [invalid_payload]" in update_result.stderr
    assert "ClaimCard payload is missing required fields: created_from_note" in update_result.stderr
