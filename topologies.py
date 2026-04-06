"""
topologies.py
─────────────
Topology Construction for Ring, 2D Mesh, and Hypercube networks.
Uses NetworkX for graph logic and provides layout positions for visualization.
"""

import math
import networkx as nx
import numpy as np


# ──────────────────────────────────────────────
#  RING TOPOLOGY
# ──────────────────────────────────────────────
def build_ring(p: int) -> tuple[nx.Graph, dict]:
    """
    Build a ring topology with p nodes.
    Node i is connected to (i+1) mod p.

    Returns:
        G   – NetworkX Graph
        pos – dict mapping node -> (x, y) position (circular layout)
    """
    G = nx.Graph()
    G.add_nodes_from(range(p))
    for i in range(p):
        G.add_edge(i, (i + 1) % p)

    # Circular layout: place nodes evenly on a circle
    pos = {}
    for i in range(p):
        angle = 2 * math.pi * i / p - math.pi / 2  # start from top
        pos[i] = (math.cos(angle), math.sin(angle))
    return G, pos


# ──────────────────────────────────────────────
#  2D MESH TOPOLOGY
# ──────────────────────────────────────────────
def build_mesh(p: int) -> tuple[nx.Graph, dict]:
    """
    Build a sqrt(p) x sqrt(p) 2D mesh topology.
    Each node (r, c) connects to neighbors in its row and column.

    Returns:
        G   – NetworkX Graph  (node labels 0 .. p-1)
        pos – dict mapping node -> (x, y) on a grid
    """
    side = int(math.isqrt(p))
    assert side * side == p, f"p={p} is not a perfect square."

    G = nx.Graph()
    G.add_nodes_from(range(p))

    for r in range(side):
        for c in range(side):
            node = r * side + c
            # Right neighbor
            if c + 1 < side:
                G.add_edge(node, r * side + (c + 1))
            # Bottom neighbor
            if r + 1 < side:
                G.add_edge(node, (r + 1) * side + c)

    # Grid layout – (col, -row) so top-left is (0, 0)
    pos = {}
    for r in range(side):
        for c in range(side):
            node = r * side + c
            pos[node] = (c, -r)
    return G, pos


# ──────────────────────────────────────────────
#  HYPERCUBE TOPOLOGY
# ──────────────────────────────────────────────
def build_hypercube(p: int) -> tuple[nx.Graph, dict]:
    """
    Build a d-dimensional hypercube where p = 2^d.
    Nodes are connected if their binary IDs differ by exactly one bit.

    Returns:
        G   – NetworkX Graph
        pos – dict mapping node -> (x, y)
    """
    d = int(math.log2(p))
    assert 2 ** d == p, f"p={p} is not a power of 2."

    G = nx.Graph()
    G.add_nodes_from(range(p))

    for i in range(p):
        for bit in range(d):
            neighbor = i ^ (1 << bit)
            if neighbor > i:  # avoid duplicate edges
                G.add_edge(i, neighbor)

    # Use a spring layout for nice hypercube visualization
    if d <= 3:
        # For small dimensions use a custom layout
        pos = _hypercube_layout(d)
    else:
        pos = nx.spring_layout(G, seed=42, iterations=200)

    return G, pos


def _hypercube_layout(d: int) -> dict:
    """Custom layout for 1D, 2D, and 3D hypercubes."""
    p = 2 ** d
    pos = {}
    if d == 1:
        pos = {0: (-1, 0), 1: (1, 0)}
    elif d == 2:
        pos = {0: (-1, -1), 1: (1, -1), 2: (-1, 1), 3: (1, 1)}
    elif d == 3:
        # Inner and outer squares
        offset = 0.4
        pos = {
            0: (-1, -1),
            1: (1, -1),
            2: (-1, 1),
            3: (1, 1),
            4: (-1 + offset, -1 + offset),
            5: (1 - offset, -1 + offset),
            6: (-1 + offset, 1 - offset),
            7: (1 - offset, 1 - offset),
        }
    return pos


# ──────────────────────────────────────────────
#  HELPER: Node ↔ (row, col) for Mesh
# ──────────────────────────────────────────────
def node_to_rc(node: int, side: int) -> tuple[int, int]:
    """Convert linear node id to (row, col)."""
    return divmod(node, side)


def rc_to_node(r: int, c: int, side: int) -> int:
    """Convert (row, col) to linear node id."""
    return r * side + c
