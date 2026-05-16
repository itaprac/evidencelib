# pybelief

[![CI](https://github.com/itaprac/pybelief/actions/workflows/ci.yml/badge.svg)](https://github.com/itaprac/pybelief/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/pybelief/badge/?version=latest)](https://pybelief.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Python library for belief-function calculations in Dempster-Shafer theory
(DST) and Dezert-Smarandache theory (DSmT).

`pybelief` provides a compact quantitative core for finite frames: symbolic
propositions, basic belief assignments, evidence fusion rules, belief measures,
and pignistic decision support.

Documentation is available on
[Read the Docs](https://pybelief.readthedocs.io/en/latest/).

---

## Installation

You can install `pybelief` using pip:

```bash
pip install pybelief
```

For local development:

```bash
git clone https://github.com/itaprac/pybelief.git
cd pybelief
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

Run the test suite:

```bash
python -m pytest -q
```

Build the documentation locally:

```bash
python -m sphinx -W -b html docs docs/_build/html
```

---

## Available Functionality

The library contains:

### Models

| Constructor | Description |
| --- | --- |
| `Frame.dst(...)` | Shafer's classical DST model with exhaustive and mutually exclusive hypotheses. |
| `Frame.dsmt(...)` | Free DSm model where hypotheses may overlap. |
| `Frame.hybrid(...)` | Constrained DSm model with explicit emptiness or exclusivity constraints. |

### Proposition Algebra

| Operation | Meaning |
| --- | --- |
| `A \| B` | Union / disjunction, `A ∪ B`. |
| `A & B` | Intersection / conjunction, `A ∩ B`. |
| `frame.proposition("A ∩ (B ∪ C)")` | Parse a proposition from text. |
| `frame.elements()` | Generate the model's power set or hyper-power set. |

### Belief Measures

| Method | Description |
| --- | --- |
| `mass(A)` | Direct mass assigned to a proposition. |
| `belief(A)` | Sum of masses contained in `A`. |
| `plausibility(A)` | Sum of masses intersecting `A`. |
| `commonality(A)` | Sum of masses containing `A`. |
| `conflict` | Mass assigned to the empty proposition. |

### Fusion Rules

| Method | Description |
| --- | --- |
| `conjunctive(...)` | Unnormalized conjunctive rule. |
| `dsmc(...)` | Classic DSm rule on a free DSm frame. |
| `smets(...)` | TBM/Smets rule, keeping conflict on the empty proposition. |
| `dempster(...)` | Normalized Dempster rule. |
| `yager(...)` | Yager rule, moving conflict to total ignorance. |
| `dsmh(...)` | Hybrid DSm rule for constrained models. |
| `dubois_prade(...)` | Static Dubois-Prade-style conflict transfer. |
| `pcr5(...)` | PCR5 for two sources. |
| `pcr6(...)` | PCR6 for two or more sources. |

### Decision Support

| Method | Description |
| --- | --- |
| `pignistic()` | Singleton pignistic scores. |
| `pignistic_regions()` | Probability distribution over disjoint model regions. |
| `decision()` | Singleton with the largest pignistic score. |

---

## Usage Example

```python
from pybelief import Frame

frame = Frame.dst(["A", "B"])
A, B = frame.symbols()

m1 = frame.mass({
    A: 0.6,
    A | B: 0.4,
})

m2 = frame.mass({
    B: 0.3,
    A | B: 0.7,
})

print(m1.dempster(m2).to_dict())
print(m1.pcr5(m2).to_dict())
```

Output:

```python
{"A": 0.5121951219512195, "A|B": 0.34146341463414637, "B": 0.14634146341463414}
{"A": 0.54, "A|B": 0.28, "B": 0.18}
```

Free DSmT example:

```python
frame = Frame.dsmt(["A", "B"])
A, B = frame.symbols()

m = frame.mass({
    A: 0.2,
    B: 0.3,
    A & B: 0.4,
    A | B: 0.1,
})

print(m.pignistic())
print(m.pignistic_regions())
```

In DSmT, singleton hypotheses can overlap, so `pignistic()` returns decision
scores that do not necessarily sum to one. Use `pignistic_regions()` for a
probability distribution over disjoint Venn regions.

More examples are available in the [`examples/`](examples/) directory and in
the documentation.

---

## References

- Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton University Press.
- Smarandache, F., & Dezert, J. (eds.). *Advances and Applications of DSmT for Information Fusion*.
- Dezert, J., & Smarandache, F. *An Introduction to DSmT*.
- Zadeh, L. A. (1986). A simple view of the Dempster-Shafer theory of evidence and its implication for the rule of combination. *AI Magazine*, 7(2), 85-90.

---

## License

`pybelief` is released under the MIT License.
