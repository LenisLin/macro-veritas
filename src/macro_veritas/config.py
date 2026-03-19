from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

import yaml

from .shared.naming import registry_subdir_names

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "project.yaml"


@dataclass(frozen=True)
class ProjectConfig:
    config_path: Path
    project_name: str
    repo_name: str
    package_name: str
    data_root: Path
    registry_root: str
    runs_root: str
    reports_root: str
    raw_root: str
    processed_root: str

    def _resolve_path(self, value: str) -> Path:
        configured = Path(value).expanduser()
        if configured.is_absolute():
            return configured
        return self.data_root / configured

    @property
    def registry_dir(self) -> Path:
        return self._resolve_path(self.registry_root)

    @property
    def runs_dir(self) -> Path:
        return self._resolve_path(self.runs_root)

    @property
    def reports_dir(self) -> Path:
        return self._resolve_path(self.reports_root)

    @property
    def raw_dir(self) -> Path:
        return self._resolve_path(self.raw_root)

    @property
    def processed_dir(self) -> Path:
        return self._resolve_path(self.processed_root)

    def registry_subdir_path(self, subdir_name: str) -> Path:
        return self.registry_dir / subdir_name

    def first_slice_registry_dirs(self) -> dict[str, Path]:
        return {
            subdir_name: self.registry_subdir_path(subdir_name)
            for subdir_name in registry_subdir_names()
        }

    def layout_paths(self) -> dict[str, Path]:
        return {
            "data_root": self.data_root,
            "registry": self.registry_dir,
            "runs": self.runs_dir,
            "reports": self.reports_dir,
            "raw": self.raw_dir,
            "processed": self.processed_dir,
        }

    def to_display_dict(self) -> dict[str, str]:
        return {
            "config_path": str(self.config_path),
            "project_name": self.project_name,
            "repo_name": self.repo_name,
            "package_name": self.package_name,
            "data_root": str(self.data_root),
            "registry_root": self.registry_root,
            "runs_root": self.runs_root,
            "reports_root": self.reports_root,
            "raw_root": self.raw_root,
            "processed_root": self.processed_root,
            "registry_dir": str(self.registry_dir),
            "runs_dir": str(self.runs_dir),
            "reports_dir": str(self.reports_dir),
            "raw_dir": str(self.raw_dir),
            "processed_dir": str(self.processed_dir),
        }


def resolve_config_path(config_path: str | Path | None = None) -> Path:
    configured = config_path or os.environ.get("MACRO_VERITAS_CONFIG") or DEFAULT_CONFIG_PATH
    resolved = Path(configured).expanduser()
    if resolved.is_absolute():
        return resolved
    return REPO_ROOT / resolved


def load_project_config(config_path: str | Path | None = None) -> ProjectConfig:
    resolved_path = resolve_config_path(config_path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Config file not found: {resolved_path}")

    parsed = yaml.safe_load(resolved_path.read_text(encoding="utf-8")) or {}
    if not isinstance(parsed, dict):
        raise ValueError(f"Project config must be a mapping: {resolved_path}")

    required_fields = ("project_name", "repo_name", "package_name", "data_root")
    missing = [field for field in required_fields if not parsed.get(field)]
    if missing:
        raise ValueError(
            f"Project config is missing required fields: {', '.join(sorted(missing))}"
        )

    return ProjectConfig(
        config_path=resolved_path,
        project_name=str(parsed["project_name"]),
        repo_name=str(parsed["repo_name"]),
        package_name=str(parsed["package_name"]),
        data_root=Path(str(parsed["data_root"])).expanduser().resolve(),
        registry_root=str(parsed.get("registry_root", "registry")),
        runs_root=str(parsed.get("runs_root", "runs")),
        reports_root=str(parsed.get("reports_root", "reports")),
        raw_root=str(parsed.get("raw_root", "raw")),
        processed_root=str(parsed.get("processed_root", "processed")),
    )
