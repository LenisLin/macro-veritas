"""Append-only snapshot helpers for pre-update registry safety.

This module preserves the exact prior YAML bytes of one canonical card file
before an update runtime overwrites that live path.

Responsibilities:
- compute one snapshot destination beneath a provided history directory
- create the parent history directory when needed
- copy exact on-disk YAML bytes into a new append-only snapshot file

Non-goals:
- restore or rollback behavior
- snapshot listing or browsing
- diffing, metadata manifests, or retention policies
"""

from __future__ import annotations

import os
from pathlib import Path

from macro_veritas.shared.naming import snapshot_filename


def preserve_pre_update_snapshot(source_path: Path, destination_dir: Path) -> Path:
    """Copy one canonical YAML file into append-only history before overwrite."""

    destination_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = _next_snapshot_path(destination_dir)
    content = source_path.read_bytes()

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    file_descriptor = os.open(snapshot_path, flags, 0o644)
    try:
        with os.fdopen(file_descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            snapshot_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise

    _fsync_directory(destination_dir)
    return snapshot_path


def _next_snapshot_path(destination_dir: Path) -> Path:
    while True:
        candidate = destination_dir / snapshot_filename()
        if not candidate.exists():
            return candidate


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY

    directory_fd = os.open(directory, flags)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


__all__ = ["preserve_pre_update_snapshot"]
