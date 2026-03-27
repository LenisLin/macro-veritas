from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from macro_veritas.registry import gateway, locks as registry_locks
from macro_veritas.registry.errors import RegistryError, UpdateLockError
from macro_veritas.registry.gateway import (
    create_claim_card,
    create_dataset_card,
    create_study_card,
    get_claim_card,
)
from macro_veritas.registry.layout import (
    claim_card_path,
    claim_lock_path,
    dataset_lock_path,
    study_lock_path,
)

_HOLD_LOCK_SCRIPT = textwrap.dedent(
    """
    import fcntl
    import os
    from pathlib import Path
    import sys

    lock_path = Path(sys.argv[1])
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    handle = os.fdopen(file_descriptor, "r+", encoding="utf-8")
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    print("locked", flush=True)
    try:
        sys.stdin.read()
    finally:
        handle.close()
    """
)

_PROBE_LOCK_SCRIPT = textwrap.dedent(
    """
    import fcntl
    import os
    from pathlib import Path
    import sys

    lock_path = Path(sys.argv[1])
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    handle = os.fdopen(file_descriptor, "r+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        sys.exit(1)
    handle.close()
    sys.exit(0)
    """
)


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


def _study_card(study_id: str = "study-001") -> dict[str, object]:
    return {
        "study_id": study_id,
        "citation_handle": f"doi:{study_id}",
        "tumor_scope_tags": ["glioma"],
        "therapy_scope_tags": ["immunotherapy"],
        "relevance_scope_tags": ["preclinical"],
        "screening_decision": "include",
        "status": "registered",
        "created_from_note": "seeded in claim ingest lock test",
    }


def _dataset_card(dataset_id: str, *, study_id: str = "study-001") -> dict[str, object]:
    return {
        "dataset_id": dataset_id,
        "study_id": study_id,
        "source_locator": f"https://example.org/{dataset_id}",
        "availability_status": "open",
        "modality_scope_tags": ["rna-seq"],
        "cohort_summary": "adult cohort",
        "platform_summary": "Illumina",
        "status": "registered",
        "locator_confidence_note": "confirmed in supplement",
    }


def _claim_card(
    claim_id: str = "claim-001",
    *,
    study_id: str = "study-001",
    dataset_ids: list[str] | None = None,
) -> dict[str, object]:
    card: dict[str, object] = {
        "claim_id": claim_id,
        "study_id": study_id,
        "claim_text": f"Claim text for {claim_id}",
        "claim_type": "association",
        "provenance_pointer": "figure-2",
        "status": "captured",
        "review_readiness": "needs_scope",
        "created_from_note": "seeded in claim ingest lock test",
    }
    if dataset_ids is not None:
        card["dataset_ids"] = dataset_ids
    return card


@pytest.fixture
def configured_registry_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config_path = tmp_path / "project.yaml"
    data_root = tmp_path / "macro_data"
    _write_config(config_path, data_root)
    monkeypatch.setenv("MACRO_VERITAS_CONFIG", str(config_path))
    return data_root.resolve() / "registry"


def _probe_lock(lock_path: Path) -> int:
    result = subprocess.run(
        [sys.executable, "-c", _PROBE_LOCK_SCRIPT, str(lock_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode


def _start_lock_holder(lock_path: Path) -> subprocess.Popen[str]:
    process = subprocess.Popen(
        [sys.executable, "-c", _HOLD_LOCK_SCRIPT, str(lock_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    ready_line = process.stdout.readline().strip() if process.stdout is not None else ""
    if ready_line != "locked":
        stderr_output = ""
        if process.stderr is not None:
            stderr_output = process.stderr.read()
        process.kill()
        process.wait(timeout=5)
        raise AssertionError(f"lock holder did not start cleanly: {stderr_output}")
    return process


def _stop_lock_holder(process: subprocess.Popen[str]) -> None:
    try:
        process.communicate("", timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate(timeout=5)
        raise


def _claim_lock_paths(registry_root: Path) -> tuple[Path, Path, Path, Path]:
    return (
        claim_lock_path(registry_root, "claim-001"),
        dataset_lock_path(registry_root, "dataset-001"),
        dataset_lock_path(registry_root, "dataset-002"),
        study_lock_path(registry_root, "study-001"),
    )


def test_create_claim_uses_reference_aware_ingest_locks_successfully(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))

    create_claim_card(_claim_card(dataset_ids=["dataset-001", "dataset-002"]))

    claim_lock, dataset_one_lock, dataset_two_lock, parent_lock = _claim_lock_paths(
        configured_registry_root
    )

    assert parent_lock.is_file()
    assert dataset_one_lock.is_file()
    assert dataset_two_lock.is_file()
    assert claim_lock.is_file()
    assert get_claim_card("claim-001")["dataset_ids"] == ["dataset-001", "dataset-002"]


def test_claim_ingest_parent_validation_happens_under_lock(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))

    lock_paths = _claim_lock_paths(configured_registry_root)
    original_parent_check = gateway._require_study_reference_exists

    def _wrapped_parent_check(
        operation_name: str,
        study_id: str,
        *,
        referencing_card_family: str,
    ) -> None:
        assert all(_probe_lock(lock_path) == 1 for lock_path in lock_paths)
        original_parent_check(
            operation_name,
            study_id,
            referencing_card_family=referencing_card_family,
        )

    monkeypatch.setattr(gateway, "_require_study_reference_exists", _wrapped_parent_check)

    create_claim_card(_claim_card(dataset_ids=["dataset-001", "dataset-002"]))


def test_claim_ingest_dataset_validation_happens_under_lock(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))

    lock_paths = _claim_lock_paths(configured_registry_root)
    original_dataset_exists = gateway._runtime_dataset_card_exists

    def _wrapped_dataset_exists(registry_root: Path, dataset_id: str) -> bool:
        assert all(_probe_lock(lock_path) == 1 for lock_path in lock_paths)
        return original_dataset_exists(registry_root, dataset_id)

    monkeypatch.setattr(gateway, "_runtime_dataset_card_exists", _wrapped_dataset_exists)

    create_claim_card(_claim_card(dataset_ids=["dataset-001", "dataset-002"]))


def test_claim_ingest_duplicate_check_happens_under_lock(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))

    claim_lock = claim_lock_path(configured_registry_root, "claim-001")
    dataset_lock = dataset_lock_path(configured_registry_root, "dataset-001")
    parent_lock = study_lock_path(configured_registry_root, "study-001")
    original_claim_exists = gateway._runtime_claim_card_exists

    def _wrapped_claim_exists(registry_root: Path, claim_id: str) -> bool:
        assert _probe_lock(claim_lock) == 1
        assert _probe_lock(dataset_lock) == 1
        assert _probe_lock(parent_lock) == 1
        return original_claim_exists(registry_root, claim_id)

    monkeypatch.setattr(gateway, "_runtime_claim_card_exists", _wrapped_claim_exists)

    create_claim_card(_claim_card(dataset_ids=["dataset-001"]))


def test_claim_ingest_uses_deterministic_sorted_lock_path_order(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))

    acquisition_order: list[tuple[str, str, str]] = []
    original_lock = registry_locks.exclusive_card_ingest_lock

    @contextmanager
    def _recording_lock(
        lock_path: Path,
        *,
        card_family: str,
        card_id: str,
    ) -> Iterator[None]:
        acquisition_order.append((str(lock_path), card_family, card_id))
        with original_lock(lock_path, card_family=card_family, card_id=card_id):
            yield

    monkeypatch.setattr(registry_locks, "exclusive_card_ingest_lock", _recording_lock)
    monkeypatch.setattr(
        gateway,
        "_runtime_create_claim_card",
        lambda registry_root, card: card,
    )

    create_claim_card(
        _claim_card(dataset_ids=["dataset-002", "dataset-001", "dataset-001"])
    )

    expected = [
        (
            str(claim_lock_path(configured_registry_root, "claim-001")),
            "ClaimCard",
            "claim-001",
        ),
        (
            str(dataset_lock_path(configured_registry_root, "dataset-001")),
            "DatasetCard",
            "dataset-001",
        ),
        (
            str(dataset_lock_path(configured_registry_root, "dataset-002")),
            "DatasetCard",
            "dataset-002",
        ),
        (
            str(study_lock_path(configured_registry_root, "study-001")),
            "StudyCard",
            "study-001",
        ),
    ]

    assert acquisition_order == expected


def test_failed_claim_ingest_releases_all_locks(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))
    create_dataset_card(_dataset_card("dataset-002"))

    claim_lock, dataset_one_lock, dataset_two_lock, parent_lock = _claim_lock_paths(
        configured_registry_root
    )

    def _raise_runtime_failure(registry_root: Path, card: object) -> object:
        assert _probe_lock(claim_lock) == 1
        assert _probe_lock(dataset_one_lock) == 1
        assert _probe_lock(dataset_two_lock) == 1
        assert _probe_lock(parent_lock) == 1
        raise RegistryError(f"simulated locked claim ingest failure for {registry_root} / {card}")

    monkeypatch.setattr(gateway, "_runtime_create_claim_card", _raise_runtime_failure)

    with pytest.raises(RegistryError, match="simulated locked claim ingest failure"):
        create_claim_card(_claim_card(dataset_ids=["dataset-001", "dataset-002"]))

    assert _probe_lock(claim_lock) == 0
    assert _probe_lock(dataset_one_lock) == 0
    assert _probe_lock(dataset_two_lock) == 0
    assert _probe_lock(parent_lock) == 0
    assert not claim_card_path(configured_registry_root, "claim-001").exists()


def test_claim_ingest_fails_cleanly_when_parent_lock_is_held_elsewhere(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card("dataset-001"))

    claim_lock = claim_lock_path(configured_registry_root, "claim-001")
    dataset_lock = dataset_lock_path(configured_registry_root, "dataset-001")
    parent_lock = study_lock_path(configured_registry_root, "study-001")
    holder = _start_lock_holder(parent_lock)
    try:
        with pytest.raises(
            UpdateLockError,
            match="StudyCard ingest could not acquire the exclusive ingest lock for 'study-001'.",
        ):
            create_claim_card(_claim_card(dataset_ids=["dataset-001"]))
    finally:
        _stop_lock_holder(holder)

    assert _probe_lock(claim_lock) == 0
    assert _probe_lock(dataset_lock) == 0
    assert _probe_lock(parent_lock) == 0
    assert not claim_card_path(configured_registry_root, "claim-001").exists()
