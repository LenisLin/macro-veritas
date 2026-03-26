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


def _study_ingest_command(
    config_path: Path,
    *,
    study_id: str = "study-001",
    status: str = "registered",
) -> list[str]:
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
        status,
        "--created-from",
        "seeded for public study update test",
        "--screening-note",
        "initial screening note",
        "--source-artifact",
        f"raw/studies/{study_id}.pdf",
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


def _update_study_command(
    config_path: Path,
    update_path: Path,
    *,
    study_id: str = "study-001",
) -> list[str]:
    return [
        sys.executable,
        "-m",
        "macro_veritas",
        "--config",
        str(config_path),
        "update",
        "study",
        "--study-id",
        study_id,
        "--from-file",
        str(update_path),
    ]


def _study_card(
    study_id: str = "study-001",
    *,
    citation_handle: str | None = None,
    status: str = "registered",
    created_from_note: str = "updated from YAML replacement",
    screening_note: str = "updated screening note",
    source_artifact_locator: str = "processed/studies/study-001.pdf",
) -> dict[str, object]:
    return {
        "study_id": study_id,
        "citation_handle": citation_handle or f"doi:{study_id}:v2",
        "tumor_scope_tags": ["glioma", "melanoma"],
        "therapy_scope_tags": ["immunotherapy"],
        "relevance_scope_tags": ["preclinical", "translational"],
        "screening_decision": "include",
        "status": status,
        "created_from_note": created_from_note,
        "screening_note": screening_note,
        "source_artifact_locator": source_artifact_locator,
    }


def _write_update_file(path: Path, payload: dict[str, object] | list[object] | str) -> None:
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
        return
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_public_update_study_from_file_succeeds_and_show_reflects_replacement(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "study-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(
        update_path,
        _study_card(
            status="closed",
            created_from_note="curation replacement from YAML",
            screening_note="ready for archival closeout",
            source_artifact_locator="processed/studies/study-001-v2.pdf",
        ),
    )

    ingest_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_study_command(config_path, update_path),
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

    payload = json.loads(show_result.stdout)

    assert ingest_result.returncode == 0, ingest_result.stderr
    assert update_result.returncode == 0, update_result.stderr
    assert update_result.stdout.strip() == "update study: updated StudyCard study-001"
    assert update_result.stderr == ""
    assert show_result.returncode == 0, show_result.stderr
    assert payload["status"] == "closed"
    assert payload["citation_handle"] == "doi:study-001:v2"
    assert payload["created_from_note"] == "curation replacement from YAML"
    assert payload["screening_note"] == "ready for archival closeout"
    assert payload["source_artifact_locator"] == "processed/studies/study-001-v2.pdf"
    assert payload["tumor_scope_tags"] == ["glioma", "melanoma"]
    assert payload["relevance_scope_tags"] == ["preclinical", "translational"]


def test_public_update_study_missing_target_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "study-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _study_card())

    update_result = subprocess.run(
        _update_study_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update study failed [missing_reference]: requested StudyCard 'study-001' was not found."
    )


def test_public_update_study_cli_and_file_target_mismatch_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "study-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _study_card(study_id="study-002"))

    ingest_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_study_command(config_path, update_path, study_id="study-001"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert ingest_result.returncode == 0, ingest_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update study failed [invalid_payload]: "
        "StudyCard update input is invalid: CLI --study-id must match file study_id: "
        "study-001 != study-002."
    )


def test_public_update_study_malformed_yaml_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "study-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, "study_id: [study-001\n")

    ingest_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_study_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert ingest_result.returncode == 0, ingest_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update study failed [invalid_payload]" in update_result.stderr
    assert "StudyCard update file is not valid YAML" in update_result.stderr


def test_public_update_study_non_mapping_yaml_root_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "study-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, ["study-001"])

    ingest_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_study_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert ingest_result.returncode == 0, ingest_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update study failed [invalid_payload]" in update_result.stderr
    assert "StudyCard update file must decode to one mapping" in update_result.stderr


def test_public_update_study_missing_required_keys_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "study-update.yaml"
    _write_config(config_path, data_root)
    payload = _study_card()
    del payload["created_from_note"]
    _write_update_file(update_path, payload)

    ingest_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_study_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert ingest_result.returncode == 0, ingest_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert "update study failed [invalid_payload]" in update_result.stderr
    assert "StudyCard payload is missing required fields: created_from_note" in update_result.stderr


def test_public_update_study_closed_to_active_transition_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    update_path = tmp_path / "study-update.yaml"
    _write_config(config_path, data_root)
    _write_update_file(update_path, _study_card(status="registered"))

    ingest_result = subprocess.run(
        _study_ingest_command(config_path, status="closed"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    update_result = subprocess.run(
        _update_study_command(config_path, update_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert ingest_result.returncode == 0, ingest_result.stderr
    assert update_result.returncode == 1
    assert update_result.stdout == ""
    assert update_result.stderr.strip() == (
        "update study failed [invalid_payload]: "
        "StudyCard update rejected invalid StudyCard state: "
        "StudyCard status 'closed' is terminal and cannot transition back to an active status."
    )
