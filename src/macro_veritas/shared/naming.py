"""Naming helpers for documented object families and frozen registry filenames.

This module exposes small, static naming helpers so descriptor modules can
share the same object-family labels, registry subdirectory names, and
first-slice card filename conventions.

It does not validate schemas, normalize identifiers, or access the filesystem.
Boundary docs: `docs/module_map.md`, `docs/registry_layout.md`,
`docs/registry_model.md`, and `docs/api_specs.md`.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .types import ObjectFamilyName, ReservedCLIFamilyName

_RESERVED_CLI_FAMILIES: tuple[ReservedCLIFamilyName, ...] = (
    "ingest",
    "update",
    "show",
    "list",
    "delete",
    "bind",
    "extract",
    "audit",
    "review",
    "run",
    "grade",
)

_OBJECT_FAMILY_NAMES: tuple[ObjectFamilyName, ...] = (
    "StudyCard",
    "DatasetCard",
    "ClaimCard",
    "MethodCard",
    "ReanalysisBundle",
    "EvidenceCard",
    "AuditRecord",
)

_OBJECT_FAMILY_LOOKUP: dict[str, ObjectFamilyName] = {
    family.lower(): family for family in _OBJECT_FAMILY_NAMES
}
_REGISTRY_SUBDIR_NAMES: tuple[str, ...] = ("studies", "datasets", "claims")
_HISTORY_SUBDIR_NAME = "history"
_LOCKS_SUBDIR_NAME = ".locks"
_CARD_FILENAME_EXTENSION = ".yaml"
_LOCK_FILENAME_EXTENSION = ".lock"


def normalize_object_family_name(name: str) -> str:
    """Normalize a documented object-family name to canonical casing.

    Inputs:
        `name`: A free-form object-family label taken from code or docs.
    Outputs:
        The canonical documented family name when the label is recognized,
        otherwise the stripped input string.
    Non-goals:
        This does not reject unknown names, validate schemas, or derive
        persistence paths.
    """

    normalized = " ".join(name.split()).lower()
    return _OBJECT_FAMILY_LOOKUP.get(normalized, name.strip())


def registry_subdir_names() -> tuple[str, ...]:
    """Return the canonical first-slice registry subdirectory names.

    Inputs:
        None.
    Outputs:
        A tuple of directory names frozen in `docs/registry_layout.md`.
    Non-goals:
        This does not create directories or inspect a registry tree.
    """

    return _REGISTRY_SUBDIR_NAMES


def history_subdir_name() -> str:
    """Return the canonical registry history root directory name.

    Inputs:
        None.
    Outputs:
        The single directory name used for append-only update snapshots.
    Non-goals:
        This does not create directories or inspect a registry tree.
    """

    return _HISTORY_SUBDIR_NAME


def lock_subdir_name() -> str:
    """Return the canonical registry lock-root directory name.

    Inputs:
        None.
    Outputs:
        The internal directory name used for mutation-time advisory lock files.
    Non-goals:
        This does not create directories or inspect a registry tree.
    """

    return _LOCKS_SUBDIR_NAME


def _card_filename(card_id: str) -> str:
    return f"{card_id}{_CARD_FILENAME_EXTENSION}"


def lock_filename(card_id: str) -> str:
    """Return the canonical filename for one mutation lock file.

    Inputs:
        `card_id`: The card identifier to embed in the filename stem.
    Outputs:
        The canonical filename `<card_id>.lock`.
    Non-goals:
        This does not validate or rewrite the identifier.
    """

    return f"{card_id}{_LOCK_FILENAME_EXTENSION}"


def study_card_filename(study_id: str) -> str:
    """Return the canonical first-slice filename for a `StudyCard`.

    Inputs:
        `study_id`: The card identifier to embed in the filename stem.
    Outputs:
        The canonical filename `<study_id>.yaml`.
    Non-goals:
        This does not validate or rewrite the identifier.
    """

    return _card_filename(study_id)


def dataset_card_filename(dataset_id: str) -> str:
    """Return the canonical first-slice filename for a `DatasetCard`.

    Inputs:
        `dataset_id`: The card identifier to embed in the filename stem.
    Outputs:
        The canonical filename `<dataset_id>.yaml`.
    Non-goals:
        This does not validate or rewrite the identifier.
    """

    return _card_filename(dataset_id)


def claim_card_filename(claim_id: str) -> str:
    """Return the canonical first-slice filename for a `ClaimCard`.

    Inputs:
        `claim_id`: The card identifier to embed in the filename stem.
    Outputs:
        The canonical filename `<claim_id>.yaml`.
    Non-goals:
        This does not validate or rewrite the identifier.
    """

    return _card_filename(claim_id)


def snapshot_filename(timestamp: datetime | None = None) -> str:
    """Return the canonical filename for one append-only update snapshot.

    Inputs:
        `timestamp`: optional UTC-aware timestamp. When omitted, the current UTC
        time is used.
    Outputs:
        A filesystem-safe filename in `YYYYMMDDTHHMMSSffffffZ.yaml` form.
    Non-goals:
        This does not ensure uniqueness on disk or create files.
    """

    current = datetime.now(timezone.utc) if timestamp is None else timestamp
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    else:
        current = current.astimezone(timezone.utc)
    return current.strftime("%Y%m%dT%H%M%S%fZ.yaml")


def list_reserved_cli_families() -> tuple[ReservedCLIFamilyName, ...]:
    """Return the reserved future CLI group names from the docs.

    Inputs:
        None.
    Outputs:
        A tuple of command-family labels reserved in `docs/api_specs.md`.
    Non-goals:
        This does not register CLI handlers or expose new user-facing commands.
    """

    return _RESERVED_CLI_FAMILIES


__all__ = [
    "claim_card_filename",
    "dataset_card_filename",
    "history_subdir_name",
    "lock_filename",
    "lock_subdir_name",
    "list_reserved_cli_families",
    "normalize_object_family_name",
    "registry_subdir_names",
    "snapshot_filename",
    "study_card_filename",
]
