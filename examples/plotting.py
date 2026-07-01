"""Plotting examples for evidencelib.

Install the optional plotting extra before running:

    pip install "evidencelib[plot]"
"""

import matplotlib.pyplot as plt

from evidencelib import (
    Frame,
    plot_belief_plausibility,
    plot_mass,
    plot_mass_comparison,
    plot_pignistic_decision,
)


def build_model_examples():
    dst_frame = Frame.dst(["A", "B", "C"])
    a_dst, b_dst, c_dst = dst_frame.symbols()
    dst = dst_frame.mass({
        a_dst: 0.35,
        b_dst: 0.20,
        a_dst | b_dst: 0.25,
        a_dst & c_dst: 0.20,
    })

    dsmt_frame = Frame.dsmt(["A", "B", "C"])
    a_dsmt, b_dsmt, c_dsmt = dsmt_frame.symbols()
    dsmt = dsmt_frame.mass({
        a_dsmt: 0.35,
        b_dsmt: 0.20,
        a_dsmt | b_dsmt: 0.25,
        a_dsmt & c_dsmt: 0.20,
    })

    hybrid_frame = Frame.hybrid(["A", "B", "C"], empty=["C"])
    a_hybrid, b_hybrid, c_hybrid = hybrid_frame.symbols()
    hybrid = hybrid_frame.mass({
        a_hybrid: 0.35,
        b_hybrid: 0.20,
        a_hybrid | b_hybrid: 0.25,
        a_hybrid & c_hybrid: 0.20,
    })

    return [("DST", dst), ("Free DSmT", dsmt), ("Hybrid DSmT", hybrid)]


def build_comparison_example():
    frame = Frame.dst(["A", "B", "C", "D"])
    a, b, c, d = frame.symbols()

    sensor = frame.mass({
        a: 0.45,
        b: 0.10,
        a | b: 0.20,
        a | b | c | d: 0.25,
    })
    expert = frame.mass({
        b: 0.35,
        c: 0.20,
        b | c: 0.25,
        a | b | c | d: 0.20,
    })
    model = frame.mass({
        a: 0.25,
        c: 0.25,
        d: 0.10,
        a | c: 0.15,
        a | b | c | d: 0.25,
    })

    return [sensor, expert, model], ["sensor", "expert", "model"]


def build_decision_example():
    frame = Frame.dst(["A", "B", "C", "D"])
    a, b, c, d = frame.symbols()

    return frame.mass({
        a: 0.22,
        b: 0.12,
        c: 0.08,
        a | b: 0.18,
        a | c: 0.14,
        b | d: 0.10,
        a | b | c | d: 0.16,
    })


def show_model_examples():
    examples = build_model_examples()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharex=True)
    for ax, (title, mass) in zip(axes, examples, strict=True):
        plot_mass(mass, ax=ax, title=title)
    fig.suptitle("Mass assignment across frame models", fontsize=14)
    fig.tight_layout()
    return fig


def show_mass_comparison_example():
    masses, labels = build_comparison_example()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    plot_mass_comparison(
        masses,
        labels=labels,
        ax=ax,
        title="Mass comparison across input sources",
    )
    fig.tight_layout()
    return fig


def show_decision_examples():
    mass = build_decision_example()
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    plot_belief_plausibility(
        mass,
        ax=axes[0],
        title="Belief-plausibility intervals",
    )
    plot_pignistic_decision(
        mass,
        ax=axes[1],
        title="Pignistic decision ranking",
    )
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    show_model_examples()
    show_mass_comparison_example()
    show_decision_examples()
    if plt.get_backend().lower() != "agg":
        plt.show()
