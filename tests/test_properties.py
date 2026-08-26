"""Deterministic invariant tests for evidence models and fusion rules."""

from __future__ import annotations

from pathlib import Path
from random import Random
from runpy import run_path

from pytest import approx

from evidencelib import Frame, MassFunction


def _deterministic_mass(frame: Frame, seed: int, focal_count: int = 6) -> MassFunction:
    candidates = sorted((prop for prop in frame.elements() if prop), key=str)
    rng = Random(seed)
    focal = rng.sample(candidates, min(focal_count, len(candidates)))
    weights = [rng.random() + 0.1 for _ in focal]
    total = sum(weights)
    return frame.mass({prop: weight / total for prop, weight in zip(focal, weights, strict=True)})


def _assert_same_masses(left: MassFunction, right: MassFunction) -> None:
    assert left.frame is right.frame
    assert set(left.focal()) == set(right.focal())
    assert left.to_dict() == approx(right.to_dict())


def test_belief_never_exceeds_plausibility_for_model_elements():
    frames = (
        Frame.dst(["A", "B", "C"]),
        Frame.dsmt(["A", "B", "C"]),
        Frame.hybrid(["A", "B", "C"], empty=["A&C"]),
    )

    for frame in frames:
        for seed in (101, 202, 303):
            mass = _deterministic_mass(frame, seed)
            for proposition in frame.elements():
                assert mass.belief(proposition) <= mass.plausibility(proposition) + 1e-12


def test_fusion_rules_conserve_total_mass():
    frame = Frame.dst(["A", "B", "C"])
    first = _deterministic_mass(frame, 401)
    second = _deterministic_mass(frame, 402)

    results = {
        "dempster": first.dempster(second),
        "yager": first.yager(second),
        "dubois_prade": first.dubois_prade(second),
        "dsmc": first.dsmc(second),
        "dsmh": first.dsmh(second),
        "pcr5": first.pcr5(second),
        "pcr6": first.pcr6(second),
    }

    for result in results.values():
        assert result.total_mass == approx(1.0)

    smets = first.smets(second)
    nonempty_mass = sum(value for prop, value in smets.items() if prop)
    assert smets.conflict > 0.0
    assert nonempty_mass + smets.conflict == approx(1.0)


def test_dsmc_is_commutative_and_associative():
    frame = Frame.dsmt(["A", "B", "C"])
    first = _deterministic_mass(frame, 501)
    second = _deterministic_mass(frame, 502)
    third = _deterministic_mass(frame, 503)

    _assert_same_masses(first.dsmc(second), second.dsmc(first))
    _assert_same_masses(first.dsmc(second).dsmc(third), first.dsmc(second.dsmc(third)))


def test_pcr5_conserves_mass_for_deterministic_assignments():
    frame = Frame.dst(["A", "B", "C"])

    for first_seed, second_seed in ((601, 602), (603, 604), (605, 606)):
        result = _deterministic_mass(frame, first_seed).pcr5(
            _deterministic_mass(frame, second_seed)
        )
        assert result.total_mass == approx(1.0)
        assert result.conflict == approx(0.0)


def test_zadeh_example_matches_the_documented_results(capsys):
    example = Path(__file__).resolve().parents[1] / "examples" / "zadeh.py"
    namespace = run_path(str(example))
    capsys.readouterr()

    first = namespace["m1"]
    second = namespace["m2"]
    m, c, t = namespace["M"], namespace["C"], namespace["T"]

    assert first.dempster(second)[t] == approx(1.0)
    assert first.yager(second)[m | c | t] == approx(0.99)
    assert first.dsmh(second).to_dict() == approx(
        {"M|C": 0.81, "C|T": 0.09, "M|T": 0.09, "T": 0.01}
    )
    assert first.dubois_prade(second).to_dict() == approx(
        {"M|C": 0.81, "C|T": 0.09, "M|T": 0.09, "T": 0.01}
    )
    assert first.pcr5(second).to_dict() == approx(
        {"C": 0.486, "M": 0.486, "T": 0.028}
    )


def test_dsmh_reduces_to_dempster_without_conflict_on_shafer_model():
    frame = Frame.dst(["A", "B"])
    a, _ = frame.symbols()
    first = frame.mass({a: 0.4, frame.total: 0.6})
    second = frame.mass({a: 0.3, frame.total: 0.7})

    _assert_same_masses(first.dsmh(second), first.dempster(second))
