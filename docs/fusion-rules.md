# Fusion Rules

All fusion methods are methods on `MassFunction`.

```python
combined = m1.dempster(m2)
```

All sources must belong to the same frame.

Every rule returns a new `MassFunction`; input sources are not modified.

## Conjunctive / DSmC / Smets

```python
m1.conjunctive(m2)
m1.dsmc(m2)
m1.smets(m2)
```

The unnormalized conjunctive rule intersects propositions and multiplies their
masses. On a free DSmT frame this is the classic DSm rule, DSmC. On a DST frame,
conflicting intersections accumulate on `empty`.

`smets()` is an alias for the same unnormalized behavior in the transferable
belief model sense.

Use this rule when you want to inspect conflict explicitly instead of
redistributing or normalizing it immediately.

## Dempster

```python
m1.dempster(m2)
```

Dempster's rule removes empty-set conflict and normalizes the remaining masses.
If conflict is total, `TotalConflictError` is raised.

This rule is appropriate when the frame is exclusive and normalized conflict
handling is acceptable for the application.

## Yager

```python
m1.yager(m2)
```

Yager's rule transfers total conflict to total ignorance.

This keeps the result normalized while representing conflict as uncertainty
instead of assigning it to specific hypotheses.

## DSmH / Dubois-Prade-style transfer

```python
m1.dsmh(m2)
m1.dubois_prade(m2)
```

`dsmh()` transfers empty intersections to the union of the propositions involved
in the conflict. If that union is empty under the model, the mass goes to total
ignorance.

For static Shafer-style problems, this is the same transfer pattern normally
associated with Dubois-Prade. Dynamic DSmH cases can differ, especially when a
hypothesis becomes empty after evidence was assigned to it.

Use DSmH with `Frame.hybrid(...)` when constraints are part of the model.

## PCR5 and PCR6

```python
m1.pcr5(m2)
m1.pcr6(m2, m3)
```

PCR rules redistribute partial conflict only to the propositions involved in
that conflict, proportionally to the masses that created it.

`pcr5()` accepts two sources. `pcr6()` supports two or more sources.

PCR rules are useful in high-conflict cases where assigning conflict to total
ignorance would be too coarse.
