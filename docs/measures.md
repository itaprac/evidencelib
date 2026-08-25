# Uncertainty Measures

`evidencelib` quantifies the uncertainty and information content of a mass
function with a family of entropy-style measures.

```python
m.deng_entropy()
m.tfb_entropy(order=2)
m.fractal_belief_entropy()
m.information_volume()
m.nonspecificity()
m.strife()
```

| Measure | Meaning | Reference |
|---|---|---|
| `deng_entropy()` | Total uncertainty; Shannon entropy for Bayesian masses | Deng, *Chaos, Solitons & Fractals* 91 (2016) |
| `tfb_entropy(order=k)` | k-order time fractal-based entropy; `order=1` is Deng entropy | Zhou & Deng, *Information Sciences* 586 (2022) |
| `fractal_belief_entropy()` | Shannon entropy of the fractal spread of masses over sub-propositions | Zhou & Deng, arXiv:2012.00235 |
| `information_volume()` | Limit of Deng entropy under iterative maximum-entropy splitting | Deng, *IJCCC* 15(6) (2020) |
| `nonspecificity()` | Generalized Hartley measure of imprecision | Klir & Wierman (1999) |
| `strife()` | Conflict-based part of total uncertainty | Klir & Wierman (1999) |

All measures require `m(empty) = 0`; normalize a TBM-style result first.

## Example

```python
from evidencelib import Frame

frame = Frame.dst(["a", "b", "c"])
a, b, c = frame.symbols()
m = frame.mass({a: 0.5, b: 0.2, a | b | c: 0.3})

m.deng_entropy()          # 2.328...
m.nonspecificity()        # 0.475...
m.information_volume()    # 3.425... (>= Deng entropy)
```

## DSm cardinality on DSmT frames

On free and hybrid DSm frames the measures replace the set cardinality `|A|`
with the **DSm cardinality**: the number of Venn regions the proposition
covers. On DST frames both cardinalities coincide, so the classical formulas
are recovered.

```python
free = Frame.dsmt(["p", "q"])
p, q = free.symbols()

free.mass({p & q: 1.0}).deng_entropy()   # 0.0  (single Venn region)
free.mass({p: 1.0}).deng_entropy()       # 1.585 (p covers two regions)
```

The k-order maximum of `tfb_entropy` on a DST frame with `n` hypotheses is the
higher order information volume of a mass function (HOIVMF),
`log2((k+2)**n - (k+1)**n)`.

## Notes

- `information_volume(epsilon=1e-3, max_iterations=1000)` matches the
  convergence threshold used in the defining paper.
- `fractal_belief_entropy()` enumerates the `2**c - 1` sub-propositions of
  each focal element; keep focal cardinalities moderate.
