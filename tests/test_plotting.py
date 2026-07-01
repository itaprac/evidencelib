import pytest

from evidencelib import (
    Frame,
    plot_belief_plausibility,
    plot_mass,
    plot_mass_comparison,
    plot_pignistic_decision,
)

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def test_plot_functions_return_axes():
    frame = Frame.dst(["A", "B", "C"])
    a, b, c = frame.symbols()
    mass = frame.mass({a: 0.35, b: 0.2, a | b: 0.25, c: 0.2})

    assert plot_mass(mass, title="Mass").get_title() == "Mass"
    assert plot_belief_plausibility(mass).get_ylabel() == "Support"
    assert plot_pignistic_decision(mass).get_xlabel() == "Pignistic score"

    plt.close("all")


def test_plot_methods_delegate_to_public_functions():
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    first = frame.mass({a: 0.6, a | b: 0.4})
    second = frame.mass({b: 0.3, a | b: 0.7})

    assert first.plot().get_xlabel() == "Assigned mass"
    assert first.plot_comparison(second, labels=["first", "second"]).get_ylabel() == "Sources"
    assert first.plot_belief_plausibility().get_xlabel() == "Hypotheses"
    assert first.plot_pignistic_decision().get_ylabel() == "Hypotheses"

    plt.close("all")


def test_mass_comparison_validates_common_frame():
    left = Frame.dst(["A", "B"])
    right = Frame.dst(["A", "B"])
    left_a, left_b = left.symbols()
    right_a, right_b = right.symbols()

    first = left.mass({left_a: 0.5, left_a | left_b: 0.5})
    second = right.mass({right_a: 0.5, right_a | right_b: 0.5})

    with pytest.raises(ValueError, match="same frame"):
        plot_mass_comparison([first, second])

    plt.close("all")


def test_plot_filters_validate_empty_results():
    frame = Frame.dst(["A", "B"])
    a, b = frame.symbols()
    mass = frame.mass({a: 0.6, a | b: 0.4})

    with pytest.raises(ValueError, match="No propositions"):
        plot_mass(mass, min_mass=0.9, show_other=False)

    with pytest.raises(ValueError, match="positive integer"):
        plot_pignistic_decision(mass, top_n=0)

    plt.close("all")
