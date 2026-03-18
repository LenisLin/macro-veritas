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
