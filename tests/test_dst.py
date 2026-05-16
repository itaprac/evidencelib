from pytest import approx, raises

from evidencelib import Frame
from evidencelib.exceptions import InvalidMassError, TotalConflictError


def test_wikipedia_cat_belief_and_plausibility():
    frame = Frame.dst(["Alive", "Dead"])
    alive, dead = frame.symbols()

    mass = frame.mass({
        alive: 0.2,
        dead: 0.5,
        alive | dead: 0.3,
    })

    assert mass.belief(alive) == approx(0.2)
    assert mass.plausibility(alive) == approx(0.5)
    assert mass.belief(dead) == approx(0.5)
    assert mass.plausibility(dead) == approx(0.8)
    assert mass.belief(alive | dead) == approx(1.0)
    assert mass.plausibility(alive | dead) == approx(1.0)
    assert sum(mass.pignistic().values()) == approx(1.0)


def test_mass_accepts_near_one_float_drift():
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()

    mass = frame.mass({a: 0.6, b: 0.399999999})

    assert mass.total_mass == approx(1.0)
    assert mass[a] == approx(0.6 / 0.999999999)
    assert mass[b] == approx(0.399999999 / 0.999999999)


def test_mass_rejects_real_sum_mismatch():
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()

    with raises(InvalidMassError):
        frame.mass({a: 0.6, b: 0.39})


def test_dempster_and_pcr5_pdf_example_1():
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()

    m1 = frame.mass({a: 0.6, a | b: 0.4})
    m2 = frame.mass({b: 0.3, a | b: 0.7})

    dempster = m1.dempster(m2)
    assert dempster[a] == approx(0.42 / 0.82)
    assert dempster[b] == approx(0.12 / 0.82)
    assert dempster[a | b] == approx(0.28 / 0.82)

    pcr5 = m1.pcr5(m2)
    assert pcr5[a] == approx(0.54)
    assert pcr5[b] == approx(0.18)
    assert pcr5[a | b] == approx(0.28)


def test_pcr5_pdf_examples_2_and_3():
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()

    m1 = frame.mass({a: 0.6, a | b: 0.4})
    m2 = frame.mass({a: 0.2, b: 0.3, a | b: 0.5})
    pcr5 = m1.pcr5(m2)
    assert pcr5[a] == approx(0.62)
    assert pcr5[b] == approx(0.18)
    assert pcr5[a | b] == approx(0.20)

    m1 = frame.mass({a: 0.6, b: 0.3, a | b: 0.1})
    m2 = frame.mass({a: 0.2, b: 0.3, a | b: 0.5})
    pcr5 = m1.pcr5(m2)
    assert pcr5[a] == approx(0.584)
    assert pcr5[b] == approx(0.366)
    assert pcr5[a | b] == approx(0.05)


def test_zadeh_example_from_dsmt_paper():
    frame = Frame.dst(["M", "C", "T"])
    m, c, t = frame.symbols()

    m1 = frame.mass({m: 0.9, t: 0.1})
    m2 = frame.mass({c: 0.9, t: 0.1})

    dempster = m1.dempster(m2)
    yager = m1.yager(m2)
    dsmh = m1.dsmh(m2)
    pcr5 = m1.pcr5(m2)

    assert dempster[t] == approx(1.0)
    assert yager[m | c | t] == approx(0.99)
    assert yager[t] == approx(0.01)
    assert dsmh[m | c] == approx(0.81)
    assert dsmh[t] == approx(0.01)
    assert dsmh[m | t] == approx(0.09)
    assert dsmh[c | t] == approx(0.09)
    assert pcr5[m] == approx(0.486)
    assert pcr5[c] == approx(0.486)
    assert pcr5[t] == approx(0.028)


def test_total_conflict_raises_for_dempster_normalization():
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()

    m1 = frame.mass({a: 1.0})
    m2 = frame.mass({b: 1.0})

    with raises(TotalConflictError):
        m1.dempster(m2)


def test_to_dict_and_string_parser():
    frame = Frame.dst(["A", "B", "C"])
    mass = frame.mass({"A": 0.2, "B": 0.3, "A | C": 0.5})

    assert mass["A ∪ C"] == approx(0.5)
    assert mass.to_dict() == {"A": 0.2, "A|C": 0.5, "B": 0.3}
    with raises(ValueError):
        frame.proposition("__import__('os').system('echo nope')")
