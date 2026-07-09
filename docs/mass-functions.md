# Mass Functions

A mass function is a basic belief assignment over propositions in a frame.

```python
m = frame.mass({
    A: 0.4,
    B: 0.2,
    A | B: 0.4,
})
```

Mass values must be finite, non-negative, and sum to one. Tiny floating-point
drift near one is normalized; `NaN`, infinities, and real sum mismatches are
rejected.

> **Meaning:** mass on `A` is direct support for `A`. Mass on `A | B` is
> unresolved support for either `A` or `B`.

## Accepted keys

Keys may be `Proposition` objects, atom names, string expressions, or iterables
of atom names:

```python
frame.mass({"A": 0.4, "B": 0.2, "A | B": 0.4})
frame.mass({A: 0.4, B: 0.2, A | B: 0.4})
```

## Inspect values

```python
m.items()
m.focal()
m.to_dict()
m.total_mass
m.conflict
```

`items()` returns `(proposition, value)` pairs sorted by proposition label.
`focal()` returns only propositions with non-zero mass. `to_dict()` is useful
for display, logging, and simple serialization.

`m.conflict` is the mass assigned to the empty proposition. It is usually zero
for a valid source, but it can appear after unnormalized combination on a
constrained model.

DSm generalized bbas assume `m(empty) = 0`. `MassFunction` can also carry the
unnormalized conflict produced by `smets()`; methods that mathematically require
closed-world source bbas, such as PCR5/PCR6 and static Dubois-Prade, reject such
inputs explicitly.

Decision transforms such as `pignistic()` and `pignistic_regions()` ignore
empty-set conflict and rescale the remaining mass by default. Pass
`normalize_conflict=False` to inspect raw unnormalized TBM scores.

## Query support

```python
m.mass(A)
m.belief(A)
m.plausibility(A)
m.commonality(A)
```

- `mass(A)` returns the direct assigned mass.
- `belief(A)` sums non-empty masses of propositions contained in `A`. Excluding
  the universal empty set has no effect for a DSm gbba and keeps the usual TBM
  interpretation when a Smets result carries conflict.
- `plausibility(A)` sums masses of propositions intersecting `A`.
- `commonality(A)` sums masses of propositions that contain `A`.

For DST, `belief(A) <= plausibility(A)` gives the usual lower and upper support
interval for `A`.

## Dictionary output

Use `to_dict()` when you want compact string keys:

```python
combined = m1.pcr5(m2)
print(combined.to_dict())
```

By default, keys look like `"A|B"`. Pass `string_keys=False` if you need
`Proposition` keys.

For JSON, CSV, and LaTeX exports, see the import/export guide.
