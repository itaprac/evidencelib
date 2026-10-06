"""PCR6 versus PCR6+ when (nearly) vacuous sources join the fusion.

Uses Example 5 of Dezert, Dezert and Smarandache, "Improvement of Proportional
Conflict Redistribution Rules of Combination of Basic Belief Assignments",
J. Adv. Inf. Fusion 16(1), 2021.  Two informative sources are fused with an
increasing number of copies of the nearly vacuous source m3 (m3(Theta) = 0.99)
and of the vacuous source (m(Theta) = 1).  PCR6 moves more and more mass to
total ignorance; PCR6+ is unaffected by vacuous sources and barely affected by
nearly vacuous ones.
"""

from evidencelib import Frame

frame = Frame.dst(["A", "B", "C", "D", "E"])
A, B, C, D, E = frame.symbols()
theta = frame.total

m1 = frame.mass({A | B: 0.70, C | D: 0.06, A | B | C | D: 0.15, E: 0.09})
m2 = frame.mass({A | B: 0.06, C | D: 0.50, A | B | C | D: 0.04, E: 0.40})
near_vacuous = frame.mass({B: 0.01, theta: 0.99})
vacuous = frame.mass({theta: 1.0})


def row(label, mass):
    values = "  ".join(f"{mass[prop]:.6f}" for prop in (A | B, C | D, E, theta))
    print(f"{label:<26s}{values}")


print(f"{'sources':<26s}{'A|B':<10s}{'C|D':<10s}{'E':<10s}{'Theta':<10s}")
row("PCR6(m1, m2)", m1.pcr6(m2))
for extra in (1, 2, 3):
    added = [near_vacuous] * extra
    row(f"PCR6  + {extra} x near-vacuous", m1.pcr6(m2, *added))
    row(f"PCR6+ + {extra} x near-vacuous", m1.pcr6_plus(m2, *added))
for extra in (1, 3):
    added = [vacuous] * extra
    row(f"PCR6  + {extra} x vacuous", m1.pcr6(m2, *added))
    row(f"PCR6+ + {extra} x vacuous", m1.pcr6_plus(m2, *added))

print()
print("Conflicting products of PCR6+(m1, m2, m3) that involve Theta:")
for transfer in m1.conflict_redistribution(m2, near_vacuous, rule="pcr6+"):
    if theta in transfer.focal:
        focal = ", ".join(str(prop) for prop in transfer.focal)
        kept = ", ".join(sorted(str(prop) for prop in transfer.kept))
        print(f"  ({focal}): conflict {transfer.conflict:.6f} -> {kept}")
