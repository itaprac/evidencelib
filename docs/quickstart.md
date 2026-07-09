# Quickstart

Install the package:

```bash
pip install evidencelib
```

`evidencelib` has no runtime dependencies. Plotting is optional:

```bash
pip install "evidencelib[plot]"
```

## 1. Create a frame

A frame lists the hypotheses you want to reason about.

```python
from evidencelib import Frame

frame = Frame.dst(["Alive", "Dead"])
Alive, Dead = frame.symbols()
```

> **DST in one line:** hypotheses are exhaustive and mutually exclusive, so
> `Alive & Dead` is `empty`.

## 2. Assign evidence

A mass function assigns support to precise hypotheses and to uncertainty.

```python
m = frame.mass({
    Alive: 0.2,
    Dead: 0.5,
    Alive | Dead: 0.3,
})
```

`Alive | Dead` means "one of these, but I cannot say which one".

## 3. Query belief measures

```python
print(m.belief(Alive))        # 0.2
print(m.plausibility(Alive))  # 0.5
print(m.pignistic())          # {'Alive': 0.35, 'Dead': 0.65}
print(m.decision())           # Dead
```

> **Read the interval:** belief is confirmed support. Plausibility is support
> that has not been ruled out.

## 4. Combine sources

Each source is a `MassFunction` on the same frame.

```python
frame = Frame.dst(["A", "B"])
A, B = frame.symbols()

m1 = frame.mass({A: 0.6, A | B: 0.4})
m2 = frame.mass({B: 0.3, A | B: 0.7})

print(m1.dempster(m2).to_dict())
print(m1.pcr5(m2).to_dict())
```

> **Rule of thumb:** start with `dempster()` for classical DST examples,
> `yager()` when conflict should become uncertainty, and `pcr5()` or `pcr6()`
> when high conflict should be redistributed only to involved hypotheses.

## 5. Use DSmT when hypotheses can overlap

```python
frame = Frame.dsmt(["A", "B"])
A, B = frame.symbols()

m = frame.mass({
    A: 0.2,
    B: 0.3,
    A & B: 0.4,
    A | B: 0.1,
})

print(m.pignistic())          # singleton event scores
print(m.pignistic_of(A & B))  # generalized score for any proposition
print(m.pignistic_regions())  # probabilities over disjoint Venn regions
```

> **DSmT in one line:** `A & B` may be a real state, not a contradiction.

## 6. Apply constraints learned later

Dynamic DSmH keeps source masses on their original frame and receives the new
model explicitly:

```python
source = Frame.dst(["A", "B", "C"])
A, B, C = source.symbols()
m1 = source.mass({A: 0.1, B: 0.4, C: 0.2, A | B: 0.3})
m2 = source.mass({A: 0.5, B: 0.1, C: 0.3, A | B: 0.1})

target = Frame.hybrid(["A", "B", "C"], exclusive=True, empty=["C"])
result = m1.dsmh(m2, model=target)
```

This ordering preserves the original focal proposition `C` until the full DSmH
`S1 + S2 + S3` transfer applies the new constraint.
