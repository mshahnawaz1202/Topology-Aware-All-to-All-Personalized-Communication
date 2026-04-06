"""
main.py
───────
Topology-Aware All-to-All Personalized Communication
=====================================================
Entry point that ties together topology construction, algorithm execution,
animated visualization, and performance analysis.

Usage:
    python main.py                  # Interactive menu (default p=16)
    python main.py --p 16           # Set node count
    python main.py --run all        # Run everything non-interactively
    python main.py --run ring       # Only ring visualization
    python main.py --run mesh       # Only mesh visualization
    python main.py --run hypercube  # Only hypercube visualization
    python main.py --run analysis   # Only analysis charts
    python main.py --run static     # Only static topology views
"""

import argparse
import math
import sys
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from topologies import build_ring, build_mesh, build_hypercube
from algorithms import ring_all_to_all, mesh_all_to_all, hypercube_all_to_all
from visualizer import animate_topology, draw_topology_static
from analysis import print_summary_table, plot_comparison_bar_chart, plot_traffic_analysis


BANNER = r"""
╔══════════════════════════════════════════════════════════════════════╗
║     TOPOLOGY-AWARE ALL-TO-ALL PERSONALIZED COMMUNICATION           ║
║                      (Total Exchange)                              ║
║──────────────────────────────────────────────────────────────────── ║
║  Topologies:  Ring  ·  2D Mesh  ·  Hypercube                       ║
║  Algorithm :  Shift · Two-Phase · Dimension-Ordered                ║
╚══════════════════════════════════════════════════════════════════════╝
"""


def validate_p(p: int):
    """Ensure p is a power of 2 and a perfect square (for mesh)."""
    if p < 4:
        print("Error: p must be >= 4.")
        sys.exit(1)
    d = math.log2(p)
    if d != int(d):
        print(f"Error: p={p} is not a power of 2.")
        sys.exit(1)
    side = math.isqrt(p)
    if side * side != p:
        print(f"Error: p={p} is not a perfect square (required for 2D Mesh).")
        sys.exit(1)
    print(f"  ✓ p = {p}  (d = {int(d)},  mesh = {side}×{side})")


def show_static_topologies(p):
    """Display all three topologies side by side."""
    G_ring, pos_ring   = build_ring(p)
    G_mesh, pos_mesh   = build_mesh(p)
    G_hyper, pos_hyper = build_hypercube(p)

    fig, axes = plt.subplots(1, 3, figsize=(20, 7), facecolor="#1A1A2E")
    fig.suptitle(f"Interconnection Topologies  (p = {p})", fontsize=16,
                 fontweight="bold", color="#ECF0F1", fontfamily="monospace", y=0.98)

    draw_topology_static(G_ring,  pos_ring,  f"Ring  (p = {p})",  ax=axes[0])
    draw_topology_static(G_mesh,  pos_mesh,  f"2D Mesh  ({int(math.isqrt(p))}×{int(math.isqrt(p))})", ax=axes[1])
    draw_topology_static(G_hyper, pos_hyper, f"Hypercube  (d = {int(math.log2(p))})", ax=axes[2])

    plt.tight_layout()
    plt.show()


def run_ring(p):
    """Build ring, run algorithm, animate."""
    print("\n  ─── RING TOPOLOGY ───")
    G, pos = build_ring(p)
    steps, total = ring_all_to_all(p)
    print(f"  Algorithm: {p-1}-step Shift")
    print(f"  Total communication steps: {total}")
    print(f"  Animating {len(steps)} steps...")
    animate_topology(G, pos, steps,
                     title=f"Ring All-to-All  (p={p},  steps={total})")


def run_mesh(p):
    """Build mesh, run algorithm, animate."""
    side = int(math.isqrt(p))
    print(f"\n  ─── 2D MESH TOPOLOGY ({side}×{side}) ───")
    G, pos = build_mesh(p)
    steps, total, phase_b = mesh_all_to_all(p)
    print(f"  Algorithm: Two-Phase Row/Column Routing")
    print(f"  Phase 1 (Row):  {side - 1} steps")
    print(f"  Phase 2 (Col):  {side - 1} steps")
    print(f"  Total steps: {total}")
    print(f"  Animating {len(steps)} steps...")
    animate_topology(G, pos, steps,
                     title=f"2D Mesh All-to-All  ({side}×{side},  steps={total})",
                     phase_boundary=phase_b)


def run_hypercube(p):
    """Build hypercube, run algorithm, animate."""
    d = int(math.log2(p))
    print(f"\n  ─── HYPERCUBE TOPOLOGY (d={d}) ───")
    G, pos = build_hypercube(p)
    steps, total = hypercube_all_to_all(p)
    print(f"  Algorithm: Dimension-Ordered Exchange")
    print(f"  Total communication steps: {total}")
    print(f"  Animating {len(steps)} steps...")
    animate_topology(G, pos, steps,
                     title=f"Hypercube All-to-All  (d={d}, p={p},  steps={total})")


def run_analysis(p):
    """Print table and show charts."""
    print("\n  ─── PERFORMANCE & COMPARATIVE ANALYSIS ───")
    print_summary_table(p)
    plot_comparison_bar_chart(p)
    plot_traffic_analysis(p)


def interactive_menu(p):
    """Interactive menu for choosing what to run."""
    while True:
        print("\n  ┌──────────────────────────────────────┐")
        print("  │         SELECT AN OPTION              │")
        print("  ├──────────────────────────────────────┤")
        print("  │  1.  View Static Topologies           │")
        print("  │  2.  Animate Ring (Shift Algorithm)   │")
        print("  │  3.  Animate 2D Mesh (Two-Phase)      │")
        print("  │  4.  Animate Hypercube (Dim-Ordered)  │")
        print("  │  5.  Performance Analysis & Charts    │")
        print("  │  6.  Run ALL (Sequential)             │")
        print("  │  0.  Exit                             │")
        print("  └──────────────────────────────────────┘")

        choice = input("  ➤  Enter choice: ").strip()

        if choice == "1":
            show_static_topologies(p)
        elif choice == "2":
            run_ring(p)
        elif choice == "3":
            run_mesh(p)
        elif choice == "4":
            run_hypercube(p)
        elif choice == "5":
            run_analysis(p)
        elif choice == "6":
            show_static_topologies(p)
            run_ring(p)
            run_mesh(p)
            run_hypercube(p)
            run_analysis(p)
        elif choice == "0":
            print("  Goodbye!")
            break
        else:
            print("  Invalid choice. Try again.")


def main():
    parser = argparse.ArgumentParser(
        description="Topology-Aware All-to-All Personalized Communication Visualizer"
    )
    parser.add_argument("--p", type=int, default=16,
                        help="Number of nodes (must be power of 2 AND perfect square). Default: 16")
    parser.add_argument("--run", type=str, default=None,
                        choices=["all", "ring", "mesh", "hypercube", "analysis", "static"],
                        help="Run a specific component non-interactively.")
    args = parser.parse_args()

    p = args.p

    print(BANNER)
    validate_p(p)

    if args.run is None:
        interactive_menu(p)
    elif args.run == "all":
        show_static_topologies(p)
        run_ring(p)
        run_mesh(p)
        run_hypercube(p)
        run_analysis(p)
    elif args.run == "ring":
        run_ring(p)
    elif args.run == "mesh":
        run_mesh(p)
    elif args.run == "hypercube":
        run_hypercube(p)
    elif args.run == "analysis":
        run_analysis(p)
    elif args.run == "static":
        show_static_topologies(p)


if __name__ == "__main__":
    main()
