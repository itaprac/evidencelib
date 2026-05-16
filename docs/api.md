# API

## Frame

```python
Frame.dst(atoms)
Frame.dsmt(atoms)
Frame.hybrid(atoms, empty=(), exclusive=False)
```

Useful methods:

```python
frame.symbols()
frame.symbols("A B")
frame.atom("A")
frame.proposition("A & (B | C)")
frame.mass({ ... })
frame.elements()
frame.region_count
```

## Proposition

Propositions are immutable and hashable.

```python
A | B
A & B
str(A | B)
(A & B).is_empty
(A | B).cardinality
(A & B).union_atoms()
```

`|` means union/disjunction. `&` means intersection/conjunction.

## MassFunction

Create:

```python
m = frame.mass({A: 0.4, B: 0.2, A | B: 0.4})
```

Inspect:

```python
m.items()
m.focal()
m.to_dict()
m.total_mass
m.conflict
```

Measures:

```python
m.mass(A)
m.belief(A)
m.plausibility(A)
m.commonality(A)
```

Fusion:

```python
m1.conjunctive(m2)
m1.dsmc(m2)
m1.smets(m2)
m1.dempster(m2)
m1.yager(m2)
m1.dubois_prade(m2)
m1.dsmh(m2)
m1.pcr5(m2)
m1.pcr6(m2, m3)
```

Decision support:

```python
m.pignistic()
m.pignistic_regions()
m.decision()
```

## Errors

- `InvalidMassError`: mass values are negative or do not sum to one.
- `TotalConflictError`: Dempster normalization is undefined because conflict is one.
- `ValueError`: propositions belong to different frames or expression parsing fails.

