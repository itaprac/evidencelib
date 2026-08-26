"""Generate the hyper-power-set scale values used in the SoftwareX article.

For dimensions two through five, the script enumerates ``Frame.elements()``
and checks the result against an independent count of antichains in the
Boolean lattice.  For dimension six, it performs only the count: materializing
millions of ``Proposition`` objects is deliberately avoided.
"""

from __future__ import annotations

from functools import cache
from typing import NamedTuple

from evidencelib import Frame


class ScaleRow(NamedTuple):
    """One verified row of the article's scale table."""

    dimension: int
    power_set_cardinality: int
    hyper_power_set_cardinality: int
    status: str
    verification: str


_STATUSES = {
    2: "trivial",
    3: "Section 3.2 case",
    4: "practical",
    5: "borderline",
    6: "infeasible to materialize",
}


def count_free_hyper_power_set(dimension: int) -> int:
    """Count free-DSm propositions without materializing them.

    A free-DSm proposition has a unique monotone disjunctive normal form.
    Its minimal conjunctions form an antichain of the non-empty subsets of
    the frame.  Counting independent sets in the subset-comparability graph
    therefore gives ``|D^Theta|`` exactly.
    """

    if dimension < 1:
        raise ValueError("dimension must be positive")

    terms = tuple(range(1, 1 << dimension))
    comparable_masks: list[int] = []
    for left in terms:
        mask = 0
        for index, right in enumerate(terms):
            if (left & right) in {left, right}:
                mask |= 1 << index
        comparable_masks.append(mask)

    @cache
    def count(candidates: int) -> int:
        if candidates == 0:
            return 1
        selected_bit = candidates & -candidates
        index = selected_bit.bit_length() - 1
        without_selected = count(candidates ^ selected_bit)
        with_selected = count(candidates & ~comparable_masks[index])
        return without_selected + with_selected

    return count((1 << len(terms)) - 1)


def generate_scale_rows() -> tuple[ScaleRow, ...]:
    """Generate and cross-check all rows proposed for the manuscript."""

    rows: list[ScaleRow] = []
    for dimension, status in _STATUSES.items():
        counted = count_free_hyper_power_set(dimension)
        if dimension <= 5:
            frame = Frame.dsmt([f"t{index}" for index in range(1, dimension + 1)])
            enumerated = len(frame.elements())
            if enumerated != counted:
                raise AssertionError(
                    f"enumeration/count mismatch for dimension {dimension}: "
                    f"{enumerated} != {counted}"
                )
            verification = "Frame.elements() and independent count"
        else:
            verification = "independent count; propositions not materialized"

        rows.append(
            ScaleRow(
                dimension=dimension,
                power_set_cardinality=1 << dimension,
                hyper_power_set_cardinality=counted,
                status=status,
                verification=verification,
            )
        )
    return tuple(rows)


def main() -> None:
    """Print the verified values in a manuscript-friendly table."""

    print("| Frame size | Power-set size | Hyper-power-set size | Status | Verification |")
    print("|---:|---:|---:|---|---|")
    for row in generate_scale_rows():
        print(
            f"| {row.dimension} | {row.power_set_cardinality} | "
            f"{row.hyper_power_set_cardinality} | {row.status} | "
            f"{row.verification} |"
        )


if __name__ == "__main__":
    main()
