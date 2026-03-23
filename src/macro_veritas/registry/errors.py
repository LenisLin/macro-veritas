"""Registry access error surface for MacroVeritas.

These exception classes freeze the minimum semantic categories expected at the
registry gateway boundary.

They define domain-level gateway semantics, not raw OS or serializer exception
types. Runtime implementations are expected to translate lower-level failures
before they cross the gateway boundary.

The current real runtime slices use these classes for StudyCard, DatasetCard,
and ClaimCard gateway operations.

They do not implement recovery policy, logging, or filesystem behavior by
themselves.
Boundary docs: `docs/registry_io_boundary.md` and `docs/gateway_contracts.md`.
"""

from __future__ import annotations


class RegistryError(Exception):
    """Base class for gateway/domain registry contract failures."""


class CardNotFoundError(RegistryError):
    """Raised when a requested target card is absent for read or update planning."""


class CardAlreadyExistsError(RegistryError):
    """Raised when create planning targets a card that already exists."""


class BrokenReferenceError(RegistryError):
    """Raised when direct gateway-owned reference checks find a missing linked card."""


class DependencyExistsError(RegistryError):
    """Raised when delete would leave dependent registry records behind."""


class InvalidStateTransitionError(RegistryError):
    """Raised when the requested change conflicts with the frozen state policy."""


class UnsupportedRegistryOperationError(RegistryError):
    """Raised when the caller asks for behavior outside the frozen gateway contract."""


__all__ = [
    "BrokenReferenceError",
    "CardAlreadyExistsError",
    "CardNotFoundError",
    "DependencyExistsError",
    "InvalidStateTransitionError",
    "RegistryError",
    "UnsupportedRegistryOperationError",
]
