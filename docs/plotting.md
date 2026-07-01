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

By default, mass bars use one familiar Matplotlib blue and avoid categorical
legends unless they add information. You can turn off value labels or provide
colors explicitly:

```python
ax = plot_mass(m, colors="#3f566a", annotate=False)
```

For proposition-kind coloring, pass a mapping and opt into the legend:

```python
ax = plot_mass(
    m,
    colors={
        "singleton": "#222222",
        "union": "#ff7f0e",
        "compound": "#2ca02c",
        "empty": "#d62728",
        "total": "#7f7f7f",
    },
    show_kind_legend=True,
)
```

`colors` accepts any Matplotlib color, a list of colors, or a palette returned
by another library such as seaborn:

```python
import seaborn as sns

palette = sns.color_palette("colorblind", n_colors=4)
ax = plot_mass(m, colors=palette)
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

All compared mass functions must belong to the same `Frame` instance. The
default heatmap uses Matplotlib's `Greens` colormap. Use `cmap` to provide any
other Matplotlib colormap name/object or a sequence of colors:

```python
ax = plot_mass_comparison([m1, m2], cmap="viridis")
ax = plot_mass_comparison([m1, m2], cmap=["#ffffff", "#08519c"])
```

Annotated heatmap cells automatically switch text color for contrast. You can
adjust the light-cell/dark-cell text colors and the normalized switch point:

```python
ax = plot_mass_comparison(
    [m1, m2],
    annotation_text_colors=("black", "white"),
    annotation_threshold=0.5,
)
```

## Belief and decision views

```python
m.plot_belief_plausibility()
m.plot_pignistic_decision()
```

The first plot shows belief-plausibility support intervals for singleton
hypotheses. The second plot ranks singleton hypotheses by pignistic score.
Decision highlighting can be disabled when a neutral ranking is preferred:

```python
ax = m.plot_pignistic_decision(highlight_decision=False, annotate=False)
```

## Selective and composed plots

Each plotting function returns a Matplotlib `Axes` object and accepts an
existing `ax`, so you can draw only the views you need and compose them into
your own figure layouts.

Plot only selected propositions or hypotheses:

```python
plot_mass(m, top_n=5, min_mass=0.05, show_other=False)
plot_belief_plausibility(m, hypotheses=["A", "B"], show_pignistic=False)
plot_pignistic_decision(m, top_n=3)
plot_mass_comparison([m1, m2], top_n=6, min_total_mass=0.05)
```

Combine arbitrary plots in one figure:

```python
import matplotlib.pyplot as plt
from evidencelib import plot_mass, plot_belief_plausibility, plot_pignistic_decision

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

plot_mass(m, ax=axes[0], title="Mass assignment")
plot_belief_plausibility(m, ax=axes[1], title="Support intervals")
plot_pignistic_decision(m, ax=axes[2], title="Decision ranking")

fig.tight_layout()
```

## Running selected examples

The repository example script can draw individual figures when you only want to
inspect one plot:

```bash
python examples/plotting.py --figure models --model dst
python examples/plotting.py --figure models --model hybrid --symbols A B C D
python examples/plotting.py --figure belief
python examples/plotting.py --figure pignistic
```

Use `--save-dir` to save PNG files without opening interactive windows:

```bash
python examples/plotting.py --figure all --save-dir /tmp/evidencelib-plots
```
