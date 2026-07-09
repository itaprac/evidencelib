# Core Concepts

This page gives the minimum theory needed to read the rest of the docs.

## Frame

A `Frame` is the model of the world you are using.

```python
frame = Frame.dst(["A", "B", "C"])
```

The atoms `A`, `B`, and `C` are the elementary hypotheses. The frame decides
whether they are exclusive, overlapping, or constrained by custom rules.

> **Mental model:** create one frame for one problem, then build every
> proposition and mass function from that frame.

## Proposition

A proposition is an event over the frame.

```python
A | B
A & B
```

`|` means union. `&` means intersection.

In DST, `A & B` is empty when `A` and `B` are mutually exclusive. In free DSmT,
`A & B` can be non-empty and can receive mass.

## Mass function

A mass function is a basic belief assignment.

```python
m = frame.mass({A: 0.4, B: 0.2, A | B: 0.4})
```

Mass can be assigned to a precise hypothesis (`A`) or to uncertainty (`A | B`).
Mass values must be non-negative and sum to one.

> **Important:** mass on `A | B` is not split automatically between `A` and
> `B`. It stays on the uncertainty until you apply a measure or transform.

## Belief and plausibility

```python
m.belief(A)
m.plausibility(A)
```

Belief is confirmed support. Plausibility is possible support. In DST, together
they form a support interval for a hypothesis.

## Fusion

Fusion combines independent sources on the same frame.

```python
combined = m1.dempster(m2)
```

Different rules handle conflict differently. Use the fusion guide when choosing
between Dempster, Yager, DSmH, PCR5, and PCR6. If the model changes after source
elicitation, keep the sources on their original frame and pass the new target
frame explicitly to `dsmh(..., model=target)`.

## Decision scores

```python
m.pignistic()
m.pignistic_of(A & B)
m.decision()
```

`pignistic()` turns belief masses into singleton scores. `pignistic_of(A)`
implements generalized BetP for any proposition. `decision()` returns the
singleton with the largest score.

> **Keep application logic separate:** `decision()` is a convenience helper.
> Real systems may still need utility, risk, thresholds, or domain-specific
> costs.
