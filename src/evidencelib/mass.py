"""Mass functions and fusion rules."""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping as MappingABC
from io import StringIO
from itertools import product
from math import prod
from typing import Any, Iterable, Iterator, Mapping, Sequence

from evidencelib.exceptions import InvalidMassError, TotalConflictError
from evidencelib.proposition import Proposition

_MASS_JSON_SCHEMA = "evidencelib.mass.v1"
_EXPORT_COLUMNS = {
    "m": ("Mass", "mass"),
    "mass": ("Mass", "mass"),
    "belief": ("Belief", "belief"),
    "bel": ("Belief", "belief"),
    "plausibility": ("Plausibility", "plausibility"),
    "pl": ("Plausibility", "plausibility"),
    "commonality": ("Commonality", "commonality"),
    "q": ("Commonality", "commonality"),
}


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

    @classmethod
    def from_dict(
        cls,
        frame,
        data: Mapping[str | Proposition | Iterable[str], float] | Mapping[str, Any],
        **kwargs: Any,
    ) -> "MassFunction":
        """Create a mass function from a plain or schema-wrapped dictionary.

        ``data`` may be a direct mapping such as ``{"A": 0.2, "A|B": 0.8}``
        or the object produced by :meth:`to_json` after JSON decoding.
        """

        if not isinstance(data, MappingABC):
            raise TypeError("Mass data must be a mapping.")

        values = data
        if isinstance(data.get("masses"), MappingABC):
            cls._validate_frame_metadata(frame, data.get("frame"))
            values = data["masses"]
        return cls(frame, values, **kwargs)

    def to_json(self, *, indent: int | None = 2) -> str:
        """Serialize this mass function to a JSON string.

        The JSON stores the mass assignment and lightweight frame metadata for
        validation. Import still requires the caller to provide the target
        frame, because hybrid DSm constraints are model semantics rather than
        just mass data.
        """

        data = {
            "schema": _MASS_JSON_SCHEMA,
            "frame": {
                "atoms": list(self.frame.atoms),
                "model": self.frame.model,
                "region_count": self.frame.region_count,
            },
            "masses": self.to_dict(),
        }
        return json.dumps(data, indent=indent)

    @classmethod
    def from_json(cls, frame, text: str | bytes, **kwargs: Any) -> "MassFunction":
        """Create a mass function from JSON produced by :meth:`to_json`."""

        data = json.loads(text)
        if not isinstance(data, MappingABC):
            raise ValueError("Mass JSON must contain an object.")
        schema = data.get("schema")
        if schema is not None and schema != _MASS_JSON_SCHEMA:
            raise ValueError(f"Unsupported mass JSON schema: {schema!r}.")
        return cls.from_dict(frame, data, **kwargs)

    def to_csv(
        self,
        *,
        include_header: bool = True,
        float_format: str | None = None,
    ) -> str:
        """Serialize this mass assignment to CSV text.

        The CSV has two columns: ``proposition`` and ``mass``. It is intended
        for data exchange and round trips, not for presentation tables.
        """

        output = StringIO()
        writer = csv.writer(output, lineterminator="\n")
        if include_header:
            writer.writerow(("proposition", "mass"))
        for prop, value in self.items():
            writer.writerow((str(prop), self._format_number(value, float_format)))
        return output.getvalue()

    @classmethod
    def from_csv(
        cls,
        frame,
        text: str,
        *,
        has_header: bool = True,
        **kwargs: Any,
    ) -> "MassFunction":
        """Create a mass function from CSV text with proposition and mass columns."""

        rows = csv.reader(StringIO(text))
        values: dict[str, float] = {}
        if has_header:
            try:
                header = next(rows)
            except StopIteration as exc:
                raise ValueError("Mass CSV is empty.") from exc
            normalized = [cell.strip().lower() for cell in header]
            if normalized != ["proposition", "mass"]:
                raise ValueError("Mass CSV header must be: proposition,mass.")

        for row_number, row in enumerate(rows, start=2 if has_header else 1):
            if not row or all(not cell.strip() for cell in row):
                continue
            if len(row) != 2:
                raise ValueError(f"Mass CSV row {row_number} must have two columns.")
            proposition, value = row
            try:
                mass = float(value)
            except ValueError as exc:
                raise ValueError(f"Mass CSV row {row_number} has invalid mass {value!r}.") from exc
            values[proposition] = values.get(proposition, 0.0) + mass
        return cls(frame, values, **kwargs)

    def to_latex(
        self,
        *,
        columns: Sequence[str] = ("mass",),
        rows: str = "focal",
        caption: str | None = None,
        label: str | None = None,
        float_format: str | None = ".4f",
        booktabs: bool = True,
        position: str = "htbp",
    ) -> str:
        """Export this mass function as a LaTeX table string.

        Parameters
        ----------
        columns:
            Any of ``mass``, ``belief``, ``plausibility``, or ``commonality``.
            Short aliases ``m``, ``bel``, ``pl``, and ``q`` are accepted.
        rows:
            ``"focal"`` for stored non-zero masses, or ``"all"`` for every
            proposition generated by the frame. ``"all"`` can be large for
            DSmT frames.
        caption, label:
            Optional LaTeX table metadata.
        float_format:
            Python format specifier such as ``".4f"``. Percent-style formats
            such as ``"%0.4f"`` are also accepted.
        booktabs:
            Use ``toprule``/``midrule``/``bottomrule`` instead of ``hline``.
        position:
            LaTeX table position specifier.
        """

        resolved_columns = self._resolve_export_columns(columns)
        row_props = self._export_rows(rows)
        alignment = "l" + ("r" * len(resolved_columns))
        lines = [f"\\begin{{table}}[{position}]", "\\centering"]
        if caption is not None:
            lines.append(f"\\caption{{{self._latex_escape_text(caption)}}}")
        if label is not None:
            lines.append(f"\\label{{{label}}}")
        lines.append(f"\\begin{{tabular}}{{{alignment}}}")
        lines.append("\\toprule" if booktabs else "\\hline")
        headers = ["Proposition", *(heading for heading, _ in resolved_columns)]
        lines.append(" & ".join(headers) + r" \\")
        lines.append("\\midrule" if booktabs else "\\hline")
        for prop in row_props:
            values = [
                self._format_number(self._export_value(prop, method), float_format)
                for _, method in resolved_columns
            ]
            lines.append(" & ".join((self._latex_proposition(prop), *values)) + r" \\")
        lines.append("\\bottomrule" if booktabs else "\\hline")
        lines.extend(["\\end{tabular}", "\\end{table}"])
        return "\n".join(lines)

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

    def pignistic(self, *, normalize_conflict: bool = True) -> dict[str, float]:
        """Return pignistic scores for singleton hypotheses.

        This is the classical pignistic transformation on DST frames. On free
        or hybrid DSmT frames, singleton hypotheses can overlap, so the returned
        event scores are useful for decisions but do not have to sum to one.

        If ``normalize_conflict`` is true, mass assigned to the empty proposition
        is ignored and the remaining scores are rescaled by ``1 - conflict``.
        This makes TBM/Smets results usable for pignistic decisions while still
        allowing raw unnormalized scores with ``normalize_conflict=False``.
        """

        denominator = 1.0
        if normalize_conflict:
            denominator = 1.0 - self.conflict
            if denominator <= self.tolerance:
                raise TotalConflictError(
                    "Pignistic transformation is undefined at total conflict."
                )

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
                    result[name] += mass * overlap / cardinality / denominator
        return result

    def pignistic_regions(self, *, normalize_conflict: bool = True) -> dict[str, float]:
        """Return a probability distribution over model Venn regions.

        If ``normalize_conflict`` is true, empty-set conflict is excluded and
        the non-empty region probabilities are rescaled by ``1 - conflict``.
        """

        denominator = 1.0
        if normalize_conflict:
            denominator = 1.0 - self.conflict
            if denominator <= self.tolerance:
                raise TotalConflictError(
                    "Pignistic transformation is undefined at total conflict."
                )

        result = {self._format_region(region): 0.0 for region in self.frame._universe}
        for prop, mass in self._masses.items():
            if not prop:
                continue
            cardinality = prop.cardinality
            if cardinality == 0:
                continue
            share = mass / cardinality / denominator
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

    @staticmethod
    def _validate_frame_metadata(frame, metadata: Any) -> None:
        if metadata is None:
            return
        if not isinstance(metadata, MappingABC):
            raise ValueError("Mass frame metadata must be an object.")
        atoms = metadata.get("atoms")
        if atoms is not None and tuple(atoms) != frame.atoms:
            raise ValueError("Mass data frame atoms do not match the target frame.")
        model = metadata.get("model")
        if model is not None and model != frame.model:
            raise ValueError("Mass data frame model does not match the target frame.")
        region_count = metadata.get("region_count")
        if region_count is not None and int(region_count) != frame.region_count:
            raise ValueError("Mass data frame region count does not match the target frame.")

    @staticmethod
    def _format_number(value: float, float_format: str | None) -> str:
        if float_format is None:
            return str(value)
        if "%" in float_format:
            return float_format % value
        return format(value, float_format)

    @staticmethod
    def _resolve_export_columns(columns: Sequence[str]) -> tuple[tuple[str, str], ...]:
        if not columns:
            raise ValueError("At least one export column is required.")
        resolved: list[tuple[str, str]] = []
        for column in columns:
            key = column.lower().strip()
            try:
                resolved.append(_EXPORT_COLUMNS[key])
            except KeyError as exc:
                choices = ", ".join(sorted(_EXPORT_COLUMNS))
                raise ValueError(f"Unknown export column {column!r}; choose from {choices}.") from exc
        return tuple(resolved)

    def _export_rows(self, rows: str) -> tuple[Proposition, ...]:
        if rows == "focal":
            return self.focal()
        if rows == "all":
            return self.frame.elements()
        raise ValueError("rows must be 'focal' or 'all'.")

    def _export_value(self, prop: Proposition, method: str) -> float:
        if method == "mass":
            return self.mass(prop)
        if method == "belief":
            return self.belief(prop)
        if method == "plausibility":
            return self.plausibility(prop)
        if method == "commonality":
            return self.commonality(prop)
        raise AssertionError(f"Unhandled export method: {method}")

    @classmethod
    def _latex_proposition(cls, prop: Proposition) -> str:
        if not prop:
            return r"$\emptyset$"
        terms = []
        for term in str(prop).split("|"):
            factors = [cls._latex_escape_math(part) for part in term.split("&")]
            terms.append(r" \cap ".join(factors))
        return "$" + r" \cup ".join(terms) + "$"

    @staticmethod
    def _latex_escape_text(value: str) -> str:
        replacements = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        return "".join(replacements.get(char, char) for char in value)

    @classmethod
    def _latex_escape_math(cls, value: str) -> str:
        return cls._latex_escape_text(value).replace(r"\textbackslash{}", r"\backslash{}")
