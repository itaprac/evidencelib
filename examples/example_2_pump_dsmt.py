"""Reproduce the free-DSm pump tables and figures from article Section 3.2."""

from __future__ import annotations

import argparse
from pathlib import Path

from evidencelib import Frame, MassFunction

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"


def build_sources() -> tuple[MassFunction, MassFunction, MassFunction]:
    """Return the three synthetic source masses reported in Section 3.2."""

    frame = Frame.dsmt(["E", "M", "H"])
    electrical, mechanical, hydraulic = frame.symbols()
    theta = electrical | mechanical | hydraulic
    current = frame.mass(
        {
            electrical: 0.65,
            electrical | mechanical: 0.20,
            theta: 0.15,
        }
    )
    vibration = frame.mass(
        {
            mechanical: 0.60,
            electrical | mechanical: 0.25,
            theta: 0.15,
        }
    )
    pressure = frame.mass(
        {
            hydraulic: 0.25,
            electrical | hydraulic: 0.15,
            mechanical | hydraulic: 0.10,
            theta: 0.50,
        }
    )
    return current, vibration, pressure


def write_table(
    current: MassFunction,
    vibration: MassFunction,
    pressure: MassFunction,
    output_dir: Path,
) -> None:
    """Write the Section 3.2 source table using the public LaTeX exporter."""

    table = current.comparison_to_latex(
        vibration,
        pressure,
        labels=("Current analysis", "Vibration analysis", "Pressure and flow"),
        propositions=("E", "M", "H", "E|M", "E|H", "M|H", "E|M|H"),
        orientation="long",
        caption="Synthetic input mass assignments for pump diagnostics.",
        label="tab:dsmt-input-masses",
        float_format=".2f",
        position="H",
    )
    (output_dir / "pump_input_masses.tex").write_text(
        table + "\n",
        encoding="utf-8",
    )


def write_figures(result: MassFunction, output_dir: Path) -> None:
    """Write the two free-DSm Section 3.2 figures as vector PDFs."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from evidencelib import plot_mass, plot_venn

    figure, axis = plt.subplots(figsize=(8.0, 5.6))
    plot_mass(
        result,
        ax=axis,
        top_n=8,
        show_other=True,
        style="proposition_types",
        title="Largest fused masses under the free DSm model",
    )
    figure.tight_layout()
    figure.savefig(output_dir / "pump_fused_masses.pdf", bbox_inches="tight")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(6.0, 5.2))
    plot_venn(
        result,
        ax=axis,
        show_region_labels=True,
        title="Free-DSm pignistic region probabilities",
    )
    figure.tight_layout()
    figure.savefig(output_dir / "pump_venn_regions.pdf", bbox_inches="tight")
    plt.close(figure)


def reproduce(output_dir: Path = DEFAULT_OUTPUT_DIR) -> MassFunction:
    """Generate every table and figure used by the free-DSm pump example."""

    output_dir.mkdir(parents=True, exist_ok=True)
    current, vibration, pressure = build_sources()
    result = current.dsmc(vibration, pressure)
    write_table(current, vibration, pressure, output_dir)
    write_figures(result, output_dir)
    return result


def main() -> None:
    """Run the complete free-DSm Section 3.2 reproduction workflow."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    result = reproduce(args.output_dir)
    electrical, mechanical, hydraulic = result.frame.symbols()
    regions = result.pignistic_regions()
    print(f"Free DSm domain size: {len(result.frame.elements())}")
    print(f"m(E&M)={result[electrical & mechanical]:.6f}")
    print(f"m(E&H)={result[electrical & hydraulic]:.6f}")
    print(f"m(E&M&H)={result[electrical & mechanical & hydraulic]:.6f}")
    print(f"Pignistic region E&M={regions['E&M']:.6f}")
    print(f"Pignistic region E&M&H={regions['E&M&H']:.6f}")
    print(f"Artifacts written to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
