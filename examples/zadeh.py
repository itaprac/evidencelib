"""Zadeh's high-conflict medical diagnosis example."""

from evidencelib import Frame


def print_mass(title, mass):
    print(title)
    for proposition, value in mass.items():
        print(f"  {proposition:7s} {value:.6f}")
    print()


frame = Frame.dst(["M", "C", "T"])
M, C, T = frame.symbols()

m1 = frame.mass({M: 0.9, T: 0.1})
m2 = frame.mass({C: 0.9, T: 0.1})

print_mass("Dempster", m1.dempster(m2))
print_mass("Yager", m1.yager(m2))
print_mass("DSmH static result", m1.dsmh(m2))
print_mass("Dubois-Prade static result", m1.dubois_prade(m2))
print_mass("PCR5", m1.pcr5(m2))
