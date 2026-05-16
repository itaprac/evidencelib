"""Package-specific exceptions."""


class PyBeliefError(Exception):
    """Base exception for pybelief."""


class InvalidMassError(PyBeliefError, ValueError):
    """Raised when a mass assignment is invalid."""


class TotalConflictError(PyBeliefError, ZeroDivisionError):
    """Raised when normalized combination is undefined due to total conflict."""

