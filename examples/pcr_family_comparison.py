"""Compare the whole PCR family with classical rules on literature examples.

Examples 12.1 (Bayesian sources) and 12.3 (Zadeh) of Smarandache and Dezert,
"Proportional Conflict Redistribution Rules for Information Fusion" (2004),
followed by a three-source case with a vacuous source, where the rules differ
in whether the ignorant source changes the result.
"""

from evidencelib import Frame

frame = Frame.dst(["A", "B", "C"])
A, B, C = frame.symbols()
RULES = ("dempster", "pcr1", "pcr2", "pcr3", "pcr4", "pcr5", "pcr6", "pcr5_plus", "pcr6_plus")


def table(title, sources, columns):
    print(title)
    print(f"  {'rule':<10s}" + "".join(f"{str(prop):>10s}" for prop in columns))
    for rule in RULES:
        result = getattr(sources[0], rule)(*sources[1:])
        print(f"  {rule:<10s}" + "".join(f"{result[prop]:>10.6f}" for prop in columns))
    print()


table(
    "Example 12.1: Bayesian sources",
    [frame.mass({A: 0.6, B: 0.3, C: 0.1}), frame.mass({A: 0.4, B: 0.4, C: 0.2})],
    (A, B, C),
)
table(
    "Example 12.3: Zadeh's example",
    [frame.mass({A: 0.9, C: 0.1}), frame.mass({B: 0.9, C: 0.1})],
    (A, B, C),
)
table(
    "Three sources, the third one vacuous",
    [
        frame.mass({A: 0.6, B: 0.3, A | B: 0.1}),
        frame.mass({A: 0.2, B: 0.3, A | B: 0.5}),
        frame.mass({frame.total: 1.0}),
    ],
    (A, B, A | B, frame.total),
)
