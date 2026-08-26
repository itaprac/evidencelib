"""Reproduce the hybrid-DSm extension of the pump example in Section 3.2."""

from __future__ import annotations

import argparse
from pathlib import Path

from evidencelib import Frame, MassFunction

DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"


def build_sources() -> tuple[MassFunction, MassFunction, MassFunction]:
    """Return the Section 3.2 sources on the original free DSm frame."""

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


def write_artifacts(result: MassFunction, output_dir: Path) -> None:
    """Write the hybrid result table and vector Venn figure."""

    output_dir.mkdir(parents=True, exist_ok=True)
    table = result.to_latex(
        caption="Fused masses under the hybrid DSm model (DSmH).",
        label="tab:dsmt-hybrid-masses",
        float_format=".4f",
        position="H",
    )
    (output_dir / "pump_hybrid_masses.tex").write_text(
        table + "\n",
        encoding="utf-8",
    )

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(6.0, 5.2))
    result.plot_venn(
        ax=axis,
        show_region_labels=True,
        title="Hybrid-DSm pignistic region probabilities",
    )
    figure.tight_layout()
    figure.savefig(output_dir / "pump_hybrid_venn_regions.pdf", bbox_inches="tight")
    plt.close(figure)


def reproduce(output_dir: Path = DEFAULT_OUTPUT_DIR) -> tuple[MassFunction, MassFunction]:
    """Generate the free baseline and hybrid DSmH result and artifacts."""

    current, vibration, pressure = build_sources()
    free_result = current.dsmc(vibration, pressure)
    hybrid_frame = Frame.hybrid(["E", "M", "H"], empty=["E&H"])
    hybrid_result = current.dsmh(vibration, pressure, model=hybrid_frame)
    write_artifacts(hybrid_result, output_dir)
    return free_result, hybrid_result


def main() -> None:
    """Run the complete hybrid-DSm Section 3.2 reproduction workflow."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    free_result, hybrid_result = reproduce(args.output_dir)
    free_e, free_m, free_h = free_result.frame.symbols()
    hybrid_e, hybrid_m, hybrid_h = hybrid_result.frame.symbols()
    regions = hybrid_result.pignistic_regions()
    print(f"Free DSm domain size: {len(free_result.frame.elements())}")
    print(f"Hybrid DSm domain size: {len(hybrid_result.frame.elements())}")
    print(f"Free m(E&H)={free_result[free_e & free_h]:.6f}")
    print(f"Free m(E&M&H)={free_result[free_e & free_m & free_h]:.6f}")
    print(f"Hybrid m(E&M)={hybrid_result[hybrid_e & hybrid_m]:.6f}")
    print(f"Hybrid m(Theta)={hybrid_result[hybrid_e | hybrid_m | hybrid_h]:.6f}")
    print(f"Hybrid pignistic region E&M={regions['E&M']:.6f}")
    print(f"Hybrid pignistic region M&H={regions['M&H']:.6f}")
    print(f"Free Deng entropy={free_result.deng_entropy():.6f}")
    print(f"Hybrid Deng entropy={hybrid_result.deng_entropy():.6f}")
    print(f"Artifacts written to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
