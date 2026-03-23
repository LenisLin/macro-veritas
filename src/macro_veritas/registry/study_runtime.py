"""Internal StudyCard runtime helpers for the first real registry slice.

This module implements narrow, file-backed runtime behavior beneath
`macro_veritas.registry.gateway` for `StudyCard` only.

Responsibilities:
- resolve the canonical StudyCard filesystem path
- serialize and deserialize one StudyCard per YAML file
- apply minimal structural validation for stored and input payloads
- write one canonical card file at a time with a temp-file + fsync + replace flow
- delete one canonical StudyCard file by canonical ID

Non-goals:
- DatasetCard or ClaimCard runtime IO
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

from macro_veritas.registry.layout import study_card_path, study_cards_dir
from macro_veritas.registry.study import (
    allowed_screening_decisions,
    allowed_statuses,
    optional_fields,
    required_fields,
    storage_field_order,
)
from macro_veritas.shared.naming import study_card_filename
from macro_veritas.shared.types import StudyCardPayload

_OPTIONAL_STRING_FIELDS: tuple[str, ...] = (
    "screening_note",
    "source_artifact_locator",
)
_TERMINAL_STUDY_STATUS = "closed"


class StudyCardIdentifierError(ValueError):
    """Raised when a lookup ID is not safe for canonical StudyCard path resolution."""


class StudyCardFormatError(ValueError):
    """Raised when serialized or input StudyCard content is malformed."""


class StudyCardStateTransitionError(ValueError):
    """Raised when a StudyCard update requests an unsupported lifecycle change."""


def study_card_exists(registry_root: Path, study_id: str) -> bool:
    """Return whether the canonical StudyCard file exists."""

    return _study_card_file(registry_root, study_id).is_file()


def read_study_card(registry_root: Path, study_id: str) -> StudyCardPayload:
    """Read and validate one StudyCard from its canonical YAML path."""

    path = _study_card_file(registry_root, study_id)
    return _read_study_card_from_path(path)


def list_study_cards(registry_root: Path) -> tuple[StudyCardPayload, ...]:
    """List all StudyCards stored beneath the canonical StudyCard directory."""

    studies_dir = study_cards_dir(registry_root)
    if not studies_dir.exists():
        return ()
    if not studies_dir.is_dir():
        raise NotADirectoryError(f"StudyCard root is not a directory: {studies_dir}")

    cards: list[StudyCardPayload] = []
    for path in sorted(studies_dir.glob("*.yaml"), key=lambda item: item.name):
        if not path.is_file():
            continue
        cards.append(_read_study_card_from_path(path))
    return tuple(cards)


def normalize_study_card_payload(card: Mapping[str, object]) -> StudyCardPayload:
    """Validate and normalize one StudyCard mapping for storage or return."""

    if not isinstance(card, Mapping):
        raise StudyCardFormatError("StudyCard payload must be a mapping.")

    expected_fields = set(required_fields()) | set(optional_fields())
    actual_fields = set(card.keys())
    missing_fields = [field for field in required_fields() if field not in card]
    unexpected_fields = sorted(actual_fields - expected_fields)
    if missing_fields:
        raise StudyCardFormatError(
            "StudyCard payload is missing required fields: "
            + ", ".join(sorted(missing_fields))
        )
    if unexpected_fields:
        raise StudyCardFormatError(
            "StudyCard payload contains unexpected fields: "
            + ", ".join(unexpected_fields)
        )

    normalized: StudyCardPayload = {
        "study_id": _normalize_study_id_from_payload(card["study_id"]),
        "citation_handle": _require_string(card, "citation_handle"),
        "tumor_scope_tags": _require_string_list(card, "tumor_scope_tags"),
        "therapy_scope_tags": _require_string_list(card, "therapy_scope_tags"),
        "relevance_scope_tags": _require_string_list(card, "relevance_scope_tags"),
        "screening_decision": _require_allowed_string(
            card,
            "screening_decision",
            allowed_screening_decisions(),
        ),
        "status": _require_allowed_string(card, "status", allowed_statuses()),
        "created_from_note": _require_string(card, "created_from_note"),
    }
    for field_name in _OPTIONAL_STRING_FIELDS:
        if field_name in card:
            normalized[field_name] = _require_string(card, field_name)

    return normalized


def serialize_study_card(card: Mapping[str, object]) -> str:
    """Serialize one validated StudyCard to YAML."""

    normalized = normalize_study_card_payload(card)
    ordered_mapping = {
        field_name: normalized[field_name]
        for field_name in storage_field_order()
        if field_name in normalized
    }
    return yaml.safe_dump(ordered_mapping, sort_keys=False)


def deserialize_study_card(document: str, *, source_path: Path | None = None) -> StudyCardPayload:
    """Deserialize one YAML document into a validated StudyCard payload."""

    try:
        parsed = yaml.safe_load(document)
    except yaml.YAMLError as exc:
        if source_path is None:
            raise StudyCardFormatError("StudyCard YAML could not be parsed.") from exc
        raise StudyCardFormatError(
            f"StudyCard YAML could not be parsed at {source_path}."
        ) from exc

    if not isinstance(parsed, Mapping):
        if source_path is None:
            raise StudyCardFormatError("StudyCard YAML must decode to one mapping.")
        raise StudyCardFormatError(
            f"StudyCard YAML must decode to one mapping at {source_path}."
        )

    return normalize_study_card_payload(parsed)


def create_study_card(registry_root: Path, card: Mapping[str, object]) -> StudyCardPayload:
    """Create one StudyCard at its canonical YAML location."""

    normalized = normalize_study_card_payload(card)
    path = study_card_path(registry_root, normalized["study_id"])
    if path.exists():
        raise FileExistsError(str(path))

    _write_study_card_file(path, normalized)
    return normalized


def ensure_study_card_update_allowed(
    current_card: Mapping[str, object],
    replacement_card: Mapping[str, object],
) -> None:
    """Validate the narrow status-transition rule for StudyCard replacement."""

    current_status = _require_allowed_string(current_card, "status", allowed_statuses())
    replacement_status = _require_allowed_string(
        replacement_card,
        "status",
        allowed_statuses(),
    )
    if current_status == _TERMINAL_STUDY_STATUS and replacement_status != _TERMINAL_STUDY_STATUS:
        raise StudyCardStateTransitionError(
            "StudyCard status 'closed' is terminal and cannot transition back to an "
            "active status."
        )


def update_study_card(registry_root: Path, card: Mapping[str, object]) -> StudyCardPayload:
    """Replace one existing StudyCard at its canonical YAML location."""

    normalized = normalize_study_card_payload(card)
    path = study_card_path(registry_root, normalized["study_id"])
    current_card = _read_study_card_from_path(path)
    ensure_study_card_update_allowed(current_card, normalized)
    _write_study_card_file(path, normalized)
    return normalized


def delete_study_card(registry_root: Path, study_id: str) -> None:
    """Delete one StudyCard from its canonical YAML location."""

    path = _study_card_file(registry_root, study_id)
    path.unlink()
    _fsync_directory(path.parent)


def _study_card_file(registry_root: Path, study_id: str) -> Path:
    return study_card_path(registry_root, _normalize_lookup_study_id(study_id))


def _normalize_lookup_study_id(study_id: str) -> str:
    if not isinstance(study_id, str):
        raise StudyCardIdentifierError("StudyCard lookup ID must be a string.")

    normalized = study_id.strip()
    if not normalized:
        raise StudyCardIdentifierError("StudyCard lookup ID must not be empty.")
    if normalized != study_id:
        raise StudyCardIdentifierError(
            "StudyCard lookup ID must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise StudyCardIdentifierError(
            "StudyCard lookup ID must be a single canonical identifier, not a path."
        )
    if "\x00" in normalized:
        raise StudyCardIdentifierError("StudyCard lookup ID must not contain NUL bytes.")
    return normalized


def _normalize_study_id_from_payload(value: object) -> str:
    if not isinstance(value, str):
        raise StudyCardFormatError("StudyCard field 'study_id' must be a string.")

    normalized = value.strip()
    if not normalized:
        raise StudyCardFormatError("StudyCard field 'study_id' must not be empty.")
    if normalized != value:
        raise StudyCardFormatError(
            "StudyCard field 'study_id' must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise StudyCardFormatError(
            "StudyCard field 'study_id' must be a canonical identifier, not a path."
        )
    if "\x00" in normalized:
        raise StudyCardFormatError("StudyCard field 'study_id' must not contain NUL bytes.")
    return normalized


def _require_string(card: Mapping[str, object], field_name: str) -> str:
    value = card[field_name]
    if not isinstance(value, str):
        raise StudyCardFormatError(f"StudyCard field '{field_name}' must be a string.")
    return value


def _require_string_list(card: Mapping[str, object], field_name: str) -> list[str]:
    value = card[field_name]
    if not isinstance(value, (list, tuple)):
        raise StudyCardFormatError(
            f"StudyCard field '{field_name}' must be a list or tuple of strings."
        )
    normalized_items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise StudyCardFormatError(
                f"StudyCard field '{field_name}' must contain only strings."
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
        raise StudyCardFormatError(
            f"StudyCard field '{field_name}' must be one of: {allowed_display}."
        )
    return value


def _read_study_card_from_path(path: Path) -> StudyCardPayload:
    document = path.read_text(encoding="utf-8")
    card = deserialize_study_card(document, source_path=path)
    expected_name = study_card_filename(card["study_id"])
    if path.name != expected_name:
        raise StudyCardFormatError(
            f"StudyCard file name {path.name} does not match study_id {card['study_id']}."
        )
    return card


def _write_study_card_file(path: Path, card: Mapping[str, object]) -> None:
    serialized = serialize_study_card(card)
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
    "StudyCardFormatError",
    "StudyCardIdentifierError",
    "StudyCardStateTransitionError",
    "create_study_card",
    "delete_study_card",
    "deserialize_study_card",
    "ensure_study_card_update_allowed",
    "list_study_cards",
    "normalize_study_card_payload",
    "read_study_card",
    "serialize_study_card",
    "study_card_exists",
    "update_study_card",
]
