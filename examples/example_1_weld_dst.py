"""Reproduce the weld-inspection tables and figures from article Section 3.1."""

from __future__ import annotations

import argparse
from pathlib import Path

from evidencelib import Frame, MassFunction

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
RULE_LABELS = ("Smets/TBM", "Dempster", "Yager", "Dubois--Prade", "PCR5")
PLOT_RULE_LABELS = ("Smets/TBM", "Dempster", "Yager", "Dubois-Prade", "PCR5")


def build_sources() -> tuple[MassFunction, MassFunction]:
    """Return the two synthetic mass functions reported in Section 3.1."""

    frame = Frame.dst(["A", "R", "J"])
    accept, repair, reject = frame.symbols()
    accept_or_repair = accept | repair
    theta = accept | repair | reject

    visual = frame.mass(
        {
            accept: 0.70,
            accept_or_repair: 0.15,
            theta: 0.15,
        }
    )
    ultrasonic = frame.mass(
        {
            repair: 0.65,
            accept_or_repair: 0.20,
            theta: 0.15,
        }
    )
    return visual, ultrasonic


def fuse_sources(
    visual: MassFunction,
    ultrasonic: MassFunction,
) -> tuple[MassFunction, ...]:
    """Apply the five fusion rules compared in the article."""

    return (
        visual.smets(ultrasonic),
        visual.dempster(ultrasonic),
        visual.yager(ultrasonic),
        visual.dubois_prade(ultrasonic),
        visual.pcr5(ultrasonic),
    )


def decision_action(mass: MassFunction) -> str:
    """Apply the illustrative decision policy stated in Section 3.1."""

    scores = mass.pignistic()
    if max(scores.values()) < 0.50:
        return "Additional inspection"
    return {"A": "Accept", "R": "Repair", "J": "Reject"}[mass.decision()]


def write_tables(
    visual: MassFunction,
    ultrasonic: MassFunction,
    results: tuple[MassFunction, ...],
    output_dir: Path,
) -> None:
    """Write the two Section 3.1 tables using the public LaTeX exporters."""

    source_table = visual.comparison_to_latex(
        ultrasonic,
        labels=("Visual inspection", "Ultrasonic testing"),
        propositions=("A", "R", "A|R", "A|R|J"),
        caption="Synthetic input mass assignments for weld inspection.",
        label="tab:dst-input-masses",
        float_format=".2f",
        position="H",
    )
    (output_dir / "weld_input_masses.tex").write_text(
        source_table + "\n",
        encoding="utf-8",
    )

    decision_table = results[0].pignistic_comparison_to_latex(
        *results[1:],
        labels=RULE_LABELS,
        actions=tuple(decision_action(result) for result in results),
        caption="Conflict, pignistic scores, and actions for DST fusion rules.",
        label="tab:dst-decisions",
        float_format=".3f",
        position="H",
        source_header="Fusion rule",
        font_size="footnotesize",
    )
    (output_dir / "weld_decisions.tex").write_text(
        decision_table + "\n",
        encoding="utf-8",
    )


def write_figures(
    visual: MassFunction,
    ultrasonic: MassFunction,
    results: tuple[MassFunction, ...],
    output_dir: Path,
) -> None:
    """Write the two Section 3.1 figures as vector PDFs."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from evidencelib import plot_mass_comparison

    figure, axis = plt.subplots(figsize=(8.0, 4.2))
    plot_mass_comparison(
        (visual, ultrasonic),
        labels=("Visual inspection", "Ultrasonic testing"),
        ax=axis,
        title="Input mass assignments for weld inspection",
        cmap=("#F7FBFF", "#08519C"),
    )
    figure.tight_layout()
    figure.savefig(output_dir / "weld_input_masses.pdf", bbox_inches="tight")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(8.0, 5.0))
    plot_mass_comparison(
        results,
        labels=PLOT_RULE_LABELS,
        ax=axis,
        title="Conflict management strategies in DST",
        cmap=("#F7FBFF", "#08519C"),
    )
    axis.set_ylabel("Fusion rules")
    figure.tight_layout()
    figure.savefig(output_dir / "weld_rule_comparison.pdf", bbox_inches="tight")
    plt.close(figure)


def reproduce(output_dir: Path = DEFAULT_OUTPUT_DIR) -> tuple[MassFunction, ...]:
    """Generate every table and figure used by the weld example."""

    output_dir.mkdir(parents=True, exist_ok=True)
    visual, ultrasonic = build_sources()
    results = fuse_sources(visual, ultrasonic)
    write_tables(visual, ultrasonic, results, output_dir)
    write_figures(visual, ultrasonic, results, output_dir)
    return results


def main() -> None:
    """Run the complete Section 3.1 reproduction workflow."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    results = reproduce(args.output_dir)
    for label, result in zip(RULE_LABELS, results, strict=True):
        scores = result.pignistic()
        print(
            f"{label}: K={result.conflict:.6f}, "
            f"BetP(A)={scores['A']:.6f}, BetP(R)={scores['R']:.6f}, "
            f"BetP(J)={scores['J']:.6f}, action={decision_action(result)}"
        )
    print(f"Artifacts written to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
