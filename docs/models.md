# Models

`evidencelib` keeps the model explicit. The same expression can mean different
things depending on the frame.

## DST

```python
frame = Frame.dst(["A", "B", "C"])
```

DST uses exhaustive and mutually exclusive hypotheses. `A & B` is therefore
`empty`, and `frame.elements()` generates the classical power set.

> **Use DST when:** exactly one hypothesis can be true, for example one label
> selected from a known set of classes.

Common workflows use `dempster()`, `yager()`, `pcr5()`, `pcr6()`, and
`pignistic()`.

## Free DSmT

```python
frame = Frame.dsmt(["A", "B", "C"])
```

Free DSmT keeps hypotheses exhaustive but allows overlap. `A & B` can be a real
state, and `frame.elements()` generates the hyper-power set.

> **Use free DSmT when:** categories are vague, overlapping, or not safely
> separable.

In this model, `A`, `B`, and `A & B` can all carry distinct mass. `dsmc()` keeps
mass on intersections instead of treating them as conflict.

## Hybrid DSmT

```python
frame = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])
```

Hybrid DSmT adds explicit constraints. Some intersections can be impossible, or
new knowledge can make a hypothesis empty.

Examples:

```python
Frame.hybrid(["A", "B"], exclusive=True)
Frame.hybrid(["A", "B", "C"], empty=["A & B"])
Frame.hybrid(["A", "B", "C"], exclusive=[("A", "B")])
```

> **Use hybrid DSmT when:** most hypotheses can overlap, but some combinations
> are impossible or have become impossible.

Use `dsmh()` when conflict should be redistributed according to model
constraints instead of normalized away.

## Element growth

DSmT proposition spaces grow quickly:

- `Frame.dsmt(["A", "B"]).elements()` has 5 elements.
- `Frame.dsmt(["A", "B", "C"]).elements()` has 19 elements.
- `Frame.dsmt(["A", "B", "C", "D"]).elements()` has 167 elements.

`Frame.elements()` has a safety limit. Pass `max_count=None` only when you
really want the full closure.
