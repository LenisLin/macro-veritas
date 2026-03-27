"""Narrow advisory file-lock helpers for update-only registry mutations.

This module owns only the local filesystem lock primitive used by the gateway's
full-replace update path.

Responsibilities:
- acquire one exclusive advisory lock for one deterministic card-specific file
- hold that lock for the caller's mutation-critical section
- release the lock when the caller finishes or fails

Non-goals:
- path planning for lock files
- distributed locking
- retries, timeouts, leasing, or force-unlock workflows
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path

from macro_veritas.registry.errors import UpdateLockError


@contextmanager
def exclusive_card_update_lock(
    lock_path: Path,
    *,
    card_family: str,
    card_id: str,
) -> Iterator[None]:
    """Acquire one non-blocking exclusive update lock for a single target card."""

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        file_descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
    except OSError as exc:
        raise UpdateLockError(
            f"{card_family} update failed while preparing the exclusive update lock "
            f"for '{card_id}' at {lock_path}: {exc}"
        ) from exc

    lock_handle = os.fdopen(file_descriptor, "r+", encoding="utf-8")
    unlock_error: UpdateLockError | None = None
    try:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise UpdateLockError(
                f"{card_family} update could not acquire the exclusive update lock "
                f"for '{card_id}'."
            ) from exc
        except OSError as exc:
            raise UpdateLockError(
                f"{card_family} update failed while preparing the exclusive update lock "
                f"for '{card_id}' at {lock_path}: {exc}"
            ) from exc

        try:
            yield
        finally:
            try:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            except OSError as exc:
                unlock_error = UpdateLockError(
                    f"{card_family} update failed while releasing the exclusive update lock "
                    f"for '{card_id}' at {lock_path}: {exc}"
                )
    finally:
        close_error: UpdateLockError | None = None
        try:
            lock_handle.close()
        except OSError as exc:
            close_error = UpdateLockError(
                f"{card_family} update failed while closing the exclusive update lock "
                f"for '{card_id}' at {lock_path}: {exc}"
            )

        if unlock_error is not None:
            raise unlock_error
        if close_error is not None:
            raise close_error


__all__ = ["exclusive_card_update_lock"]
