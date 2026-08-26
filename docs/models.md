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
frame = Frame.hybrid(["E", "M", "H"], empty=["E&H"])
```

Hybrid DSmT adds explicit constraints. Some intersections can be impossible, or
new knowledge can make a hypothesis empty.

### 1. Define the constraints

Use `empty` for proposition expressions that are impossible. Use
`exclusive=True` when every pair of atoms is mutually exclusive, or pass atom
groups to `exclusive` when only selected intersections are impossible.

```python
Frame.hybrid(["A", "B"], exclusive=True)
Frame.hybrid(["A", "B", "C"], empty=["A & B"])
Frame.hybrid(["A", "B", "C"], exclusive=[("A", "B")])
```

The last two calls impose the same pairwise constraint. `empty` is more useful
for compound expressions, while `exclusive` is concise for atom groups.

> **Use hybrid DSmT when:** most hypotheses can overlap, but some combinations
> are impossible or have become impossible.

### 2. Inspect the constrained domain

Constraints are closed automatically. If `E&H` is empty, every Venn region
contained in that intersection is removed, including `E&M&H`.

```python
from evidencelib import Frame

frame = Frame.hybrid(["E", "M", "H"], empty=["E&H"])
E, M, H = frame.symbols()

assert not E & H
assert not E & M & H
assert frame.region_count == 5
assert len(frame.elements()) == 13
```

The user declares the physical constraint. The frame computes its closure, so
higher-order intersections do not need to be listed separately.

### 3. Assign masses and apply DSmH

Create static source assignments directly on the constrained frame when no
source assigns mass to an impossible proposition. Apply `dsmh()` to transfer
products whose intersection is forbidden to the corresponding disjunction.

```python
sensor = frame.mass({E: 0.6, E | M: 0.4})
expert = frame.mass({H: 0.5, M: 0.3, E | M | H: 0.2})

fused = sensor.dsmh(expert)
assert fused.total_mass == 1.0

print({name: round(value, 2) for name, value in fused.to_dict().items()})
# {'E': 0.12, 'E&M': 0.18, 'E|H': 0.3,
#  'E|M': 0.08, 'M': 0.12, 'M&H': 0.2}
```

Here, the product of the masses assigned to `E` and `H` cannot remain on
`E&H`. DSmH transfers it to `E|H`; the other products remain on propositions
permitted by the hybrid model.

### Static and dynamic constraints

For a static model, create sources directly on the constrained frame when they
assign no mass to impossible propositions. For constraints discovered after the
sources were elicited, keep the source masses on their original frame and pass
the target model explicitly:

```python
source = Frame.dsmt(["A", "B", "C"])
A, B, C = source.symbols()
m1 = source.mass({A & B: 1.0})
m2 = source.mass({A & B: 1.0})

target = Frame.hybrid(["A", "B", "C"], empty=["A&B"])
result = m1.dsmh(m2, model=target)
assert result.to_dict() == {"A|B": 1.0}
```

The original `A&B` expression is essential here: the `S2` term uses
`u(A&B) = A|B`. Creating the masses on `target` would discard that provenance.
Target projection may add constraints, but it cannot make Venn regions possible
that were absent from the source model; constraint relaxation requires a new
source model and re-elicited/reconstructed masses.

## Element growth

DSmT proposition spaces grow quickly:

- `Frame.dsmt(["A", "B"]).elements()` has 5 elements.
- `Frame.dsmt(["A", "B", "C"]).elements()` has 19 elements.
- `Frame.dsmt(["A", "B", "C", "D"]).elements()` has 167 elements.
- A five-atom free model already has 7,580 elements.

`Frame.elements()` has a safety limit. Pass `max_count=None` only when you
really want the full closure.
