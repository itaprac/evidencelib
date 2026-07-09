"""Hybrid DSmT example where one hypothesis is later found empty."""

from evidencelib import Frame


def print_mass(title, mass):
    print(title)
    for proposition, value in mass.items():
        print(f"  {proposition:11s} {value:.6f}")
    print()


free_frame = Frame.dsmt(["t1", "t2", "t3"])
t1, t2, t3 = free_frame.symbols()

m1 = free_frame.mass({t1: 0.1, t2: 0.4, t3: 0.2, t1 | t2: 0.3})
m2 = free_frame.mass({t1: 0.5, t2: 0.1, t3: 0.3, t1 | t2: 0.1})
print_mass("Free DSm model / DSmC", m1.dsmc(m2))

hybrid_frame = Frame.hybrid(["t1", "t2", "t3"], exclusive=True, empty=["t3"])
print_mass(
    "Hybrid model / DSmH after t3 becomes empty",
    m1.dsmh(m2, model=hybrid_frame),
)
