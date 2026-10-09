"""Fidelity of fusion rules to their published definitions (v1.3.0 fixes).

Each test pins a case where an earlier implementation deviated from the
original rule: silent trimming and renormalization of fusion results, DSmC
applied outside the free DSm model, Yager on unnormalized sources, and
Dubois-Prade restricted to two sources and static models.
"""

from __future__ import annotations

import random
from fractions import Fraction
from itertools import product
from math import prod

import pytest
from pytest import approx

from evidencelib import Frame, MassFunction
from evidencelib.exceptions import InvalidMassError, TotalConflictError

# ---------------------------------------------------------------------------
# 1. Fusion results are exact: no trimming, no silent renormalization
# ---------------------------------------------------------------------------


def test_dempster_keeps_small_products_before_normalization() -> None:
    # K is close to one, so Dempster's 1/(1-K) amplifies every non-conflicting
    # product.  Trimming products below the tolerance changed the answer from
    # {A: 0.45, B: 0.55} to {B: 1.0}.
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    eps = 3e-5
    small = 1.1e-9 / (1 - eps)
    m1 = frame.mass({a: eps, b: 1 - eps})
    m2 = frame.mass({a: eps, b: small, c: 1 - eps - small})

    result = m1.dempster(m2)

    assert result[a] == approx(0.45, rel=1e-6)
    assert result[b] == approx(0.55, rel=1e-6)
    assert result.total_mass == approx(1.0)


def test_dempster_is_defined_for_any_conflict_below_one() -> None:
    # K = 1 - 9e-10 < 1, so Dempster's rule is defined and gives {A: 1}.
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    eps = 3e-5

    result = frame.mass({a: eps, b: 1 - eps}).dempster(frame.mass({a: eps, c: 1 - eps}))

    assert result.to_dict() == {"A": approx(1.0)}


def test_dempster_raises_only_at_total_conflict() -> None:
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()

    with pytest.raises(TotalConflictError):
        frame.mass({a: 1.0}).dempster(frame.mass({b: 1.0}))


def test_conjunctive_keeps_products_below_tolerance() -> None:
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    m1 = frame.mass({a: 1e-6, b: 1 - 1e-6})
    m2 = frame.mass({a: 1e-6, b: 1 - 1e-6})

    result = m1.conjunctive(m2)

    assert result[a] == approx(1e-12, rel=1e-9, abs=0.0)
    assert result.total_mass == approx(1.0)


def test_pignistic_near_total_conflict_is_defined() -> None:
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    eps = 3e-5
    tbm = frame.mass({a: eps, b: 1 - eps}).smets(frame.mass({a: eps, c: 1 - eps}))

    assert tbm.pignistic()["A"] == approx(1.0)


def _exact_dempster(sources, atoms):
    combined: dict[frozenset[str], Fraction] = {}
    for combo in product(*[list(source.items()) for source in sources]):
        focal = frozenset.intersection(*(frozenset(str(p).split("|")) for p, _ in combo))
        amount = prod((Fraction(v) for _, v in combo), start=Fraction(1))
        combined[focal] = combined.get(focal, Fraction(0)) + amount
    conflict = combined.pop(frozenset(), Fraction(0))
    if not combined:
        return {}
    return {"|".join(sorted(k, key=atoms.index)): v / (1 - conflict) for k, v in combined.items()}


def test_dempster_matches_exact_rational_computation() -> None:
    atoms = ["A", "B", "C", "D"]
    frame = Frame.dst(atoms)
    elements = [prop for prop in frame.elements() if prop]
    rng = random.Random(1976)
    for _ in range(40):
        sources = []
        for _ in range(3):
            chosen = rng.sample(elements, rng.randint(1, 4))
            weights = [rng.random() ** 6 + 1e-7 for _ in chosen]
            total = sum(weights)
            sources.append(frame.mass({p: w / total for p, w in zip(chosen, weights)}))
        expected = _exact_dempster(sources, atoms)
        if not expected:
            # Total conflict: no non-empty product survives.
            with pytest.raises(TotalConflictError):
                sources[0].dempster(*sources[1:])
            continue
        result = sources[0].dempster(*sources[1:])
        for key, value in expected.items():
            assert result[key] == approx(float(value), rel=1e-9, abs=1e-15)


# ---------------------------------------------------------------------------
# 2. DSmC is defined on the free DSm model only
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "frame",
    [Frame.dst(["A", "B"]), Frame.hybrid(["A", "B", "C"], empty=["A&B"])],
    ids=["dst", "hybrid"],
)
def test_dsmc_rejects_non_free_models(frame: Frame) -> None:
    m1 = frame.mass({"A": 0.6, "B": 0.4})
    m2 = frame.mass({"A": 0.3, "B": 0.7})

    with pytest.raises(ValueError, match="free DSm model"):
        m1.dsmc(m2)
    assert m1.conjunctive(m2).conflict > 0  # the TBM result remains available


def test_dsmc_on_free_model_equals_conjunctive_formula() -> None:
    frame = Frame.dsmt(["A", "B"])
    a, b = frame.symbols()
    m1 = frame.mass({a: 0.6, b: 0.4})
    m2 = frame.mass({a: 0.3, b: 0.7})

    result = m1.dsmc(m2)

    assert result.to_dict() == approx(
        {"A": 0.18, "B": 0.28, "A&B": 0.6 * 0.7 + 0.4 * 0.3}
    )
    assert result.conflict == 0.0


# ---------------------------------------------------------------------------
# 4. Yager's rule combines normal assignments
# ---------------------------------------------------------------------------


def test_yager_rejects_unnormalized_sources() -> None:
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    tbm = frame.mass({a: 0.6, b: 0.4}).smets(frame.mass({a: 0.3, c: 0.7}))
    assert tbm.conflict > 0

    with pytest.raises(ValueError, match="Yager requires"):
        tbm.yager(frame.mass({a: 1.0}))


# ---------------------------------------------------------------------------
# Domain checks: closed-world rules require m(empty) = 0 exactly
# ---------------------------------------------------------------------------


def _tiny_tbm_conflict():
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    tbm = frame.mass({a: 1e-6, frame.total: 1 - 1e-6}).smets(
        frame.mass({b: 1e-6, frame.total: 1 - 1e-6})
    )
    assert tbm.conflict == approx(1e-12)  # below the default tolerance
    return frame, tbm


@pytest.mark.parametrize(
    "rule", ["yager", "dubois_prade", "dsmh", "pcr5", "pcr6", "pcr5_plus", "pcr6_plus"]
)
def test_closed_world_rules_reject_any_positive_empty_mass(rule) -> None:
    frame, tbm = _tiny_tbm_conflict()

    with pytest.raises(ValueError, match="m\\(empty\\) = 0|collapsed onto empty"):
        getattr(tbm, rule)(frame.mass({"A": 1.0}))


def test_measures_reject_any_positive_empty_mass() -> None:
    _, tbm = _tiny_tbm_conflict()

    with pytest.raises(InvalidMassError, match="m\\(empty\\) = 0"):
        tbm.deng_entropy()


def test_dsmc_rejects_source_mass_on_empty() -> None:
    frame = Frame.dsmt(["A", "B"])
    vacuous_conflict = MassFunction(frame, {frame.empty: 1.0})

    with pytest.raises(ValueError, match="DSmC requires"):
        vacuous_conflict.dsmc(frame.mass({"A": 1.0}))


# ---------------------------------------------------------------------------
# PCR6 (eqs. 16-17): no tolerance cutoff, no premature underflow
# ---------------------------------------------------------------------------


def test_pcr6_redistributes_conflicts_with_masses_below_tolerance() -> None:
    # Sources produced by fusion keep masses below their tolerance; PCR6 must
    # redistribute every conflicting product, not skip those whose masses sum
    # to at most the tolerance.
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    base1 = frame.mass({a: 0.02, b: 0.98}, tolerance=0.01)
    base2 = frame.mass({a: 0.98, b: 0.02}, tolerance=0.01)
    m1 = base1.dempster(base1)
    m2 = base2.dempster(base2)
    assert min(value for _, value in m1.items()) < 0.01

    result = m1.pcr6(m2)

    assert result[a] == approx(0.5, abs=1e-15)
    assert result[b] == approx(0.5, abs=1e-15)


def test_pcr6_shares_do_not_underflow_before_division() -> None:
    frame = Frame.dst(["A", "B", "C", "D"])
    a, b, c, d = frame.symbols()
    x = 1e-110
    m1 = frame.mass({a: x, c: 1 - x}, tolerance=0.0)
    m2 = frame.mass({b: x, d: 1 - x}, tolerance=0.0)

    result = m1.pcr6(m2)

    # A receives half of m1(A) m2(B) = x^2 and the share x / (x + 1 - x) of
    # m1(A) m2(D) = x (1 - x): m(A) = 1.5e-220.  Computing amount * mass first
    # underflowed the second term to zero.
    expected_a = x * (1 - x) * (x / (x + 1 - x)) + x * x * 0.5
    assert result[a] == approx(expected_a, rel=1e-9, abs=0.0)


# ---------------------------------------------------------------------------
# Pignistic transformation: normalize before splitting (subnormal masses)
# ---------------------------------------------------------------------------


def test_pignistic_normalizes_before_dividing_by_cardinality() -> None:
    frame = Frame.dst(["A", "B", "C", "D"])
    a, b, c, d = frame.symbols()
    x = 2e-162
    tbm = frame.mass({a | b: x, c: 1 - x}, tolerance=0.0).smets(
        frame.mass({a | b: x, d: 1 - x}, tolerance=0.0)
    )
    assert 0.0 < tbm[a | b] < 1e-300

    assert tbm.pignistic() == approx({"A": 0.5, "B": 0.5, "C": 0.0, "D": 0.0})
    assert tbm.pignistic_regions() == approx({"A": 0.5, "B": 0.5, "C": 0.0, "D": 0.0})


# ---------------------------------------------------------------------------
# Incomplete assignments (dynamic Dubois-Prade) are not silently rescaled
# ---------------------------------------------------------------------------


def _dynamic_dubois_prade():
    source = Frame.dsmt(["t1", "t2", "t3"])
    t1, t2, t3 = source.symbols()
    m1 = source.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
    m2 = source.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})
    target = Frame.hybrid(["t1", "t2", "t3"], exclusive=True, empty=["t3"])
    result = m1.dubois_prade(m2, model=target)
    assert result.total_mass == approx(0.94)
    return target, result


def test_incomplete_assignment_is_rejected_where_a_bba_is_required() -> None:
    target, incomplete = _dynamic_dubois_prade()
    t1 = target.proposition("t1")

    with pytest.raises(InvalidMassError, match="summing to 1"):
        incomplete.pignistic()
    with pytest.raises(InvalidMassError, match="summing to 1"):
        incomplete.deng_entropy()
    with pytest.raises(InvalidMassError, match="summing to 1"):
        incomplete.dempster(target.mass({t1: 1.0}))
    # Direct readings of the assignment remain available.
    assert incomplete.belief(t1) == approx(0.34)


def test_incomplete_assignment_can_be_normalized_explicitly() -> None:
    _, incomplete = _dynamic_dubois_prade()

    normalized = incomplete.normalize()

    assert normalized.total_mass == approx(1.0)
    assert normalized["t1"] == approx(0.34 / 0.94)
    assert normalized.pignistic()["t1"] == approx((0.34 + 0.35 / 2) / 0.94)


# ---------------------------------------------------------------------------
# Lossless import/export of computed results
# ---------------------------------------------------------------------------


def test_exact_json_and_csv_round_trips_keep_tiny_masses() -> None:
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    fused = frame.mass({a: 1e-6, b: 1 - 1e-6}).dempster(frame.mass({a: 1e-6, b: 1 - 1e-6}))
    assert 0.0 < fused[a] < fused.tolerance

    for restored in (
        MassFunction.from_json(frame, fused.to_json(), exact=True),
        MassFunction.from_csv(frame, fused.to_csv(), exact=True),
        MassFunction.from_dict(frame, fused.to_dict(), exact=True),
    ):
        assert restored.to_dict() == fused.to_dict()
    # The default import treats data as elicited input and cleans it.
    assert MassFunction.from_json(frame, fused.to_json()).to_dict() == {"B": 1.0}


def test_exact_import_restores_incomplete_assignment() -> None:
    target, incomplete = _dynamic_dubois_prade()

    restored = MassFunction.from_json(target, incomplete.to_json(), exact=True)

    assert restored.to_dict() == incomplete.to_dict()
    with pytest.raises(InvalidMassError):
        MassFunction.from_json(target, incomplete.to_json())


def test_exact_import_validates_values() -> None:
    frame = Frame.dst(["A", "B"])

    with pytest.raises(InvalidMassError):
        MassFunction.from_dict(frame, {"A": -0.1, "B": 1.1}, exact=True)
    with pytest.raises(TypeError, match="validate"):
        MassFunction.from_dict(frame, {"A": 1.0}, exact=True, validate=True)


def test_latex_comparison_lists_masses_below_tolerance() -> None:
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    fused = frame.mass({a: 1e-6, b: 1 - 1e-6}).dempster(frame.mass({a: 1e-6, b: 1 - 1e-6}))

    table = fused.comparison_to_latex(frame.mass({a: 1.0}), orientation="long", float_format=None)

    assert 0.0 < fused[a] < fused.tolerance
    assert repr(fused[a]) in table


def test_latex_comparison_accepts_incomplete_assignment() -> None:
    target, incomplete = _dynamic_dubois_prade()

    table = incomplete.comparison_to_latex(incomplete.normalize(), float_format=".2f")

    assert "0.35" in table


# ---------------------------------------------------------------------------
# Review round 2: extreme magnitudes and tiny Dubois-Prade losses
# ---------------------------------------------------------------------------


def _tiny_dynamic_dubois_prade():
    source = Frame.dst(["A", "B"])
    a, b = source.symbols()
    m = source.mass({a: 1 - 1e-6, b: 1e-6})
    target = Frame.hybrid(["A", "B"], exclusive=True, empty=["B"])
    result = m.dubois_prade(m, model=target)
    # m(B) m(B) = 1e-12 is lost: far below any floating-point slack.
    assert result.total_mass == approx(1 - 1e-12, abs=1e-18)
    return target, result


def test_tiny_dubois_prade_loss_is_still_an_incomplete_assignment() -> None:
    target, incomplete = _tiny_dynamic_dubois_prade()

    with pytest.raises(InvalidMassError, match="summing to 1"):
        incomplete.pignistic()
    with pytest.raises(InvalidMassError, match="summing to 1"):
        incomplete.deng_entropy()
    with pytest.raises(InvalidMassError, match="summing to 1"):
        incomplete.dempster(target.mass({"A": 1.0}))
    assert incomplete.normalize().pignistic()["A"] == approx(1.0)


def test_lost_mass_survives_json_round_trip() -> None:
    target, incomplete = _tiny_dynamic_dubois_prade()
    text = incomplete.to_json()

    restored = MassFunction.from_json(target, text, exact=True)

    with pytest.raises(InvalidMassError, match="summing to 1"):
        restored.pignistic()
    with pytest.raises(InvalidMassError, match="exact=True"):
        MassFunction.from_json(target, text)


def test_measures_accept_subnormal_masses() -> None:
    frame = Frame.dst(["A", "B", "C", "D"])
    a, b, c, d = frame.symbols()
    m = frame.mass({a | b: 2e-162, c | d: 1 - 2e-162}, tolerance=0.0)
    fused = m.dempster(m)
    assert 0.0 < fused[a | b] < 1e-300

    # Contributions of a subnormal mass are ~0; the measures stay finite and
    # equal those of the categorical assignment {C|D: 1}.
    categorical = frame.mass({c | d: 1.0})
    assert fused.deng_entropy() == approx(categorical.deng_entropy())
    assert fused.tfb_entropy(2) == approx(categorical.tfb_entropy(2))
    assert fused.information_volume() == approx(categorical.information_volume())


def test_dempster_survives_product_underflow() -> None:
    # The only non-empty product, 1e-200 * 1e-200, underflows in floating
    # point, but it is positive, so K < 1 and Dempster's rule gives {A: 1}.
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    x = 1e-200
    m1 = frame.mass({a: x, b: 1 - x}, tolerance=0.0)
    m2 = frame.mass({a: x, c: 1 - x}, tolerance=0.0)

    assert m1.dempster(m2).to_dict() == {"A": approx(1.0)}


def test_exact_import_rejects_non_finite_aggregates() -> None:
    frame = Frame.dst(["A", "B"])

    with pytest.raises(InvalidMassError, match="finite"):
        MassFunction.from_dict(frame, {"A": 1e308, "A&A": 1e308}, exact=True)
