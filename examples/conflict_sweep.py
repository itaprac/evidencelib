"""Quantify how DST fusion rules respond to increasing source conflict.

This repository-only analysis extends the weld-inspection example from the
SoftwareX article.  It is a sensitivity analysis, not an error benchmark,
because the illustrative case has no ground-truth decision against which a
fusion rule could be scored.

The parameterization reproduces the article inputs at ``t = 0.70`` while
keeping every mass non-negative over the full sweep from 0.10 to 0.80.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from evidencelib import Frame, MassFunction

if TYPE_CHECKING:
    from matplotlib.axes import Axes


OUTPUT_PATH = Path(__file__).resolve().parent.parent / "output" / "fig_conflict_sweep.pdf"
ARTICLE_T = 0.70
DEFAULT_T_VALUES = tuple(value / 100 for value in range(10, 81))


@dataclass(frozen=True)
class SweepPoint:
    """One conflict level and the resulting acceptance scores."""

    t: float
    conflict: float
    betp_a: dict[str, float]


def build_sources(t: float) -> tuple[MassFunction, MassFunction]:
    """Return the two weld-inspection sources at conflict-control value ``t``."""

    if not 0.10 <= t <= 0.80:
        raise ValueError("t must be between 0.10 and 0.80 inclusive")

    frame = Frame.dst(["A", "R", "J"])
    acceptance, repair, rejection = frame.symbols()
    accept_or_repair = acceptance | repair
    theta = acceptance | repair | rejection

    visual = frame.mass(
        {
            acceptance: t,
            accept_or_repair: (1.0 - t) / 2.0,
            theta: (1.0 - t) / 2.0,
        }
    )
    ultrasonic = frame.mass(
        {
            repair: t - 0.05,
            accept_or_repair: 0.20,
            theta: 0.85 - t,
        }
    )
    return visual, ultrasonic


def evaluate(t: float) -> SweepPoint:
    """Evaluate all five fusion rules at one valid value of ``t``."""

    visual, ultrasonic = build_sources(t)
    smets = visual.smets(ultrasonic)
    fused = {
        "Dempster": visual.dempster(ultrasonic),
        "Yager": visual.yager(ultrasonic),
        "Dubois-Prade": visual.dubois_prade(ultrasonic),
        "PCR5": visual.pcr5(ultrasonic),
        "Smets/TBM": smets,
    }
    return SweepPoint(
        t=t,
        conflict=smets.conflict,
        betp_a={name: mass.pignistic()["A"] for name, mass in fused.items()},
    )


def generate_sweep(t_values: Iterable[float] = DEFAULT_T_VALUES) -> list[SweepPoint]:
    """Return sweep results in the order supplied by ``t_values``."""

    return [evaluate(t) for t in t_values]


def render(points: list[SweepPoint], output_path: Path = OUTPUT_PATH) -> Axes:
    """Render the conflict sensitivity plot and save it as a vector PDF."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not points:
        raise ValueError("at least one sweep point is required")

    styles = {
        "Dempster": {"color": "#0072B2", "linewidth": 2.0, "marker": "o", "markevery": 8},
        "Yager": {"color": "#E69F00", "linewidth": 2.0},
        "Dubois-Prade": {"color": "#009E73", "linewidth": 2.0},
        "PCR5": {"color": "#D55E00", "linewidth": 2.0},
        "Smets/TBM": {"color": "#332288", "linewidth": 1.8, "linestyle": "--"},
    }

    figure, axis = plt.subplots(figsize=(8.2, 4.8), constrained_layout=True)
    conflicts = [point.conflict for point in points]
    for name, style in styles.items():
        axis.plot(conflicts, [point.betp_a[name] for point in points], label=name, **style)

    article_point = evaluate(ARTICLE_T)
    axis.axhline(0.50, color="#666666", linewidth=1.2, linestyle=":", label="Decision threshold")
    axis.axvline(article_point.conflict, color="#000000", linewidth=1.2, linestyle="-.")
    axis.annotate(
        f"Article case  K = {article_point.conflict:.3f}",
        xy=(article_point.conflict, 0.985),
        xycoords=("data", "axes fraction"),
        xytext=(-6, -4),
        textcoords="offset points",
        ha="right",
        va="top",
        fontsize=9,
    )

    axis.set(
        xlabel="Conjunctive conflict  K",
        ylabel="Pignistic acceptance score  BetP(A)",
        title="Sensitivity of the acceptance score to source conflict",
    )
    axis.grid(True, color="#D9D9D9", linewidth=0.7, alpha=0.8)
    axis.legend(frameon=False, loc="center left", bbox_to_anchor=(1.01, 0.5))
    axis.set_xlim(left=0.0)
    axis.set_ylim(0.40, 0.58)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(figure)
    return axis


def print_selected_points(points: list[SweepPoint]) -> None:
    """Print reproducibility values for the sweep endpoints and article case."""

    selected = {0.10, ARTICLE_T, 0.80}
    for point in points:
        if round(point.t, 2) not in selected:
            continue
        scores = ", ".join(f"{name}={value:.6f}" for name, value in point.betp_a.items())
        print(f"t={point.t:.2f}, K={point.conflict:.6f}: {scores}")


def main() -> None:
    """Run the repository analysis and write its vector figure."""

    points = generate_sweep()
    render(points)
    print_selected_points(points)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
