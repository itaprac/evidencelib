# pybelief

`pybelief` is a small computational library for belief functions in
Dempster-Shafer theory (DST) and Dezert-Smarandache theory (DSmT).

It is designed as a practical quantitative core: finite frames, symbolic
propositions, mass functions, standard fusion rules, pignistic transforms, and
literature-backed examples.

## Install

```bash
pip install pybelief
```

For local development:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Full documentation can be built locally with:

```bash
pip install -e ".[dev,docs]"
python -m sphinx -W -b html docs docs/_build/html
```

## Quick Start

```python
from pybelief import Frame

frame = Frame.dst(["Alive", "Dead"])
Alive, Dead = frame.symbols()

m = frame.mass({
    Alive: 0.2,
    Dead: 0.5,
    Alive | Dead: 0.3,
})

print(m.belief(Alive))       # 0.2
print(m.plausibility(Alive)) # 0.5
print(m.pignistic())         # {"Alive": 0.35, "Dead": 0.65}
```

## Models

```python
dst = Frame.dst(["A", "B", "C"])
dsmt = Frame.dsmt(["A", "B", "C"])
hybrid = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])
```

- `Frame.dst(...)` creates Shafer's classical DST model with exhaustive and
  mutually exclusive hypotheses.
- `Frame.dsmt(...)` creates the free DSm model, where hypotheses can overlap.
- `Frame.hybrid(...)` creates a constrained DSm model with explicit emptiness
  or exclusivity constraints.

## Propositions

Use Python's symbolic operators:

```python
A, B, C = frame.symbols()

A | B       # union / disjunction, A ∪ B
A & B       # intersection / conjunction, A ∩ B
(A | B) & C # parentheses are recommended for compound expressions
```

String expressions are supported too:

```python
frame.proposition("A | B")
frame.proposition("A ∩ (B ∪ C)")
```

## Fusion Rules

```python
m1.conjunctive(m2)   # unnormalized conjunctive rule
m1.dsmc(m2)          # classic DSm rule on a free DSm frame
m1.smets(m2)         # TBM/Smets rule, conflict remains on empty
m1.dempster(m2)      # normalized Dempster rule
m1.yager(m2)         # Yager rule
m1.dsmh(m2)          # hybrid DSm rule
m1.dubois_prade(m2)  # static Dubois-Prade-style transfer
m1.pcr5(m2)          # PCR5 for two sources
m1.pcr6(m2, m3)      # PCR6 for two or more sources
```

## Measures

```python
m.mass(A)
m.belief(A)
m.plausibility(A)
m.commonality(A)
m.conflict
m.pignistic()
m.pignistic_regions()
m.decision()
```

For DST, `pignistic()` returns a probability distribution over singleton
hypotheses. In free or hybrid DSmT, singleton hypotheses may overlap, so
`pignistic()` returns decision scores that do not necessarily sum to one. Use
`pignistic_regions()` when you need a distribution over disjoint Venn regions.

## Literature Checks

The test suite includes numerical checks from:

- the common Dempster-Shafer alive/dead example,
- DSmC and DSmH examples from Dezert-Smarandache introductory material,
- PCR5 examples,
- Zadeh's high-conflict example.

Run:

```bash
python -m pytest -q
```

Or inspect examples:

```bash
python examples/rules_dst.py
python examples/zadeh.py
python examples/hybrid_dsmt.py
```

## Scope of v1

`pybelief` v1 covers precise quantitative belief masses on finite frames.

Not included in v1:

- imprecise interval-valued belief masses,
- qualitative label algebra,
- continuous frames,
- automatic model learning from data.
