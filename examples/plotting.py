"""Plotting examples for evidencelib.

Install the optional plotting extra before running:

    pip install "evidencelib[plot]"

Examples:

    python examples/plotting.py --figure models --model dst
    python examples/plotting.py --figure venn
    python examples/plotting.py --figure belief
    python examples/plotting.py --figure pignistic
    python examples/plotting.py --figure all --save-dir /tmp/evidencelib-plots
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from evidencelib import (
    Frame,
    plot_belief_plausibility,
    plot_mass,
    plot_mass_comparison,
    plot_pignistic_decision,
    plot_venn,
)

MODEL_NAMES = ("dst", "dsmt", "hybrid")
MODEL_TITLES = {
    "dst": "DST",
    "dsmt": "Free DSmT",
    "hybrid": "Hybrid DSmT",
}


def build_model_example(
    model: str = "dst",
    *,
    symbols: tuple[str, ...] = ("A", "B", "C"),
    hybrid_empty: tuple[str, ...] | None = None,
):
    """Build one mass-assignment example for a selected frame model."""

    if model not in MODEL_NAMES:
        choices = ", ".join(MODEL_NAMES)
        raise ValueError(f"model must be one of: {choices}.")
    if len(symbols) < 3:
        raise ValueError("At least three symbols are required.")

    if model == "dst":
        frame = Frame.dst(symbols)
    elif model == "dsmt":
        frame = Frame.dsmt(symbols)
    else:
        empty = hybrid_empty if hybrid_empty is not None else (symbols[2],)
        frame = Frame.hybrid(symbols, empty=empty)

    a, b, c = frame.symbols()[:3]
    mass = frame.mass({
        a: 0.35,
        b: 0.20,
        a | b: 0.25,
        a & c: 0.20,
    })
    return MODEL_TITLES[model], mass


def build_model_examples(
    models: tuple[str, ...] = MODEL_NAMES,
    *,
    symbols: tuple[str, ...] = ("A", "B", "C"),
    hybrid_empty: tuple[str, ...] | None = None,
):
    return [
        build_model_example(model, symbols=symbols, hybrid_empty=hybrid_empty)
        for model in models
    ]


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


def build_venn_example():
    frame = Frame.dsmt(["A", "B", "C"])
    a, b, c = frame.symbols()

    return frame.mass({
        a: 0.20,
        b: 0.18,
        c: 0.12,
        a & b: 0.22,
        a & c: 0.10,
        b | c: 0.08,
        a | b | c: 0.10,
    })


def show_model_examples(
    models: tuple[str, ...] = MODEL_NAMES,
    *,
    symbols: tuple[str, ...] = ("A", "B", "C"),
    hybrid_empty: tuple[str, ...] | None = None,
):
    examples = build_model_examples(
        models,
        symbols=symbols,
        hybrid_empty=hybrid_empty,
    )
    if len(examples) == 1:
        fig, ax = plt.subplots(figsize=(7.0, 4.8))
        title, mass = examples[0]
        plot_mass(mass, ax=ax, title=title)
        fig.tight_layout()
        return fig

    fig, axes = plt.subplots(
        1,
        len(examples),
        figsize=(5 * len(examples), 4.8),
        sharex=True,
    )
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


def show_venn_regions_example():
    mass = build_venn_example()
    fig, ax = plt.subplots(figsize=(5.4, 4.8))
    plot_venn(
        mass,
        ax=ax,
        title="Pignistic Venn-region probabilities",
        show_region_labels=True,
    )
    fig.tight_layout()
    return fig


def show_belief_plausibility_example():
    mass = build_decision_example()
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    plot_belief_plausibility(
        mass,
        ax=ax,
        title="Belief-plausibility intervals",
    )
    fig.tight_layout()
    return fig


def show_pignistic_decision_example():
    mass = build_decision_example()
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    plot_pignistic_decision(
        mass,
        ax=ax,
        title="Pignistic decision ranking",
    )
    fig.tight_layout()
    return fig


def _parse_args():
    parser = argparse.ArgumentParser(description="Run evidencelib plotting examples.")
    parser.add_argument(
        "--figure",
        choices=(
            "all",
            "models",
            "comparison",
            "venn",
            "decision",
            "belief",
            "pignistic",
        ),
        default="all",
        help="Which example figure to draw.",
    )
    parser.add_argument(
        "--model",
        choices=(*MODEL_NAMES, "all"),
        default="all",
        help="Frame model for --figure models.",
    )
    parser.add_argument(
        "--symbols",
        nargs="+",
        default=("A", "B", "C"),
        help="Frame symbols used by the model examples.",
    )
    parser.add_argument(
        "--hybrid-empty",
        nargs="*",
        default=None,
        help="Symbols constrained to empty in the hybrid model example.",
    )
    parser.add_argument(
        "--save-dir",
        type=Path,
        default=None,
        help="Directory where selected figures should be saved as PNG files.",
    )
    return parser.parse_args()


def _selected_models(model: str) -> tuple[str, ...]:
    if model == "all":
        return MODEL_NAMES
    return (model,)


def _build_selected_figures(args):
    symbols = tuple(args.symbols)
    hybrid_empty = None if args.hybrid_empty is None else tuple(args.hybrid_empty)
    models = _selected_models(args.model)
    figures = []

    if args.figure in {"all", "models"}:
        figures.append((
            "mass-models",
            show_model_examples(
                models,
                symbols=symbols,
                hybrid_empty=hybrid_empty,
            ),
        ))
    if args.figure in {"all", "comparison"}:
        figures.append(("mass-comparison", show_mass_comparison_example()))
    if args.figure in {"all", "venn"}:
        figures.append(("venn-regions", show_venn_regions_example()))
    if args.figure in {"all", "decision"}:
        figures.append(("decision-combined", show_decision_examples()))
    if args.figure == "belief":
        figures.append(("belief-plausibility", show_belief_plausibility_example()))
    if args.figure == "pignistic":
        figures.append(("pignistic-decision", show_pignistic_decision_example()))

    return figures


def _save_figures(figures, save_dir: Path) -> None:
    save_dir.mkdir(parents=True, exist_ok=True)
    for name, fig in figures:
        path = save_dir / f"{name}.png"
        fig.savefig(path, dpi=180)
        print(path)


if __name__ == "__main__":
    args = _parse_args()
    selected = _build_selected_figures(args)
    if args.save_dir is not None:
        _save_figures(selected, args.save_dir)
    if args.save_dir is None and plt.get_backend().lower() != "agg":
        plt.show()
