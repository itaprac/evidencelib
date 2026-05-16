# Decision Support

`pybelief` includes simple pignistic transforms for decision support.

```python
m.pignistic()
m.pignistic_regions()
m.decision()
```

`decision()` returns the singleton with the largest value from `pignistic()`.
It is a convenience method, not a replacement for application-specific utility
or loss functions.

## DST

In a DST frame, singleton hypotheses are disjoint. Therefore `pignistic()`
returns a probability distribution over the singleton hypotheses.

```python
frame = Frame.dst(["A", "B"])
A, B = frame.symbols()
m = frame.mass({A: 0.4, B: 0.2, A | B: 0.4})

assert sum(m.pignistic().values()) == 1.0
```

## DSmT

In a free or hybrid DSmT frame, singleton hypotheses can overlap. Therefore
`pignistic()` returns singleton event scores useful for ranking decisions, but
the scores do not have to sum to one.

Use `pignistic_regions()` if you need a probability distribution over disjoint
Venn regions.

```python
frame = Frame.dsmt(["A", "B"])
A, B = frame.symbols()
m = frame.mass({A: 0.2, B: 0.3, A & B: 0.4, A | B: 0.1})

scores = m.pignistic()
regions = m.pignistic_regions()
```

`regions` is useful when the downstream calculation requires mutually exclusive
states.
