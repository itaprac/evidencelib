"""Mass functions and fusion rules."""

from __future__ import annotations

from itertools import product
from math import prod
from typing import Any, Iterable, Iterator, Mapping, Sequence

from evidencelib.exceptions import InvalidMassError, TotalConflictError
from evidencelib.proposition import Proposition


class MassFunction:
    """A basic belief assignment over a frame.

    Parameters
    ----------
    frame:
        Frame of discernment that owns all propositions in the assignment.
    values:
        Mapping from propositions, proposition expressions, or iterables of
        atom names to assigned masses.
    validate:
        Validate that masses are non-negative and sum to one.
    tolerance:
        Numerical tolerance used when cleaning and validating masses.
    """

    normalization_tolerance = 1e-6

    def __init__(
        self,
        frame,
        values: Mapping[str | Proposition | Iterable[str], float],
        *,
        validate: bool = True,
        tolerance: float = 1e-9,
    ) -> None:
        self.frame = frame
        self.tolerance = tolerance
        masses: dict[Proposition, float] = {}
        for key, value in values.items():
            prop = frame.proposition(key)
            mass = float(value)
            if mass < -tolerance:
                raise InvalidMassError("Mass values must be non-negative.")
            if abs(mass) <= tolerance:
                continue
            masses[prop] = masses.get(prop, 0.0) + mass
        self._masses = self._clean(masses)
        if validate:
            self._validate_sum()

    def __getitem__(self, key: str | Proposition | Iterable[str]) -> float:
        return self.mass(key)

    def __iter__(self) -> Iterator[tuple[Proposition, float]]:
        return iter(self.items())

    def __repr__(self) -> str:
        body = ", ".join(f"{prop}: {value:.6g}" for prop, value in self.items())
        return f"MassFunction({{{body}}})"

    def items(self) -> tuple[tuple[Proposition, float], ...]:
        """Return focal propositions and masses sorted by proposition label."""

        return tuple(sorted(self._masses.items(), key=lambda item: str(item[0])))

    def focal(self) -> tuple[Proposition, ...]:
        """Return propositions with non-zero assigned mass."""

        return tuple(prop for prop, _ in self.items())

    def to_dict(self, *, string_keys: bool = True) -> dict[str | Proposition, float]:
        """Return the mass assignment as a plain dictionary."""

        if string_keys:
            return {str(prop): value for prop, value in self.items()}
        return dict(self.items())

    @property
    def total_mass(self) -> float:
        """Sum of all stored masses."""

        return sum(self._masses.values())

    def mass(self, key: str | Proposition | Iterable[str]) -> float:
        """Return the direct mass assigned to a proposition."""

        return self._masses.get(self.frame.proposition(key), 0.0)

    def belief(self, key: str | Proposition | Iterable[str]) -> float:
        """Return belief, the mass of propositions contained in ``key``."""

        target = self.frame.proposition(key)
        return sum(value for prop, value in self._masses.items() if prop <= target)

    def plausibility(self, key: str | Proposition | Iterable[str]) -> float:
        """Return plausibility, the mass of propositions intersecting ``key``."""

        target = self.frame.proposition(key)
        return sum(value for prop, value in self._masses.items() if prop.intersects(target))

    def commonality(self, key: str | Proposition | Iterable[str]) -> float:
        """Return commonality, the mass of propositions containing ``key``."""

        target = self.frame.proposition(key)
        return sum(value for prop, value in self._masses.items() if target <= prop)

    @property
    def conflict(self) -> float:
        """Mass assigned to the empty proposition."""

        return self.mass(self.frame.empty)

    def conjunctive(self, *others: "MassFunction") -> "MassFunction":
        """Unnormalized conjunctive rule.

        On a free DSm frame this is the classic DSm rule (DSmC). On Shafer's
        DST model, contradictory intersections are accumulated on ``empty``.
        """

        return self._combine_intersection((self, *others), normalize=False)

    def dsmc(self, *others: "MassFunction") -> "MassFunction":
        """Alias for the classic conjunctive DSm rule."""

        return self.conjunctive(*others)

    def smets(self, *others: "MassFunction") -> "MassFunction":
        """Smets/TBM unnormalized rule, keeping conflict on the empty set."""

        return self.conjunctive(*others)

    def dempster(self, *others: "MassFunction") -> "MassFunction":
        """Dempster's normalized rule of combination."""

        return self._combine_intersection((self, *others), normalize=True)

    def yager(self, *others: "MassFunction") -> "MassFunction":
        """Yager's rule: transfer total conflict to total ignorance."""

        conjunctive = self.conjunctive(*others)
        conflict = conjunctive.conflict
        masses = {prop: value for prop, value in conjunctive.items() if prop}
        if conflict:
            masses[self.frame.total] = masses.get(self.frame.total, 0.0) + conflict
        return MassFunction(self.frame, masses)

    def dubois_prade(self, *others: "MassFunction") -> "MassFunction":
        """Dubois-Prade style transfer of conflicts to disjunctions."""

        return self.dsmh(*others)

    def dsmh(self, *others: "MassFunction") -> "MassFunction":
        """Hybrid DSm rule for constrained models.

        Products whose intersection is non-empty go to that intersection.
        Products whose intersection is empty are transferred to the union of
        the involved propositions. If that union is also empty under the model,
        the mass goes to total ignorance.
        """

        self._check_sources((self, *others))
        masses: dict[Proposition, float] = {}
        for props, values in self._focal_product((self, *others)):
            amount = prod(values)
            intersection = self._intersection_all(props)
            if intersection:
                target = intersection
            else:
                target = self._union_all(props)
                if not target:
                    target = self.frame.total
            masses[target] = masses.get(target, 0.0) + amount
        masses.pop(self.frame.empty, None)
        return MassFunction(self.frame, masses)

    def pcr5(self, other: "MassFunction") -> "MassFunction":
        """PCR5 for two sources."""

        return self.pcr6(other)

    def pcr6(self, *others: "MassFunction") -> "MassFunction":
        """PCR6 proportional conflict redistribution for two or more sources."""

        sources = (self, *others)
        self._check_sources(sources)
        masses: dict[Proposition, float] = {}
        for props, values in self._focal_product(sources):
            amount = prod(values)
            intersection = self._intersection_all(props)
            if intersection:
                masses[intersection] = masses.get(intersection, 0.0) + amount
                continue

            denominator = sum(values)
            if denominator <= self.tolerance:
                continue
            for prop, source_mass in zip(props, values, strict=True):
                target = prop if prop else self.frame.total
                if not target:
                    continue
                share = amount * source_mass / denominator
                masses[target] = masses.get(target, 0.0) + share
        masses.pop(self.frame.empty, None)
        return MassFunction(self.frame, masses)

    def normalize(self) -> "MassFunction":
        """Normalize a conjunctive result by removing empty-set conflict."""

        conflict = self.conflict
        denominator = 1.0 - conflict
        if denominator <= self.tolerance:
            raise TotalConflictError("Dempster normalization is undefined at total conflict.")
        masses = {
            prop: value / denominator
            for prop, value in self._masses.items()
            if prop and abs(value) > self.tolerance
        }
        return MassFunction(self.frame, masses)

    def pignistic(self) -> dict[str, float]:
        """Return pignistic scores for singleton hypotheses.

        This is the classical pignistic transformation on DST frames. On free
        or hybrid DSmT frames, singleton hypotheses can overlap, so the returned
        event scores are useful for decisions but do not have to sum to one.
        """

        result = {name: 0.0 for name in self.frame.atoms}
        singletons = dict(zip(self.frame.atoms, self.frame.symbols(), strict=True))
        for prop, mass in self._masses.items():
            if not prop:
                continue
            cardinality = prop.cardinality
            if cardinality == 0:
                continue
            for name, atom in singletons.items():
                overlap = (atom & prop).cardinality
                if overlap:
                    result[name] += mass * overlap / cardinality
        return result

    def pignistic_regions(self) -> dict[str, float]:
        """Return a probability distribution over model Venn regions."""

        result = {self._format_region(region): 0.0 for region in self.frame._universe}
        for prop, mass in self._masses.items():
            if not prop:
                continue
            cardinality = prop.cardinality
            if cardinality == 0:
                continue
            share = mass / cardinality
            for region in prop.regions:
                result[self._format_region(region)] += share
        return result

    def decision(self) -> str:
        """Return the singleton with the largest pignistic probability."""

        probabilities = self.pignistic()
        return max(probabilities, key=probabilities.__getitem__)

    def plot(self, *, ax: Any = None, **kwargs: Any) -> Any:
        """Plot this mass assignment as a horizontal bar chart.

        This method requires the optional plotting dependency. Install it with
        ``pip install 'evidencelib[plot]'``.
        """

        from evidencelib.plotting import plot_mass

        return plot_mass(self, ax=ax, **kwargs)

    def plot_comparison(
        self,
        *others: "MassFunction",
        labels: Sequence[str] | None = None,
        ax: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Plot a heatmap comparing this mass assignment with other sources."""

        from evidencelib.plotting import plot_mass_comparison

        return plot_mass_comparison((self, *others), labels=labels, ax=ax, **kwargs)

    def plot_belief_plausibility(self, *, ax: Any = None, **kwargs: Any) -> Any:
        """Plot belief-plausibility intervals for this mass assignment."""

        from evidencelib.plotting import plot_belief_plausibility

        return plot_belief_plausibility(self, ax=ax, **kwargs)

    def plot_pignistic_decision(self, *, ax: Any = None, **kwargs: Any) -> Any:
        """Plot the pignistic decision ranking for this mass assignment."""

        from evidencelib.plotting import plot_pignistic_decision

        return plot_pignistic_decision(self, ax=ax, **kwargs)

    def plot_venn(self, *, ax: Any = None, **kwargs: Any) -> Any:
        """Plot pignistic or direct mass values over disjoint Venn regions."""

        from evidencelib.plotting import plot_venn

        return plot_venn(self, ax=ax, **kwargs)

    @classmethod
    def _from_unchecked(cls, frame, values: Mapping[Proposition, float]) -> "MassFunction":
        return cls(frame, values, validate=False)

    def _combine_intersection(
        self,
        sources: tuple["MassFunction", ...],
        *,
        normalize: bool,
    ) -> "MassFunction":
        self._check_sources(sources)
        masses: dict[Proposition, float] = {}
        for props, values in self._focal_product(sources):
            target = self._intersection_all(props)
            masses[target] = masses.get(target, 0.0) + prod(values)
        result = MassFunction(self.frame, masses)
        return result.normalize() if normalize else result

    def _focal_product(
        self,
        sources: tuple["MassFunction", ...],
    ) -> Iterator[tuple[tuple[Proposition, ...], tuple[float, ...]]]:
        item_groups = [source.items() for source in sources]
        for combo in product(*item_groups):
            props = tuple(prop for prop, _ in combo)
            values = tuple(value for _, value in combo)
            yield props, values

    def _intersection_all(self, props: Iterable[Proposition]) -> Proposition:
        iterator = iter(props)
        result = next(iterator)
        for prop in iterator:
            result = result & prop
        return result

    def _union_all(self, props: Iterable[Proposition]) -> Proposition:
        result = self.frame.empty
        for prop in props:
            result = result | prop
        return result

    def _check_sources(self, sources: tuple["MassFunction", ...]) -> None:
        if len(sources) < 2:
            raise ValueError("At least two sources are required.")
        if any(source.frame is not self.frame for source in sources):
            raise ValueError("All mass functions must belong to the same frame.")

    def _validate_sum(self) -> None:
        total = sum(self._masses.values())
        if abs(total - 1.0) <= self.tolerance:
            return
        if abs(total - 1.0) <= self.normalization_tolerance:
            self._masses = {prop: value / total for prop, value in self._masses.items()}
            return
        if abs(total - 1.0) > self.tolerance:
            raise InvalidMassError(f"Mass values must sum to 1.0, got {total}.")

    def _clean(self, masses: Mapping[Proposition, float]) -> dict[Proposition, float]:
        return {
            prop: value
            for prop, value in masses.items()
            if abs(value) > self.tolerance
        }

    def _format_region(self, region: int) -> str:
        names = [name for i, name in enumerate(self.frame.atoms) if region & (1 << i)]
        return "&".join(names)
