"""Render the README/notebook charts to reports/img/ (token, cost, ROC).

Run: ``uv run python scripts/make_charts.py``. Keyless and deterministic; saves three PNGs.
The same ``fig_*`` builders are imported by ``notebooks/project_run.ipynb`` so the inline
visuals and the committed images share one source of truth.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import chart_data

IMG_DIR = Path("reports/img")
GG, NAIVE = "#2563eb", "#94a3b8"  # graph-guided (blue) vs naive (slate)


def _style() -> None:
    plt.style.use("seaborn-v0_8-darkgrid")
    plt.rcParams.update({"figure.dpi": 140, "font.size": 11, "axes.titleweight": "bold"})


def _grouped_bars(
    ax: Axes,
    groups: Sequence[str],
    gg_vals: Sequence[float],
    naive_vals: Sequence[float],
    fmt: Callable[[float], str],
) -> None:
    import numpy as np

    x = np.arange(len(groups))
    series = ((-0.2, gg_vals, GG, "graph-guided"), (0.2, naive_vals, NAIVE, "naive"))
    for offset, vals, colour, label in series:
        bars = ax.bar(x + offset, vals, 0.38, color=colour, label=label)
        ax.bar_label(bars, labels=[fmt(v) for v in vals], padding=3, fontsize=9)
    ax.set_xticks(x, groups)
    ax.legend(frameon=True)


def _annotate_reduction(ax: Axes, gg: Sequence[float], nv: Sequence[float]) -> None:
    """Print the graph-guided saving (``-NN%``) above each group."""
    for i in range(len(gg)):
        ax.text(
            i,
            max(gg[i], nv[i]) * 1.12,
            f"-{chart_data.reduction(gg[i], nv[i])}%",
            ha="center",
            color=GG,
            fontweight="bold",
        )


def fig_tokens() -> Figure:
    """Input-token bars: keyless + keyed, with the % reduction annotated per group."""
    runs = {"Keyless": chart_data.keyless_run(), "Keyed (live)": chart_data.keyed_run()}
    groups = list(runs)
    gg = [runs[g]["graph_guided"]["input"] for g in groups]
    nv = [runs[g]["naive"]["input"] for g in groups]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    _grouped_bars(ax, groups, gg, nv, lambda v: f"{int(v)}")
    _annotate_reduction(ax, gg, nv)
    ax.set_ylabel("Input tokens into the LLM")
    ax.set_title("Graph-guided cuts the input context vs the naive dump")
    fig.tight_layout()
    return fig


def fig_cost() -> Figure:
    """USD cost bars: keyless + keyed, % cheaper annotated per group."""
    runs = {"Keyless": chart_data.keyless_run(), "Keyed (live)": chart_data.keyed_run()}
    groups = list(runs)
    gg = [runs[g]["graph_guided"]["cost"] for g in groups]
    nv = [runs[g]["naive"]["cost"] for g in groups]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    _grouped_bars(ax, groups, gg, nv, lambda v: f"${v:.4f}")
    _annotate_reduction(ax, gg, nv)
    ax.set_ylabel("Cost (USD) — tokens x config pricing")
    ax.set_title("Graph-guided is cheaper per fix run")
    fig.tight_layout()
    return fig


def fig_roc() -> Figure:
    """Bug-localization ROC: composite (hot.md) vs raw-centrality node rankings."""
    curves = chart_data.roc_curves()
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    names = {
        "composite": ("centrality x proximity (hot.md)", GG),
        "centrality": ("raw centrality", "#f59e0b"),
    }
    for name, (label, colour) in names.items():
        fpr, tpr, auc = curves[name]
        ax.plot(fpr, tpr, color=colour, lw=2.4, marker="o", ms=3, label=f"{label} — AUC {auc:.2f}")
    ax.plot([0, 1], [0, 1], "--", color="#cbd5e1", lw=1, label="chance — AUC 0.50")
    ax.set_xlabel("False-positive rate")
    ax.set_ylabel("True-positive rate")
    ax.set_title("Ranking surfaces the buggy file (polygons.py)")
    ax.legend(loc="lower right", frameon=True, fontsize=9)
    fig.tight_layout()
    return fig


def main() -> None:
    _style()
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    builders = {
        "token_comparison": fig_tokens,
        "cost_comparison": fig_cost,
        "bug_localization_roc": fig_roc,
    }
    for name, builder in builders.items():
        path = IMG_DIR / f"{name}.png"
        builder().savefig(path, bbox_inches="tight")
        print("wrote", path)


if __name__ == "__main__":
    main()
