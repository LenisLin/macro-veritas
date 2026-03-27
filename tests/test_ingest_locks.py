from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from macro_veritas.registry import gateway
from macro_veritas.registry.errors import RegistryError, UpdateLockError
from macro_veritas.registry.gateway import create_dataset_card, create_study_card, get_dataset_card
from macro_veritas.registry.layout import (
    dataset_card_path,
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
        "created_from_note": "seeded in ingest lock test",
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


def test_create_dataset_uses_parent_and_target_ingest_locks_successfully(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    create_dataset_card(_dataset_card())

    parent_lock = study_lock_path(configured_registry_root, "study-001")
    target_lock = dataset_lock_path(configured_registry_root, "dataset-001")

    assert parent_lock.is_file()
    assert target_lock.is_file()
    assert get_dataset_card("dataset-001")["status"] == "identified"


def test_dataset_ingest_parent_validation_and_duplicate_check_happen_under_lock(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())

    parent_lock = study_lock_path(configured_registry_root, "study-001")
    target_lock = dataset_lock_path(configured_registry_root, "dataset-001")
    original_parent_check = gateway._require_study_reference_exists
    original_target_exists = gateway._runtime_dataset_card_exists

    def _wrapped_parent_check(
        operation_name: str,
        study_id: str,
        *,
        referencing_card_family: str,
    ) -> None:
        assert _probe_lock(parent_lock) == 1
        assert _probe_lock(target_lock) == 1
        original_parent_check(
            operation_name,
            study_id,
            referencing_card_family=referencing_card_family,
        )

    def _wrapped_target_exists(registry_root: Path, dataset_id: str) -> bool:
        assert _probe_lock(parent_lock) == 1
        assert _probe_lock(target_lock) == 1
        return original_target_exists(registry_root, dataset_id)

    monkeypatch.setattr(gateway, "_require_study_reference_exists", _wrapped_parent_check)
    monkeypatch.setattr(gateway, "_runtime_dataset_card_exists", _wrapped_target_exists)

    create_dataset_card(_dataset_card())


def test_dataset_ingest_uses_deterministic_parent_then_target_lock_order(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())

    acquisition_order: list[tuple[str, str]] = []
    original_lock = gateway.exclusive_card_ingest_lock

    @contextmanager
    def _recording_lock(
        lock_path: Path,
        *,
        card_family: str,
        card_id: str,
    ) -> Iterator[None]:
        acquisition_order.append((card_family, card_id))
        with original_lock(lock_path, card_family=card_family, card_id=card_id):
            yield

    monkeypatch.setattr(gateway, "exclusive_card_ingest_lock", _recording_lock)

    create_dataset_card(_dataset_card())

    assert acquisition_order == [
        ("StudyCard", "study-001"),
        ("DatasetCard", "dataset-001"),
    ]


def test_failed_dataset_ingest_releases_both_locks(
    configured_registry_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create_study_card(_study_card())

    parent_lock = study_lock_path(configured_registry_root, "study-001")
    target_lock = dataset_lock_path(configured_registry_root, "dataset-001")

    def _raise_runtime_failure(registry_root: Path, card: object) -> object:
        assert _probe_lock(parent_lock) == 1
        assert _probe_lock(target_lock) == 1
        raise RegistryError(f"simulated locked ingest failure for {registry_root} / {card}")

    monkeypatch.setattr(gateway, "_runtime_create_dataset_card", _raise_runtime_failure)

    with pytest.raises(RegistryError, match="simulated locked ingest failure"):
        create_dataset_card(_dataset_card())

    assert _probe_lock(parent_lock) == 0
    assert _probe_lock(target_lock) == 0
    assert not dataset_card_path(configured_registry_root, "dataset-001").exists()


def test_dataset_ingest_fails_cleanly_when_parent_lock_is_held_elsewhere(
    configured_registry_root: Path,
) -> None:
    create_study_card(_study_card())

    parent_lock = study_lock_path(configured_registry_root, "study-001")
    holder = _start_lock_holder(parent_lock)
    try:
        with pytest.raises(
            UpdateLockError,
            match="StudyCard ingest could not acquire the exclusive ingest lock for 'study-001'.",
        ):
            create_dataset_card(_dataset_card())
    finally:
        _stop_lock_holder(holder)

    assert not dataset_card_path(configured_registry_root, "dataset-001").exists()
