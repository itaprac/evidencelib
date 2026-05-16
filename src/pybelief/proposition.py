"""Symbolic propositions used by DST and DSmT frames."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, FrozenSet

if TYPE_CHECKING:
    from pybelief.frame import Frame


@dataclass(frozen=True)
class Proposition:
    """A canonical proposition represented by possible Venn regions.

    Users normally create propositions through a :class:`pybelief.Frame` and
    combine them with ``|`` for union and ``&`` for intersection.
    """

    frame: "Frame"
    regions: FrozenSet[int]

    def __post_init__(self) -> None:
        normalized = self.frame._normalize_regions(self.regions)
        object.__setattr__(self, "regions", frozenset(normalized))

    def __or__(self, other: "Proposition") -> "Proposition":
        self._check_same_frame(other)
        return Proposition(self.frame, self.regions | other.regions)

    def __and__(self, other: "Proposition") -> "Proposition":
        self._check_same_frame(other)
        return Proposition(self.frame, self.regions & other.regions)

    def __le__(self, other: "Proposition") -> bool:
        self._check_same_frame(other)
        return self.regions <= other.regions

    def __lt__(self, other: "Proposition") -> bool:
        return self <= other and self.regions != other.regions

    def __bool__(self) -> bool:
        return bool(self.regions)

    def __str__(self) -> str:
        return self.frame.format(self)

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)

    def __repr__(self) -> str:
        return f"Proposition({str(self)!r})"

    @property
    def is_empty(self) -> bool:
        return not self.regions

    @property
    def cardinality(self) -> int:
        """DSm cardinality: number of non-empty model regions."""

        return len(self.regions)

    def intersects(self, other: "Proposition") -> bool:
        self._check_same_frame(other)
        return bool(self.regions & other.regions)

    def union_atoms(self) -> "Proposition":
        """Return the disjunction of singleton hypotheses involved in this proposition."""

        mask = 0
        for region in self.regions:
            mask |= region
        if mask == 0:
            return self.frame.empty
        return Proposition(self.frame, frozenset(r for r in self.frame._universe if r & mask))

    def _check_same_frame(self, other: "Proposition") -> None:
        if not isinstance(other, Proposition) or other.frame is not self.frame:
            raise ValueError("Propositions must belong to the same frame.")
