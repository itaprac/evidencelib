"""Conformance tests for PCR5, PCR6, PCR5+, and PCR6+ with S >= 2 sources.

Reference: T. Dezert, J. Dezert, F. Smarandache, "Improvement of Proportional
Conflict Redistribution Rules of Combination of Basic Belief Assignments",
J. Adv. Inf. Fusion 16(1):48-73, 2021 (JAIF 2021 below).  Example and table
numbers refer to that paper.  The paper rounds results to six decimals, so
printed values are checked with a tolerance of 1e-6.  Every numerical example
is additionally checked to 1e-12 against an exact rational transcription of
eqs. (14), (15), (23), (25), and (26) (``_reference_pcr``).

A few printed values are mis-rounded in the paper; all lie within 1e-6 of the
exact result:

- Example 5, PCR6(m1, m2): A|B printed 0.465309, exact 0.4653084848...
- Table I: PCR5 C|D printed 0.203385, exact 0.2033843187...; PCR5+ B printed
  0.001107, exact 0.0011075824...  The text (p. 57) gives PCR5 E = 0.115967,
  exact 0.1159663822... (Table I's 0.115966 is right).
- Table II: PCR6 E printed 0.116038, exact 0.1160374430...
- Tables XIII-XIV: Theta printed 0.212244, exact 3051/14375 = 0.2122434782...
"""

from __future__ import annotations

import random
from fractions import Fraction
from itertools import combinations, product
from math import prod

import pytest
from pytest import approx

from evidencelib import ConflictTransfer, Frame, MassFunction
from evidencelib.mass import _keeping_masks

PAPER = 1e-6
RULES = ("pcr5", "pcr6", "pcr5_plus", "pcr6_plus")


def _fuse(rule: str, sources: list[MassFunction]) -> MassFunction:
    return getattr(sources[0], rule)(*sources[1:])


def _assert_masses(result: MassFunction, expected: dict, *, abs_tol: float = PAPER) -> None:
    support = {prop for prop, value in expected.items() if value > 0}
    assert set(result.focal()) == support
    assert result.total_mass == approx(1.0)
    for prop, value in expected.items():
        assert result[prop] == approx(float(value), abs=abs_tol)


def _categorical(frame: Frame, *props) -> list[MassFunction]:
    return [frame.mass({prop: 1.0}) for prop in props]


def _reference_pcr(sources: list[MassFunction], rule: str) -> dict[str, Fraction]:
    """Exact rational PCR5/PCR6/PCR5+/PCR6+, written directly from the paper.

    Independent of the library's implementation: focal elements are frozensets
    of atom names (Shafer's model) and masses are Fractions.
    """

    def atoms(prop) -> frozenset[str]:
        return frozenset(str(prop).split("|"))

    bbas = [
        [(atoms(p), Fraction(v).limit_denominator(10**9)) for p, v in s.items()]
        for s in sources
    ]
    pcr5 = rule.startswith("pcr5")
    improved = rule.endswith("_plus")
    result: dict[frozenset[str], Fraction] = {}
    for combo in product(*bbas):
        focal = [x for x, _ in combo]
        amount = prod((m for _, m in combo), start=Fraction(1))
        meet = frozenset.intersection(*focal)
        if meet:
            result[meet] = result.get(meet, Fraction(0)) + amount
            continue
        distinct = set(focal)
        kappa = (
            {x: 0 if _eq23_discards(x, distinct) else 1 for x in distinct}
            if improved
            else dict.fromkeys(distinct, 1)
        )
        w = {}
        for x in distinct:
            masses = [m for y, m in combo if y == x]
            w[x] = kappa[x] * (prod(masses, start=Fraction(1)) if pcr5 else sum(masses))
        total = sum(w.values())
        for x, wx in w.items():
            if wx:
                result[x] = result.get(x, Fraction(0)) + amount * wx / total
    return {"|".join(sorted(x)): v for x, v in result.items() if v}


def _eq23_discards(x: frozenset[str], distinct: set[frozenset[str]]) -> bool:
    """kappa_j(x) = 0 per eq. (23): the product of delta indicators is one."""

    return all(
        xp <= xl
        for xl in distinct
        for xp in distinct
        if xp != xl and len(x) <= len(xl) and len(xp) <= len(xl)
    )


def _assert_matches_reference(sources: list[MassFunction], rule: str) -> None:
    expected = _reference_pcr(sources, rule)
    actual = {"|".join(sorted(k.split("|"))): v for k, v in _fuse(rule, sources).to_dict().items()}
    assert set(actual) == set(expected)
    for key, value in expected.items():
        assert actual[key] == approx(float(value), abs=1e-12)


# --------------------------------------------------------------------------
# Example sources
# --------------------------------------------------------------------------


@pytest.fixture
def ab():
    frame = Frame.dst(["A", "B"])
    return frame, *frame.symbols()


def _example_2(frame, a, b) -> list[MassFunction]:
    return [
        frame.mass({a: 0.6, b: 0.1, a | b: 0.3}),
        frame.mass({a: 0.5, b: 0.3, a | b: 0.2}),
        frame.mass({a: 0.4, b: 0.1, a | b: 0.5}),
    ]


def _example_5():
    frame = Frame.dst(list("ABCDE"))
    a, b, c, d, e = frame.symbols()
    sources = [
        frame.mass({a | b: 0.70, c | d: 0.06, a | b | c | d: 0.15, e: 0.09}),
        frame.mass({a | b: 0.06, c | d: 0.50, a | b | c | d: 0.04, e: 0.40}),
        frame.mass({b: 0.01, frame.total: 0.99}),
    ]
    return frame, sources, (a, b, c, d, e)


def _example_13():
    frame = Frame.dst(list("ABCD"))
    a, b, c, d = frame.symbols()
    sources = [
        frame.mass({a | b: 0.8, c | d: 0.2}),
        frame.mass({a | b: 0.4, c | d: 0.6}),
        frame.mass({b: 0.1, frame.total: 0.9}),
    ]
    return frame, sources, (a, b, c, d)


# --------------------------------------------------------------------------
# Examples 1-5: numerical BBAs
# --------------------------------------------------------------------------


@pytest.mark.parametrize("rule", RULES)
def test_example_1_two_sources_all_rules_coincide(ab, rule) -> None:
    # Example 1 (Section III-B) and Example 1 revisited (Section VII).
    frame, a, b = ab
    m1 = frame.mass({a: 0.1, b: 0.2, a | b: 0.7})
    m2 = frame.mass({a: 0.4, b: 0.3, a | b: 0.3})

    result = _fuse(rule, [m1, m2])

    # Paper (four decimals): A = 0.4108, B = 0.3792, A|B = 0.21.
    _assert_masses(result, {a: 0.4108, b: 0.3792, a | b: 0.21}, abs_tol=1e-4)
    _assert_masses(
        result,
        {a: 0.35 + 0.0075 + 0.032 / 0.6, b: 0.33 + 0.0225 + 0.016 / 0.6, a | b: 0.21},
        abs_tol=1e-12,
    )


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        ("pcr5", (0.723281, 0.182460, 0.094259)),
        ("pcr6", (0.743496, 0.162245, 0.094259)),
        ("pcr5_plus", (0.768631, 0.201369, 0.03)),
        ("pcr6_plus", (0.788847, 0.181153, 0.03)),
    ],
)
def test_example_2_three_sources(ab, rule, expected) -> None:
    # Example 2 (Section IV) and Example 2 revisited (Section VII).
    frame, a, b = ab
    sources = _example_2(frame, a, b)
    result = _fuse(rule, sources)

    _assert_masses(result, dict(zip((a, b, a | b), expected, strict=True)))
    _assert_matches_reference(sources, rule)


def test_example_2_conjunctive_part_and_partial_conflicts(ab) -> None:
    frame, a, b = ab
    sources = _example_2(frame, a, b)

    conjunctive = sources[0].conjunctive(*sources[1:])
    assert conjunctive[a] == approx(0.5370)
    assert conjunctive[b] == approx(0.0900)
    assert conjunctive[a | b] == approx(0.0300)
    assert conjunctive.conflict == approx(0.3430)

    transfers = sources[0].conflict_redistribution(*sources[1:], rule="pcr6")
    assert len(transfers) == 12
    assert sum(t.conflict for t in transfers) == approx(0.3430)

    # pi_1 = m1(A) m2(A) m3(B) = 0.03: PCR5 gives 0.0225/0.0075 (p. 55),
    # PCR6 gives 0.0275/0.0025.
    pcr5 = sources[0].conflict_redistribution(*sources[1:], rule="pcr5")
    first5 = next(t for t in pcr5 if t.focal == (a, a, b))
    first6 = next(t for t in transfers if t.focal == (a, a, b))
    assert first5.conflict == approx(0.03)
    assert first5.shares[a] == approx(0.0225)
    assert first5.shares[b] == approx(0.0075)
    assert first6.shares[a] == approx(0.0275)
    assert first6.shares[b] == approx(0.0025)

    # pi_7 = m1(A|B) m2(A) m3(B) = 0.015 has no duplicates, so PCR5 = PCR6.
    seventh = next(t for t in transfers if t.focal == (a | b, a, b))
    assert seventh.shares[a | b] == approx(0.0050)
    assert seventh.shares[a] == approx(0.0083, abs=1e-4)
    assert seventh.shares[b] == approx(0.0017, abs=1e-4)


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        ("pcr5", (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))),
        ("pcr6", (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4))),
        ("pcr5_plus", (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))),
        ("pcr6_plus", (Fraction(1, 2), Fraction(1, 4), Fraction(1, 4))),
    ],
)
def test_example_3_four_categorical_sources(rule, expected) -> None:
    # Example 3 and Example 3 revisited: m1(A|B) = m2(B) = m3(A|B) = m4(C) = 1.
    # Paper typo: the BBA is defined as m2(B) = 1, but the conflicting product
    # and some kappa expressions are then written with m2(A).  The printed
    # results (masses on A|B, B, and C) follow the definition, so B is used.
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    sources = _categorical(frame, a | b, b, a | b, c)

    result = _fuse(rule, sources)

    _assert_masses(result, dict(zip((a | b, b, c), expected, strict=True)), abs_tol=1e-12)


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        ("pcr5", (0.654604, 0.144825, 0.200571)),
        ("pcr6", (0.647113, 0.128342, 0.224545)),
        ("pcr5_plus", (0.768631, 0.201369, 0.03)),
        ("pcr6_plus", (0.788847, 0.181153, 0.03)),
    ],
)
def test_example_4_vacuous_fourth_source(ab, rule, expected) -> None:
    # Example 4 and Example 4 revisited: m4 is the vacuous BBA.
    frame, a, b = ab
    sources = [*_example_2(frame, a, b), frame.mass({a | b: 1.0})]

    with_vacuous = _fuse(rule, sources)

    _assert_masses(with_vacuous, dict(zip((a, b, a | b), expected, strict=True)))
    _assert_matches_reference(sources, rule)
    without = _fuse(rule, sources[:3])
    if rule.endswith("_plus"):
        assert with_vacuous.to_dict() == approx(without.to_dict(), abs=1e-12)
    else:
        assert with_vacuous[a | b] > without[a | b] + 0.1


@pytest.mark.parametrize("rule", RULES)
def test_example_5_two_source_reference(rule) -> None:
    # Example 5: PCR6(m1, m2) = PCR5 = PCR5+ = PCR6+ for two sources.
    _, sources, (a, b, c, d, e) = _example_5()

    result = _fuse(rule, sources[:2])

    _assert_matches_reference(sources[:2], rule)
    _assert_masses(
        result,
        {a | b: 0.465309, c | d: 0.296299, a | b | c | d: 0.023471, e: 0.214921},
    )


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        # Table I (PCR5 column); see the module docstring for mis-rounded
        # entries.
        ("pcr5", (0.001103, 0.286107, 0.203385, 0.012203, 0.115966, 0.381236)),
        # Table II (PCR6 column).
        ("pcr6", (0.000962, 0.286107, 0.203454, 0.012203, 0.116038, 0.381236)),
        # Table I (PCR5+ column).
        ("pcr5_plus", (0.001107, 0.464483, 0.296186, 0.023408, 0.214816, 0.0)),
        # Table II (PCR6+ column).
        ("pcr6_plus", (0.000967, 0.464483, 0.296255, 0.023408, 0.214887, 0.0)),
    ],
)
def test_example_5_tables_I_and_II(rule, expected) -> None:
    frame, sources, (a, b, c, d, e) = _example_5()
    keys = (b, a | b, c | d, a | b | c | d, e, frame.total)

    result = _fuse(rule, sources)

    _assert_masses(result, dict(zip(keys, expected, strict=True)))
    _assert_matches_reference(sources, rule)


def test_example_5_conjunctive_part_and_mass_of_theta() -> None:
    frame, sources, (a, b, c, d, e) = _example_5()

    conjunctive = sources[0].conjunctive(*sources[1:])
    assert conjunctive[b] == approx(0.00085)
    assert conjunctive[a | b] == approx(0.07821)
    assert conjunctive[c | d] == approx(0.106326)
    assert conjunctive[a | b | c | d] == approx(0.00594)
    assert conjunctive[e] == approx(0.03564)
    assert conjunctive.conflict == approx(0.773034)

    # p. 58: the eight products involving Theta give x_j(Theta) summing to
    # 0.381236 under PCR5; PCR5+ redistributes nothing to Theta.
    transfers = sources[0].conflict_redistribution(*sources[1:], rule="pcr5")
    to_theta = [t.shares[frame.total] for t in transfers if frame.total in t.shares]
    assert len(to_theta) == 8
    assert sum(to_theta) == approx(0.381236, abs=PAPER)
    plus = sources[0].conflict_redistribution(*sources[1:], rule="pcr5+")
    assert all(frame.total not in t.shares for t in plus)


# --------------------------------------------------------------------------
# Examples 6-13: binary keeping indexes and categorical BBAs
# --------------------------------------------------------------------------


def _single_transfer(sources: list[MassFunction], rule: str = "pcr6+") -> ConflictTransfer:
    (transfer,) = sources[0].conflict_redistribution(*sources[1:], rule=rule)
    return transfer


def _abcd():
    frame = Frame.dst(list("ABCD"))
    return frame, *frame.symbols()


def test_example_6_keeping_indexes_and_tables_III_IV() -> None:
    frame, a, b, c, d = _abcd()
    sources = _categorical(frame, a, b | c, a | c, b | c, a | b | c, frame.total)

    assert _single_transfer(sources).kept == {a, b | c, a | c}
    keys = (a, a | c, b | c, a | b | c, frame.total)
    third, fifth, sixth = Fraction(1, 3), Fraction(1, 5), Fraction(1, 6)
    expected = {
        "pcr5": (fifth, fifth, fifth, fifth, fifth),
        "pcr5_plus": (third, third, third, 0, 0),
        "pcr6": (sixth, sixth, 2 * sixth, sixth, sixth),
        "pcr6_plus": (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2), 0, 0),
    }
    for rule, values in expected.items():
        _assert_masses(_fuse(rule, sources), dict(zip(keys, values, strict=True)), abs_tol=1e-12)


def test_example_7_keeping_indexes_and_tables_V_VI() -> None:
    frame = Frame.dst(list("ABCDE"))
    a, b, c, d, e = frame.symbols()
    sources = _categorical(
        frame, a | e, b | c | e, a | c | e, b | c | e, a | b | c | e, frame.total, a
    )

    assert _single_transfer(sources).kept == {a | e, b | c | e, a | c | e, a}
    keys = (a, a | e, a | c | e, b | c | e, a | b | c | e, frame.total)
    q, s = Fraction(1, 4), Fraction(1, 6)
    expected = {
        "pcr5": (s, s, s, s, s, s),
        "pcr5_plus": (q, q, q, q, 0, 0),
        "pcr6": tuple(Fraction(n, 7) for n in (1, 1, 1, 2, 1, 1)),
        "pcr6_plus": tuple(Fraction(n, 5) for n in (1, 1, 1, 2, 0, 0)),
    }
    for rule, values in expected.items():
        _assert_masses(_fuse(rule, sources), dict(zip(keys, values, strict=True)), abs_tol=1e-12)


def test_example_8_keeping_indexes_and_tables_VII_VIII() -> None:
    frame, a, b, c, d = _abcd()
    sources = _categorical(frame, a, b | c, a | c, b | c, frame.total)

    assert _single_transfer(sources).kept == {a, b | c, a | c}
    keys = (a, a | c, b | c, frame.total)
    t, q, f = Fraction(1, 3), Fraction(1, 4), Fraction(1, 5)
    expected = {
        "pcr5": (q, q, q, q),
        "pcr5_plus": (t, t, t, 0),
        "pcr6": (f, f, 2 * f, f),
        "pcr6_plus": (q, q, 2 * q, 0),
    }
    for rule, values in expected.items():
        _assert_masses(_fuse(rule, sources), dict(zip(keys, values, strict=True)), abs_tol=1e-12)


def test_example_9_keeping_indexes_and_tables_IX_X() -> None:
    frame, a, b, c, d = _abcd()
    sources = _categorical(frame, a, b | c, a | c, b | c, frame.total, a | b | c, a | b | c)

    assert _single_transfer(sources).kept == {a, b | c, a | c}
    keys = (a, a | c, b | c, a | b | c, frame.total)
    t, q, f = Fraction(1, 3), Fraction(1, 4), Fraction(1, 5)
    expected = {
        "pcr5": (f, f, f, f, f),
        "pcr5_plus": (t, t, t, 0, 0),
        "pcr6": tuple(Fraction(n, 7) for n in (1, 1, 2, 2, 1)),
        "pcr6_plus": (q, q, 2 * q, 0, 0),
    }
    for rule, values in expected.items():
        _assert_masses(_fuse(rule, sources), dict(zip(keys, values, strict=True)), abs_tol=1e-12)


@pytest.mark.parametrize("rule", RULES)
def test_example_10_nothing_discarded_table_XI(rule) -> None:
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    sources = _categorical(frame, a, b | c, a | c)

    assert _single_transfer(sources).kept == {a, b | c, a | c}
    third = Fraction(1, 3)
    _assert_masses(_fuse(rule, sources), {a: third, a | c: third, b | c: third}, abs_tol=1e-12)


@pytest.mark.parametrize("rule", RULES)
def test_example_11_nothing_discarded(rule) -> None:
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    sources = _categorical(frame, a, b | c, a | c, a | b)

    assert _single_transfer(sources).kept == {a, b | c, a | c, a | b}
    q = Fraction(1, 4)
    _assert_masses(
        _fuse(rule, sources), {a: q, a | b: q, a | c: q, b | c: q}, abs_tol=1e-12
    )


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        ("pcr5", (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))),
        ("pcr6", (Fraction(1, 3), Fraction(1, 3), Fraction(1, 3))),
        ("pcr5_plus", (Fraction(1, 2), Fraction(1, 2), 0)),
        ("pcr6_plus", (Fraction(1, 2), Fraction(1, 2), 0)),
    ],
)
def test_example_12_table_XII(rule, expected) -> None:
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    sources = _categorical(frame, frame.total, a, b | c)

    assert _single_transfer(sources).kept == {a, b | c}
    _assert_masses(
        _fuse(rule, sources), dict(zip((a, b | c, frame.total), expected, strict=True)),
        abs_tol=1e-12,
    )


def test_example_13_keeping_indexes() -> None:
    frame, sources, (a, b, c, d) = _example_13()
    transfers = sources[0].conflict_redistribution(*sources[1:], rule="pcr6+")

    # Section VI-A: pi_3 .. pi_7 and their binary keeping indexes.
    kept = {t.focal: t.kept for t in transfers}
    assert kept == {
        (a | b, c | d, b): {a | b, c | d, b},
        (a | b, c | d, frame.total): {a | b, c | d},
        (c | d, a | b, b): {c | d, a | b, b},
        (c | d, a | b, frame.total): {c | d, a | b},
        (c | d, c | d, b): {c | d, b},
    }
    conflicts = {t.focal: t.conflict for t in transfers}
    assert conflicts[(a | b, c | d, b)] == approx(0.048)
    assert conflicts[(a | b, c | d, frame.total)] == approx(0.432)
    assert conflicts[(c | d, a | b, b)] == approx(0.008)
    assert conflicts[(c | d, a | b, frame.total)] == approx(0.072)
    assert conflicts[(c | d, c | d, b)] == approx(0.012)


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        ("pcr5", (0.041797, 0.487632, 0.258327, 0.212244)),  # Table XIII
        ("pcr5_plus", (0.041797, 0.613029, 0.345174, 0.0)),  # Table XIII
        ("pcr6", (0.037676, 0.487632, 0.262448, 0.212244)),  # Table XIV
        ("pcr6_plus", (0.037676, 0.613029, 0.349295, 0.0)),  # Table XIV
    ],
)
def test_example_13_tables_XIII_XIV(rule, expected) -> None:
    frame, sources, (a, b, c, d) = _example_13()

    result = _fuse(rule, sources)

    _assert_masses(result, dict(zip((b, a | b, c | d, frame.total), expected, strict=True)))
    _assert_matches_reference(sources, rule)


# --------------------------------------------------------------------------
# Binary keeping index: direct definition (eq. 23) versus iterative (eq. 24)
# --------------------------------------------------------------------------


def _keeping_index_eq23(masks: frozenset[int]) -> frozenset[int]:
    """Literal transcription of eq. (23), used as an independent oracle."""

    def delta(smaller: int, larger: int) -> bool:
        return smaller & larger == smaller

    kept = set()
    for x in masks:
        product_is_one = all(
            delta(xp, xl)
            for xl in masks
            for xp in masks
            if xp != xl
            and x.bit_count() <= xl.bit_count()
            and xp.bit_count() <= xl.bit_count()
        )
        if not product_is_one:
            kept.add(x)
    return frozenset(kept)


def test_keeping_index_iterative_form_matches_direct_definition() -> None:
    rng = random.Random(20211)
    for universe_bits in range(2, 7):
        universe = range(1, 1 << universe_bits)
        for _ in range(400):
            masks = frozenset(rng.sample(universe, rng.randint(2, min(7, len(universe)))))
            assert _keeping_masks(masks) == _keeping_index_eq23(masks)


def test_keeping_index_exhaustive_on_three_atoms() -> None:
    universe = range(1, 8)
    for size in range(2, 8):
        for masks in combinations(universe, size):
            frozen = frozenset(masks)
            assert _keeping_masks(frozen) == _keeping_index_eq23(frozen)


def test_keeping_index_discards_total_ignorance_in_conflicting_products() -> None:
    # Remark 1: kappa(Theta) = 0 whenever Theta takes part in a conflict.
    full = 0b1111
    rng = random.Random(7)
    for _ in range(200):
        masks = set(rng.sample(range(1, full), 3))
        assert full not in _keeping_masks(frozenset({*masks, full}))


# --------------------------------------------------------------------------
# Properties
# --------------------------------------------------------------------------


def _random_mass(frame: Frame, rng: random.Random, focal: int) -> MassFunction:
    elements = [prop for prop in frame.elements() if prop]
    chosen = rng.sample(elements, min(focal, len(elements)))
    weights = [rng.random() + 0.05 for _ in chosen]
    total = sum(weights)
    return frame.mass({prop: weight / total for prop, weight in zip(chosen, weights)})


def _frames() -> list[Frame]:
    return [
        Frame.dst(["A", "B", "C"]),
        Frame.dst(["A", "B", "C", "D"]),
        Frame.dsmt(["A", "B", "C"]),
        Frame.hybrid(["A", "B", "C"], empty=["A&C"]),
    ]


@pytest.mark.parametrize("frame", _frames(), ids=["dst3", "dst4", "free3", "hybrid3"])
def test_vacuous_source_is_neutral_for_improved_rules_only(frame: Frame) -> None:
    # Theorem of Section VI-B: the vacuous BBA is neutral in PCR5+ and PCR6+.
    rng = random.Random(2021)
    vacuous = frame.mass({frame.total: 1.0})
    non_neutral = 0
    for _ in range(25):
        sources = [_random_mass(frame, rng, rng.randint(2, 4)) for _ in range(rng.randint(2, 3))]
        for rule in ("pcr5_plus", "pcr6_plus"):
            base = _fuse(rule, sources)
            for extra in (1, 2):
                augmented = _fuse(rule, [*sources, *[vacuous] * extra])
                assert augmented.to_dict() == approx(base.to_dict(), abs=1e-12)
        if len(sources) > 1:
            plain = _fuse("pcr6", sources)
            if _fuse("pcr6", [*sources, vacuous]).to_dict() != approx(plain.to_dict()):
                non_neutral += 1
    # PCR6 itself is not neutral (eq. 20) whenever conflicts can occur; the
    # free DSm model has no empty intersections, hence no conflict at all.
    assert (non_neutral > 0) == (frame.model != "dsmt")


@pytest.mark.parametrize("frame", _frames(), ids=["dst3", "dst4", "free3", "hybrid3"])
def test_improved_rules_coincide_with_classic_rules_for_two_sources(frame: Frame) -> None:
    # Remark 3: for S = 2, PCR5 = PCR5+ = PCR6 = PCR6+.
    rng = random.Random(3)
    for _ in range(30):
        m1, m2 = _random_mass(frame, rng, 4), _random_mass(frame, rng, 4)
        reference = m1.pcr6(m2).to_dict()
        for rule in RULES:
            assert _fuse(rule, [m1, m2]).to_dict() == approx(reference, abs=1e-12)


@pytest.mark.parametrize("frame", _frames(), ids=["dst3", "dst4", "free3", "hybrid3"])
def test_trace_reconstructs_fusion_and_conserves_mass(frame: Frame) -> None:
    rng = random.Random(11)
    for _ in range(20):
        sources = [_random_mass(frame, rng, 3) for _ in range(3)]
        conjunctive = sources[0].conjunctive(*sources[1:])
        for rule, method in zip(("pcr5", "pcr6", "pcr5+", "pcr6+"), RULES, strict=True):
            transfers = sources[0].conflict_redistribution(*sources[1:], rule=rule)
            assert sum(t.conflict for t in transfers) == approx(conjunctive.conflict)
            rebuilt = {prop: value for prop, value in conjunctive.items() if prop}
            for transfer in transfers:
                assert sum(transfer.shares.values()) == approx(transfer.conflict)
                assert set(transfer.shares) == set(transfer.kept)
                assert set(transfer.kept) <= set(transfer.focal)
                assert len(transfer.kept) >= 2
                for prop, share in transfer.shares.items():
                    rebuilt[prop] = rebuilt.get(prop, 0.0) + share
            fused = _fuse(method, sources)
            assert fused.total_mass == approx(1.0)
            assert {str(k): v for k, v in rebuilt.items() if v > 1e-12} == approx(
                fused.to_dict(), abs=1e-12
            )


def test_improved_rules_never_increase_mass_of_discarded_elements(ab) -> None:
    # PCR5+/PCR6+ give no conflict share to a discarded element, so a
    # discarded element keeps exactly its conjunctive mass (Example 2: A|B).
    frame, a, b = ab
    sources = _example_2(frame, a, b)
    conjunctive = sources[0].conjunctive(*sources[1:])
    for rule in ("pcr5_plus", "pcr6_plus"):
        assert _fuse(rule, sources)[a | b] == approx(conjunctive[a | b])


def test_pcr_rules_are_not_associative(ab) -> None:
    # Eqs. (16)-(17): sequential fusion differs from fusing all sources jointly.
    frame, a, b = ab
    m1, m2, m3 = _example_2(frame, a, b)
    for rule in RULES:
        joint = _fuse(rule, [m1, m2, m3])
        sequential = _fuse(rule, [_fuse(rule, [m1, m2]), m3])
        assert joint[a] != approx(sequential[a], abs=1e-4)


def test_conflict_redistribution_rule_names_and_validation(ab) -> None:
    frame, a, b = ab
    m1 = frame.mass({a: 1.0})
    m2 = frame.mass({b: 1.0})
    for name in ("pcr5", "PCR6", "pcr5+", "pcr6_plus", "PCR6+"):
        (transfer,) = m1.conflict_redistribution(m2, rule=name)
        assert transfer.shares == {a: approx(0.5), b: approx(0.5)}
    with pytest.raises(ValueError, match="rule must be one of"):
        m1.conflict_redistribution(m2, rule="dempster")
    with pytest.raises(ValueError, match="At least two sources"):
        m1.pcr6_plus()
    with pytest.raises(ValueError, match="same frame"):
        m1.pcr5_plus(Frame.dst(["A", "B"]).mass({"A": 1.0}))
    no_conflict = m1.conflict_redistribution(frame.mass({a | b: 1.0}))
    assert no_conflict == ()


@pytest.mark.parametrize("rule", RULES)
def test_reference_implementation_on_random_dst_sources(rule) -> None:
    rng = random.Random(1606)
    for atoms in (3, 4):
        frame = Frame.dst(list("ABCD"[:atoms]))
        vacuous = frame.mass({frame.total: 1.0})
        for _ in range(15):
            sources = [_random_mass(frame, rng, rng.randint(1, 4)) for _ in range(3)]
            if rng.random() < 0.3:
                sources.append(vacuous)
            _assert_matches_reference(sources, rule)


@pytest.mark.parametrize("rule", RULES)
def test_tiny_masses_do_not_underflow(rule) -> None:
    # Products of tiny masses must neither divide by zero (PCR5 weights) nor
    # silently lose a representable conflict.
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()

    sources = [
        frame.mass({x: 1e-200, frame.total: 1 - 1e-200}, tolerance=0.0)
        for x in (a, a, b, b)
    ]
    result = _fuse(rule, sources)
    assert result.total_mass == approx(1.0)
    assert result[a] == approx(2e-200, rel=1e-9, abs=0.0)
    assert result[b] == approx(2e-200, rel=1e-9, abs=0.0)

    sources = [
        frame.mass({x: 1e-100, frame.total: 1 - 1e-100}, tolerance=0.0)
        for x in (a, b, c)
    ]
    key = rule.replace("_plus", "+")
    (smallest,) = [
        t for t in sources[0].conflict_redistribution(*sources[1:], rule=key)
        if t.focal == (a, b, c)
    ]
    assert smallest.conflict == approx(1e-300, rel=1e-9, abs=0.0)
    assert sum(smallest.shares.values()) == approx(1e-300, rel=1e-9, abs=0.0)
