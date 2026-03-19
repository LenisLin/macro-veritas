from __future__ import annotations

from typing import get_args

from macro_veritas.commands import audit, bind, extract, grade, ingest, review, run
from macro_veritas.shared import types as shared_types


def test_first_slice_payload_literals_are_frozen() -> None:
    assert get_args(shared_types.StudyScreeningDecision) == (
        "pending",
        "include",
        "exclude",
    )
    assert get_args(shared_types.DatasetAvailabilityStatus) == (
        "unknown",
        "open",
        "restricted",
        "unavailable",
    )
    assert get_args(shared_types.ClaimReviewReadiness) == (
        "needs_scope",
        "reviewable",
        "execution_candidate",
    )
    assert get_args(shared_types.MutationInputRequirement) == ("full_card_payload",)


def test_first_slice_payload_typed_dict_keys_are_frozen() -> None:
    assert shared_types.StudyCardPayload.__required_keys__ == {
        "study_id",
        "citation_handle",
        "tumor_scope_tags",
        "therapy_scope_tags",
        "relevance_scope_tags",
        "screening_decision",
        "status",
        "created_from_note",
    }
    assert shared_types.StudyCardPayload.__optional_keys__ == {
        "screening_note",
        "source_artifact_locator",
    }

    assert shared_types.DatasetCardPayload.__required_keys__ == {
        "dataset_id",
        "study_id",
        "source_locator",
        "availability_status",
        "modality_scope_tags",
        "cohort_summary",
        "platform_summary",
        "status",
        "locator_confidence_note",
    }
    assert shared_types.DatasetCardPayload.__optional_keys__ == {
        "accession_id",
        "artifact_locator",
        "availability_note",
    }

    assert shared_types.ClaimCardPayload.__required_keys__ == {
        "claim_id",
        "study_id",
        "claim_text",
        "claim_type",
        "provenance_pointer",
        "status",
        "review_readiness",
        "created_from_note",
    }
    assert shared_types.ClaimCardPayload.__optional_keys__ == {
        "dataset_ids",
        "claim_summary_handle",
    }


def test_command_payload_touchpoints_match_mvp_scope() -> None:
    assert [item["usage"] for item in ingest.describe_payload_contracts()] == [
        "prepare_create",
        "prepare_create",
        "prepare_create",
    ]
    assert [item["usage"] for item in bind.describe_payload_contracts()] == [
        "prepare_update",
        "prepare_update",
        "prepare_update",
    ]
    assert [item["usage"] for item in extract.describe_payload_contracts()] == [
        "prepare_update",
        "prepare_update",
        "prepare_create_or_update",
    ]

    for module in (audit, review, run, grade):
        assert all(
            item["usage"] == "read_only" for item in module.describe_payload_contracts()
        )
