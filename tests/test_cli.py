from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from macro_veritas.config import load_project_config

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


def test_load_project_config_resolves_relative_layout_paths(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    config = load_project_config(config_path)

    assert config.data_root == data_root.resolve()
    assert config.registry_dir == data_root.resolve() / "registry"
    assert config.runs_dir == data_root.resolve() / "runs"
    assert config.reports_dir == data_root.resolve() / "reports"
    assert config.raw_dir == data_root.resolve() / "raw"
    assert config.processed_dir == data_root.resolve() / "processed"


def test_python_module_help_succeeds() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "MacroVeritas scaffold CLI" in result.stdout
    assert "init-layout" in result.stdout
    assert "ingest" in result.stdout
    assert "update" in result.stdout
    assert "show" in result.stdout
    assert "list" in result.stdout
    assert "delete" in result.stdout


def test_ingest_help_shows_public_study_dataset_and_claim_subcommands_only() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "ingest", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "study" in result.stdout
    assert "dataset" in result.stdout
    assert "claim" in result.stdout
    assert "bind" not in result.stdout
    assert "extract" not in result.stdout


def test_update_help_shows_public_study_dataset_and_claim_subcommands_only() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "update", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    study_result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "update", "study", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "update", "dataset", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    claim_result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "update", "claim", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "dataset" in result.stdout
    assert "study" in result.stdout
    assert "claim" in result.stdout
    assert study_result.returncode == 0, study_result.stderr
    assert "--study-id" in study_result.stdout
    assert "--from-file" in study_result.stdout
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert "--dataset-id" in dataset_result.stdout
    assert "--from-file" in dataset_result.stdout
    assert claim_result.returncode == 0, claim_result.stderr
    assert "--claim-id" in claim_result.stdout
    assert "--from-file" in claim_result.stdout


def test_ingest_help_shows_from_file_option_for_all_three_card_families() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "ingest", "claim", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    study_result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "ingest", "study", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )
    dataset_result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "ingest", "dataset", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "--from-file" in result.stdout
    assert study_result.returncode == 0, study_result.stderr
    assert dataset_result.returncode == 0, dataset_result.stderr
    assert "--from-file" in study_result.stdout
    assert "--from-file" in dataset_result.stdout


def test_show_help_shows_public_study_dataset_and_claim_subcommands_only() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "show", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "study" in result.stdout
    assert "dataset" in result.stdout
    assert "claim" in result.stdout
    assert "bind" not in result.stdout
    assert "extract" not in result.stdout



def test_list_help_shows_public_studies_datasets_and_claims_subcommands_only() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "list", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "studies" in result.stdout
    assert "datasets" in result.stdout
    assert "claims" in result.stdout
    assert "bind" not in result.stdout
    assert "extract" not in result.stdout


def test_delete_help_shows_public_study_dataset_and_claim_subcommands_only() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "macro_veritas", "delete", "--help"],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "study" in result.stdout
    assert "dataset" in result.stdout
    assert "claim" in result.stdout
    assert "bind" not in result.stdout
    assert "extract" not in result.stdout

def test_init_layout_creates_placeholder_directories(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "macro_veritas",
            "--config",
            str(config_path),
            "init-layout",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert (data_root / "registry").is_dir()
    assert (data_root / "runs").is_dir()
    assert (data_root / "reports").is_dir()
    assert (data_root / "raw").is_dir()
    assert (data_root / "processed").is_dir()


def test_status_command_still_runs_without_public_ingest_changes(tmp_path: Path) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "macro_veritas",
            "--config",
            str(config_path),
            "status",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert "MacroVeritas scaffold status" in result.stdout
    assert "stage: Initialization / scaffold" in result.stdout


def test_show_config_command_still_runs_without_public_ingest_changes(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "macro_veritas",
            "--config",
            str(config_path),
            "show-config",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=_subprocess_env(),
    )

    assert result.returncode == 0, result.stderr
    assert '"project_name": "MacroVeritas"' in result.stdout
    assert '"registry_dir"' in result.stdout
