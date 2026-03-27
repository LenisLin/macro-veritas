from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from macro_veritas.registry import gateway
from macro_veritas.registry.errors import DependencyExistsError, RegistryError, UpdateLockError
from macro_veritas.registry.gateway import (
    create_claim_card,
    create_dataset_card,
    create_study_card,
    delete_claim_card,
    delete_dataset_card,
    delete_study_card,
)
from macro_veritas.registry.layout import (
    claim_card_path,
    claim_lock_path,
    dataset_card_path,
    dataset_lock_path,
    study_card_path,
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


def _study_card(
    study_id: str = "study-001",
    *,
    status: str = "registered",
    created_from_note: str = "seeded in test",
) -> dict[str, object]:
    return {
        "study_id": study_id,
        "citation_handle": f"doi:{study_id}",
        "tumor_scope_tags": ["glioma"],
        "therapy_scope_tags": ["immunotherapy"],
        "relevance_scope_tags": ["preclinical"],
        "screening_decision": "include",
        "status": status,
        "created_from_note": created_from_note,
    }


def _dataset_card(
    dataset_id: str = "dataset-001",
    *,
    study_id: str = "study-001",
    status: str = "identified",
) -> dict[str, object]:
    return {
        "dataset_id": dataset_id,
        "study_id": study_id,
        "source_locator": f"https://example.org/{dataset_id}",
        "availability_status": "open",
        "modality_scope_tags": ["rna-seq"],
        "cohort_summary": "adult cohort",
        "platform_summary": "Illumina",
        "status": status,
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
        "created_from_note": "seeded in test",
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


def test_delete_study_creates_lock_file_and_deletes_successfully(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    delete_study_card("study-001")

    lock_path = study_lock_path(configured_registry_root, "study-001")

    assert lock_path.is_file()
    assert not study_card_path(configured_registry_root, "study-001").exists()


def test_delete_dataset_creates_lock_file_and_deletes_successfully(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card())

    delete_dataset_card("dataset-001")

    lock_path = dataset_lock_path(configured_registry_root, "dataset-001")

    assert lock_path.is_file()
    assert not dataset_card_path(configured_registry_root, "dataset-001").exists()


def test_delete_claim_creates_lock_file_and_deletes_successfully(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_claim_card(_claim_card())

    delete_claim_card("claim-001")

    lock_path = claim_lock_path(configured_registry_root, "claim-001")

    assert lock_path.is_file()
    assert not claim_card_path(configured_registry_root, "claim-001").exists()


def test_delete_study_remains_blocked_by_dependent_dataset(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card())

    with pytest.raises(
        DependencyExistsError,
        match=(
            "cannot delete StudyCard 'study-001' because dependent DatasetCard\\(s\\) "
            "exist: dataset-001\\."
        ),
    ):
        delete_study_card("study-001")

    assert study_card_path(configured_registry_root, "study-001").exists()


def test_delete_study_remains_blocked_by_dependent_claim(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_claim_card(_claim_card())

    with pytest.raises(
        DependencyExistsError,
        match=(
            "cannot delete StudyCard 'study-001' because dependent ClaimCard\\(s\\) "
            "exist: claim-001\\."
        ),
    ):
        delete_study_card("study-001")

    assert study_card_path(configured_registry_root, "study-001").exists()


def test_delete_dataset_remains_blocked_by_dependent_claim(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())
    create_dataset_card(_dataset_card())
    create_claim_card(_claim_card(dataset_ids=["dataset-001"]))

    with pytest.raises(
        DependencyExistsError,
        match=(
            "cannot delete DatasetCard 'dataset-001' because dependent ClaimCard\\(s\\) "
            "exist: claim-001\\."
        ),
    ):
        delete_dataset_card("dataset-001")

    assert dataset_card_path(configured_registry_root, "dataset-001").exists()


def test_study_delete_dependency_check_happens_while_lock_is_held(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())

    lock_path = study_lock_path(configured_registry_root, "study-001")
    original_check = gateway._require_study_delete_allowed

    def _wrapped_delete_check(study_id: str) -> None:
        assert _probe_lock(lock_path) == 1
        original_check(study_id)

    monkeypatch.setattr(gateway, "_require_study_delete_allowed", _wrapped_delete_check)

    delete_study_card("study-001")


def test_failed_study_delete_releases_lock(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())

    lock_path = study_lock_path(configured_registry_root, "study-001")

    def _raise_runtime_failure(registry_root: Path, study_id: str) -> None:
        raise RegistryError(f"simulated locked delete failure for {registry_root} / {study_id}")

    monkeypatch.setattr(gateway, "_runtime_delete_study_card", _raise_runtime_failure)

    with pytest.raises(RegistryError):
        delete_study_card("study-001")

    assert _probe_lock(lock_path) == 0
    assert study_card_path(configured_registry_root, "study-001").exists()


def test_delete_study_fails_cleanly_when_lock_is_held_elsewhere(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    lock_path = study_lock_path(configured_registry_root, "study-001")
    holder = _start_lock_holder(lock_path)
    try:
        with pytest.raises(
            UpdateLockError,
            match="StudyCard delete could not acquire the exclusive delete lock for 'study-001'.",
        ):
            delete_study_card("study-001")
    finally:
        _stop_lock_holder(holder)

    assert study_card_path(configured_registry_root, "study-001").exists()
