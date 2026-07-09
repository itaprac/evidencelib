from itertools import permutations
from math import isclose, nan
from random import Random

import pytest
from pytest import approx

from evidencelib import Frame, MassFunction, Proposition
from evidencelib.exceptions import InvalidMassError


def test_dsmh_preserves_partially_possible_intersection() -> None:
    source = Frame.dsmt(["A", "B", "C"])
    a, b, c = source.symbols()
    target = Frame.hybrid(["A", "B", "C"], empty=["A&B"])

    result = source.mass({a | c: 1.0}).dsmh(
        source.mass({b: 1.0}),
        model=target,
    )

    target_b, target_c = target.symbols()[1:]
    assert result.to_dict() == {str(target_b & target_c): 1.0}


def test_dsmh_s2_transfers_nonexistent_atom_to_total_ignorance() -> None:
    source = Frame.dst(["A", "B", "C"])
    _, _, c = source.symbols()
    target = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])

    result = source.mass({c: 1.0}).dsmh(source.mass({c: 1.0}), model=target)

    assert result.to_dict() == {"A|B": 1.0}


def test_dsmh_reduces_to_dsmc_on_free_model() -> None:
    frame = Frame.dsmt(["A", "B", "C"])
    a, b, c = frame.symbols()
    first = frame.mass({a: 0.4, b | c: 0.6})
    second = frame.mass({b: 0.3, a & c: 0.7})

    assert first.dsmh(second).to_dict() == first.dsmc(second).to_dict()


def test_dynamic_target_may_add_but_not_relax_constraints() -> None:
    source = Frame.dst(["A", "B"])
    a, _ = source.symbols()
    mass = source.mass({a: 1.0})

    with pytest.raises(ValueError, match="cannot make regions possible"):
        mass.dsmh(source.mass({a: 1.0}), model=Frame.dsmt(["A", "B"]))
    with pytest.raises(ValueError, match="same ordered frame atoms"):
        mass.dsmh(source.mass({a: 1.0}), model=Frame.dst(["A", "C"]))


def test_dubois_prade_static_zadeh_matches_dsmh() -> None:
    frame = Frame.dst(["M", "C", "T"])
    meningitis, concussion, tumor = frame.symbols()
    first = frame.mass({meningitis: 0.9, tumor: 0.1})
    second = frame.mass({concussion: 0.9, tumor: 0.1})

    result = first.dubois_prade(second)

    assert result[meningitis | concussion] == approx(0.81)
    assert result[meningitis | tumor] == approx(0.09)
    assert result[concussion | tumor] == approx(0.09)
    assert result[tumor] == approx(0.01)
    assert result.to_dict() == first.dsmh(second).to_dict()


def test_dubois_prade_rejects_more_than_two_sources() -> None:
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    sources = (frame.mass({a: 1.0}), frame.mass({b: 1.0}), frame.mass({a | b: 1.0}))

    with pytest.raises(ValueError, match="exactly two"):
        sources[0].dubois_prade(*sources[1:])


def test_pcr_invariants_for_total_conflict_and_vacuous_source() -> None:
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    first = frame.mass({a: 1.0})
    second = frame.mass({b: 1.0})
    vacuous = frame.mass({a | b: 1.0})

    assert first.pcr5(second)[a] == approx(0.5)
    assert first.pcr5(second)[b] == approx(0.5)
    assert first.pcr5(vacuous).to_dict() == first.to_dict()


def test_pcr6_three_way_total_conflict_is_uniform() -> None:
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()

    result = frame.mass({a: 1.0}).pcr6(
        frame.mass({b: 1.0}),
        frame.mass({c: 1.0}),
    )

    assert result[a] == approx(1 / 3)
    assert result[b] == approx(1 / 3)
    assert result[c] == approx(1 / 3)


def test_pcr5_hybrid_example_from_paper_page_22() -> None:
    frame = Frame.hybrid(["J", "G", "D"], empty=["J&D", "G&D"])
    john, george, david = frame.symbols()
    first = frame.mass({john: 0.9, david: 0.1})
    second = frame.mass({george: 0.8, david: 0.2})

    result = first.pcr5(second)

    assert result[john] == approx(0.18 * 0.9 / 1.1)
    assert result[george] == approx(0.08 * 0.8 / 0.9)
    assert result[david] == approx(0.02 + 0.18 * 0.2 / 1.1 + 0.08 * 0.1 / 0.9)
    assert result[john & george] == approx(0.72)


def test_pcr_rejects_source_mass_on_universal_empty() -> None:
    frame = Frame.dst(["A", "B"])
    conflicted = frame.mass({"empty": 0.2, "A": 0.8})

    with pytest.raises(ValueError, match=r"m\(empty\) = 0"):
        conflicted.pcr5(frame.mass({"B": 1.0}))
    with pytest.raises(ValueError, match=r"m\(empty\) = 0"):
        conflicted.dsmh(frame.mass({"B": 1.0}), model=frame)


def test_union_atoms_uses_canonical_dnf_support() -> None:
    frame = Frame.dsmt(["A", "B", "C"])
    a, b, c = frame.symbols()

    assert (a & b).union_atoms() == a | b
    assert (a & (b | c)).union_atoms() == a | b | c


def test_noncanonical_raw_region_proposition_is_rejected() -> None:
    frame = Frame.dsmt(["A", "B"])

    with pytest.raises(ValueError, match="canonical"):
        Proposition(frame, frozenset({1}))


def test_tbm_belief_excludes_empty_set_conflict() -> None:
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    result = frame.mass({a: 1.0}).smets(frame.mass({a: 0.6, b: 0.4}))

    assert result.conflict == approx(0.4)
    assert result.belief(frame.empty) == 0.0
    assert result.belief(a) == approx(0.6)
    assert result.plausibility(a) == approx(0.6)
    assert result.belief(frame.total) == approx(0.6)


def test_nonfinite_mass_is_rejected_even_when_other_values_sum_to_one() -> None:
    frame = Frame.dst(["A", "B"])

    with pytest.raises(InvalidMassError, match="finite"):
        frame.mass({"A": 1.0, "B": nan})


def test_tolerance_is_propagated_through_fusion() -> None:
    frame = Frame.dst(["A", "B"])
    first = frame.mass({"A": 0.5, "B": 0.5}, tolerance=1e-5)
    second = frame.mass({"A|B": 1.0})

    assert first.dempster(second).tolerance == 1e-5
    assert first.yager(second).tolerance == 1e-5
    assert first.pcr5(second).tolerance == 1e-5


def test_json_v2_rejects_different_hybrid_constraint_structure() -> None:
    source = Frame.hybrid(["A", "B", "C"], empty=["A&B"])
    target = Frame.hybrid(["A", "B", "C"], empty=["A&C"])
    text = source.mass({"A&C": 1.0}).to_json(indent=None)

    with pytest.raises(ValueError, match="constraints"):
        MassFunction.from_json(target, text)


def test_hybrid_json_without_exact_region_metadata_is_rejected() -> None:
    frame = Frame.hybrid(["A", "B", "C"], empty=["A&B"])
    ambiguous_payload = {
        "frame": {
            "atoms": ["A", "B", "C"],
            "model": "hybrid",
            "region_count": frame.region_count,
        },
        "masses": {"A|B|C": 1.0},
    }

    with pytest.raises(ValueError, match="exact frame-region metadata"):
        MassFunction.from_dict(frame, ambiguous_payload)


def test_dst_construction_and_element_generation_avoid_free_universe() -> None:
    frame = Frame.dst([f"H{index}" for index in range(20)])

    assert frame.region_count == 20
    assert len(Frame.dst([f"H{index}" for index in range(10)]).elements()) == 1024


def test_randomized_dsmh_and_pcr6_invariants() -> None:
    random = Random(20260709)
    source = Frame.dsmt(["A", "B", "C"])
    target = Frame.hybrid(["A", "B", "C"], empty=["A&B"])
    focal_pool = source.elements()[1:]

    for _ in range(20):
        sources = []
        for _source_index in range(3):
            focal = random.sample(focal_pool, 4)
            raw = [random.random() for _ in focal]
            total = sum(raw)
            sources.append(source.mass({prop: value / total for prop, value in zip(focal, raw)}))

        result = sources[0].dsmh(*sources[1:], model=target)
        assert result.frame is target
        assert result.conflict == 0.0
        assert result.total_mass == approx(1.0)

    dst = Frame.dst(["A", "B", "C"])
    a, b, c = dst.symbols()
    deterministic = [dst.mass({a: 1.0}), dst.mass({b: 1.0}), dst.mass({c: 1.0})]
    reference = deterministic[0].pcr6(*deterministic[1:])
    for ordering in permutations(deterministic):
        candidate = ordering[0].pcr6(*ordering[1:])
        assert set(candidate.focal()) == set(reference.focal())
        assert all(
            isclose(candidate[prop], reference[prop], abs_tol=1e-12)
            for prop in reference.focal()
        )
