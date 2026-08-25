"""Tests for the uncertainty measures of :class:`MassFunction`.

Reference values come from the defining papers: Y. Deng, "Information volume
of mass function", IJCCC 15(6) (2020) 3983 (Examples 4.1-4.3); Q. Zhou and
Y. Deng, "Higher order information volume of mass function", Information
Sciences 586 (2022) 501-513; Q. Zhou and Y. Deng, "Fractal-based belief
entropy" (arXiv:2012.00235).
"""

from __future__ import annotations

from math import log2

import pytest
from pytest import approx

from evidencelib import Frame
from evidencelib.exceptions import InvalidMassError


def _uniform_over_power_set(frame):
    a, b, c = frame.symbols()
    props = [a, b, c, a | b, a | c, b | c, a | b | c]
    return frame.mass({prop: 1 / 7 for prop in props})


def test_deng_entropy_matches_literature_value() -> None:
    frame = Frame.dst(["a", "b", "c"])
    mass = _uniform_over_power_set(frame)

    assert mass.deng_entropy() == approx(3.887675, abs=1e-6)


def test_deng_entropy_is_zero_for_a_certain_singleton() -> None:
    frame = Frame.dst(["a", "b"])
    a, _ = frame.symbols()

    assert frame.mass({a: 1.0}).deng_entropy() == approx(0.0)


def test_deng_entropy_reduces_to_shannon_for_bayesian_masses() -> None:
    frame = Frame.dst(["a", "b", "c"])
    a, b, c = frame.symbols()
    mass = frame.mass({a: 0.5, b: 0.3, c: 0.2})

    shannon = -(0.5 * log2(0.5) + 0.3 * log2(0.3) + 0.2 * log2(0.2))
    assert mass.deng_entropy() == approx(shannon)
    assert mass.fractal_belief_entropy() == approx(shannon)
    assert mass.strife() == approx(shannon)
    assert mass.nonspecificity() == approx(0.0)


def test_tfb_entropy_order_one_is_deng_entropy() -> None:
    frame = Frame.dst(["a", "b", "c"])
    mass = _uniform_over_power_set(frame)

    assert mass.tfb_entropy(order=1) == approx(mass.deng_entropy())


def test_tfb_entropy_of_the_vacuous_assignment_hits_the_hoivmf_bound() -> None:
    # Zhou and Deng (2022), Example 3.3: E_k = log2((k+1)^n - k^n) for the
    # vacuous assignment; its maximum over assignments is the HOIVMF
    # log2((k+2)^n - (k+1)^n).
    frame = Frame.dst(["a", "b"])
    vacuous = frame.mass({frame.total: 1.0})

    for order in (1, 2, 3, 4):
        expected = log2((order + 1) ** 2 - order**2)
        assert vacuous.tfb_entropy(order=order) == approx(expected)


def test_tfb_entropy_rejects_non_positive_order() -> None:
    frame = Frame.dst(["a", "b"])
    a, _ = frame.symbols()

    with pytest.raises(ValueError):
        frame.mass({a: 1.0}).tfb_entropy(order=0)


def test_fractal_belief_entropy_of_the_vacuous_assignment() -> None:
    # Zhou and Deng: the vacuous assignment reaches the maximum log2(2^n - 1).
    frame = Frame.dst(["a", "b"])
    vacuous = frame.mass({frame.total: 1.0})

    assert vacuous.fractal_belief_entropy() == approx(log2(3))


def test_information_volume_matches_deng_2020_examples() -> None:
    frame = Frame.dst(["a", "b", "c"])
    a, b, c = frame.symbols()

    # Example 4.1: Bayesian assignments keep their Shannon entropy.
    uniform = frame.mass({a: 1 / 3, b: 1 / 3, c: 1 / 3})
    assert uniform.information_volume() == approx(1.584963, abs=1e-6)

    # Example 4.2: uniform assignment over the seven non-empty subsets.
    assert _uniform_over_power_set(frame).information_volume() == approx(
        5.199486, abs=1e-6
    )

    # Example 4.3: the maximum Deng entropy assignment on a two-element frame.
    small = Frame.dst(["x", "y"])
    x, y = small.symbols()
    maximum = small.mass({x: 0.2, y: 0.2, x | y: 0.6})
    assert maximum.information_volume() == approx(3.425933, abs=1e-6)


def test_information_volume_exceeds_deng_entropy_for_compound_focals() -> None:
    frame = Frame.dst(["a", "b", "c"])
    mass = _uniform_over_power_set(frame)

    assert mass.information_volume() > mass.deng_entropy()


def test_nonspecificity_of_the_vacuous_assignment() -> None:
    frame = Frame.dst(["a", "b"])

    assert frame.mass({frame.total: 1.0}).nonspecificity() == approx(1.0)


def test_measures_use_dsm_cardinality_on_dsmt_frames() -> None:
    frame = Frame.dsmt(["p", "q"])
    p, q = frame.symbols()

    # p & q covers a single Venn region: it is an elementary state, so a
    # certain assignment on it carries no uncertainty.
    assert frame.mass({p & q: 1.0}).deng_entropy() == approx(0.0)

    # p covers two Venn regions, so a certain assignment on it keeps the
    # nonspecificity of a two-region proposition.
    certain_p = frame.mass({p: 1.0})
    assert certain_p.deng_entropy() == approx(log2(3))
    assert certain_p.nonspecificity() == approx(1.0)

    # The total proposition covers three Venn regions.
    vacuous = frame.mass({frame.total: 1.0})
    assert vacuous.fractal_belief_entropy() == approx(log2(7))


def test_measures_reject_assignments_with_empty_set_mass() -> None:
    frame = Frame.dst(["a", "b"])
    a, b = frame.symbols()
    smets = frame.mass({a: 0.7, a | b: 0.3}).smets(frame.mass({b: 0.6, a | b: 0.4}))
    assert smets.conflict > 0.0

    with pytest.raises(InvalidMassError):
        smets.deng_entropy()
    with pytest.raises(InvalidMassError):
        smets.information_volume()
