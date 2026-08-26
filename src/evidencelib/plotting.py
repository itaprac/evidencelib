"""Matplotlib-based visualizations for belief mass functions."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, Literal, TYPE_CHECKING

from evidencelib.proposition import Proposition

if TYPE_CHECKING:
    from evidencelib.mass import MassFunction

__all__ = [
    "plot_belief_plausibility",
    "plot_mass",
    "plot_mass_comparison",
    "plot_pignistic_decision",
    "plot_venn",
]

SortBy = Literal["pignistic", "belief", "plausibility", "uncertainty"] | None
ColorSpec = str | Sequence[str] | Mapping[str, str] | None
VennValues = Literal["pignistic", "mass"]
MassPlotStyle = Literal["proposition_types"] | None

COLORS = {
    "singleton": "#1F77B4",
    "union": "#FF7F0E",
    "compound": "#2CA02C",
    "empty": "#D62728",
    "total": "#7F7F7F",
    "other": "#C7C7C7",
}

KIND_LABELS = {
    "singleton": "single hypothesis",
    "union": "union / uncertainty",
    "compound": "compound proposition",
    "empty": "empty / conflict",
    "total": "total ignorance",
    "other": "aggregated propositions",
}

_BAR_COLOR = "#1F77B4"
_DECISION_COLOR = "#1F77B4"
_PIGNISTIC_COLOR = "#FF7F0E"
_OTHER_COLOR = "#C7C7C7"
_SECONDARY_BAR_COLOR = "#AEC7E8"
_TEXT_COLOR = "#222222"
_MUTED_TEXT_COLOR = "#555555"
_GRID_COLOR = "#E8EAED"
_SPINE_COLOR = "#B8BDC2"
_LIGHT_SPINE_COLOR = "#D1D5D9"
_BACKGROUND_COLOR = "#FFFFFF"
_OTHER_LABEL = "Other propositions"

_HEATMAP_CMAP = "Greens"
_VENN_COLORS = (_BAR_COLOR, _PIGNISTIC_COLOR, COLORS["compound"])
_PROPOSITION_TYPE_COLORS = {
    "singleton": "#4472C4",
    "union": "#A5A5A5",
    "compound": "#ED7D31",
    "empty": "#C00000",
    "total": "#70AD47",
    "other": _OTHER_COLOR,
}


def plot_mass(
    mass: MassFunction,
    *,
    ax: Any = None,
    title: str | None = None,
    sort: bool = True,
    top_n: int | None = None,
    min_mass: float | None = None,
    show_other: bool = True,
    style: MassPlotStyle = None,
    colors: ColorSpec = None,
    show_kind_legend: bool | None = None,
    annotate: bool = True,
) -> Any:
    """Draw a horizontal bar plot for one mass assignment.

    Parameters
    ----------
    mass:
        Mass function to visualize.
    ax:
        Optional matplotlib axes. If omitted, a new figure and axes are created.
    title:
        Optional custom title.
    sort:
        Sort focal propositions by descending mass.
    top_n:
        Keep only the largest ``top_n`` visible propositions.
    min_mass:
        Hide propositions below this direct mass threshold.
    show_other:
        Aggregate hidden propositions into an ``Other propositions`` bar.
    style:
        Optional built-in presentation style. ``"proposition_types"`` colors
        singleton hypotheses, unions, intersections, conflict, and ignorance
        consistently and enables the proposition-kind legend.
    colors:
        Optional color override. Pass a single matplotlib color for all bars,
        a sequence to cycle through bars, or a mapping keyed by proposition
        kind (``singleton``, ``union``, ``compound``, ``empty``, ``total``,
        ``other``) or displayed label. By default all regular bars use one
        color, and the aggregated ``other`` bar is muted.
    show_kind_legend:
        Display a legend for proposition kinds. By default it is enabled by
        the ``"proposition_types"`` style and disabled otherwise.
    annotate:
        Draw numeric mass labels at the end of bars.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the plot.
    """

    _validate_positive_int("top_n", top_n)
    _validate_non_negative("min_mass", min_mass)
    if style not in {None, "proposition_types"}:
        raise ValueError("style must be 'proposition_types' or None.")
    if style == "proposition_types" and colors is None:
        colors = _PROPOSITION_TYPE_COLORS
    if show_kind_legend is None:
        show_kind_legend = style == "proposition_types"

    items = _prepare_mass_items(
        mass,
        sort=sort,
        top_n=top_n,
        min_mass=min_mass,
        show_other=show_other,
    )
    if not items:
        raise ValueError("No propositions remain after filtering.")

    plt, _, _ = _load_matplotlib()

    if ax is None:
        height = max(4.0, 0.48 * len(items) + 1.6)
        _, ax = plt.subplots(figsize=(7.5, height))

    labels = [_pretty_label(prop) for prop, _ in items]
    values = [value for _, value in items]
    kinds = [_proposition_kind(prop, mass.frame) for prop, _ in items]
    bar_colors = _resolve_colors(
        colors,
        labels=labels,
        kinds=kinds,
        default_color=_BAR_COLOR,
        default_by_kind={"other": _OTHER_COLOR},
    )

    bars = ax.barh(
        labels,
        values,
        color=bar_colors,
        edgecolor=_BACKGROUND_COLOR,
        linewidth=0.7,
        height=0.56,
    )

    ax.set_title(title or f"Mass assignment ({mass.frame.model})", pad=12)
    ax.set_xlabel("Assigned mass")
    ax.set_ylabel("Hypotheses / propositions")
    _set_fractional_xlim(ax, values, padding=1.28)
    ax.invert_yaxis()

    ax.grid(axis="x", color=_GRID_COLOR, linewidth=0.7)
    ax.set_axisbelow(True)
    _soften_bar_axes(ax)
    if annotate:
        _annotate_horizontal_bars(ax, bars, values)

    if show_kind_legend:
        used_kinds = list(dict.fromkeys(kinds))
        handles = [
            plt.Rectangle(
                (0, 0),
                1,
                1,
                color=_first_color_for_kind(kind, kinds, bar_colors),
                label=KIND_LABELS[kind],
            )
            for kind in used_kinds
        ]
        ax.legend(
            handles=handles,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.16),
            ncol=min(3, len(handles)),
            frameon=False,
            fontsize=8,
        )

    return ax


def plot_mass_comparison(
    masses: Sequence[MassFunction],
    *,
    labels: Sequence[str] | None = None,
    ax: Any = None,
    title: str | None = None,
    sort: bool = True,
    top_n: int | None = None,
    min_total_mass: float | None = None,
    annotate: bool = True,
    vmax: float | None = None,
    cmap: Any = None,
    colorbar: bool = True,
    annotation_text_colors: Sequence[str] = (_TEXT_COLOR, _BACKGROUND_COLOR),
    annotation_threshold: float = 0.45,
) -> Any:
    """Draw a heatmap comparing mass assignments across sources.

    Rows represent mass functions, columns represent propositions that appear in
    at least one source, and cell values are assigned masses.

    Parameters
    ----------
    cmap:
        Optional matplotlib colormap name/object or a sequence of colors used
        to build a linear colormap.
    colorbar:
        Draw the assigned-mass colorbar.
    annotation_text_colors:
        Pair of matplotlib colors used for annotated values on light and dark
        heatmap cells.
    annotation_threshold:
        Normalized cell intensity, from 0 to 1, where annotations switch from
        the first text color to the second text color.
    """

    masses = tuple(masses)
    _validate_positive_int("top_n", top_n)
    _validate_non_negative("min_total_mass", min_total_mass)
    _validate_positive("vmax", vmax)
    _validate_fraction("annotation_threshold", annotation_threshold)
    text_colors = _validate_color_pair("annotation_text_colors", annotation_text_colors)
    frame = _require_common_frame(masses)

    if labels is None:
        labels = [f"source {index + 1}" for index in range(len(masses))]
    elif len(labels) != len(masses):
        raise ValueError("labels must have the same length as masses.")

    columns = _prepare_mass_comparison_columns(
        masses,
        sort=sort,
        top_n=top_n,
        min_total_mass=min_total_mass,
    )
    if not columns:
        raise ValueError("No propositions remain after filtering.")

    values = [[mass.mass(prop) for prop in columns] for mass in masses]
    plt, LinearSegmentedColormap, _ = _load_matplotlib()
    heatmap_cmap = _resolve_cmap(cmap, LinearSegmentedColormap)

    if ax is None:
        width = max(7.0, 0.62 * len(columns) + 2.0)
        height = max(3.8, 0.55 * len(masses) + 2.0)
        _, ax = plt.subplots(figsize=(width, height))

    max_value = max((value for row in values for value in row), default=1.0)
    color_max = vmax if vmax is not None else max(max_value, 0.01)
    heatmap = ax.pcolormesh(
        range(len(columns)),
        range(len(masses)),
        values,
        cmap=heatmap_cmap,
        vmin=0,
        vmax=color_max,
        shading="nearest",
    )
    ax.set_aspect("auto")
    ax.invert_yaxis()

    ax.set_title(title or f"Mass comparison ({frame.model})", pad=12)
    ax.set_xlabel("Hypotheses / propositions")
    ax.set_ylabel("Sources")
    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels([_pretty_label(prop) for prop in columns], rotation=35, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    ax.set_xticks([index - 0.5 for index in range(len(columns) + 1)], minor=True)
    ax.set_yticks([index - 0.5 for index in range(len(masses) + 1)], minor=True)
    ax.grid(which="minor", color=_BACKGROUND_COLOR, linewidth=1.4)
    ax.tick_params(which="minor", bottom=False, left=False)

    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color(_SPINE_COLOR)
        ax.spines[side].set_linewidth(0.8)
    ax.set_facecolor(_BACKGROUND_COLOR)
    _style_text(ax)

    if annotate:
        _annotate_heatmap(
            ax,
            values,
            color_max,
            text_colors=text_colors,
            threshold=annotation_threshold,
        )

    if colorbar:
        cbar = ax.figure.colorbar(heatmap, ax=ax, fraction=0.035, pad=0.02)
        cbar.solids.set_rasterized(False)
        cbar.set_label("Assigned mass")
        cbar.outline.set_edgecolor(_SPINE_COLOR)
        cbar.outline.set_linewidth(0.8)
        cbar.ax.tick_params(colors=_TEXT_COLOR, labelsize=8)
        cbar.ax.yaxis.label.set_color(_TEXT_COLOR)

    return ax


def plot_venn(
    mass: MassFunction,
    *,
    ax: Any = None,
    title: str | None = None,
    labels: Sequence[str] | None = None,
    values: VennValues = "pignistic",
    colors: ColorSpec = None,
    alpha: float = 0.32,
    annotate: bool = True,
    show_zero_values: bool = True,
    show_region_labels: bool = False,
    value_formatter: Callable[[float], str] | None = None,
) -> Any:
    """Draw a compact Venn-style diagram for one to three hypotheses.

    The diagram labels disjoint model regions, so it is most useful for DSmT
    and hybrid DSm frames where overlaps are meaningful. By default, region
    values come from the pignistic transformation over Venn regions. Pass
    ``values="mass"`` to show only direct mass assigned to each elementary
    region.

    Parameters
    ----------
    labels:
        Optional display labels for the frame atoms.
    values:
        ``"pignistic"`` for distributed pignistic region probabilities, or
        ``"mass"`` for direct mass assigned to elementary Venn regions.
    colors:
        Optional circle color override. Pass a single Matplotlib color, a
        sequence cycled across circles, or a mapping keyed by atom label.
    alpha:
        Circle fill opacity.
    annotate:
        Draw region values inside the diagram.
    show_zero_values:
        Display zero-valued possible regions as ``0.00``. Disable to hide them.
    show_region_labels:
        Include the region name above each numeric value.
    value_formatter:
        Optional callable used to format region values.
    """

    frame = mass.frame
    atom_count = len(frame.atoms)
    if atom_count > 3:
        raise ValueError("Venn plots support at most three frame atoms.")
    _validate_fraction("alpha", alpha)

    atom_labels = _resolve_venn_labels(frame, labels)
    region_values = _prepare_venn_region_values(mass, values)
    plt, _, _ = _load_matplotlib()

    if ax is None:
        width = 4.8 if atom_count < 3 else 5.4
        _, ax = plt.subplots(figsize=(width, 4.6))

    layout = _venn_layout(atom_count, _venn_has_only_singletons(frame))
    circle_colors = _resolve_venn_colors(colors, atom_labels)
    for center, radius, color in zip(
        layout["centers"],
        layout["radii"],
        circle_colors,
        strict=True,
    ):
        circle = plt.Circle(
            center,
            radius,
            facecolor=color,
            edgecolor=color,
            linewidth=1.8,
            alpha=alpha,
        )
        ax.add_patch(circle)

    for label, position in zip(atom_labels, layout["label_positions"], strict=True):
        ax.text(
            *position,
            label,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color=_TEXT_COLOR,
        )

    formatter = value_formatter or (lambda value: f"{value:.2f}")
    if annotate:
        for region, position in layout["region_positions"].items():
            if region not in frame._universe:
                continue
            value = region_values.get(region, 0.0)
            is_zero = abs(value) <= mass.tolerance
            if not show_zero_values and is_zero:
                continue
            text = formatter(value)
            if show_region_labels:
                region_name = _format_venn_region(region, atom_labels)
                text = f"{region_name}\n{text}"
            ax.text(
                *position,
                text,
                ha="center",
                va="center",
                fontsize=9,
                color=_MUTED_TEXT_COLOR if is_zero else _TEXT_COLOR,
            )

    default_title = (
        "Pignistic Venn regions"
        if values == "pignistic"
        else "Direct Venn-region mass"
    )
    ax.set_title(title or f"{default_title} ({frame.model})", pad=12)
    ax.set_xlim(*layout["xlim"])
    ax.set_ylim(*layout["ylim"])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    _style_text(ax)
    return ax


def plot_belief_plausibility(
    mass: MassFunction,
    *,
    hypotheses: Sequence[str | Proposition | Iterable[str]] | None = None,
    ax: Any = None,
    title: str | None = None,
    show_pignistic: bool = True,
    show_decision: bool = True,
    sort_by: SortBy = "pignistic",
    annotate_intervals: bool = False,
    interval_color: str = _BAR_COLOR,
    decision_color: str = _DECISION_COLOR,
    pignistic_color: str = _PIGNISTIC_COLOR,
    show_legend: bool = True,
) -> Any:
    """Draw belief-plausibility intervals for singleton hypotheses.

    The interval for each hypothesis starts at belief and ends at plausibility.
    When enabled, pignistic scores are drawn as point markers.

    Parameters
    ----------
    interval_color, decision_color, pignistic_color:
        Matplotlib colors for support intervals, selected-decision interval,
        and pignistic markers.
    show_legend:
        Display the compact explanation legend.
    """

    if sort_by is not None and sort_by not in {
        "pignistic",
        "belief",
        "plausibility",
        "uncertainty",
    }:
        raise ValueError(
            "sort_by must be pignistic, belief, plausibility, uncertainty, or None."
        )

    if hypotheses is None:
        selected = mass.frame.symbols()
    else:
        selected = tuple(mass.frame.proposition(hypothesis) for hypothesis in hypotheses)
    if not selected:
        raise ValueError("At least one hypothesis is required.")

    pignistic = mass.pignistic() if show_pignistic or sort_by == "pignistic" else {}
    decision_name = mass.decision() if show_decision else None
    decision = mass.frame.proposition(decision_name) if decision_name is not None else None

    rows: list[dict[str, Any]] = []
    for hypothesis in selected:
        belief = mass.belief(hypothesis)
        plausibility = mass.plausibility(hypothesis)
        rows.append(
            {
                "label": _pretty_label(hypothesis),
                "belief": belief,
                "plausibility": plausibility,
                "uncertainty": plausibility - belief,
                "pignistic": pignistic.get(str(hypothesis)),
                "is_decision": hypothesis == decision,
            }
        )

    if sort_by is not None:
        rows = sorted(
            rows,
            key=lambda row: row[sort_by] if row[sort_by] is not None else -1.0,
            reverse=True,
        )

    plt, _, MultipleLocator = _load_matplotlib()
    if ax is None:
        width = max(7.0, 0.75 * len(rows) + 2.0)
        _, ax = plt.subplots(figsize=(width, 5.0))

    x_positions = list(range(len(rows)))
    for x, row in zip(x_positions, rows, strict=True):
        line_color = decision_color if row["is_decision"] else interval_color
        line_width = 2.0 if row["is_decision"] else 1.5

        center = (row["belief"] + row["plausibility"]) / 2
        lower_error = center - row["belief"]
        upper_error = row["plausibility"] - center
        ax.errorbar(
            x,
            center,
            yerr=[[lower_error], [upper_error]],
            fmt="none",
            ecolor=line_color,
            elinewidth=line_width,
            capsize=8,
            capthick=line_width,
            zorder=2,
        )

        if show_pignistic and row["pignistic"] is not None:
            ax.scatter(
                x,
                row["pignistic"],
                s=30,
                marker="o",
                color=pignistic_color,
                edgecolor=_BACKGROUND_COLOR,
                linewidth=0.8,
                zorder=4,
            )

        if annotate_intervals:
            ax.text(
                x,
                min(row["plausibility"] + 0.04, 1.06),
                f"[{row['belief']:.2f}, {row['plausibility']:.2f}]",
                ha="center",
                va="bottom",
                fontsize=8,
                color=_MUTED_TEXT_COLOR,
            )

    ax.set_title(title or f"Belief / plausibility intervals ({mass.frame.model})", pad=12)
    ax.set_xlabel("Hypotheses")
    ax.set_ylabel("Support")
    ax.set_ylim(-0.02, 1.08)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([row["label"] for row in rows], rotation=0)
    ax.yaxis.set_major_locator(MultipleLocator(0.1))

    ax.grid(axis="y", color=_GRID_COLOR, linewidth=0.7)
    ax.set_axisbelow(True)
    _soften_support_axes(ax)

    handles = [
        plt.Line2D(
            [0],
            [0],
            color=interval_color,
            linewidth=1.5,
            label="belief-plausibility interval",
        ),
    ]
    if show_pignistic:
        handles.append(
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor=pignistic_color,
                markeredgecolor=pignistic_color,
                markersize=7,
                label="pignistic score",
            )
        )
    if show_decision and decision is not None:
        handles.append(
            plt.Line2D(
                [0],
                [0],
                color=decision_color,
                linewidth=2.0,
                label="selected decision",
            )
        )

    if show_legend:
        ax.legend(
            handles=handles,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.14),
            ncol=min(3, len(handles)),
            frameon=False,
            fontsize=8,
        )

    return ax


def plot_pignistic_decision(
    mass: MassFunction,
    *,
    ax: Any = None,
    title: str | None = None,
    top_n: int | None = None,
    colors: ColorSpec = None,
    highlight_decision: bool = True,
    decision_color: str = _DECISION_COLOR,
    annotate: bool = True,
    show_legend: bool = False,
) -> Any:
    """Draw a horizontal ranking of pignistic decision scores.

    Parameters
    ----------
    colors:
        Optional color override. Pass a single matplotlib color for all bars,
        a sequence to cycle through bars, or a mapping keyed by hypothesis
        label, ``decision``, ``hypothesis``, or ``default``.
    highlight_decision:
        Emphasize the top pignistic score. Disable for a neutral ranking plot.
    decision_color:
        Matplotlib color for the selected decision when highlighting is active.
    annotate:
        Draw numeric pignistic scores at the end of bars.
    show_legend:
        Display a legend for the decision highlight.
    """

    _validate_positive_int("top_n", top_n)

    scores = mass.pignistic()
    if not scores:
        raise ValueError("No pignistic scores are available.")

    rows = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if top_n is not None:
        rows = rows[:top_n]

    winner = rows[0][0]
    plt, _, _ = _load_matplotlib()

    if ax is None:
        height = max(4.0, 0.5 * len(rows) + 1.8)
        _, ax = plt.subplots(figsize=(7.5, height))

    labels = [label for label, _ in rows]
    values = [value for _, value in rows]
    if colors is None:
        if highlight_decision:
            bar_colors = [
                decision_color if label == winner else _SECONDARY_BAR_COLOR
                for label in labels
            ]
        else:
            bar_colors = [_BAR_COLOR for _ in labels]
    else:
        kinds = ["decision" if label == winner else "hypothesis" for label in labels]
        bar_colors = _resolve_colors(
            colors,
            labels=labels,
            kinds=kinds,
            default_color=_BAR_COLOR,
            default_by_kind={
                "decision": decision_color,
                "hypothesis": _SECONDARY_BAR_COLOR,
            },
        )

    bars = ax.barh(
        labels,
        values,
        color=bar_colors,
        edgecolor=_BACKGROUND_COLOR,
        linewidth=0.7,
        height=0.56,
    )
    ax.invert_yaxis()

    ax.set_title(title or f"Pignistic decision ranking ({mass.frame.model})", pad=12)
    ax.set_xlabel("Pignistic score")
    ax.set_ylabel("Hypotheses")
    _set_fractional_xlim(ax, values, padding=1.25)

    ax.grid(axis="x", color=_GRID_COLOR, linewidth=0.7)
    ax.set_axisbelow(True)
    _soften_bar_axes(ax)
    if annotate:
        _annotate_horizontal_bars(ax, bars, values)

    if show_legend and highlight_decision:
        handles = [
            plt.Rectangle((0, 0), 1, 1, color=decision_color, label="selected decision"),
            plt.Rectangle(
                (0, 0),
                1,
                1,
                color=_SECONDARY_BAR_COLOR,
                label="other hypotheses",
            ),
        ]
        ax.legend(
            handles=handles,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.14),
            ncol=2,
            frameon=False,
            fontsize=8,
        )

    return ax


def _prepare_mass_items(
    mass: MassFunction,
    *,
    sort: bool,
    top_n: int | None,
    min_mass: float | None,
    show_other: bool,
) -> list[tuple[Proposition | str, float]]:
    items = list(mass.items())

    if min_mass is None:
        visible = items
        hidden: list[tuple[Proposition, float]] = []
    else:
        visible = [(prop, value) for prop, value in items if value >= min_mass]
        hidden = [(prop, value) for prop, value in items if value < min_mass]

    if sort:
        visible = sorted(visible, key=lambda item: item[1], reverse=True)

    if top_n is not None and len(visible) > top_n:
        visible, extra = visible[:top_n], visible[top_n:]
        hidden.extend(extra)

    other_mass = sum(value for _, value in hidden)
    result: list[tuple[Proposition | str, float]] = list(visible)
    if show_other and other_mass > mass.tolerance:
        result.append((_OTHER_LABEL, other_mass))
    return result


def _prepare_mass_comparison_columns(
    masses: Sequence[MassFunction],
    *,
    sort: bool,
    top_n: int | None,
    min_total_mass: float | None,
) -> list[Proposition]:
    totals: dict[Proposition, float] = {}
    for mass in masses:
        for prop, value in mass.items():
            totals[prop] = totals.get(prop, 0.0) + value

    items = list(totals.items())
    if min_total_mass is not None:
        items = [(prop, total) for prop, total in items if total >= min_total_mass]
    if sort:
        items = sorted(items, key=lambda item: item[1], reverse=True)
    if top_n is not None:
        items = items[:top_n]
    return [prop for prop, _ in items]


def _prepare_venn_region_values(
    mass: MassFunction,
    values: VennValues,
) -> dict[int, float]:
    frame = mass.frame
    if values not in {"pignistic", "mass"}:
        raise ValueError("values must be 'pignistic' or 'mass'.")

    result = {region: 0.0 for region in frame._universe}
    if values == "mass":
        for prop, assigned_mass in mass.items():
            if len(prop.regions) == 1:
                result[next(iter(prop.regions))] += assigned_mass
        return result

    probabilities = mass.pignistic_regions()
    for region in frame._universe:
        result[region] = probabilities[mass._format_region(region)]
    return result


def _resolve_venn_labels(frame: Any, labels: Sequence[str] | None) -> tuple[str, ...]:
    if labels is None:
        return tuple(frame.atoms)
    if isinstance(labels, str):
        raise ValueError("labels must be a sequence of atom labels, not a string.")
    resolved = tuple(labels)
    if len(resolved) != len(frame.atoms):
        raise ValueError("labels must have the same length as frame atoms.")
    return resolved


def _resolve_venn_colors(colors: ColorSpec, labels: Sequence[str]) -> list[str]:
    if isinstance(colors, str):
        return [colors for _ in labels]
    if isinstance(colors, Mapping):
        return [
            colors.get(label, colors.get("default", _VENN_COLORS[index % len(_VENN_COLORS)]))
            for index, label in enumerate(labels)
        ]
    if colors is not None:
        color_list = list(colors)
        if not color_list:
            raise ValueError("colors must not be empty.")
        return [color_list[index % len(color_list)] for index, _ in enumerate(labels)]
    return [_VENN_COLORS[index % len(_VENN_COLORS)] for index, _ in enumerate(labels)]


def _venn_has_only_singletons(frame: Any) -> bool:
    singleton_regions = {1 << index for index, _ in enumerate(frame.atoms)}
    return set(frame._universe) == singleton_regions


def _format_venn_region(region: int, labels: Sequence[str]) -> str:
    return "\u2229".join(
        label for index, label in enumerate(labels) if region & (1 << index)
    )


def _venn_layout(atom_count: int, disjoint: bool) -> dict[str, Any]:
    if atom_count == 1:
        return {
            "centers": [(0.0, 0.0)],
            "radii": [0.82],
            "label_positions": [(0.0, 1.0)],
            "region_positions": {1: (0.0, 0.0)},
            "xlim": (-1.25, 1.25),
            "ylim": (-1.05, 1.25),
        }

    if atom_count == 2:
        if disjoint:
            return {
                "centers": [(-0.72, 0.0), (0.72, 0.0)],
                "radii": [0.52, 0.52],
                "label_positions": [(-0.72, 0.72), (0.72, 0.72)],
                "region_positions": {
                    1: (-0.72, 0.0),
                    2: (0.72, 0.0),
                    3: (0.0, 0.0),
                },
                "xlim": (-1.45, 1.45),
                "ylim": (-0.9, 1.0),
            }
        return {
            "centers": [(-0.48, 0.0), (0.48, 0.0)],
            "radii": [0.78, 0.78],
            "label_positions": [(-0.83, 0.86), (0.83, 0.86)],
            "region_positions": {
                1: (-0.72, 0.0),
                2: (0.72, 0.0),
                3: (0.0, 0.0),
            },
            "xlim": (-1.45, 1.45),
            "ylim": (-1.0, 1.1),
        }

    if disjoint:
        return {
            "centers": [(-0.82, 0.32), (0.82, 0.32), (0.0, -0.72)],
            "radii": [0.48, 0.48, 0.48],
            "label_positions": [(-0.82, 0.96), (0.82, 0.96), (0.0, -1.34)],
            "region_positions": {
                1: (-0.82, 0.32),
                2: (0.82, 0.32),
                3: (0.0, 0.32),
                4: (0.0, -0.72),
                5: (-0.42, -0.22),
                6: (0.42, -0.22),
                7: (0.0, -0.08),
            },
            "xlim": (-1.45, 1.45),
            "ylim": (-1.55, 1.2),
        }

    return {
        "centers": [(-0.5, 0.22), (0.5, 0.22), (0.0, -0.5)],
        "radii": [0.78, 0.78, 0.78],
        "label_positions": [(-1.02, 1.0), (1.02, 1.0), (0.0, -1.36)],
        "region_positions": {
            1: (-0.78, 0.43),
            2: (0.78, 0.43),
            3: (0.0, 0.48),
            4: (0.0, -0.88),
            5: (-0.39, -0.28),
            6: (0.39, -0.28),
            7: (0.0, -0.06),
        },
        "xlim": (-1.45, 1.45),
        "ylim": (-1.55, 1.25),
    }


def _proposition_kind(prop: Proposition | str, frame: Any) -> str:
    if isinstance(prop, str):
        if prop == _OTHER_LABEL:
            return "other"
        return "compound"
    if prop.is_empty:
        return "empty"
    if prop == frame.total:
        return "total"
    if prop in frame.symbols():
        return "singleton"
    if prop == prop.union_atoms():
        return "union"
    return "compound"


def _pretty_label(prop: Proposition | str) -> str:
    if isinstance(prop, str):
        return prop
    if prop.is_empty:
        return "empty / conflict"
    return str(prop).replace("|", " \u222a ").replace("&", " \u2229 ")


def _resolve_colors(
    colors: ColorSpec,
    *,
    labels: Sequence[str],
    kinds: Sequence[str],
    default_color: str,
    default_by_kind: Mapping[str, str] | None = None,
) -> list[str]:
    if isinstance(colors, str):
        return [colors for _ in labels]

    if isinstance(colors, Mapping):
        defaults = default_by_kind or {}
        fallback = colors.get("default", default_color)
        return [
            colors.get(label, colors.get(kind, defaults.get(kind, fallback)))
            for label, kind in zip(labels, kinds, strict=True)
        ]

    if colors is not None:
        color_list = list(colors)
        if not color_list:
            raise ValueError("colors must not be empty.")
        return [color_list[index % len(color_list)] for index, _ in enumerate(labels)]

    defaults = default_by_kind or {}
    return [defaults.get(kind, default_color) for kind in kinds]


def _resolve_cmap(cmap: Any, linear_segmented_colormap: Any) -> Any:
    if cmap is None:
        return _HEATMAP_CMAP
    if isinstance(cmap, str):
        return cmap
    if isinstance(cmap, Sequence):
        colors = list(cmap)
        if not colors:
            raise ValueError("cmap color sequence must not be empty.")
        return linear_segmented_colormap.from_list("evidencelib_custom", colors)
    return cmap


def _first_color_for_kind(kind: str, kinds: Sequence[str], colors: Sequence[str]) -> str:
    for candidate_kind, color in zip(kinds, colors, strict=True):
        if candidate_kind == kind:
            return color
    return COLORS.get(kind, _BAR_COLOR)


def _load_matplotlib() -> tuple[Any, Any, Any]:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib.ticker import MultipleLocator
    except ImportError as exc:  # pragma: no cover - depends on installed extras.
        raise ImportError(
            "Plotting requires matplotlib. Install it with "
            "`pip install 'evidencelib[plot]'`."
        ) from exc
    return plt, LinearSegmentedColormap, MultipleLocator


def _require_common_frame(masses: Sequence[MassFunction]) -> Any:
    if not masses:
        raise ValueError("At least one mass function is required.")
    frame = masses[0].frame
    if any(mass.frame is not frame for mass in masses):
        raise ValueError("All mass functions must belong to the same frame.")
    return frame


def _validate_positive_int(name: str, value: int | None) -> None:
    if value is not None and value < 1:
        raise ValueError(f"{name} must be a positive integer or None.")


def _validate_non_negative(name: str, value: float | None) -> None:
    if value is not None and value < 0:
        raise ValueError(f"{name} must be non-negative or None.")


def _validate_positive(name: str, value: float | None) -> None:
    if value is not None and value <= 0:
        raise ValueError(f"{name} must be positive or None.")


def _validate_fraction(name: str, value: float) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")


def _validate_color_pair(name: str, value: Sequence[str]) -> tuple[str, str]:
    if isinstance(value, str):
        raise ValueError(f"{name} must contain exactly two colors.")
    colors = tuple(value)
    if len(colors) != 2:
        raise ValueError(f"{name} must contain exactly two colors.")
    return colors


def _set_fractional_xlim(ax: Any, values: Sequence[float], *, padding: float) -> None:
    max_value = max(values, default=0.0)
    upper = max(0.1, max_value * padding)
    ax.set_xlim(0, min(1.05, upper))


def _soften_bar_axes(ax: Any) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(_LIGHT_SPINE_COLOR)
    ax.spines["bottom"].set_color(_LIGHT_SPINE_COLOR)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    _style_text(ax)


def _soften_support_axes(ax: Any) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(_LIGHT_SPINE_COLOR)
    ax.spines["bottom"].set_color(_LIGHT_SPINE_COLOR)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    _style_text(ax)


def _style_text(ax: Any) -> None:
    ax.set_facecolor(_BACKGROUND_COLOR)
    ax.figure.patch.set_facecolor(_BACKGROUND_COLOR)
    ax.title.set_color(_TEXT_COLOR)
    ax.xaxis.label.set_color(_TEXT_COLOR)
    ax.yaxis.label.set_color(_TEXT_COLOR)
    ax.tick_params(axis="both", colors=_TEXT_COLOR, labelsize=9)


def _annotate_horizontal_bars(ax: Any, bars: Any, values: Sequence[float]) -> None:
    axis_max = ax.get_xlim()[1]
    offset = axis_max * 0.025
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            value + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}",
            va="center",
            fontsize=9,
            color=_TEXT_COLOR,
        )


def _annotate_heatmap(
    ax: Any,
    values: Sequence[Sequence[float]],
    color_max: float,
    *,
    text_colors: tuple[str, str],
    threshold: float,
) -> None:
    for row_index, row in enumerate(values):
        for col_index, value in enumerate(row):
            if value == 0:
                ax.text(
                    col_index,
                    row_index,
                    "-",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color=_SPINE_COLOR,
                )
                continue
            text_color = text_colors[1] if value / color_max >= threshold else text_colors[0]
            ax.text(
                col_index,
                row_index,
                f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=8,
                color=text_color,
            )
