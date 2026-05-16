from pytest import approx

from pybelief import Frame


def test_free_dsmt_dsmc_pdf_example():
    frame = Frame.dsmt(["t1", "t2", "t3"])
    t1, t2, t3 = frame.symbols()

    m1 = frame.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
    m2 = frame.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})

    result = m1.dsmc(m2)

    assert result[t1] == approx(0.21)
    assert result[t2] == approx(0.11)
    assert result[t3] == approx(0.06)
    assert result[t1 | t2] == approx(0.03)
    assert result[t1 & t2] == approx(0.21)
    assert result[t1 & t3] == approx(0.13)
    assert result[t2 & t3] == approx(0.14)
    assert result[t3 & (t1 | t2)] == approx(0.11)


def test_hybrid_dsmh_dynamic_pdf_example():
    frame = Frame.hybrid(["t1", "t2", "t3"], exclusive=True, empty=["t3"])
    t1, t2, t3 = frame.symbols()

    m1 = frame.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
    m2 = frame.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})

    result = m1.dsmh(m2)

    assert result[t1] == approx(0.34)
    assert result[t2] == approx(0.25)
    assert result[t1 | t2] == approx(0.41)
    assert str(t1 | t2) == "t1|t2"
    assert result.frame.empty not in dict(result.items())


def test_elements_match_small_cardinalities():
    assert len(Frame.dst(["A", "B", "C"]).elements()) == 8
    assert len(Frame.dsmt(["A", "B"]).elements()) == 5
    assert len(Frame.dsmt(["A", "B", "C"]).elements()) == 19
    assert Frame.dsmt(["A", "B", "C"]).region_count == 7


def test_generalized_pignistic_uses_overlapping_events():
    frame = Frame.dsmt(["A", "B"])
    a, b = frame.symbols()
    mass = frame.mass({a: 0.2, b: 0.3, a & b: 0.4, a | b: 0.1})

    betp = mass.pignistic()
    regions = mass.pignistic_regions()

    assert betp["A"] == approx(0.8166666666666667)
    assert betp["B"] == approx(0.8666666666666667)
    assert sum(regions.values()) == approx(1.0)
    assert set(betp) == {"A", "B"}
