# Plotting

Plotting is optional so the computational core can stay dependency-free.
Install the extra before using the plotting API:

```bash
pip install "evidencelib[plot]"
```

## Mass assignment

Use `MassFunction.plot()` for a compact horizontal bar chart:

```python
from evidencelib import Frame

frame = Frame.dst(["A", "B", "C"])
A, B, C = frame.symbols()

m = frame.mass({
    A: 0.35,
    B: 0.20,
    A | B: 0.25,
    C: 0.20,
})

ax = m.plot(title="Sensor mass assignment")
```

The function form is equivalent:

```python
from evidencelib import plot_mass

ax = plot_mass(m, top_n=8, min_mass=0.02)
```

## Comparing sources

```python
ax = m1.plot_comparison(m2, labels=["sensor", "expert"])
```

or:

```python
from evidencelib import plot_mass_comparison

ax = plot_mass_comparison([m1, m2], labels=["sensor", "expert"])
```

All compared mass functions must belong to the same `Frame` instance.

## Belief and decision views

```python
m.plot_belief_plausibility()
m.plot_pignistic_decision()
```

The first plot shows belief-plausibility support intervals for singleton
hypotheses. The second plot ranks singleton hypotheses by pignistic score.
