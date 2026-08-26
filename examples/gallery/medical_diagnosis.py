"""MYCIN-style medical expert system example on a classical DST frame.

Three candidate conditions: bacterial infection (B), viral infection (V), and
an allergic reaction (L). Two evidence sources emulate expert rules: a symptom
screening that mostly separates infections from allergy, and a laboratory test
that points to a bacterial cause. All masses are synthetic and illustrative;
this is not a validated clinical model.
"""

from __future__ import annotations

from evidencelib import Frame


def main() -> None:
    frame = Frame.dst(["B", "V", "L"])
    bacterial, viral, allergic = frame.symbols()
    infection = bacterial | viral

    symptoms = frame.mass(
        {
            infection: 0.60,
            allergic: 0.25,
            frame.total: 0.15,
        }
    )
    laboratory = frame.mass(
        {
            bacterial: 0.55,
            infection: 0.25,
            frame.total: 0.20,
        }
    )

    fused = symptoms.dempster(laboratory)
    print("Fused masses:")
    for proposition, value in sorted(fused.items(), key=lambda item: -item[1]):
        print(f"  {str(proposition):5s} {value:.4f}")

    print("Belief / plausibility intervals:")
    for name, proposition in (("B", bacterial), ("V", viral), ("L", allergic)):
        print(
            f"  {name}: [{fused.belief(proposition):.4f}, "
            f"{fused.plausibility(proposition):.4f}]"
        )

    scores = fused.pignistic()
    print(f"Pignistic scores: { {k: round(v, 4) for k, v in scores.items()} }")
    print(f"Suggested working diagnosis: {fused.decision()}")


if __name__ == "__main__":
    main()
