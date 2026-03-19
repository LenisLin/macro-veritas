"""Internal DatasetCard runtime helpers for the second real registry slice.

This module implements narrow, file-backed runtime behavior beneath
`macro_veritas.registry.gateway` for `DatasetCard` only.

Responsibilities:
- resolve the canonical DatasetCard filesystem path
- serialize and deserialize one DatasetCard per YAML file
- apply minimal structural validation for stored and input payloads
- write one canonical card file at a time with a temp-file + fsync + replace flow

Non-goals:
- StudyCard referential-integrity checks (owned by the gateway boundary)
- ClaimCard runtime IO
- CLI exposure
- scientific logic or evidence grading
- multi-card transactions or locking
"""

from __future__ import annotations

from collections.abc import Mapping
import os
import tempfile
from pathlib import Path

import yaml

from macro_veritas.registry.dataset import (
    allowed_availability_statuses,
    allowed_statuses,
    optional_fields,
    required_fields,
    storage_field_order,
)
from macro_veritas.registry.layout import dataset_card_path, dataset_cards_dir
from macro_veritas.shared.naming import dataset_card_filename
from macro_veritas.shared.types import DatasetCardPayload

_OPTIONAL_STRING_FIELDS: tuple[str, ...] = (
    "accession_id",
    "artifact_locator",
    "availability_note",
)


class DatasetCardIdentifierError(ValueError):
    """Raised when a lookup ID is not safe for canonical DatasetCard path resolution."""


class DatasetCardFormatError(ValueError):
    """Raised when serialized or input DatasetCard content is malformed."""


def dataset_card_exists(registry_root: Path, dataset_id: str) -> bool:
    """Return whether the canonical DatasetCard file exists."""

    return _dataset_card_file(registry_root, dataset_id).is_file()


def read_dataset_card(registry_root: Path, dataset_id: str) -> DatasetCardPayload:
    """Read and validate one DatasetCard from its canonical YAML path."""

    path = _dataset_card_file(registry_root, dataset_id)
    return _read_dataset_card_from_path(path)


def list_dataset_cards(registry_root: Path) -> tuple[DatasetCardPayload, ...]:
    """List all DatasetCards stored beneath the canonical DatasetCard directory."""

    datasets_dir = dataset_cards_dir(registry_root)
    if not datasets_dir.exists():
        return ()
    if not datasets_dir.is_dir():
        raise NotADirectoryError(f"DatasetCard root is not a directory: {datasets_dir}")

    cards: list[DatasetCardPayload] = []
    for path in sorted(datasets_dir.glob("*.yaml"), key=lambda item: item.name):
        if not path.is_file():
            continue
        cards.append(_read_dataset_card_from_path(path))
    return tuple(cards)


def normalize_dataset_card_payload(card: Mapping[str, object]) -> DatasetCardPayload:
    """Validate and normalize one DatasetCard mapping for storage or return."""

    if not isinstance(card, Mapping):
        raise DatasetCardFormatError("DatasetCard payload must be a mapping.")

    expected_fields = set(required_fields()) | set(optional_fields())
    actual_fields = set(card.keys())
    missing_fields = [field for field in required_fields() if field not in card]
    unexpected_fields = sorted(actual_fields - expected_fields)
    if missing_fields:
        raise DatasetCardFormatError(
            "DatasetCard payload is missing required fields: "
            + ", ".join(sorted(missing_fields))
        )
    if unexpected_fields:
        raise DatasetCardFormatError(
            "DatasetCard payload contains unexpected fields: "
            + ", ".join(unexpected_fields)
        )

    normalized: DatasetCardPayload = {
        "dataset_id": _normalize_dataset_id_from_payload(card["dataset_id"]),
        "study_id": _normalize_study_reference_id_from_payload(card["study_id"]),
        "source_locator": _require_string(card, "source_locator"),
        "availability_status": _require_allowed_string(
            card,
            "availability_status",
            allowed_availability_statuses(),
        ),
        "modality_scope_tags": _require_string_list(card, "modality_scope_tags"),
        "cohort_summary": _require_string(card, "cohort_summary"),
        "platform_summary": _require_string(card, "platform_summary"),
        "status": _require_allowed_string(card, "status", allowed_statuses()),
        "locator_confidence_note": _require_string(card, "locator_confidence_note"),
    }
    for field_name in _OPTIONAL_STRING_FIELDS:
        if field_name in card:
            normalized[field_name] = _require_string(card, field_name)

    return normalized


def serialize_dataset_card(card: Mapping[str, object]) -> str:
    """Serialize one validated DatasetCard to YAML."""

    normalized = normalize_dataset_card_payload(card)
    ordered_mapping = {
        field_name: normalized[field_name]
        for field_name in storage_field_order()
        if field_name in normalized
    }
    return yaml.safe_dump(ordered_mapping, sort_keys=False)


def deserialize_dataset_card(
    document: str,
    *,
    source_path: Path | None = None,
) -> DatasetCardPayload:
    """Deserialize one YAML document into a validated DatasetCard payload."""

    try:
        parsed = yaml.safe_load(document)
    except yaml.YAMLError as exc:
        if source_path is None:
            raise DatasetCardFormatError("DatasetCard YAML could not be parsed.") from exc
        raise DatasetCardFormatError(
            f"DatasetCard YAML could not be parsed at {source_path}."
        ) from exc

    if not isinstance(parsed, Mapping):
        if source_path is None:
            raise DatasetCardFormatError("DatasetCard YAML must decode to one mapping.")
        raise DatasetCardFormatError(
            f"DatasetCard YAML must decode to one mapping at {source_path}."
        )

    return normalize_dataset_card_payload(parsed)


def create_dataset_card(registry_root: Path, card: Mapping[str, object]) -> DatasetCardPayload:
    """Create one DatasetCard at its canonical YAML location."""

    normalized = normalize_dataset_card_payload(card)
    path = dataset_card_path(registry_root, normalized["dataset_id"])
    if path.exists():
        raise FileExistsError(str(path))

    _write_dataset_card_file(path, normalized)
    return normalized


def update_dataset_card(registry_root: Path, card: Mapping[str, object]) -> DatasetCardPayload:
    """Replace one existing DatasetCard at its canonical YAML location."""

    normalized = normalize_dataset_card_payload(card)
    path = dataset_card_path(registry_root, normalized["dataset_id"])
    _read_dataset_card_from_path(path)
    _write_dataset_card_file(path, normalized)
    return normalized


def _dataset_card_file(registry_root: Path, dataset_id: str) -> Path:
    return dataset_card_path(registry_root, _normalize_lookup_dataset_id(dataset_id))


def _normalize_lookup_dataset_id(dataset_id: str) -> str:
    if not isinstance(dataset_id, str):
        raise DatasetCardIdentifierError("DatasetCard lookup ID must be a string.")

    normalized = dataset_id.strip()
    if not normalized:
        raise DatasetCardIdentifierError("DatasetCard lookup ID must not be empty.")
    if normalized != dataset_id:
        raise DatasetCardIdentifierError(
            "DatasetCard lookup ID must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise DatasetCardIdentifierError(
            "DatasetCard lookup ID must be a single canonical identifier, not a path."
        )
    if "\x00" in normalized:
        raise DatasetCardIdentifierError("DatasetCard lookup ID must not contain NUL bytes.")
    return normalized


def _normalize_dataset_id_from_payload(value: object) -> str:
    if not isinstance(value, str):
        raise DatasetCardFormatError("DatasetCard field 'dataset_id' must be a string.")

    normalized = value.strip()
    if not normalized:
        raise DatasetCardFormatError("DatasetCard field 'dataset_id' must not be empty.")
    if normalized != value:
        raise DatasetCardFormatError(
            "DatasetCard field 'dataset_id' must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise DatasetCardFormatError(
            "DatasetCard field 'dataset_id' must be a canonical identifier, not a path."
        )
    if "\x00" in normalized:
        raise DatasetCardFormatError("DatasetCard field 'dataset_id' must not contain NUL bytes.")
    return normalized


def _normalize_study_reference_id_from_payload(value: object) -> str:
    if not isinstance(value, str):
        raise DatasetCardFormatError("DatasetCard field 'study_id' must be a string.")

    normalized = value.strip()
    if not normalized:
        raise DatasetCardFormatError("DatasetCard field 'study_id' must not be empty.")
    if normalized != value:
        raise DatasetCardFormatError(
            "DatasetCard field 'study_id' must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise DatasetCardFormatError(
            "DatasetCard field 'study_id' must be a canonical identifier, not a path."
        )
    if "\x00" in normalized:
        raise DatasetCardFormatError("DatasetCard field 'study_id' must not contain NUL bytes.")
    return normalized


def _require_string(card: Mapping[str, object], field_name: str) -> str:
    value = card[field_name]
    if not isinstance(value, str):
        raise DatasetCardFormatError(f"DatasetCard field '{field_name}' must be a string.")
    return value


def _require_string_list(card: Mapping[str, object], field_name: str) -> list[str]:
    value = card[field_name]
    if not isinstance(value, (list, tuple)):
        raise DatasetCardFormatError(
            f"DatasetCard field '{field_name}' must be a list or tuple of strings."
        )
    normalized_items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise DatasetCardFormatError(
                f"DatasetCard field '{field_name}' must contain only strings."
            )
        normalized_items.append(item)
    return normalized_items


def _require_allowed_string(
    card: Mapping[str, object],
    field_name: str,
    allowed_values: tuple[str, ...],
) -> str:
    value = _require_string(card, field_name)
    if value not in allowed_values:
        allowed_display = ", ".join(allowed_values)
        raise DatasetCardFormatError(
            f"DatasetCard field '{field_name}' must be one of: {allowed_display}."
        )
    return value


def _read_dataset_card_from_path(path: Path) -> DatasetCardPayload:
    document = path.read_text(encoding="utf-8")
    card = deserialize_dataset_card(document, source_path=path)
    expected_name = dataset_card_filename(card["dataset_id"])
    if path.name != expected_name:
        raise DatasetCardFormatError(
            f"DatasetCard file name {path.name} does not match dataset_id {card['dataset_id']}."
        )
    return card


def _write_dataset_card_file(path: Path, card: Mapping[str, object]) -> None:
    serialized = serialize_dataset_card(card)
    path.parent.mkdir(parents=True, exist_ok=True)

    file_descriptor, temp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        _fsync_directory(path.parent)
    except Exception:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY

    directory_fd = os.open(directory, flags)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


__all__ = [
    "DatasetCardFormatError",
    "DatasetCardIdentifierError",
    "create_dataset_card",
    "dataset_card_exists",
    "deserialize_dataset_card",
    "list_dataset_cards",
    "normalize_dataset_card_payload",
    "read_dataset_card",
    "serialize_dataset_card",
    "update_dataset_card",
]
