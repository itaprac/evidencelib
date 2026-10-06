# Discounting, Distance, and Probabilistic Transforms

## Reliability discounting

```python
weaker = m.discount(0.8)
```

Shafer's discounting with reliability factor `a` in [0, 1] multiplies every
mass by `a` and gives the remainder `1 - a` to total ignorance `Theta`
(Shafer, 1976, p. 252; Smarandache, Dezert and Tacnet, 2010, eq. 4). `a = 1`
keeps the source, `a = 0` makes it vacuous. On hybrid frames `Theta` is the
union of all hypotheses that the model allows.

Discount unreliable sources before fusion:

```python
frame = Frame.dst(["A", "B"])
A, B = frame.symbols()
m1 = frame.mass({A: 0.8, B: 0.2}).discount(0.2)
m2 = frame.mass({A: 0.4, B: 0.6}).discount(0.8)
m1.pcr5(m2).to_dict()   # approx. {'A': 0.3698, 'A|B': 0.16, 'B': 0.4702}
```

## Jousselme distance

```python
d = m1.jousselme_distance(m2)
```

`d = sqrt(0.5 (m1 - m2)^T D (m1 - m2))` with `D(A, B) = |A & B| / |A | B|`
(Jousselme, Grenier and Bosse, 2001). The distance lies in [0, 1] and is 0 only
for identical assignments. On free and hybrid DSm frames, `|.|` is the DSm
cardinality, as for the uncertainty measures. Both assignments need
`m(empty) = 0`. The distance measures dissimilarity, which is not the same as
conjunctive conflict `m(empty)`: two identical but imprecise sources have
distance 0 and may still conflict.

## DSmP

```python
m.dsmp(epsilon=0.001)          # singleton scores
m.dsmp_of(A & B, epsilon=0.001)
m.dsmp_regions(epsilon=0.001)  # probability over disjoint Venn regions
```

DSmP (Dezert and Smarandache, 2008, eq. 11) splits the mass of each
proposition over its parts in proportion to the masses of the
DSm-cardinality-one elements it contains, plus `epsilon` times their DSm
cardinality. Small `epsilon` gives the most specific probability (highest
probabilistic information content); `epsilon = 0` is undefined when a focal
proposition contains no such mass and then raises `ValueError`. With
`epsilon = 1` and no mass on cardinality-one elements, DSmP equals the
pignistic transformation. DSmP works on Shafer's, free, and hybrid models.

## Decision criteria

```python
m.decision()                       # BetP, as before
m.decision("dsmp", epsilon=0.001)
m.decision("belief")               # maximum of credibility
m.decision("plausibility")         # maximum of plausibility
m.decisions("pignistic")           # all maximizers, to see ties
m.decision_scores("belief")        # the scores themselves
```

`decision()` returns one singleton and resolves exact ties by frame order.
`decisions()` returns every singleton whose score is within `1e-12` of the
maximum.
