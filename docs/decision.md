# Decision Support

`evidencelib` includes pignistic transforms for decision support.

```python
m.pignistic()
m.pignistic_regions()
m.decision()
```

`decision()` returns the singleton with the largest value from `pignistic()`.
It is a convenience method, not a replacement for application-specific utility,
risk, or loss functions.

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
regions = m.pignistic_regions()
```

`regions` is useful when the downstream calculation requires mutually exclusive
states.

> **Use this output when:** you need probabilities over disjoint states rather
> than scores for overlapping events.
