"""Static relative-path helpers for the frozen first-slice registry layout.

This module mirrors the filesystem conventions frozen in
`docs/registry_layout.md` and returns canonical relative paths for first-slice
card files.

It does not access the filesystem for callers, implement serialization, or
resolve live references at runtime. It does expose the canonical StudyCard,
DatasetCard, and ClaimCard directory/path helpers used by the internal runtime
helpers. Boundary docs: `docs/registry_layout.md`,
`docs/registry_io_boundary.md`, and `docs/claimcard_runtime.md`.
"""

from __future__ import annotations

from pathlib import Path

from macro_veritas.shared.naming import (
    claim_card_filename,
    dataset_card_filename,
    history_subdir_name,
    lock_filename,
    lock_subdir_name,
    registry_subdir_names,
    study_card_filename,
)

_STUDIES_SUBDIR, _DATASETS_SUBDIR, _CLAIMS_SUBDIR = registry_subdir_names()
_HISTORY_SUBDIR = history_subdir_name()
_LOCKS_SUBDIR = lock_subdir_name()


def study_card_relative_path(study_id: str) -> str:
    """Return the canonical relative path for a first-slice `StudyCard`."""

    return f"{_STUDIES_SUBDIR}/{study_card_filename(study_id)}"


def dataset_card_relative_path(dataset_id: str) -> str:
    """Return the canonical relative path for a first-slice `DatasetCard`."""

    return f"{_DATASETS_SUBDIR}/{dataset_card_filename(dataset_id)}"


def claim_card_relative_path(claim_id: str) -> str:
    """Return the canonical relative path for a first-slice `ClaimCard`."""

    return f"{_CLAIMS_SUBDIR}/{claim_card_filename(claim_id)}"


def study_cards_dir(registry_root: str | Path) -> Path:
    """Return the canonical StudyCard directory beneath a resolved registry root."""

    return Path(registry_root) / _STUDIES_SUBDIR


def study_card_path(registry_root: str | Path, study_id: str) -> Path:
    """Return the canonical filesystem path for a first-slice `StudyCard`."""

    return study_cards_dir(registry_root) / study_card_filename(study_id)


def dataset_cards_dir(registry_root: str | Path) -> Path:
    """Return the canonical DatasetCard directory beneath a resolved registry root."""

    return Path(registry_root) / _DATASETS_SUBDIR


def dataset_card_path(registry_root: str | Path, dataset_id: str) -> Path:
    """Return the canonical filesystem path for a first-slice `DatasetCard`."""

    return dataset_cards_dir(registry_root) / dataset_card_filename(dataset_id)


def claim_cards_dir(registry_root: str | Path) -> Path:
    """Return the canonical ClaimCard directory beneath a resolved registry root."""

    return Path(registry_root) / _CLAIMS_SUBDIR


def claim_card_path(registry_root: str | Path, claim_id: str) -> Path:
    """Return the canonical filesystem path for a first-slice `ClaimCard`."""

    return claim_cards_dir(registry_root) / claim_card_filename(claim_id)


def history_root(registry_root: str | Path) -> Path:
    """Return the append-only history root beneath a resolved registry root."""

    return Path(registry_root) / _HISTORY_SUBDIR


def lock_root(registry_root: str | Path) -> Path:
    """Return the mutation-lock root beneath a resolved registry root."""

    return Path(registry_root) / _LOCKS_SUBDIR


def study_history_dir(registry_root: str | Path, study_id: str) -> Path:
    """Return the history directory for one `StudyCard` identifier."""

    return history_root(registry_root) / _STUDIES_SUBDIR / study_id


def study_lock_dir(registry_root: str | Path) -> Path:
    """Return the StudyCard mutation-lock directory beneath a resolved registry root."""

    return lock_root(registry_root) / _STUDIES_SUBDIR


def study_lock_path(registry_root: str | Path, study_id: str) -> Path:
    """Return the StudyCard mutation-lock path for one canonical identifier."""

    return study_lock_dir(registry_root) / lock_filename(study_id)


def dataset_history_dir(registry_root: str | Path, dataset_id: str) -> Path:
    """Return the history directory for one `DatasetCard` identifier."""

    return history_root(registry_root) / _DATASETS_SUBDIR / dataset_id


def dataset_lock_dir(registry_root: str | Path) -> Path:
    """Return the DatasetCard mutation-lock directory beneath a resolved registry root."""

    return lock_root(registry_root) / _DATASETS_SUBDIR


def dataset_lock_path(registry_root: str | Path, dataset_id: str) -> Path:
    """Return the DatasetCard mutation-lock path for one canonical identifier."""

    return dataset_lock_dir(registry_root) / lock_filename(dataset_id)


def claim_history_dir(registry_root: str | Path, claim_id: str) -> Path:
    """Return the history directory for one `ClaimCard` identifier."""

    return history_root(registry_root) / _CLAIMS_SUBDIR / claim_id


def claim_lock_dir(registry_root: str | Path) -> Path:
    """Return the ClaimCard mutation-lock directory beneath a resolved registry root."""

    return lock_root(registry_root) / _CLAIMS_SUBDIR


def claim_lock_path(registry_root: str | Path, claim_id: str) -> Path:
    """Return the ClaimCard mutation-lock path for one canonical identifier."""

    return claim_lock_dir(registry_root) / lock_filename(claim_id)


def describe_first_slice_layout() -> dict[str, dict[str, str | bool]]:
    """Describe the frozen first-slice registry layout.

    Inputs:
        None.
    Outputs:
        A mapping from card family to canonical root, filename pattern, and
        format label.
    Non-goals:
        This does not create directories or read registry cards.
    """

    return {
        "StudyCard": {
            "root_subdir": _STUDIES_SUBDIR,
            "filename_pattern": "<study_id>.yaml",
            "one_card_per_file": True,
            "format_label": "yaml",
        },
        "DatasetCard": {
            "root_subdir": _DATASETS_SUBDIR,
            "filename_pattern": "<dataset_id>.yaml",
            "one_card_per_file": True,
            "format_label": "yaml",
        },
        "ClaimCard": {
            "root_subdir": _CLAIMS_SUBDIR,
            "filename_pattern": "<claim_id>.yaml",
            "one_card_per_file": True,
            "format_label": "yaml",
        },
    }


def describe_layout_vs_gateway_boundary() -> dict[str, str | bool]:
    """Describe the split between static layout helpers and future access logic.

    Inputs:
        None.
    Outputs:
        A static mapping that distinguishes path conventions from access responsibility.
    Non-goals:
        This does not perform access checks or gateway operations.
    """

    return {
        "layout_role": "canonical relative paths and naming conventions only",
        "gateway_role": "sole boundary for registry retrieval and persistence",
        "layout_is_access_api": False,
        "cli_should_use_layout_as_io_layer": False,
        "governance_should_use_layout_as_io_layer": False,
    }


__all__ = [
    "claim_card_path",
    "claim_cards_dir",
    "claim_card_relative_path",
    "claim_history_dir",
    "claim_lock_dir",
    "claim_lock_path",
    "dataset_card_path",
    "dataset_cards_dir",
    "dataset_card_relative_path",
    "dataset_history_dir",
    "dataset_lock_dir",
    "dataset_lock_path",
    "describe_first_slice_layout",
    "describe_layout_vs_gateway_boundary",
    "history_root",
    "lock_root",
    "study_card_path",
    "study_cards_dir",
    "study_card_relative_path",
    "study_history_dir",
    "study_lock_dir",
    "study_lock_path",
]
