"""Frames of discernment for DST and DSmT."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable, Iterator, Mapping, Sequence

from evidencelib.parser import PropositionParser
from evidencelib.proposition import Proposition

_RESERVED_ATOM_NAMES = {"empty", "EMPTY", "∅"}
_ATOM_NAME_DELIMITERS = set("()&|∩∧∪∨")


class Frame:
    """A finite frame of discernment.

    The internal representation uses Venn regions. This lets the same
    proposition algebra represent Shafer's exclusive DST model, the free DSmT
    model, and constrained hybrid DSm models.

    Parameters
    ----------
    atoms:
        Names of the elementary hypotheses.
    empty:
        Propositions that are constrained to be empty in a hybrid model.
    exclusive:
        If ``True``, all atom pairs are mutually exclusive. An iterable of atom
        groups may be supplied to mark only selected intersections as empty.
    model:
        Descriptive model name stored on the frame.
    """

    def __init__(
        self,
        atoms: Sequence[str],
        *,
        empty: Iterable[str | Proposition] = (),
        exclusive: bool | Iterable[Sequence[str]] = False,
        model: str = "hybrid",
    ) -> None:
        if not atoms:
            raise ValueError("A frame needs at least one atom.")

        for atom in atoms:
            self._validate_atom_name(atom)
        if len(set(atoms)) != len(atoms):
            raise ValueError("Frame atom names must be unique.")

        self.atoms = tuple(atoms)
        self.model = model
        self._index = {name: i for i, name in enumerate(self.atoms)}
        self._full_universe = frozenset(range(1, 1 << len(self.atoms)))
        self._impossible_regions: set[int] = set()
        self._universe = self._full_universe

        constraints: list[str | Proposition] = []
        if exclusive is True:
            constraints.extend("&".join(pair) for pair in combinations(self.atoms, 2))
        elif exclusive:
            constraints.extend("&".join(group) for group in exclusive)
        constraints.extend(empty)

        for constraint in constraints:
            prop = self._parse_free(constraint)
            self._impossible_regions.update(prop.regions)
            self._universe = frozenset(self._full_universe - self._impossible_regions)

        self.empty = Proposition(self, frozenset())
        self.total = Proposition(self, self._universe)

    @classmethod
    def dst(cls, atoms: Sequence[str]) -> "Frame":
        """Create Shafer's DST model with mutually exclusive hypotheses."""

        return cls(atoms, exclusive=True, model="dst")

    @classmethod
    def dsmt(cls, atoms: Sequence[str]) -> "Frame":
        """Create the free DSm model where hypotheses may overlap."""

        return cls(atoms, model="dsmt")

    @classmethod
    def hybrid(
        cls,
        atoms: Sequence[str],
        *,
        empty: Iterable[str | Proposition] = (),
        exclusive: bool | Iterable[Sequence[str]] = False,
    ) -> "Frame":
        """Create a constrained DSm model."""

        return cls(atoms, empty=empty, exclusive=exclusive, model="hybrid")

    @staticmethod
    def _validate_atom_name(name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("Frame atom names must be strings.")
        if not name:
            raise ValueError("Frame atom names must not be empty.")
        if name in _RESERVED_ATOM_NAMES:
            raise ValueError(f"Frame atom name {name!r} is reserved proposition syntax.")
        if any(char.isspace() for char in name):
            raise ValueError(f"Frame atom name {name!r} must not contain whitespace.")
        if any(char in _ATOM_NAME_DELIMITERS for char in name):
            raise ValueError(f"Frame atom name {name!r} contains proposition syntax.")

    def symbols(self, names: str | None = None) -> tuple[Proposition, ...]:
        """Return atom propositions.

        ``names`` may be omitted to return all frame atoms, or supplied as a
        whitespace/comma-separated subset.
        """

        if names is None:
            selected = self.atoms
        else:
            selected = tuple(part for part in names.replace(",", " ").split() if part)
        return tuple(self.atom(name) for name in selected)

    def atom(self, name: str) -> Proposition:
        """Return the singleton proposition for an atom name."""

        if name not in self._index:
            raise KeyError(f"Unknown frame atom: {name!r}")
        bit = 1 << self._index[name]
        return Proposition(self, frozenset(r for r in self._universe if r & bit))

    def proposition(self, value: str | Proposition | Iterable[str]) -> Proposition:
        """Coerce a string, proposition, or iterable of atoms into a proposition."""

        if isinstance(value, Proposition):
            if value.frame is not self:
                raise ValueError("Proposition belongs to a different frame.")
            return value
        if isinstance(value, str):
            return self._parse(value)
        prop = self.empty
        for atom in value:
            prop = prop | self.atom(atom)
        return prop

    def mass(self, values: Mapping[str | Proposition | Iterable[str], float], **kwargs):
        """Create a mass function on this frame.

        Parameters
        ----------
        values:
            Mapping from propositions, proposition expressions, or iterables of
            atom names to assigned masses.
        **kwargs:
            Additional options passed to :class:`evidencelib.MassFunction`.
        """

        from evidencelib.mass import MassFunction

        return MassFunction(self, values, **kwargs)

    @property
    def region_count(self) -> int:
        """Number of non-empty disjoint Venn regions in the current model."""

        return len(self._universe)

    def elements(self, *, max_count: int | None = 100_000) -> tuple[Proposition, ...]:
        """Generate the model's closure under union and intersection.

        The result is the power set for DST and the hyper-power set for the free
        DSm model. DSmT cardinality grows very quickly; pass ``max_count=None``
        only when you really want the full closure.
        """

        elements = {self.empty, *self.symbols()}
        changed = True
        while changed:
            changed = False
            current = tuple(elements)
            for left in current:
                for right in current:
                    for combined in (left | right, left & right):
                        if combined not in elements:
                            elements.add(combined)
                            changed = True
                            if max_count is not None and len(elements) > max_count:
                                raise RuntimeError(
                                    "Element generation exceeded max_count; "
                                    "DSmT hyper-power sets grow very quickly."
                                )
        return tuple(sorted(elements, key=lambda p: (len(p.regions), str(p))))

    def format(self, prop: Proposition) -> str:
        """Format a proposition as a compact expression using frame atom names."""

        if not prop.regions:
            return "empty"

        terms = self._minimal_terms(prop.regions)
        rendered_terms = []
        for term in terms:
            names = [name for i, name in enumerate(self.atoms) if term & (1 << i)]
            rendered_terms.append("&".join(names))
        return "|".join(rendered_terms)

    def _normalize_regions(self, regions: Iterable[int]) -> frozenset[int]:
        return frozenset(r for r in regions if r in self._universe)

    def _parse_free(self, value: str | Proposition) -> Proposition:
        old_universe = self._universe
        self._universe = self._full_universe
        try:
            return self._parse(value)
        finally:
            self._universe = old_universe

    def _parse(self, value: str | Proposition) -> Proposition:
        if isinstance(value, Proposition):
            if value.frame is not self:
                raise ValueError("Proposition belongs to a different frame.")
            return value

        try:
            result = PropositionParser(self).parse(value)
        except Exception as exc:  # pragma: no cover - exception message is the value.
            raise ValueError(f"Could not parse proposition {value!r}") from exc
        return result

    def _minimal_terms(self, regions: Iterable[int]) -> tuple[int, ...]:
        region_set = set(regions)
        terms: list[int] = []
        for region in sorted(region_set, key=lambda r: (r.bit_count(), r)):
            if any((term & region) == term for term in terms):
                continue
            upward = {r for r in self._universe if (r & region) == region}
            if upward & region_set:
                terms.append(region)
        return tuple(terms)

    def __iter__(self) -> Iterator[Proposition]:
        return iter(self.symbols())

    def __repr__(self) -> str:
        return f"Frame({self.atoms!r}, model={self.model!r})"
