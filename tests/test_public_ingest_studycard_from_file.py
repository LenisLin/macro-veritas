from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from macro_veritas.cli import main
from macro_veritas.commands import ingest
from macro_veritas.registry.layout import study_card_path

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


def _study_ingest_data(study_id: str = "study-001") -> dict[str, object]:
    return {
        "study_id": study_id,
        "citation_handle": f"doi:{study_id}",
        "tumor_type": ["glioma"],
        "therapy_scope": ["immunotherapy"],
        "relevance_scope": ["preclinical"],
        "screening_decision": "include",
        "status": "draft",
        "created_from": "seeded in public study from-file test",
        "screening_note": "passed CLI review",
        "source_artifact": "raw/studies/study-001.pdf",
    }


def _write_study_ingest_file(path: Path, data: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _study_from_file_command(
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
        "study",
        "--from-file",
        str(ingest_path),
    ]
    if extra_args is not None:
        command.extend(extra_args)
    return command


def test_public_ingest_study_from_file_succeeds_and_writes_canonical_studycard(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "study-input.yaml"
    _write_config(config_path, data_root)
    _write_study_ingest_file(ingest_path, _study_ingest_data())

    result = subprocess.run(
        _study_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    canonical_path = study_card_path(data_root.resolve() / "registry", "study-001")

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ingest study: created StudyCard study-001"
    assert canonical_path.read_text(encoding="utf-8") == (
        "\n".join(
            [
                "study_id: study-001",
                "citation_handle: doi:study-001",
                "tumor_scope_tags:",
                "- glioma",
                "therapy_scope_tags:",
                "- immunotherapy",
                "relevance_scope_tags:",
                "- preclinical",
                "screening_decision: include",
                "status: draft",
                "created_from_note: seeded in public study from-file test",
                "screening_note: passed CLI review",
                "source_artifact_locator: raw/studies/study-001.pdf",
                "",
            ]
        )
    )


def test_public_ingest_study_from_file_missing_file_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        _study_from_file_command(config_path, tmp_path / "missing-study.yaml"),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest study failed [invalid_payload]" in result.stderr
    assert "StudyCard ingest file was not found" in result.stderr


def test_public_ingest_study_from_file_malformed_yaml_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "study-input.yaml"
    _write_config(config_path, data_root)
    ingest_path.write_text("study_id: [study-001\n", encoding="utf-8")

    result = subprocess.run(
        _study_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest study failed [invalid_payload]" in result.stderr
    assert "StudyCard ingest file is not valid YAML" in result.stderr


def test_public_ingest_study_from_file_non_mapping_root_fails_cleanly(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "study-input.yaml"
    _write_config(config_path, data_root)
    ingest_path.write_text(yaml.safe_dump(["study-001"], sort_keys=False), encoding="utf-8")

    result = subprocess.run(
        _study_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest study failed [invalid_payload]" in result.stderr
    assert "StudyCard ingest file must decode to one mapping" in result.stderr


def test_public_ingest_study_from_file_missing_required_keys_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "study-input.yaml"
    _write_config(config_path, data_root)
    data = _study_ingest_data()
    data.pop("screening_decision")
    _write_study_ingest_file(ingest_path, data)

    result = subprocess.run(
        _study_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 1
    assert "ingest study failed [invalid_payload]" in result.stderr
    assert "StudyCard ingest file is missing required keys" in result.stderr
    assert "screening_decision" in result.stderr


def test_public_ingest_study_from_file_duplicate_create_fails_cleanly(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "study-input.yaml"
    _write_config(config_path, data_root)
    _write_study_ingest_file(ingest_path, _study_ingest_data())

    first_result = subprocess.run(
        _study_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _study_from_file_command(config_path, ingest_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 1
    assert "ingest study failed [duplicate_target]" in second_result.stderr
    assert "canonical StudyCard already exists" in second_result.stderr


def test_public_ingest_study_from_file_mixed_with_field_flags_fails_before_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    ingest_path = tmp_path / "study-input.yaml"
    _write_config(config_path, data_root)
    _write_study_ingest_file(ingest_path, _study_ingest_data())

    def _unexpected(*args: object, **kwargs: object) -> object:
        raise AssertionError("mixed-input study ingest should fail before execution")

    monkeypatch.setattr(ingest, "execute_studycard_ingest_from_file", _unexpected)
    monkeypatch.setattr(ingest, "execute_studycard_ingest_input", _unexpected)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "study",
            "--from-file",
            str(ingest_path),
            "--study-id",
            "study-override",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest study failed [invalid_payload]" in captured.err
    assert "StudyCard --from-file cannot be combined with field flags" in captured.err
    assert "--study-id" in captured.err
