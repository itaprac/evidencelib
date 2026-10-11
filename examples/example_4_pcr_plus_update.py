"""PCR5/PCR6 versus PCR5+/PCR6+ with three sources: the v1.3 update example.

Reproduces the illustrative example of the SoftwareX software-update article
for version 1.3.  Three synthetic sources on Theta = {A, B} are fused jointly;
the third one is nearly vacuous.  The script prints the fused masses, the
redistribution of the conflicting product (A, B, Theta), the fused masses
when the third source is replaced by the vacuous assignment, and the
decision scores after discounting the first source.
"""

from __future__ import annotations

from evidencelib import Frame, MassFunction

RULES = ("pcr5", "pcr6", "pcr5+", "pcr6+")
METHODS = {"pcr5": "pcr5", "pcr6": "pcr6", "pcr5+": "pcr5_plus", "pcr6+": "pcr6_plus"}

frame = Frame.dst(["A", "B"])
A, B = frame.symbols()
theta = frame.total

m1 = frame.mass({A: 0.70, B: 0.20, theta: 0.10})
m2 = frame.mass({A: 0.20, B: 0.60, theta: 0.20})
m3 = frame.mass({A: 0.05, theta: 0.95})
vacuous = frame.mass({theta: 1.0})


def fuse(rule: str, *others: MassFunction) -> MassFunction:
    return getattr(m1, METHODS[rule])(*others)


def row(label: str, values: tuple[float, ...]) -> str:
    return f"{label:<6s} " + " ".join(f"{value:.6f}" for value in values)


def main() -> None:
    print("Fused masses m(A) m(B) m(Theta):")
    for rule in RULES:
        result = fuse(rule, m2, m3)
        print(row(rule, tuple(result[p] for p in (A, B, theta))))

    print("Shares of the conflicting product (A, B, Theta) to A B Theta:")
    for rule in RULES:
        transfers = m1.conflict_redistribution(m2, m3, rule=rule)
        t = next(t for t in transfers if t.focal == (A, B, theta))
        print(row(rule, tuple(t.shares.get(p, 0.0) for p in (A, B, theta))))

    print("Third source replaced by the vacuous assignment, m(A) m(B) m(Theta):")
    for rule in RULES:
        result = fuse(rule, m2, vacuous)
        print(row(rule, tuple(result[p] for p in (A, B, theta))))

    print("Width of [Bel(A), Pl(A)]:")
    for rule in RULES:
        result = fuse(rule, m2, m3)
        print(row(rule, (result.plausibility(A) - result.belief(A),)))

    fused = m1.discount(0.8).pcr6_plus(m2, m3)
    print("First source discounted (0.8), PCR6+, m(A) m(B) m(Theta):")
    print(row("pcr6+", tuple(fused[p] for p in (A, B, theta))))
    print("Decision scores A B and decision:")
    for criterion in ("pignistic", "dsmp", "belief", "plausibility"):
        scores = fused.decision_scores(criterion)
        decision = fused.decision(criterion)
        print(f"{criterion:<12s} {scores['A']:.6f} {scores['B']:.6f} {decision}")


if __name__ == "__main__":
    main()
