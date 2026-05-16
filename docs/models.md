# Models

`evidencelib` keeps the model explicit. This matters because DST and DSmT use the
same-looking propositions with different assumptions about intersections.

## DST / Shafer model

```python
frame = Frame.dst(["A", "B", "C"])
```

In this model, hypotheses are exhaustive and mutually exclusive. Therefore
`A & B` is the empty proposition, and `frame.elements()` generates the classical
power set.

Use this when the hypotheses are known to be exclusive alternatives, such as
one true class among several labels.

Typical DST workflows use `dempster()`, `yager()`, `pcr5()`, or pignistic
probabilities over singleton hypotheses.

## Free DSm model

```python
frame = Frame.dsmt(["A", "B", "C"])
```

In the free DSm model, hypotheses are exhaustive but may overlap. Intersections
such as `A & B` can be non-empty. `frame.elements()` generates the hyper-power
set.

Use this when the hypotheses are vague, overlapping, or not safely separable.

In this model, `A`, `B`, and `A & B` can all carry distinct mass. The
conjunctive rule `dsmc()` keeps mass on intersections instead of treating them
as conflict.

## Hybrid DSm model

```python
frame = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])
```

Hybrid models add explicit constraints. They are useful when some intersections
are impossible or when new knowledge makes a hypothesis empty.

Examples:

```python
Frame.hybrid(["A", "B"], exclusive=True)
Frame.hybrid(["A", "B", "C"], empty=["A & B"])
Frame.hybrid(["A", "B", "C"], exclusive=[("A", "B")])
```

The `exclusive=True` shortcut constrains every pairwise intersection to be
empty, matching Shafer-style exclusivity.

Use `dsmh()` when conflict should be redistributed according to these model
constraints instead of normalized away.
