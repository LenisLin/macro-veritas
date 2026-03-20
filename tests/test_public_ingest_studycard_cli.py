from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

from macro_veritas.cli import main
from macro_veritas.commands import ingest
from macro_veritas.registry.errors import RegistryError
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
        "draft",
        "--created-from",
        "seeded in public CLI test",
        "--screening-note",
        "passed CLI review",
        "--source-artifact",
        "raw/studies/study-001.pdf",
    ]


def test_public_ingest_study_cli_succeeds_and_writes_canonical_studycard(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        _study_ingest_command(config_path),
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
                "created_from_note: seeded in public CLI test",
                "screening_note: passed CLI review",
                "source_artifact_locator: raw/studies/study-001.pdf",
                "",
            ]
        )
    )


def test_public_ingest_study_cli_duplicate_create_returns_user_facing_failure(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    first_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    second_result = subprocess.run(
        _study_ingest_command(config_path),
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert first_result.returncode == 0, first_result.stderr
    assert second_result.returncode == 1
    assert "ingest study failed [duplicate_target]" in second_result.stderr
    assert "canonical StudyCard already exists" in second_result.stderr


def test_public_ingest_study_cli_invalid_argument_set_exits_non_zero(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    command = _study_ingest_command(config_path)
    status_index = command.index("draft")
    command[status_index] = "invalid-status"

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode != 0
    assert "invalid choice" in result.stderr
    assert "--status" in result.stderr


def test_public_ingest_study_cli_translates_unsafe_study_id(
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
            "ingest",
            "study",
            "--study-id",
            "../study-001",
            "--citation-handle",
            "doi:study-001",
            "--tumor-type",
            "glioma",
            "--therapy-scope",
            "immunotherapy",
            "--relevance-scope",
            "preclinical",
            "--screening-decision",
            "include",
            "--status",
            "draft",
            "--created-from",
            "seeded in direct CLI test",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest study failed [unsupported_operation]" in captured.err
    assert "unsafe canonical study identifier" in captured.err


def test_public_ingest_study_cli_translates_registry_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    def _raise_registry_failure(card: object) -> object:
        raise RegistryError("simulated registry gateway failure")

    monkeypatch.setattr(ingest, "create_study_card", _raise_registry_failure)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "ingest",
            "study",
            "--study-id",
            "study-001",
            "--citation-handle",
            "doi:study-001",
            "--tumor-type",
            "glioma",
            "--therapy-scope",
            "immunotherapy",
            "--relevance-scope",
            "preclinical",
            "--screening-decision",
            "include",
            "--status",
            "draft",
            "--created-from",
            "seeded in direct CLI test",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "ingest study failed [registry_failure]" in captured.err
    assert "registry gateway boundary" in captured.err
