# Decision Support

`evidencelib` includes pignistic transforms for decision support.

```python
m.pignistic()
m.pignistic_of(A)
m.pignistic_regions()
m.decision()
```

`decision()` returns the singleton with the largest value from `pignistic()`.
It is a convenience method, not a replacement for application-specific utility,
risk, or loss functions.

When a mass function contains empty-set conflict, for example after
`conjunctive()` / `smets()`, `pignistic()` excludes the empty proposition and
rescales the remaining scores by `1 - m(empty)` by default. Pass
`normalize_conflict=False` if you need raw unnormalized TBM scores instead.

## DST

In DST, singleton hypotheses are disjoint. `pignistic()` returns a probability
distribution over singletons.

```python
frame = Frame.dst(["A", "B"])
A, B = frame.symbols()
m = frame.mass({A: 0.4, B: 0.2, A | B: 0.4})

assert sum(m.pignistic().values()) == 1.0
```

> **Use this output when:** a downstream system expects one probability per
> exclusive hypothesis.

## DSmT

In free or hybrid DSmT, singleton hypotheses can overlap. `pignistic()` returns
singleton event scores useful for ranking, but the scores do not have to sum to
one.

Use `pignistic_regions()` if you need a probability distribution over disjoint
Venn regions.

```python
frame = Frame.dsmt(["A", "B"])
A, B = frame.symbols()
m = frame.mass({A: 0.2, B: 0.3, A & B: 0.4, A | B: 0.1})

scores = m.pignistic()
intersection_score = m.pignistic_of(A & B)
regions = m.pignistic_regions()
```

`pignistic_of(A)` implements the generalized pignistic transformation for any
proposition using the DSm-cardinality ratio `C_M(X & A) / C_M(X)`. The singleton
dictionary returned by `pignistic()` is a convenience view built from the same
calculation.

`pignistic_regions()` uses the same conflict normalization behavior as
`pignistic()`.

`regions` is useful when the downstream calculation requires mutually exclusive
states.

> **Use this output when:** you need probabilities over disjoint states rather
> than scores for overlapping events.
