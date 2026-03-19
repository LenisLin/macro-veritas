from __future__ import annotations

from typing import get_args

from macro_veritas.registry import claim, dataset, study
from macro_veritas.shared import types as shared_types

FIRST_SLICE_CONTRACT_VERSION = "2026-03-first-slice"


def test_shared_status_literals_match_frozen_card_contracts() -> None:
    assert get_args(shared_types.StudyCardStatus) == ("draft", "registered", "closed")
    assert get_args(shared_types.DatasetCardStatus) == (
        "identified",
        "registered",
        "bound",
        "retired",
    )
    assert get_args(shared_types.ClaimCardStatus) == ("captured", "scoped", "ready", "closed")
    assert get_args(shared_types.DatasetAvailabilityStatus) == (
        "unknown",
        "open",
        "restricted",
        "unavailable",
    )


def test_study_card_contract_metadata() -> None:
    assert study.contract_version() == FIRST_SLICE_CONTRACT_VERSION
    assert study.required_fields() == (
        "study_id",
        "citation_handle",
        "tumor_scope_tags",
        "therapy_scope_tags",
        "relevance_scope_tags",
        "screening_decision",
        "status",
        "created_from_note",
    )
    assert study.optional_fields() == (
        "screening_note",
        "source_artifact_locator",
    )
    assert study.allowed_screening_decisions() == ("pending", "include", "exclude")
    assert study.allowed_statuses() == ("draft", "registered", "closed")
    assert study.list_lifecycle_states() == study.allowed_statuses()
    assert study.storage_field_order() == (
        "study_id",
        "citation_handle",
        "tumor_scope_tags",
        "therapy_scope_tags",
        "relevance_scope_tags",
        "screening_decision",
        "status",
        "created_from_note",
        "screening_note",
        "source_artifact_locator",
    )
    assert study.relationship_pointers() == {
        "inbound_from": ("DatasetCard.study_id", "ClaimCard.study_id")
    }


def test_dataset_card_contract_metadata() -> None:
    assert dataset.contract_version() == FIRST_SLICE_CONTRACT_VERSION
    assert dataset.required_fields() == (
        "dataset_id",
        "study_id",
        "source_locator",
        "availability_status",
        "modality_scope_tags",
        "cohort_summary",
        "platform_summary",
        "status",
        "locator_confidence_note",
    )
    assert dataset.optional_fields() == (
        "accession_id",
        "artifact_locator",
        "availability_note",
    )
    assert dataset.allowed_availability_statuses() == (
        "unknown",
        "open",
        "restricted",
        "unavailable",
    )
    assert dataset.allowed_statuses() == ("identified", "registered", "bound", "retired")
    assert dataset.list_lifecycle_states() == dataset.allowed_statuses()
    assert dataset.storage_field_order() == (
        "dataset_id",
        "study_id",
        "source_locator",
        "availability_status",
        "modality_scope_tags",
        "cohort_summary",
        "platform_summary",
        "status",
        "locator_confidence_note",
        "accession_id",
        "artifact_locator",
        "availability_note",
    )
    assert dataset.relationship_pointers() == {
        "study_id": ("StudyCard.study_id",),
    }


def test_claim_card_contract_metadata() -> None:
    assert claim.contract_version() == FIRST_SLICE_CONTRACT_VERSION
    assert claim.required_fields() == (
        "claim_id",
        "study_id",
        "claim_text",
        "claim_type",
        "provenance_pointer",
        "status",
        "review_readiness",
        "created_from_note",
    )
    assert claim.optional_fields() == (
        "dataset_ids",
        "claim_summary_handle",
    )
    assert claim.allowed_statuses() == ("captured", "scoped", "ready", "closed")
    assert claim.list_lifecycle_states() == claim.allowed_statuses()
    assert claim.relationship_pointers() == {
        "study_id": ("StudyCard.study_id",),
        "dataset_ids": ("DatasetCard.dataset_id",),
    }
