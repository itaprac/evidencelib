"""Conformance tests for Dezert and Smarandache's DSmT introduction.

The page references below refer to ``IntroductionToDSmT.pdf`` (2011), as
provided with the project review.  These tests intentionally exercise the
paper's numerical examples and formulas independently of the smaller unit
tests for individual implementation details.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from pytest import approx

from evidencelib import Frame
from evidencelib.proposition import Proposition


def _assert_mass_function(result, expected: Mapping[Proposition, float]) -> None:
    """Assert both the support and values of a normalized fusion result."""

    assert result.frame is next(iter(expected)).frame
    assert set(result.focal()) == set(expected)
    assert result.total_mass == approx(1.0)
    for proposition, value in expected.items():
        assert result[proposition] == approx(value)


@pytest.mark.parametrize(
    ("dimension", "cardinality"),
    [(1, 2), (2, 5), (3, 19), (4, 167), (5, 7580)],
)
def test_free_hyper_power_set_cardinalities_from_table_2(
    dimension: int,
    cardinality: int,
) -> None:
    # Paper pp. 4-5 and Table 2: Dedekind cardinalities of D^Theta.
    frame = Frame.dsmt([f"t{index}" for index in range(1, dimension + 1)])

    assert len(frame.elements()) == cardinality


def test_dsm_cardinality_table_for_the_paper_hybrid_model() -> None:
    # Paper p. 28.  The section 2.2 model permits t1&t2, while all
    # intersections involving t3 are constrained to be empty.
    frame = Frame.hybrid(
        ["t1", "t2", "t3"],
        empty=["t1&t3", "t2&t3"],
    )
    t1, t2, t3 = frame.symbols()

    expected = {
        frame.empty: 0,
        t1 & t2: 1,
        t3: 1,
        t1: 2,
        t2: 2,
        t1 | t2: 3,
        t1 | t3: 3,
        t2 | t3: 3,
        t1 | t2 | t3: 4,
    }

    assert {proposition: proposition.cardinality for proposition in expected} == expected


def test_dsmc_example_from_pages_15_and_16() -> None:
    frame = Frame.dsmt(["t1", "t2", "t3"])
    t1, t2, t3 = frame.symbols()
    m1 = frame.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
    m2 = frame.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})

    result = m1.dsmc(m2)

    _assert_mass_function(
        result,
        {
            t1: 0.21,
            t2: 0.11,
            t3: 0.06,
            t1 | t2: 0.03,
            t1 & t2: 0.21,
            t1 & t3: 0.13,
            t2 & t3: 0.14,
            t3 & (t1 | t2): 0.11,
        },
    )


def test_dempster_smets_and_yager_example_from_pages_15_and_16() -> None:
    # Shafer exclusivity and the non-existential constraint t3=empty are both
    # part of the model used for these three results in the paper.
    source = Frame.dst(["t1", "t2", "t3"])
    t1, t2, t3 = source.symbols()
    m1 = source.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
    m2 = source.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})
    frame = Frame.hybrid(["t1", "t2", "t3"], exclusive=True, empty=["t3"])
    target_t1, target_t2, _ = frame.symbols()

    dempster = m1.dempster(m2, model=frame)
    _assert_mass_function(
        dempster,
        {
            target_t1: 0.21 / 0.35,
            target_t2: 0.11 / 0.35,
            target_t1 | target_t2: 0.03 / 0.35,
        },
    )

    smets = m1.smets(m2, model=frame)
    assert set(smets.focal()) == {
        frame.empty,
        target_t1,
        target_t2,
        target_t1 | target_t2,
    }
    assert smets.total_mass == approx(1.0)
    assert smets.conflict == approx(0.65)
    assert smets[target_t1] == approx(0.21)
    assert smets[target_t2] == approx(0.11)
    assert smets[target_t1 | target_t2] == approx(0.03)

    _assert_mass_function(
        m1.yager(m2, model=frame),
        {
            target_t1: 0.21,
            target_t2: 0.11,
            target_t1 | target_t2: 0.68,
        },
    )


def test_dynamic_dsmh_example_uses_an_explicit_target_model() -> None:
    # Paper pp. 15-16: source masses are defined before t3 is discovered to be
    # non-existent.  DSmH therefore combines on the free model and transfers
    # the products under the newly supplied hybrid target model.
    source_frame = Frame.dsmt(["t1", "t2", "t3"])
    t1, t2, t3 = source_frame.symbols()
    m1 = source_frame.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
    m2 = source_frame.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})
    target_frame = Frame.hybrid(
        ["t1", "t2", "t3"],
        exclusive=True,
        empty=["t3"],
    )
    target_t1, target_t2, _ = target_frame.symbols()

    result = m1.dsmh(m2, model=target_frame)

    _assert_mass_function(
        result,
        {
            target_t1: 0.34,
            target_t2: 0.25,
            target_t1 | target_t2: 0.41,
        },
    )


def test_dsmh_s2_transfers_a_relatively_empty_conjunction_to_its_union() -> None:
    # Formulae (5)-(8), especially S2 in formula (7): if both source focal
    # elements A&B become relatively empty, u(A&B)=A|B receives their product.
    source_frame = Frame.dsmt(["A", "B", "C"])
    a, b, _ = source_frame.symbols()
    m1 = source_frame.mass({a & b: 1.0})
    m2 = source_frame.mass({a & b: 1.0})
    target_frame = Frame.hybrid(["A", "B", "C"], empty=["A&B"])
    target_a, target_b, _ = target_frame.symbols()

    result = m1.dsmh(m2, model=target_frame)

    _assert_mass_function(result, {target_a | target_b: 1.0})


def test_dubois_prade_rejects_an_explicit_dynamic_target_model() -> None:
    # Paper p. 16: Dubois-Prade loses mass in this dynamic case (total 0.94),
    # so accepting a changing target model and returning DSmH would be false.
    source_frame = Frame.dsmt(["t1", "t2", "t3"])
    t1, t2, t3 = source_frame.symbols()
    m1 = source_frame.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
    m2 = source_frame.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})
    target_frame = Frame.hybrid(
        ["t1", "t2", "t3"],
        exclusive=True,
        empty=["t3"],
    )

    with pytest.raises(ValueError, match="(?i)dynamic"):
        m1.dubois_prade(m2, model=target_frame)


@pytest.mark.parametrize(
    ("source_1", "source_2", "expected"),
    [
        (
            {"A": 0.6, "A|B": 0.4},
            {"B": 0.3, "A|B": 0.7},
            {"A": 0.540, "B": 0.180, "A|B": 0.280},
        ),
        (
            {"A": 0.6, "A|B": 0.4},
            {"A": 0.2, "B": 0.3, "A|B": 0.5},
            {"A": 0.620, "B": 0.180, "A|B": 0.200},
        ),
        (
            {"A": 0.6, "B": 0.3, "A|B": 0.1},
            {"A": 0.2, "B": 0.3, "A|B": 0.5},
            {"A": 0.584, "B": 0.366, "A|B": 0.050},
        ),
    ],
)
def test_pcr5_examples_1_to_3_from_pages_21_and_22(
    source_1: Mapping[str, float],
    source_2: Mapping[str, float],
    expected: Mapping[str, float],
) -> None:
    frame = Frame.dst(["A", "B"])
    result = frame.mass(source_1).pcr5(frame.mass(source_2))

    _assert_mass_function(
        result,
        {frame.proposition(proposition): value for proposition, value in expected.items()},
    )


def test_pcr6_three_source_redistribution_matches_formula_16() -> None:
    # A single three-source conflict A&B&B has product one and denominator
    # three.  Formula (16) assigns one share to A and two shares to B.
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    m1 = frame.mass({a: 1.0})
    m2 = frame.mass({b: 1.0})
    m3 = frame.mass({b: 1.0})

    result = m1.pcr6(m2, m3)

    _assert_mass_function(result, {a: 1 / 3, b: 2 / 3})


def test_generalized_pignistic_probability_for_any_proposition() -> None:
    # Formula (27), p. 28.  For A&B the four focal contributions below are
    # 0.2/2 + 0.3/2 + 0.4/1 + 0.1/3 = 41/60.
    frame = Frame.dsmt(["A", "B"])
    a, b = frame.symbols()
    mass = frame.mass({a: 0.2, b: 0.3, a & b: 0.4, a | b: 0.1})

    assert mass.pignistic_of(a & b) == approx(41 / 60)
    assert mass.pignistic_of(a | b) == approx(1.0)
