"""Hybrid DSm extension of the pump diagnosis example (paper Section 3.2).

Same frame {E, M, H}, same three sources and masses as the free-DSm example.
Only the model changes: the constraint E & H = empty (a purely electrical and
a purely hydraulic fault do not co-occur in the considered mode) turns the
free DSm model into a hybrid one, and fusion uses DSmH instead of DSmC.
Every number quoted in the manuscript extension must come from this script.
"""

from pathlib import Path

from evidencelib import Frame

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def print_mass(title, mass, *, limit=None):
    print(title)
    items = sorted(mass.items(), key=lambda item: -item[1])
    if limit is not None:
        items = items[:limit]
    for proposition, value in items:
        print(f"  {str(proposition):13s} {value:.4f}")
    print(f"  {'total':13s} {mass.total_mass:.4f}")
    print()


def make_sources(frame):
    e, m, h = frame.symbols()
    current = frame.mass({e: 0.65, e | m: 0.20, e | m | h: 0.15})
    vibration = frame.mass({m: 0.60, e | m: 0.25, e | m | h: 0.15})
    pressure = frame.mass({h: 0.25, e | h: 0.15, m | h: 0.10, e | m | h: 0.50})
    return current, vibration, pressure


free_frame = Frame.dsmt(["E", "M", "H"])
current, vibration, pressure = make_sources(free_frame)

print(f"Free DSm domain size: {len(free_frame.elements())}")
free_result = current.dsmc(vibration, pressure)
print_mass("Free DSm model / DSmC (paper baseline)", free_result, limit=8)

hybrid_frame = Frame.hybrid(["E", "M", "H"], empty=["E&H"])
print(f"Hybrid domain size (E&H = empty): {len(hybrid_frame.elements())}")
e, m, h = free_frame.symbols()
print(f"Forbidden E&H mass under free DSmC: {free_result[e & h]:.4f}")
print(f"E&M&H under free DSmC: {free_result[e & m & h]:.4f}")
print()

hybrid_result = current.dsmh(vibration, pressure, model=hybrid_frame)
print_mass("Hybrid DSm model / DSmH", hybrid_result)

print("Generalized pignistic probabilities of the disjoint regions:")
for name, value in sorted(
    hybrid_result.pignistic_regions().items(), key=lambda item: -item[1]
):
    print(f"  {name:13s} {value:.4f}")
print()

print("LaTeX table (hybrid DSmH result):")
print(hybrid_result.to_latex(caption="Fused masses under the hybrid DSm model (DSmH).",
                             label="tab:dsmt-hybrid-masses"))

try:
    OUTPUT_DIR.mkdir(exist_ok=True)
    ax = hybrid_result.plot_venn(show_region_labels=True)
    figure_path = OUTPUT_DIR / "fig5_hybrid.pdf"
    ax.figure.savefig(figure_path, format="pdf", bbox_inches="tight")
    print(f"Venn figure saved to {figure_path}")
except ModuleNotFoundError:
    print("Matplotlib not installed; skipping the Venn figure.")

print("Deng entropy (uncertainty of the fused assignments):")
print(f"  free DSmC result:    {free_result.deng_entropy():.4f}")
print(f"  hybrid DSmH result:  {hybrid_result.deng_entropy():.4f}")
