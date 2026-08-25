"""Symbolic propositions used by DST and DSmT frames."""

from __future__ import annotations

from typing import TYPE_CHECKING, FrozenSet, Iterable

if TYPE_CHECKING:
    from evidencelib.frame import Frame


class Proposition:
    """A canonical proposition represented by possible Venn regions.

    Users normally create propositions through a :class:`evidencelib.Frame` and
    combine them with ``|`` for union and ``&`` for intersection.

    Internally the region set is encoded as an integer bitmask over the
    frame's dense region index, so set algebra reduces to integer ``|``,
    ``&``, and mask tests.  Canonical region sets are closed under union and
    intersection, which lets the operators skip re-normalization.
    """

    __slots__ = ("frame", "_mask", "_regions")

    frame: "Frame"
    _mask: int
    _regions: FrozenSet[int] | None

    def __init__(self, frame: "Frame", regions: Iterable[int]) -> None:
        object.__setattr__(self, "frame", frame)
        normalized = frame._normalize_regions(regions)
        mask = 0
        region_bit = frame._region_bit
        for region in normalized:
            mask |= region_bit[region]
        object.__setattr__(self, "_mask", mask)
        object.__setattr__(self, "_regions", normalized)

    @classmethod
    def _from_mask(cls, frame: "Frame", mask: int) -> "Proposition":
        """Build a proposition from an already-canonical region bitmask."""

        prop = cls.__new__(cls)
        object.__setattr__(prop, "frame", frame)
        object.__setattr__(prop, "_mask", mask)
        object.__setattr__(prop, "_regions", None)
        return prop

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Proposition instances are immutable.")

    @property
    def regions(self) -> FrozenSet[int]:
        """The possible Venn regions covered by this proposition."""

        regions = self._regions
        if regions is None:
            by_bit = self.frame._region_by_bit
            decoded = []
            mask = self._mask
            while mask:
                low = mask & -mask
                decoded.append(by_bit[low.bit_length() - 1])
                mask ^= low
            regions = frozenset(decoded)
            object.__setattr__(self, "_regions", regions)
        return regions

    def __or__(self, other: "Proposition") -> "Proposition":
        self._check_same_frame(other)
        return Proposition._from_mask(self.frame, self._mask | other._mask)

    def __and__(self, other: "Proposition") -> "Proposition":
        self._check_same_frame(other)
        return Proposition._from_mask(self.frame, self._mask & other._mask)

    def __le__(self, other: "Proposition") -> bool:
        self._check_same_frame(other)
        return self._mask & other._mask == self._mask

    def __lt__(self, other: "Proposition") -> bool:
        return self <= other and self._mask != other._mask

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Proposition):
            return NotImplemented
        return self.frame is other.frame and self._mask == other._mask

    def __hash__(self) -> int:
        return hash((id(self.frame), self._mask))

    def __bool__(self) -> bool:
        return self._mask != 0

    def __str__(self) -> str:
        return self.frame.format(self)

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)

    def __repr__(self) -> str:
        return f"Proposition({str(self)!r})"

    @property
    def is_empty(self) -> bool:
        """Whether this proposition contains no possible model regions."""

        return self._mask == 0

    @property
    def cardinality(self) -> int:
        """DSm cardinality: number of non-empty model regions."""

        return self._mask.bit_count()

    def intersects(self, other: "Proposition") -> bool:
        """Return whether two propositions share at least one model region."""

        self._check_same_frame(other)
        return bool(self._mask & other._mask)

    def union_atoms(self) -> "Proposition":
        """Return the disjunction of singleton hypotheses involved in this proposition."""

        mask = 0
        # u(X) is defined from the atoms that syntactically compose the
        # canonical DNF of X.  OR-ing every Venn region is incorrect: in a free
        # three-atom model the regions of A&B include A&B&C, which would
        # spuriously make C part of u(A&B).
        for term in self.frame._minimal_terms(self.regions):
            mask |= term
        if mask == 0:
            return self.frame.empty
        return Proposition(self.frame, frozenset(r for r in self.frame._universe if r & mask))

    def _check_same_frame(self, other: "Proposition") -> None:
        if not isinstance(other, Proposition) or other.frame is not self.frame:
            raise ValueError("Propositions must belong to the same frame.")
