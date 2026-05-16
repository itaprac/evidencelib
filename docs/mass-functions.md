# Mass Functions

A mass function is a basic belief assignment over propositions in a frame.

```python
m = frame.mass({
    A: 0.4,
    B: 0.2,
    A | B: 0.4,
})
```

Mass values must be non-negative and sum to one by default.

## Inspecting masses

```python
m.items()
m.focal()
m.to_dict()
m.total_mass
m.conflict
```

`m.conflict` is the mass assigned to the empty proposition. It is usually zero
for a valid source, but it can appear after unnormalized combination on a
constrained model.

## Belief measures

```python
m.mass(A)
m.belief(A)
m.plausibility(A)
m.commonality(A)
```

- `mass(A)` returns the direct assigned mass.
- `belief(A)` sums masses of propositions contained in `A`.
- `plausibility(A)` sums masses of propositions intersecting `A`.
- `commonality(A)` sums masses of propositions that contain `A`.

