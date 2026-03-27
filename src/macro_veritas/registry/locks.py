"""Narrow advisory file-lock helpers for single-card registry mutations.

This module owns only the local filesystem lock primitive used by the gateway's
single-card update and delete paths plus the parent-aware DatasetCard ingest
path and reference-aware ClaimCard ingest path.

Responsibilities:
- acquire one exclusive advisory lock for one deterministic card-specific file
- acquire one deterministic ordered set of ClaimCard ingest locks
- hold that lock for the caller's mutation-critical section
- release the lock when the caller finishes or fails

Non-goals:
- path planning for lock files
- distributed locking
- retries, timeouts, leasing, or force-unlock workflows
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from contextlib import ExitStack, contextmanager
import fcntl
import os
from pathlib import Path
from typing import NamedTuple

from macro_veritas.registry.errors import UpdateLockError


class IngestLockTarget(NamedTuple):
    """Describe one deterministic ingest lock target."""

    lock_path: Path
    card_family: str
    card_id: str


@contextmanager
def exclusive_card_lock(
    lock_path: Path,
    *,
    card_family: str,
    card_id: str,
    operation_name: str,
) -> Iterator[None]:
    """Acquire one non-blocking exclusive lock for a single target card."""

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        file_descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    except OSError as exc:
        raise UpdateLockError(
            f"{card_family} {operation_name} failed while preparing the exclusive "
            f"{operation_name} lock "
            f"for '{card_id}' at {lock_path}: {exc}"
        ) from exc

    lock_handle = os.fdopen(file_descriptor, "r+", encoding="utf-8")
    unlock_error: UpdateLockError | None = None
    try:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise UpdateLockError(
                f"{card_family} {operation_name} could not acquire the exclusive "
                f"{operation_name} lock "
                f"for '{card_id}'."
            ) from exc
        except OSError as exc:
            raise UpdateLockError(
                f"{card_family} {operation_name} failed while preparing the exclusive "
                f"{operation_name} lock "
                f"for '{card_id}' at {lock_path}: {exc}"
            ) from exc

        try:
            yield
        finally:
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            except OSError as exc:
                unlock_error = UpdateLockError(
                    f"{card_family} {operation_name} failed while releasing the exclusive "
                    f"{operation_name} lock "
                    f"for '{card_id}' at {lock_path}: {exc}"
                )
    finally:
        close_error: UpdateLockError | None = None
        try:
            lock_handle.close()
        except OSError as exc:
            close_error = UpdateLockError(
                f"{card_family} {operation_name} failed while closing the exclusive "
                f"{operation_name} lock "
                f"for '{card_id}' at {lock_path}: {exc}"
            )

        if unlock_error is not None:
            raise unlock_error
        if close_error is not None:
            raise close_error


@contextmanager
def exclusive_card_delete_lock(
    lock_path: Path,
    *,
    card_family: str,
    card_id: str,
) -> Iterator[None]:
    """Acquire one non-blocking exclusive delete lock for a single target card."""

    with exclusive_card_lock(
        lock_path,
        card_family=card_family,
        card_id=card_id,
        operation_name="delete",
    ):
        yield


@contextmanager
def exclusive_card_ingest_lock(
    lock_path: Path,
    *,
    card_family: str,
    card_id: str,
) -> Iterator[None]:
    """Acquire one non-blocking exclusive ingest lock for a single target card."""

    with exclusive_card_lock(
        lock_path,
        card_family=card_family,
        card_id=card_id,
        operation_name="ingest",
    ):
        yield


@contextmanager
def exclusive_card_update_lock(
    lock_path: Path,
    *,
    card_family: str,
    card_id: str,
) -> Iterator[None]:
    """Acquire one non-blocking exclusive update lock for a single target card."""

    with exclusive_card_lock(
        lock_path,
        card_family=card_family,
        card_id=card_id,
        operation_name="update",
    ):
        yield


@contextmanager
def exclusive_ordered_ingest_locks(
    lock_targets: Iterable[IngestLockTarget],
) -> Iterator[None]:
    """Acquire deterministic ClaimCard ingest locks in sorted lock-path order."""

    unique_targets: dict[str, IngestLockTarget] = {}
    for target in lock_targets:
        unique_targets.setdefault(str(target.lock_path), target)

    with ExitStack() as stack:
        for target in sorted(unique_targets.values(), key=lambda item: str(item.lock_path)):
            stack.enter_context(
                exclusive_card_ingest_lock(
                    target.lock_path,
                    card_family=target.card_family,
                    card_id=target.card_id,
                )
            )
        yield


__all__ = [
    "IngestLockTarget",
    "exclusive_card_delete_lock",
    "exclusive_card_ingest_lock",
    "exclusive_card_lock",
    "exclusive_ordered_ingest_locks",
    "exclusive_card_update_lock",
]
