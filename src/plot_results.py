"""Render the versioned figures from the saved calculation tables."""

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch
import numpy as np

from src.grid_support import AREAS, TURNS, read_csv


def save(figure, name, folder):
    folder.mkdir(exist_ok=True)
    figure.savefig(folder / f"{name}.png", facecolor="white", dpi=360)
    plt.close(figure)


def generate(data, figures):
    rows = read_csv(data / "all_1107_candidates.csv")
    comparison = read_csv(data / "baseline_vs_optimum.csv")
    summary = read_csv(data / "scenario_summary.csv")
    assert [(int(r["primary_turns"]), float(r["effective_area_cm2"])) for r in rows] == [
        (turns, area) for area in AREAS for turns in TURNS
    ]

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10.5, "axes.labelsize": 11,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "svg.fonttype": "none",
    })
    shape = (len(AREAS), len(TURNS))
    image_options = dict(origin="lower", aspect="auto", interpolation="nearest",
                         extent=(TURNS[0] - 12.5, TURNS[-1] + 12.5, AREAS[0] - .25, AREAS[-1] + .25))
    baseline, optimum = [r for r in comparison if r["scenario"] == "medium"]
    loss = np.array([float(r["total_medium_w"]) for r in rows]).reshape(shape)
    fig, ax = plt.subplots(figsize=(8.2, 5.0), layout="constrained")
    image = ax.imshow(loss, cmap="viridis", **image_options)
    assert np.array_equal(image.get_array(), loss)
    for row, marker, label in ((baseline, "o", "Baseline"), (optimum, "*", "Screened minimum")):
        ax.scatter(int(row["primary_turns"]), float(row["effective_area_cm2"]), marker=marker,
                   s=120 if marker == "*" else 55, c="white", edgecolors="#1E293B",
                   linewidths=1.0, label=label)
    ax.set(xlabel="Primary turns", ylabel="Effective core area (cm²)")
    ax.legend(loc="upper right", frameon=True, facecolor="white")
    fig.colorbar(image, ax=ax, label="Medium-scenario modelled loss (W)")
    save(fig, "medium_total_loss_heatmap", figures)

    flux_fails = np.array([r["flux_pass"] == "False" for r in rows]).reshape(shape)
    voltage_fails = np.array([r["voltage_pass"] == "False" for r in rows]).reshape(shape)
    combined = flux_fails.astype(int) + 2 * voltage_fails
    green, violet, orange, dark = "#BDDDCC", "#77548C", "#DF9D56", "#3F3541"
    fig, axes = plt.subplots(1, 3, figsize=(11.9, 4.6), sharey=True, layout="constrained")
    panels = (
        ("No-drop peak flux", flux_fails.astype(int), (green, violet), ("Passes", "Above 1.50 T")),
        ("Loaded terminal voltage", voltage_fails.astype(int), (green, orange), ("Passes", "Below 22.0 V")),
        ("Combined screening", combined, (green, violet, orange, dark),
         ("Passes both", "Fails flux only", "Fails voltage only", "Fails both")),
    )
    for ax, (title, array, colors, labels) in zip(axes, panels):
        image = ax.imshow(array, cmap=ListedColormap(colors),
                          norm=BoundaryNorm(np.arange(len(colors) + 1) - .5, len(colors)),
                          **image_options)
        assert np.array_equal(image.get_array(), array)
        ax.set(title=title, xlabel="Primary turns", xticks=[450, 600, 750, 900, 1100])
        ax.legend(handles=[Patch(facecolor=c, label=l) for c, l in zip(colors, labels)],
                  loc="upper left", fontsize=8, frameon=True, facecolor="white")
    axes[0].set_ylabel("Effective core area (cm²)")
    save(fig, "two_constraint_screening_heatmaps", figures)

    fields = ("copper_w", "eddy_medium_w", "hysteresis_medium_w", "total_medium_w")
    labels = ("Winding\ncopper", "Classical\neddy current", "Illustrative\nhysteresis", "Total")
    fig, ax = plt.subplots(figsize=(8.7, 4.35), layout="constrained")
    x = np.arange(len(fields))
    for row, offset, color in ((baseline, -.19, "#627990"), (optimum, .19, "#087569")):
        values = [float(row[field]) for field in fields]
        bars = ax.bar(x + offset, values, width=.36, label=row["case"], color=color)
        assert [bar.get_height() for bar in bars] == values
        ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=9)
    ax.set(xticks=x, xticklabels=labels, ylabel="Medium-scenario modelled loss (W)")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.08)
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=.2)
    ax.legend(loc="upper left")
    save(fig, "medium_baseline_vs_optimum_losses", figures)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.55), layout="constrained")
    names = [r["scenario"].title() for r in summary]
    positions = np.arange(len(names))
    for key, offset, label, color in (("baseline_total_w", -.19, "Baseline", "#627990"),
                                     ("total_w", .19, "Screened minimum", "#087569")):
        values = [float(r[key]) for r in summary]
        bars = axes[0].bar(positions + offset, values, width=.36, label=label, color=color)
        assert [bar.get_height() for bar in bars] == values
        axes[0].bar_label(bars, fmt="%.2f", padding=3, fontsize=8)
    axes[0].set(xticks=positions, xticklabels=names, xlabel="Coefficient scenario", ylabel="Total loss (W)")
    axes[0].set_ylim(0, axes[0].get_ylim()[1] * 1.15)
    axes[0].legend(loc="upper left")
    opt_x = [int(r["primary_turns"]) for r in summary]
    opt_y = [float(r["effective_area_cm2"]) for r in summary]
    points = axes[1].scatter(opt_x, opt_y, s=65, c=("#49618C", "#087569", "#A34E16"))
    assert np.array_equal(points.get_offsets(), np.column_stack((opt_x, opt_y)))
    coincident = {}
    for name, x, y in zip(names, opt_x, opt_y):
        coincident.setdefault((x, y), []).append(name)
    for (x, y), names_here in coincident.items():
        axes[1].annotate(" / ".join(names_here), (x, y), xytext=(8, 6), textcoords="offset points")
    axes[1].axvline(TURNS[0], color="#76879A", linestyle=":", linewidth=1.1)
    axes[1].set(xlabel="Primary turns of screened minimum", ylabel="Effective core area (cm²)",
                xlim=(TURNS[0] - 15, max(opt_x) + 100),
                ylim=(min(opt_y) - .8, max(opt_y) + .8))
    for ax in axes:
        ax.set_axisbelow(True)
        ax.grid(axis="y", alpha=.2)
    save(fig, "coefficient_scenario_comparison", figures)
    print("Verified heatmap cells, bar heights and scenario coordinates against the saved CSVs.")
