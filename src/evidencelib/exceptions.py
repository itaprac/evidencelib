"""Package-specific exceptions."""


class EvidenceLibError(Exception):
    """Base exception for evidencelib."""


class InvalidMassError(EvidenceLibError, ValueError):
    """Raised when a mass assignment is invalid."""


class TotalConflictError(EvidenceLibError, ZeroDivisionError):
    """Raised when normalized combination is undefined due to total conflict."""

