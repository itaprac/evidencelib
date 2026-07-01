# evidencelib

[![CI](https://github.com/itaprac/evidencelib/actions/workflows/ci.yml/badge.svg)](https://github.com/itaprac/evidencelib/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/evidencelib.svg)](https://pypi.org/project/evidencelib/)
[![Python Version](https://img.shields.io/pypi/pyversions/evidencelib.svg)](https://pypi.org/project/evidencelib/)
[![Documentation Status](https://readthedocs.org/projects/evidencelib/badge/?version=latest)](https://evidencelib.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**evidencelib** is a Python library for belief-function calculations in Dempster-Shafer theory (DST) and Dezert-Smarandache theory (DSmT). It provides a compact, zero-dependency quantitative core for reasoning under uncertainty using belief functions.

- **Documentation:** https://evidencelib.readthedocs.io
- **Source Code:** https://github.com/itaprac/evidencelib
- **PyPI:** https://pypi.org/project/evidencelib/
- **Issue Tracker:** https://github.com/itaprac/evidencelib/issues

---

## Features

- **Multiple models** — Shafer's classical DST, free DSmT, and constrained hybrid DSm models
- **Proposition algebra** — symbolic construction of unions, intersections, and parsing from strings
- **Fusion rules** — Dempster, Yager, Smets/TBM, Dubois-Prade, Hybrid DSm, PCR5, PCR6
- **Belief measures** — mass, belief, plausibility, commonality, conflict
- **Decision support** — pignistic transformation over singletons and disjoint Venn regions
- **Optional plotting** — mass assignment bars, source comparison heatmaps, and decision plots
- **Zero dependencies** — pure Python, no external packages required
- **Fully typed** — type hints throughout the codebase

---

## Installation

```bash
pip install evidencelib
```

For plotting support:

```bash
pip install "evidencelib[plot]"
```

Requires Python 3.10 or later.

---

## Quick Start

### Basic DST Example

```python
from evidencelib import Frame

# Create a frame with mutually exclusive hypotheses
frame = Frame.dst(["Alive", "Dead"])
Alive, Dead = frame.symbols()

# Define a basic belief assignment
m = frame.mass({
    Alive: 0.2,
    Dead: 0.5,
    Alive | Dead: 0.3,
})

# Query belief measures
print(m.belief(Alive))        # 0.2
print(m.plausibility(Alive))  # 0.5
print(m.pignistic())          # {"Alive": 0.35, "Dead": 0.65}
print(m.decision())           # "Dead"
```

### Combining Evidence

```python
from evidencelib import Frame

frame = Frame.dst(["A", "B"])
A, B = frame.symbols()

m1 = frame.mass({A: 0.6, A | B: 0.4})
m2 = frame.mass({B: 0.3, A | B: 0.7})

# Dempster's rule
print(m1.dempster(m2).to_dict())
# {"A": 0.512, "A|B": 0.341, "B": 0.146}

# PCR6
print(m1.pcr6(m2).to_dict())
# {"A": 0.54, "A|B": 0.28, "B": 0.18}
```

### DSmT with Overlapping Hypotheses

```python
from evidencelib import Frame

# Free DSm model — hypotheses may overlap
frame = Frame.dsmt(["A", "B"])
A, B = frame.symbols()

m = frame.mass({
    A: 0.2,
    B: 0.3,
    A & B: 0.4,
    A | B: 0.1,
})

print(m.pignistic())          # singleton scores (may not sum to 1)
print(m.pignistic_regions())  # probability over disjoint Venn regions
```

---

## API Overview

### Frames

| Constructor | Description |
|---|---|
| `Frame.dst(atoms)` | Shafer's model — exhaustive and mutually exclusive hypotheses |
| `Frame.dsmt(atoms)` | Free DSm model — hypotheses may overlap |
| `Frame.hybrid(atoms, empty=..., exclusive=...)` | Constrained DSm model with explicit constraints |

### Propositions

| Operation | Description |
|---|---|
| `A \| B` | Union / disjunction |
| `A & B` | Intersection / conjunction |
| `frame.proposition("A ∩ (B ∪ C)")` | Parse from string |
| `frame.elements()` | Generate power set or hyper-power set |

### Belief Measures

| Method | Description |
|---|---|
| `mass(A)` | Direct mass assigned to proposition A |
| `belief(A)` | Sum of masses contained in A |
| `plausibility(A)` | Sum of masses intersecting A |
| `commonality(A)` | Sum of masses containing A |
| `conflict` | Mass assigned to the empty proposition |

### Fusion Rules

| Method | Description |
|---|---|
| `conjunctive(...)` | Unnormalized conjunctive rule |
| `dempster(...)` | Dempster's normalized rule |
| `smets(...)` | TBM/Smets rule — keeps conflict on empty set |
| `yager(...)` | Yager's rule — transfers conflict to total ignorance |
| `dsmc(...)` | Classic DSm conjunctive rule |
| `dsmh(...)` | Hybrid DSm rule for constrained models |
| `dubois_prade(...)` | Dubois-Prade conflict transfer |
| `pcr5(...)` | PCR5 for two sources |
| `pcr6(...)` | PCR6 for two or more sources |

### Decision Support

| Method | Description |
|---|---|
| `pignistic()` | Singleton pignistic scores |
| `pignistic_regions()` | Probability distribution over disjoint Venn regions |
| `decision()` | Singleton with the largest pignistic probability |

### Plotting

Plotting is optional and requires `evidencelib[plot]`.

```python
m.plot()
m.plot_belief_plausibility()
m.plot_pignistic_decision()
m1.plot_comparison(m2, labels=["sensor", "expert"])
```

Plots keep bar charts simple by default and use a green heatmap colormap.
Colors, legends, annotations, and heatmap colormaps can be customized with
Matplotlib-compatible values when needed:

```python
m.plot(colors="tab:blue", annotate=False)
m1.plot_comparison(
    m2,
    cmap="viridis",
    annotation_text_colors=("black", "white"),
)
m.plot_pignistic_decision(highlight_decision=False)
```

Function forms are also available:

```python
from evidencelib import plot_mass, plot_mass_comparison
```

---

## Development

```bash
git clone https://github.com/itaprac/evidencelib.git
cd evidencelib
python3.10 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docs]"
```

Run tests:

```bash
python -m pytest -q
```

Build documentation:

```bash
python -m sphinx -W -b html docs docs/_build/html
```

---

## Examples

See the [`examples/`](examples/) directory for complete scripts:

- [`basic_dst.py`](examples/basic_dst.py) — simple DST frame and belief measures
- [`rules_dst.py`](examples/rules_dst.py) — comparing fusion rules
- [`zadeh.py`](examples/zadeh.py) — Zadeh's classic counterexample
- [`dsmt_fusion.py`](examples/dsmt_fusion.py) — DSmT evidence fusion
- [`hybrid_dsmt.py`](examples/hybrid_dsmt.py) — constrained hybrid DSm model
- [`plotting.py`](examples/plotting.py) — optional plotting examples

---

## References

- Shafer, G. (1976). *A Mathematical Theory of Evidence*. Princeton University Press.
- Smarandache, F., & Dezert, J. (eds.). *Advances and Applications of DSmT for Information Fusion*.
- Dezert, J., & Smarandache, F. *An Introduction to DSmT*.
- Zadeh, L. A. (1986). A simple view of the Dempster-Shafer theory of evidence and its implication for the rule of combination. *AI Magazine*, 7(2), 85-90.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
