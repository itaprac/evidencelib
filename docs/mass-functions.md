# Mass Functions

A mass function is a basic belief assignment over propositions in a frame.

```python
m = frame.mass({
    A: 0.4,
    B: 0.2,
    A | B: 0.4,
})
```

Mass values must be non-negative and sum to one by default. Tiny floating-point
drift near one is normalized, while real sum mismatches are still rejected.

Keys may be `Proposition` objects, atom names, string expressions, or iterables
of atom names:

```python
frame.mass({"A": 0.4, "B": 0.2, "A | B": 0.4})
frame.mass({A: 0.4, B: 0.2, A | B: 0.4})
```

## Inspecting masses

```python
m.items()
m.focal()
m.to_dict()
m.total_mass
m.conflict
```

`items()` returns `(proposition, value)` pairs sorted by proposition label.
`focal()` returns only propositions with non-zero mass. `to_dict()` is useful
for display, serialization, and examples.

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

For DST, `belief(A) <= plausibility(A)` gives the usual lower and upper support
interval for `A`.
