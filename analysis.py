"""
analysis.py
───────────
Performance & Comparative Analysis for All-to-All Personalized Communication.
Generates a summary table and a bar chart comparing Ring, 2D Mesh, and Hypercube.
"""

import math
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from tabulate import tabulate


def compute_metrics(p: int) -> list[dict]:
    """
    Compute theoretical performance metrics for each topology.
    """
    side = int(math.isqrt(p))
    d = int(math.log2(p))

    metrics = [
        {
            "Topology":       "Ring",
            "Steps":          p - 1,
            "Complexity":     "O(p)",
            "Type":           "Linear",
            "Why":            "Simple but slow for many nodes.",
        },
        {
            "Topology":       "2D Mesh",
            "Steps":          2 * (side - 1),
            "Complexity":     "O(sqrt(p))",
            "Type":           "Square Root",
            "Why":            "Better than ring; splits work into rows/columns.",
        },
        {
            "Topology":       "Hypercube",
            "Steps":          d,
            "Complexity":     "O(log2(p))",
            "Type":           "Logarithmic",
            "Why":            "Fastest steps, but high traffic on links.",
        },
    ]
    return metrics


def print_summary_table(p: int):
    """Print a formatted comparison table to the console."""
    metrics = compute_metrics(p)

    headers = ["Topology", "Steps Counted", "Complexity Logic", "Type", "Why?"]
    rows = []
    for m in metrics:
        rows.append([m["Topology"], m["Steps"], m["Complexity"],
                      m["Type"], m["Why"]])

    print("\n" + "=" * 90)
    print(f"  PERFORMANCE COMPARISON  –  All-to-All Personalized Communication  (p = {p})")
    print("=" * 90)
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid",
                   numalign="center", stralign="left"))
    print()


def plot_comparison_bar_chart(p: int, save_path: str = None):
    """
    Generate a bar chart comparing communication steps across topologies.
    Also plots scaling curves for multiple values of p.
    """
    metrics = compute_metrics(p)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor="#1A1A2E")

    # ── LEFT: Bar chart for current p ─────────────────────
    ax1 = axes[0]
    ax1.set_facecolor("#16213E")

    names = [m["Topology"] for m in metrics]
    steps_vals = [m["Steps"] for m in metrics]
    colors = ["#E74C3C", "#F39C12", "#2ECC71"]
    bar_edge = ["#C0392B", "#E67E22", "#27AE60"]

    bars = ax1.bar(names, steps_vals, color=colors, edgecolor=bar_edge,
                   linewidth=2, width=0.5, zorder=3)

    # Value labels on bars
    for bar, val in zip(bars, steps_vals):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 str(val), ha="center", va="bottom", fontsize=14,
                 fontweight="bold", color="#ECF0F1", fontfamily="monospace")

    ax1.set_title(f"Communication Steps  (p = {p})", fontsize=14,
                  fontweight="bold", color="#ECF0F1", fontfamily="monospace")
    ax1.set_ylabel("Number of Steps", fontsize=12, color="#ECF0F1")
    ax1.tick_params(colors="#ECF0F1", labelsize=11)
    ax1.spines["bottom"].set_color("#566573")
    ax1.spines["left"].set_color("#566573")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.grid(axis="y", alpha=0.2, color="#566573")

    # ── RIGHT: Scaling curves ─────────────────────────────
    ax2 = axes[1]
    ax2.set_facecolor("#16213E")

    # Powers of 2 that are also perfect squares (for mesh)
    p_values = [4, 16, 64, 256, 1024]
    ring_steps   = [pv - 1 for pv in p_values]
    mesh_steps   = [2 * (int(math.isqrt(pv)) - 1) for pv in p_values]
    hyper_steps  = [int(math.log2(pv)) for pv in p_values]

    ax2.plot(p_values, ring_steps, "o-", color="#E74C3C", linewidth=2.5,
             markersize=8, label="Ring  O(p)", zorder=3)
    ax2.plot(p_values, mesh_steps, "s-", color="#F39C12", linewidth=2.5,
             markersize=8, label="Mesh  O(√p)", zorder=3)
    ax2.plot(p_values, hyper_steps, "D-", color="#2ECC71", linewidth=2.5,
             markersize=8, label="Hypercube  O(log p)", zorder=3)

    ax2.set_title("Scaling Comparison", fontsize=14,
                  fontweight="bold", color="#ECF0F1", fontfamily="monospace")
    ax2.set_xlabel("Number of Nodes (p)", fontsize=12, color="#ECF0F1")
    ax2.set_ylabel("Communication Steps", fontsize=12, color="#ECF0F1")
    ax2.set_xscale("log", base=2)
    ax2.set_yscale("log", base=2)
    ax2.tick_params(colors="#ECF0F1", labelsize=10)
    ax2.spines["bottom"].set_color("#566573")
    ax2.spines["left"].set_color("#566573")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(alpha=0.2, color="#566573")
    ax2.legend(fontsize=10, facecolor="#16213E", edgecolor="#1ABC9C",
               labelcolor="#ECF0F1")

    plt.tight_layout(pad=2)

    if save_path:
        fig.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(),
                    bbox_inches="tight")
        print(f"  Chart saved to: {save_path}")

    plt.show()


def plot_traffic_analysis(p: int):
    """
    Additional chart: per-step message traffic volume comparison.
    """
    side = int(math.isqrt(p))
    d = int(math.log2(p))
    m = 1024  # message size in bytes

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#1A1A2E")
    ax.set_facecolor("#16213E")

    # Ring: each step, p messages of size m travel
    # Mesh: Phase 1 – each step p msgs of size m; Phase 2 same
    # Hypercube: step j – p/2 exchanges, each of size m * 2^j (doubling)

    topologies = ["Ring", "2D Mesh", "Hypercube"]
    # Total data moved (bytes)
    ring_total   = (p - 1) * p * m
    mesh_total   = 2 * (side - 1) * p * m
    hyper_total  = sum(p // 2 * (p // (2 ** (j + 1))) * m * 2 for j in range(d))
    # Simplified: just show total messages exchanged across all steps
    ring_msgs  = (p - 1) * p
    mesh_msgs  = 2 * (side - 1) * p
    hyper_msgs = d * (p // 2)  # pairs per step

    totals = [ring_msgs, mesh_msgs, hyper_msgs]
    colors = ["#E74C3C", "#F39C12", "#2ECC71"]

    bars = ax.bar(topologies, totals, color=colors, edgecolor="white",
                  linewidth=1.5, width=0.45, zorder=3)

    for bar, val in zip(bars, totals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(totals) * 0.02,
                str(val), ha="center", va="bottom", fontsize=13,
                fontweight="bold", color="#ECF0F1", fontfamily="monospace")

    ax.set_title(f"Total Link Transfers  (p = {p}, m = {m} B)", fontsize=14,
                 fontweight="bold", color="#ECF0F1", fontfamily="monospace")
    ax.set_ylabel("Total Message Transfers", fontsize=12, color="#ECF0F1")
    ax.tick_params(colors="#ECF0F1", labelsize=11)
    ax.spines["bottom"].set_color("#566573")
    ax.spines["left"].set_color("#566573")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.2, color="#566573")

    plt.tight_layout()
    plt.show()
