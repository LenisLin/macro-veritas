"""Internal ClaimCard runtime helpers for the third real registry slice.

This module implements narrow, file-backed runtime behavior beneath
`macro_veritas.registry.gateway` for `ClaimCard` only.

Responsibilities:
- resolve the canonical ClaimCard filesystem path
- serialize and deserialize one ClaimCard per YAML file
- apply minimal structural validation for stored and input payloads
- write one canonical card file at a time with a temp-file + fsync + replace flow
- delete one canonical ClaimCard file by canonical ID

Non-goals:
- StudyCard or DatasetCard referential-integrity checks
- CLI exposure
- scientific logic or evidence grading
- multi-card transactions or locking
"""

from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path
import tempfile

import yaml

from macro_veritas.registry.claim import (
    allowed_review_readiness,
    allowed_statuses,
    optional_fields,
    required_fields,
    storage_field_order,
)
from macro_veritas.registry.layout import claim_card_path, claim_cards_dir
from macro_veritas.shared.naming import claim_card_filename
from macro_veritas.shared.types import ClaimCardPayload

_OPTIONAL_STRING_FIELDS: tuple[str, ...] = ("claim_summary_handle",)


class ClaimCardIdentifierError(ValueError):
    """Raised when a lookup ID is not safe for canonical ClaimCard path resolution."""


class ClaimCardFormatError(ValueError):
    """Raised when serialized or input ClaimCard content is malformed."""


def claim_card_exists(registry_root: Path, claim_id: str) -> bool:
    """Return whether the canonical ClaimCard file exists."""

    return _claim_card_file(registry_root, claim_id).is_file()


def read_claim_card(registry_root: Path, claim_id: str) -> ClaimCardPayload:
    """Read and validate one ClaimCard from its canonical YAML path."""

    path = _claim_card_file(registry_root, claim_id)
    return _read_claim_card_from_path(path)


def list_claim_cards(registry_root: Path) -> tuple[ClaimCardPayload, ...]:
    """List all ClaimCards stored beneath the canonical ClaimCard directory."""

    claims_dir = claim_cards_dir(registry_root)
    if not claims_dir.exists():
        return ()
    if not claims_dir.is_dir():
        raise NotADirectoryError(f"ClaimCard root is not a directory: {claims_dir}")

    cards: list[ClaimCardPayload] = []
    for path in sorted(claims_dir.glob("*.yaml"), key=lambda item: item.name):
        if not path.is_file():
            continue
        cards.append(_read_claim_card_from_path(path))
    return tuple(cards)


def normalize_claim_card_payload(card: Mapping[str, object]) -> ClaimCardPayload:
    """Validate and normalize one ClaimCard mapping for storage or return."""

    if not isinstance(card, Mapping):
        raise ClaimCardFormatError("ClaimCard payload must be a mapping.")

    expected_fields = set(required_fields()) | set(optional_fields())
    actual_fields = set(card.keys())
    missing_fields = [field for field in required_fields() if field not in card]
    unexpected_fields = sorted(actual_fields - expected_fields)
    if missing_fields:
        raise ClaimCardFormatError(
            "ClaimCard payload is missing required fields: "
            + ", ".join(sorted(missing_fields))
        )
    if unexpected_fields:
        raise ClaimCardFormatError(
            "ClaimCard payload contains unexpected fields: "
            + ", ".join(unexpected_fields)
        )

    normalized: ClaimCardPayload = {
        "claim_id": _normalize_claim_id_from_payload(card["claim_id"]),
        "study_id": _normalize_study_reference_id_from_payload(card["study_id"]),
        "claim_text": _require_string(card, "claim_text"),
        "claim_type": _require_string(card, "claim_type"),
        "provenance_pointer": _require_string(card, "provenance_pointer"),
        "status": _require_allowed_string(card, "status", allowed_statuses()),
        "review_readiness": _require_allowed_string(
            card,
            "review_readiness",
            allowed_review_readiness(),
        ),
        "created_from_note": _require_string(card, "created_from_note"),
    }
    if "dataset_ids" in card:
        normalized["dataset_ids"] = _require_dataset_reference_ids(card, "dataset_ids")
    for field_name in _OPTIONAL_STRING_FIELDS:
        if field_name in card:
            normalized[field_name] = _require_string(card, field_name)

    return normalized


def serialize_claim_card(card: Mapping[str, object]) -> str:
    """Serialize one validated ClaimCard to YAML."""

    normalized = normalize_claim_card_payload(card)
    ordered_mapping = {
        field_name: normalized[field_name]
        for field_name in storage_field_order()
        if field_name in normalized
    }
    return yaml.safe_dump(ordered_mapping, sort_keys=False)


def deserialize_claim_card(document: str, *, source_path: Path | None = None) -> ClaimCardPayload:
    """Deserialize one YAML document into a validated ClaimCard payload."""

    try:
        parsed = yaml.safe_load(document)
    except yaml.YAMLError as exc:
        if source_path is None:
            raise ClaimCardFormatError("ClaimCard YAML could not be parsed.") from exc
        raise ClaimCardFormatError(
            f"ClaimCard YAML could not be parsed at {source_path}."
        ) from exc

    if not isinstance(parsed, Mapping):
        if source_path is None:
            raise ClaimCardFormatError("ClaimCard YAML must decode to one mapping.")
        raise ClaimCardFormatError(
            f"ClaimCard YAML must decode to one mapping at {source_path}."
        )

    return normalize_claim_card_payload(parsed)


def create_claim_card(registry_root: Path, card: Mapping[str, object]) -> ClaimCardPayload:
    """Create one ClaimCard at its canonical YAML location."""

    normalized = normalize_claim_card_payload(card)
    path = claim_card_path(registry_root, normalized["claim_id"])
    if path.exists():
        raise FileExistsError(str(path))

    _write_claim_card_file(path, normalized)
    return normalized


def update_claim_card(registry_root: Path, card: Mapping[str, object]) -> ClaimCardPayload:
    """Replace one existing ClaimCard at its canonical YAML location."""

    normalized = normalize_claim_card_payload(card)
    path = claim_card_path(registry_root, normalized["claim_id"])
    _read_claim_card_from_path(path)
    _write_claim_card_file(path, normalized)
    return normalized


def delete_claim_card(registry_root: Path, claim_id: str) -> None:
    """Delete one ClaimCard from its canonical YAML location."""

    path = _claim_card_file(registry_root, claim_id)
    path.unlink()
    _fsync_directory(path.parent)


def _claim_card_file(registry_root: Path, claim_id: str) -> Path:
    return claim_card_path(registry_root, _normalize_lookup_claim_id(claim_id))


def _normalize_lookup_claim_id(claim_id: str) -> str:
    if not isinstance(claim_id, str):
        raise ClaimCardIdentifierError("ClaimCard lookup ID must be a string.")

    normalized = claim_id.strip()
    if not normalized:
        raise ClaimCardIdentifierError("ClaimCard lookup ID must not be empty.")
    if normalized != claim_id:
        raise ClaimCardIdentifierError(
            "ClaimCard lookup ID must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise ClaimCardIdentifierError(
            "ClaimCard lookup ID must be a single canonical identifier, not a path."
        )
    if "\x00" in normalized:
        raise ClaimCardIdentifierError("ClaimCard lookup ID must not contain NUL bytes.")
    return normalized


def _normalize_claim_id_from_payload(value: object) -> str:
    if not isinstance(value, str):
        raise ClaimCardFormatError("ClaimCard field 'claim_id' must be a string.")

    normalized = value.strip()
    if not normalized:
        raise ClaimCardFormatError("ClaimCard field 'claim_id' must not be empty.")
    if normalized != value:
        raise ClaimCardFormatError(
            "ClaimCard field 'claim_id' must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise ClaimCardFormatError(
            "ClaimCard field 'claim_id' must be a canonical identifier, not a path."
        )
    if "\x00" in normalized:
        raise ClaimCardFormatError("ClaimCard field 'claim_id' must not contain NUL bytes.")
    return normalized


def _normalize_study_reference_id_from_payload(value: object) -> str:
    if not isinstance(value, str):
        raise ClaimCardFormatError("ClaimCard field 'study_id' must be a string.")

    normalized = value.strip()
    if not normalized:
        raise ClaimCardFormatError("ClaimCard field 'study_id' must not be empty.")
    if normalized != value:
        raise ClaimCardFormatError(
            "ClaimCard field 'study_id' must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise ClaimCardFormatError(
            "ClaimCard field 'study_id' must be a canonical identifier, not a path."
        )
    if "\x00" in normalized:
        raise ClaimCardFormatError("ClaimCard field 'study_id' must not contain NUL bytes.")
    return normalized


def _normalize_dataset_reference_id_from_payload(value: object) -> str:
    if not isinstance(value, str):
        raise ClaimCardFormatError("ClaimCard field 'dataset_ids' must contain only strings.")

    normalized = value.strip()
    if not normalized:
        raise ClaimCardFormatError("ClaimCard field 'dataset_ids' entries must not be empty.")
    if normalized != value:
        raise ClaimCardFormatError(
            "ClaimCard field 'dataset_ids' entries must not contain surrounding whitespace."
        )
    if "/" in normalized or "\\" in normalized or normalized in {".", ".."}:
        raise ClaimCardFormatError(
            "ClaimCard field 'dataset_ids' entries must be canonical identifiers, not paths."
        )
    if "\x00" in normalized:
        raise ClaimCardFormatError(
            "ClaimCard field 'dataset_ids' entries must not contain NUL bytes."
        )
    return normalized


def _require_string(card: Mapping[str, object], field_name: str) -> str:
    value = card[field_name]
    if not isinstance(value, str):
        raise ClaimCardFormatError(f"ClaimCard field '{field_name}' must be a string.")
    return value


def _require_dataset_reference_ids(card: Mapping[str, object], field_name: str) -> list[str]:
    value = card[field_name]
    if not isinstance(value, (list, tuple)):
        raise ClaimCardFormatError(
            "ClaimCard field 'dataset_ids' must be a list or tuple of strings."
        )
    return [_normalize_dataset_reference_id_from_payload(item) for item in value]


def _require_allowed_string(
    card: Mapping[str, object],
    field_name: str,
    allowed_values: tuple[str, ...],
) -> str:
    value = _require_string(card, field_name)
    if value not in allowed_values:
        allowed_display = ", ".join(allowed_values)
        raise ClaimCardFormatError(
            f"ClaimCard field '{field_name}' must be one of: {allowed_display}."
        )
    return value


def _read_claim_card_from_path(path: Path) -> ClaimCardPayload:
    document = path.read_text(encoding="utf-8")
    card = deserialize_claim_card(document, source_path=path)
    expected_name = claim_card_filename(card["claim_id"])
    if path.name != expected_name:
        raise ClaimCardFormatError(
            f"ClaimCard file name {path.name} does not match claim_id {card['claim_id']}."
        )
    return card


def _write_claim_card_file(path: Path, card: Mapping[str, object]) -> None:
    serialized = serialize_claim_card(card)
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
    "ClaimCardFormatError",
    "ClaimCardIdentifierError",
    "claim_card_exists",
    "create_claim_card",
    "delete_claim_card",
    "deserialize_claim_card",
    "list_claim_cards",
    "normalize_claim_card_payload",
    "read_claim_card",
    "serialize_claim_card",
    "update_claim_card",
]
