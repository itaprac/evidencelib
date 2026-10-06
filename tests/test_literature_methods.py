"""Conformance tests for the methods added in v1.3.0 beyond PCR5+/PCR6+.

Every expected value is printed in the cited source.  Printed values are
rounded to the number of decimals shown in the source; the tolerance follows
that rounding.  Known misprints in the sources are documented where they
occur.

Sources
-------
[SD04]  F. Smarandache, J. Dezert, "Proportional Conflict Redistribution
        Rules for Information Fusion", arXiv:cs/0408064 (2004); also Ch. 1 of
        *Advances and Applications of DSmT for Information Fusion*, Vol. 2
        (2006).  PCR1-PCR5.
[DS08]  J. Dezert, F. Smarandache, "A new probabilistic transformation of
        belief mass assignment", Fusion 2008, arXiv:0807.3669.  DSmP.
[SDT10] F. Smarandache, J. Dezert, J.-M. Tacnet, "Fusion of sources of
        evidence with different importances and reliabilities", Fusion 2010,
        hal-00559233.  Shafer discounting (eq. 4, Table 3).
[D08]   T. Denoeux, "Conjunctive and disjunctive combination of belief
        functions induced by nondistinct bodies of evidence", Artificial
        Intelligence 172 (2008); preprint version.  TBM disjunctive rule
        (eq. 13, Table 5).
[J17]   W. Jiang, "A correlation coefficient of belief functions",
        arXiv:1612.05497 (2017).  Reproduces the Jousselme distance examples
        of Jousselme, Grenier and Bosse (Information Fusion 2, 2001).
"""

from __future__ import annotations

import pytest
from pytest import approx

from evidencelib import Frame, MassFunction


def _assert_masses(result: MassFunction, expected: dict, *, abs_tol: float) -> None:
    support = {prop for prop, value in expected.items() if value > 0}
    assert set(result.focal()) == support
    assert result.total_mass == approx(1.0)
    for prop, value in expected.items():
        assert result[prop] == approx(value, abs=abs_tol)


@pytest.fixture
def abc():
    frame = Frame.dst(["A", "B", "C"])
    return frame, *frame.symbols()


@pytest.fixture
def ab():
    frame = Frame.dst(["A", "B"])
    return frame, *frame.symbols()


# ===========================================================================
# PCR1-PCR4 [SD04]
# ===========================================================================


@pytest.mark.parametrize(
    ("rule", "expected", "tol"),
    [
        ("pcr1", (0.550, 0.337, 0.113), 5e-4),
        ("pcr2", (0.550, 0.337, 0.113), 5e-4),
        ("pcr3", (0.574842, 0.338235, 0.086923), 1e-6),
        # Printed C = 0.046594; exact 0.02 + 0.16 * 0.02 / 0.26 + 0.10 * 0.02 / 0.14
        # = 0.0465934..., i.e. a rounding misprint within 1e-6.
        ("pcr4", (0.627692, 0.325714, 0.046594), 1e-6),
        ("pcr5", (0.574571, 0.335429, 0.090000), 1e-6),
    ],
)
def test_sd04_example_12_1_bayesian_sources(abc, rule, expected, tol) -> None:
    frame, a, b, c = abc
    m1 = frame.mass({a: 0.6, b: 0.3, c: 0.1})
    m2 = frame.mass({a: 0.4, b: 0.4, c: 0.2})

    result = getattr(m1, rule)(m2)

    _assert_masses(result, dict(zip((a, b, c), expected, strict=True)), abs_tol=tol)


@pytest.mark.parametrize(
    ("rule", "expected", "tol"),
    [
        ("pcr1", (0.7180, 0.2125, 0.0695), 5e-5),
        ("pcr2", (0.752941, 0.227059, 0.02), 1e-6),
        ("pcr3", (0.752941, 0.227059, 0.02), 1e-6),
        ("pcr4", (0.784, 0.196, 0.02), 1e-9),
        ("pcr5", (0.739849, 0.240151, 0.02), 1e-6),
        ("dempster", (0.776119, 0.194030, 0.029851), 1e-6),
    ],
)
def test_sd04_example_12_2(ab, rule, expected, tol) -> None:
    # Also Sec. 8.2 (PCR1 versus PCR2).
    frame, a, b = ab
    m1 = frame.mass({a: 0.7, b: 0.1, a | b: 0.2})
    m2 = frame.mass({a: 0.5, b: 0.4, a | b: 0.1})

    result = getattr(m1, rule)(m2)

    _assert_masses(result, dict(zip((a, b, a | b), expected, strict=True)), abs_tol=tol)


@pytest.mark.parametrize("rule", ["pcr2", "pcr3", "pcr4"])
def test_sd04_vacuous_source_is_neutral_for_pcr2_to_pcr4(ab, rule) -> None:
    # Secs. 8.3 (PCR2), 9.4 (PCR3), 10.4 (PCR4): the conflict A & B & (A|B)
    # has canonical form A & B, so A|B receives nothing.
    frame, a, b = ab
    m1 = frame.mass({a: 0.7, b: 0.1, a | b: 0.2})
    m2 = frame.mass({a: 0.5, b: 0.4, a | b: 0.1})
    vacuous = frame.mass({a | b: 1.0})

    with_vacuous = getattr(m1, rule)(m2, vacuous)

    assert with_vacuous.to_dict() == approx(getattr(m1, rule)(m2).to_dict(), abs=1e-12)


def test_sd04_pcr1_is_not_neutral_to_the_vacuous_source(ab) -> None:
    # Sec. 7.1: "a severe limitation of PCR1 (as for WAO) is the
    # non-preservation of the neutral impact of the VBA".
    frame, a, b = ab
    m1 = frame.mass({a: 0.7, b: 0.1, a | b: 0.2})
    m2 = frame.mass({a: 0.5, b: 0.4, a | b: 0.1})
    vacuous = frame.mass({a | b: 1.0})

    with_vacuous = m1.pcr1(m2, vacuous)

    # Column sums 1.2, 0.5, 1.3 over d = 3: A|B gets 0.02 + 1.3 / 3 * 0.33.
    assert with_vacuous[a | b] == approx(0.02 + 1.3 / 3 * 0.33)
    assert with_vacuous[a | b] != approx(m1.pcr1(m2)[a | b])


def test_sd04_section_9_4_pcr3_with_vacuous_source(abc) -> None:
    frame, a, b, c = abc
    m1 = frame.mass({a: 0.6, b: 0.3, c: 0.1})
    m2 = frame.mass({a: 0.4, b: 0.4, c: 0.2})

    result = m1.pcr3(m2, frame.mass({frame.total: 1.0}))

    _assert_masses(result, {a: 0.574842, b: 0.338235, c: 0.086923}, abs_tol=1e-6)


@pytest.mark.parametrize(
    ("rule", "expected", "tol"),
    [
        ("pcr1", (0.4455, 0.4455, 0.1090), 5e-5),
        ("pcr2", (0.4455, 0.4455, 0.1090), 5e-5),
        # Printed C = 0.042728; exact 0.01 + 2 * 0.09 * 0.2 / 1.1 = 0.0427272...
        ("pcr3", (0.478636, 0.478636, 0.042728), 1e-6),
        ("pcr4", (0.478636, 0.478636, 0.042728), 1e-6),
        ("pcr5", (0.486, 0.486, 0.028), 1e-9),
    ],
)
def test_sd04_example_12_3_zadeh(abc, rule, expected, tol) -> None:
    frame, a, b, c = abc
    m1 = frame.mass({a: 0.9, c: 0.1})
    m2 = frame.mass({b: 0.9, c: 0.1})

    result = getattr(m1, rule)(m2)

    _assert_masses(result, dict(zip((a, b, c), expected, strict=True)), abs_tol=tol)


@pytest.mark.parametrize(
    ("rule", "expected", "tol"),
    [
        ("pcr1", (0.487, 0.182, 0.071), 1e-9),
        ("pcr2", (0.52, 0.20, 0.02), 1e-9),
        ("pcr3", (0.52, 0.20, 0.02), 1e-9),
        ("pcr4", (0.56842, 0.15158, 0.02), 5e-6),
        ("pcr5", (0.51543, 0.20457, 0.02), 5e-6),
    ],
)
def test_sd04_example_12_4_hybrid_model(rule, expected, tol) -> None:
    # Hybrid model: A & B = empty, A & C and B & C non-empty.
    frame = Frame.hybrid(["A", "B", "C"], empty=["A&B"])
    a, b, c = frame.symbols()
    m1 = frame.mass({a: 0.5, b: 0.4, c: 0.1})
    m2 = frame.mass({a: 0.6, b: 0.2, c: 0.2})

    result = getattr(m1, rule)(m2)

    expected_masses = dict(zip((a, b, c), expected, strict=True))
    expected_masses.update({a & c: 0.16, b & c: 0.10})
    _assert_masses(result, expected_masses, abs_tol=tol)


def test_sd04_section_10_3_pcr4(ab) -> None:
    frame, a, b = ab
    m1 = frame.mass({a: 0.6, b: 0.3, a | b: 0.1})
    m2 = frame.mass({a: 0.2, b: 0.3, a | b: 0.5})

    result = m1.pcr4(m2)

    _assert_masses(result, {a: 0.5887, b: 0.3613, a | b: 0.05}, abs_tol=5e-5)
    # Bayesian 2D case: PCR4 = Dempster (p. 22).
    bayes1 = frame.mass({a: 0.6, b: 0.4})
    bayes2 = frame.mass({a: 0.1, b: 0.9})
    _assert_masses(bayes1.pcr4(bayes2), {a: 0.142857, b: 0.857143}, abs_tol=1e-6)
    assert bayes1.pcr4(bayes2).to_dict() == approx(bayes1.dempster(bayes2).to_dict())


def test_sd04_section_10_5_pcr4_with_zero_conjunctive_masses() -> None:
    # m12(A) = m12(B) = 0, so conflicts involving A or B fall back to the
    # mass-matrix column sums c(A) = 0.6, c(B) = 0.4, c(C) = 0.6, c(D) = 0.4.
    # Misprint in the source: for A & C it uses 0.5 instead of c(C) = 0.6
    # (x/0.6 = z/0.5), giving A = 0.343636 and C = 0.310364.  Following the
    # rule as defined gives A = 0.33 and C = 0.324; B and D match the source.
    frame = Frame.dst(["A", "B", "C", "D"])
    a, b, c, d = frame.symbols()
    m1 = frame.mass({b: 0.4, c: 0.5, d: 0.1})
    m2 = frame.mass({a: 0.6, c: 0.1, d: 0.3})

    result = m1.pcr4(m2)

    assert result[b] == approx(0.172, abs=1e-9)
    assert result[d] == approx(0.174, abs=1e-9)
    assert result[a] == approx(0.144 + 0.30 * 0.6 / 1.2 + 0.036)
    assert result[c] == approx(0.05 + 0.30 * 0.6 / 1.2 + 0.024 + 0.10)


@pytest.mark.parametrize(
    ("rule", "first", "second"),
    [
        ("pcr1", (0.595, 0.405), (0.496203, 0.503797)),
        ("pcr2", (0.595, 0.405), (0.496203, 0.503797)),
        ("pcr3", (0.595, 0.405), (0.496203, 0.503797)),
        ("pcr4", (0.595, 0.405), (0.494802, 0.505198)),
        ("pcr5", (0.573684, 0.426316), (0.480268, 0.519732)),
    ],
)
def test_sd04_example_12_5_target_identification(ab, rule, first, second) -> None:
    # Sequential update: the fused result becomes the prior of the next step.
    frame, a, b = ab
    prior = frame.mass({a: 1.0})
    observation = frame.mass({a: 0.1, b: 0.9})
    update = frame.mass({a: 0.4, b: 0.6})

    step1 = getattr(prior, rule)(observation)
    step2 = getattr(step1, rule)(update)

    _assert_masses(step1, dict(zip((a, b), first, strict=True)), abs_tol=1e-6)
    _assert_masses(step2, dict(zip((a, b), second, strict=True)), abs_tol=1.5e-6)


@pytest.mark.parametrize("rule", ["pcr1", "pcr2", "pcr3", "pcr4"])
def test_pcr1_to_pcr4_accept_many_sources_and_conserve_mass(abc, rule) -> None:
    frame, a, b, c = abc
    sources = [
        frame.mass({a: 0.6, b | c: 0.4}),
        frame.mass({b: 0.5, a | c: 0.5}),
        frame.mass({c: 0.2, frame.total: 0.8}),
        frame.mass({a: 0.3, b: 0.3, c: 0.4}),
    ]

    result = getattr(sources[0], rule)(*sources[1:])

    assert result.total_mass == approx(1.0)
    assert result.conflict == 0.0


def test_pcr3_redistributes_to_the_canonical_form_only(abc) -> None:
    # A & B & (A|B) has canonical form A & B: A|B is absorbed.
    frame, a, b, c = abc
    sources = [frame.mass({a: 1.0}), frame.mass({b: 1.0}), frame.mass({a | b: 1.0})]

    result = sources[0].pcr3(*sources[1:])

    # Column sums c(A) = c(B) = 1, so A and B share the conflict equally.
    _assert_masses(result, {a: 0.5, b: 0.5}, abs_tol=1e-12)


def test_sd04_section_7_1_pcr1_with_tbm_source(ab) -> None:
    # Sec. 7.1: a source with m(empty) > 0 (Smets' TBM) combined with the
    # vacuous assignment: the empty mass is a conflict that PCR1 transfers by
    # column sums (A: 0.5, A|B: 1.0), so A gets 1/6 and A|B gets 1/3.
    frame, a, b = ab
    tbm = MassFunction(frame, {frame.empty: 0.5, a: 0.5})

    result = tbm.pcr1(frame.mass({a | b: 1.0}))

    _assert_masses(result, {a: 2 / 3, a | b: 1 / 3}, abs_tol=1e-12)


def _section_7_2_sources():
    source = Frame.dst(["A", "B", "C"])
    a, b, c = source.symbols()
    m1 = source.mass({a: 0.3, b: 0.4, c: 0.3})
    m2 = source.mass({a: 0.5, b: 0.1, c: 0.4})
    target = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["B"])
    return m1, m2, target


def test_sd04_section_7_2_dynamic_pcr1() -> None:
    # B is learned to be empty after the sources were elicited: m12(B) = 0.04
    # joins the conflict (k = 0.73), redistributed by c(A) = 0.8, c(C) = 0.7.
    m1, m2, target = _section_7_2_sources()
    a, _, c = target.symbols()

    result = m1.pcr1(m2, model=target)

    assert result.frame is target
    _assert_masses(result, {a: 0.5393, c: 0.4607}, abs_tol=5e-5)


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        # PCR2: every conflict involves A or C, so k = 0.73 goes to {A, C} by
        # column sums, as in PCR1.
        ("pcr2", {"A": 0.15 + 0.73 * 0.8 / 1.5, "C": 0.12 + 0.73 * 0.7 / 1.5}),
        # PCR3: (A,B) 0.03 and (B,A) 0.20 go to A only; (B,C) 0.16 and (C,B)
        # 0.03 to C only; (A,C) 0.12 and (C,A) 0.15 to A and C by 0.8 : 0.7;
        # (B,B) 0.04 has no non-empty proposition: u(B) = B is empty, so the
        # mass goes to total ignorance A|C.
        ("pcr3", {"A": 0.15 + 0.23 + 0.27 * 0.8 / 1.5, "C": 0.12 + 0.19 + 0.27 * 0.7 / 1.5, "A|C": 0.04}),
        # PCR4: as PCR3, but (A,C) and (C,A) by conjunctive masses 0.15 : 0.12.
        ("pcr4", {"A": 0.15 + 0.23 + 0.27 * 0.15 / 0.27, "C": 0.12 + 0.19 + 0.27 * 0.12 / 0.27, "A|C": 0.04}),
    ],
)
def test_dynamic_pcr2_to_pcr4_follow_their_definitions(rule, expected) -> None:
    # Hand-computed from [SD04] eqs. 24, 28, 30-31 (the source gives a
    # numerical dynamic example for PCR1 only).
    m1, m2, target = _section_7_2_sources()

    result = getattr(m1, rule)(m2, model=target)

    assert result.frame is target
    assert result.to_dict() == approx(expected, abs=1e-12)


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        # PCR2/PCR3: the conflict A & B (now empty) has no non-empty
        # proposition left, so it goes to u(A & B) = A | B.
        ("pcr2", {"A|B": 1.0}),
        ("pcr3", {"A|B": 1.0}),
        # PCR4 (Sec. 10.2): to the partial ignorance X | Y = A & B, empty in
        # the target, hence to total ignorance.
        ("pcr4", {"A|B|C": 1.0}),
    ],
)
def test_dynamic_canonical_form_keeps_the_vacuous_source_neutral(rule, expected) -> None:
    # Free model -> Shafer's model.  With a vacuous third source the product
    # (A&B) & (A&B) & Theta keeps the canonical form A & B (Theta stays
    # absorbed), so the vacuous source must not change the result ([SD04]
    # Sec. 11.1 neutrality argument).
    source = Frame.dsmt(["A", "B", "C"])
    a, b, _ = source.symbols()
    m = source.mass({a & b: 1.0})
    target = Frame.dst(["A", "B", "C"])

    without = getattr(m, rule)(m, model=target)
    with_vacuous = getattr(m, rule)(m, source.mass({source.total: 1.0}), model=target)

    assert without.to_dict() == approx(expected)
    assert with_vacuous.to_dict() == approx(expected)


@pytest.mark.parametrize("rule", ["pcr2", "pcr3", "pcr4"])
def test_projection_cannot_make_total_ignorance_a_recipient(rule) -> None:
    # Sources A|B, A|C, B|C; C is learned to be empty.  Projected, the
    # canonical form {A|B, A|C, B|C} becomes {A|B, A, B}: A|B now contains A
    # and B (and equals the target's total ignorance), so only A and B
    # receive the conflict, and a vacuous source must change nothing.
    source = Frame.dst(["A", "B", "C"])
    a, b, c = source.symbols()
    sources = [source.mass({a | b: 1.0}), source.mass({a | c: 1.0}), source.mass({b | c: 1.0})]
    target = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])

    plain = getattr(sources[0], rule)(*sources[1:], model=target)
    with_vacuous = getattr(sources[0], rule)(
        *sources[1:], source.mass({source.total: 1.0}), model=target
    )

    assert plain.to_dict() == approx({"A": 0.5, "B": 0.5})
    assert with_vacuous.to_dict() == approx(plain.to_dict())


@pytest.mark.parametrize("rule", ["pcr1", "pcr2", "pcr3", "pcr4"])
def test_empty_source_proposition_absorbs_nothing(ab, rule) -> None:
    # [SD04] Secs. 9.1, 10.2: when one proposition of a conflict is empty, the
    # mass goes to the non-empty one.  m1(empty) m2(A) = 0.5 goes to A.
    frame, a, b = ab
    tbm = MassFunction(frame, {frame.empty: 0.5, a: 0.5})

    result = getattr(tbm, rule)(frame.mass({a: 1.0}))

    assert result.to_dict() == approx({"A": 1.0})


@pytest.mark.parametrize("rule", ["pcr1", "pcr2"])
def test_void_problem_keeps_the_conflict_on_empty(ab, rule) -> None:
    # Secs. 7.1 and 8.1: when the disjunctive form of the sets is empty too,
    # "the problem degenerates truly to a void problem and thus all
    # conflicting mass is transferred onto the empty set".
    frame, *_ = ab
    void = MassFunction(frame, {frame.empty: 1.0})

    result = getattr(void, rule)(void)

    assert result.to_dict() == {"empty": 1.0}


def test_pcr4_does_not_mistake_underflow_for_zero(ab) -> None:
    # m12(A) = 0.5 * 1e-200 * 1e-200 underflows to 0.0 in floating point but
    # is positive, so PCR4 must weight by conjunctive masses (A gets ~0), not
    # fall back to column sums.
    frame, a, b = ab
    tiny = frame.mass({a: 1e-200, b: 1 - 1e-200}, tolerance=0.0)

    result = frame.mass({a: 0.5, b: 0.5}).pcr4(tiny, tiny)

    assert result[a] < 1e-100
    assert result[b] == approx(1.0)


def test_canonical_form_is_taken_over_focal_elements() -> None:
    # Interpretation (documented in pcr3()): the canonical form keeps the
    # minimal focal elements of a conflicting product; composite DSm
    # propositions are not split into conjunctive-normal-form clauses, because
    # PCR1-PCR4 redistribute to focal elements weighted by their column sums.
    frame = Frame.hybrid(["A", "B", "C", "D"], empty=["A&D"])
    a, b, c, d = frame.symbols()
    composite = a & (b | c)
    m1 = frame.mass({composite: 1.0})
    m2 = frame.mass({d: 1.0})

    result = m1.pcr3(m2)

    _assert_masses(result, {composite: 0.5, d: 0.5}, abs_tol=1e-12)


def test_sd04_section_11_5_differs_from_the_general_pcr5_formula(ab) -> None:
    # [SD04] Sec. 11.5 applies PCR5 to m1, m2 and the vacuous assignment with
    # the canonical form A & B & (A|B) = A & B and reports neutrality
    # (0.584, 0.366, 0.05).  The paper's own general formula (eq. 33), read
    # literally, gives A|B a share, as does its equivalent form in Dezert,
    # Dezert and Smarandache (JAIF 2021, eq. 14), which `pcr5()` implements;
    # the vacuous source is then not neutral (JAIF 2021, eq. 19, Example 4).
    # The inconsistency is between [SD04]'s formula and its worked example;
    # this test pins the formula-based behaviour.
    frame, a, b = ab
    m1 = frame.mass({a: 0.6, b: 0.3, a | b: 0.1})
    m2 = frame.mass({a: 0.2, b: 0.3, a | b: 0.5})

    two = m1.pcr5(m2)
    three = m1.pcr5(m2, frame.mass({a | b: 1.0}))

    _assert_masses(two, {a: 0.584, b: 0.366, a | b: 0.05}, abs_tol=1e-9)
    assert three[a | b] > two[a | b]


# ===========================================================================
# TBM disjunctive rule [D08]
# ===========================================================================


def test_d08_table_5_disjunctive_rule() -> None:
    frame = Frame.dst(["a", "b", "c"])
    a, b, c = frame.symbols()
    m1 = frame.mass({frame.empty: 0.1, a | b: 0.3, b | c: 0.6})
    m2 = frame.mass({frame.empty: 0.1, b: 0.5, b | c: 0.4})

    result = m1.disjunctive(m2)

    expected = {frame.empty: 0.01, b: 0.05, a | b: 0.18, b | c: 0.64, frame.total: 0.12}
    _assert_masses(result, expected, abs_tol=1e-12)


def test_disjunctive_rule_is_associative_and_has_empty_as_neutral(abc) -> None:
    frame, a, b, c = abc
    m1 = frame.mass({a: 0.6, b | c: 0.4})
    m2 = frame.mass({b: 0.5, a | c: 0.5})
    m3 = frame.mass({c: 0.2, a: 0.8})
    neutral = MassFunction(frame, {frame.empty: 1.0})

    joint = m1.disjunctive(m2, m3)

    assert joint.to_dict() == approx(m1.disjunctive(m2).disjunctive(m3).to_dict())
    assert m1.disjunctive(neutral).to_dict() == approx(m1.to_dict())
