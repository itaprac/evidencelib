"""Compare DST/PCR rules on a two-hypothesis literature example."""

from evidencelib import Frame


def print_mass(title, mass):
    print(title)
    for proposition, value in mass.items():
        print(f"  {proposition:5s} {value:.6f}")
    print()


frame = Frame.dst(["A", "B"])
A, B = frame.symbols()

m1 = frame.mass({A: 0.6, A | B: 0.4})
m2 = frame.mass({B: 0.3, A | B: 0.7})

print_mass("Dempster", m1.dempster(m2))
print_mass("Smets/TBM", m1.smets(m2))
print_mass("Yager", m1.yager(m2))
print_mass("DSmH/Dubois-Prade", m1.dsmh(m2))
print_mass("PCR5", m1.pcr5(m2))

