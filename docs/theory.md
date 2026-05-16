# Theory Notes

This page maps the main DST and DSmT concepts to `evidencelib` objects.

## DST

Dempster-Shafer theory works on a frame of discernment `Theta` whose hypotheses
are exhaustive and mutually exclusive. In `evidencelib` this is:

```python
frame = Frame.dst(["A", "B", "C"])
```

The generated proposition space is the power set `2^Theta`. Intersections such
as `A & B` collapse to `empty`.

## DSmT

The free DSm model keeps hypotheses exhaustive but does not require them to be
exclusive:

```python
frame = Frame.dsmt(["A", "B", "C"])
```

The generated proposition space is the hyper-power set: expressions built from
atoms using union and intersection. For small frames:

- `|Theta| = 2` gives 5 elements,
- `|Theta| = 3` gives 19 elements,
- `|Theta| = 4` gives 167 elements.

`Frame.elements()` has a safety limit because these spaces grow quickly.

## Hybrid Models

A hybrid DSm model adds explicit constraints:

```python
frame = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])
```

This can represent static exclusivity constraints and dynamic situations where
new knowledge makes a hypothesis or intersection empty.

## Pignistic Output

In DST, singleton hypotheses are disjoint, so pignistic singleton probabilities
sum to one.

In free DSmT, singleton hypotheses can overlap. `pignistic()` returns singleton
event scores for decisions, while `pignistic_regions()` returns a distribution
over disjoint Venn regions.
