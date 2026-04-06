"""
visualizer.py
─────────────
Animated visualization of All-to-All Personalized Communication
on Ring, 2D Mesh, and Hypercube topologies using Matplotlib.

Colored "packets" travel along edges during each communication step.
"""

import math
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation

# ── Color palette for packet animation ──────────────────
PACKET_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
    "#F1948A", "#82E0AA", "#F8C471", "#AED6F1", "#D7BDE2",
    "#A3E4D7",
]

NODE_COLOR       = "#2C3E50"
NODE_EDGE_COLOR  = "#1ABC9C"
EDGE_COLOR       = "#566573"
BG_COLOR         = "#1A1A2E"
TEXT_COLOR        = "#ECF0F1"
PHASE_COLORS     = {"Phase 1 (Row)": "#E74C3C", "Phase 2 (Col)": "#3498DB"}


def _lerp(a, b, t):
    """Linear interpolation between points a and b."""
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def animate_topology(G, pos, steps, title, phase_boundary=None,
                     interval=120, frames_per_step=20, figsize=(10, 8)):
    """
    Animate the all-to-all communication on a given topology.

    Parameters
    ----------
    G              : nx.Graph
    pos            : dict  {node: (x, y)}
    steps          : list of rounds, each round = [(src, dst, msgs), ...]
    title          : str
    phase_boundary : int or None  (for Mesh: step index where Phase 2 starts)
    interval       : ms between frames
    frames_per_step: animation smoothness
    figsize        : figure size
    """
    p = G.number_of_nodes()

    fig, ax = plt.subplots(figsize=figsize, facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)

    # Title
    ax.set_title(title, fontsize=16, fontweight="bold", color=TEXT_COLOR,
                 pad=15, fontfamily="monospace")

    # Draw edges
    for u, v in G.edges():
        x_vals = [pos[u][0], pos[v][0]]
        y_vals = [pos[u][1], pos[v][1]]
        ax.plot(x_vals, y_vals, color=EDGE_COLOR, linewidth=1.5,
                alpha=0.4, zorder=1)

    # Draw nodes
    node_size = max(300, 700 - p * 20)
    font_size = max(7, 12 - p // 4)
    for n in G.nodes():
        circle = plt.Circle(pos[n], 0.08, color=NODE_COLOR,
                            ec=NODE_EDGE_COLOR, linewidth=2, zorder=3)
        ax.add_patch(circle)
        ax.text(pos[n][0], pos[n][1], str(n), ha="center", va="center",
                fontsize=font_size, fontweight="bold", color=TEXT_COLOR, zorder=4)

    # Auto-scale axes
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    margin = 0.4
    ax.set_xlim(min(xs) - margin, max(xs) + margin)
    ax.set_ylim(min(ys) - margin, max(ys) + margin)

    # Step counter text
    step_text = ax.text(0.02, 0.96, "", transform=ax.transAxes,
                        fontsize=12, color="#F39C12", fontfamily="monospace",
                        verticalalignment="top", fontweight="bold")

    # Phase text (for mesh)
    phase_text = ax.text(0.98, 0.96, "", transform=ax.transAxes,
                         fontsize=11, color="#E74C3C", fontfamily="monospace",
                         verticalalignment="top", horizontalalignment="right",
                         fontweight="bold")

    # Legend
    legend_patches = [
        mpatches.Patch(color=NODE_EDGE_COLOR, label=f"Nodes (p={p})"),
        mpatches.Patch(color=PACKET_COLORS[0], label="Data packets"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=9,
              facecolor="#16213E", edgecolor="#1ABC9C", labelcolor=TEXT_COLOR)

    # Packet scatter (will be updated each frame)
    packet_dots = ax.scatter([], [], s=100, zorder=5, edgecolors="white", linewidth=0.5)

    # Total frames
    total_frames = len(steps) * frames_per_step + frames_per_step  # extra pause at end

    def update(frame):
        step_idx = min(frame // frames_per_step, len(steps) - 1)
        sub_frame = (frame % frames_per_step) / frames_per_step  # 0..1 progress

        if frame >= len(steps) * frames_per_step:
            # Final pause – show completion
            step_text.set_text(f"✓ Complete  |  {len(steps)} steps total")
            packet_dots.set_offsets(np.empty((0, 2)))
            phase_text.set_text("")
            return packet_dots, step_text, phase_text

        # Update step label
        step_text.set_text(f"Step {step_idx + 1} / {len(steps)}")

        # Update phase label for mesh
        if phase_boundary is not None:
            if step_idx < phase_boundary:
                phase_text.set_text("⬛ Phase 1: Row Sweep")
                phase_text.set_color("#E74C3C")
            else:
                phase_text.set_text("⬛ Phase 2: Column Sweep")
                phase_text.set_color("#3498DB")

        # Compute packet positions for this frame
        round_data = steps[step_idx]
        pkt_positions = []
        pkt_colors = []

        for idx, (src, dst, msgs) in enumerate(round_data):
            t = sub_frame
            # Ease-in-out for smoother animation
            t = t * t * (3 - 2 * t)

            px, py = _lerp(pos[src], pos[dst], t)

            # Slight offset so overlapping packets fan out
            offset = (idx % 5) * 0.015
            angle = idx * 0.7
            px += offset * math.cos(angle)
            py += offset * math.sin(angle)

            color = PACKET_COLORS[src % len(PACKET_COLORS)]
            pkt_positions.append([px, py])
            pkt_colors.append(color)

        if pkt_positions:
            packet_dots.set_offsets(np.array(pkt_positions))
            packet_dots.set_facecolors(pkt_colors)
            # Size based on number of messages
            sizes = [min(180, 60 + len(round_data[i][2]) * 8)
                     for i in range(len(round_data))]
            packet_dots.set_sizes(sizes)
        else:
            packet_dots.set_offsets(np.empty((0, 2)))

        return packet_dots, step_text, phase_text

    anim = FuncAnimation(fig, update, frames=total_frames,
                         interval=interval, blit=False, repeat=False)

    plt.tight_layout()
    plt.show()
    return anim


# ──────────────────────────────────────────────
#  Static topology snapshot (no animation)
# ──────────────────────────────────────────────
def draw_topology_static(G, pos, title, ax=None):
    """Draw a static view of the topology on a given axes."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG_COLOR)
        standalone = True
    else:
        standalone = False

    ax.set_facecolor(BG_COLOR)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=14, fontweight="bold",
                 color=TEXT_COLOR, fontfamily="monospace")

    # Edges
    for u, v in G.edges():
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                color=EDGE_COLOR, linewidth=1.5, alpha=0.5, zorder=1)

    # Nodes
    p = G.number_of_nodes()
    font_size = max(7, 12 - p // 4)
    for n in G.nodes():
        circle = plt.Circle(pos[n], 0.08, color=NODE_COLOR,
                            ec=NODE_EDGE_COLOR, linewidth=2, zorder=3)
        ax.add_patch(circle)
        ax.text(pos[n][0], pos[n][1], str(n), ha="center", va="center",
                fontsize=font_size, fontweight="bold", color=TEXT_COLOR, zorder=4)

    # Margins
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    margin = 0.35
    ax.set_xlim(min(xs) - margin, max(xs) + margin)
    ax.set_ylim(min(ys) - margin, max(ys) + margin)

    if standalone:
        plt.tight_layout()
        plt.show()
