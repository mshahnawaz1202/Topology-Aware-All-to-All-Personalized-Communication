"""
algorithms.py
─────────────
All-to-All Personalized Communication algorithms for Ring, 2D Mesh, and Hypercube.

Each algorithm returns a list of "steps", where each step is a list of
(source, destination, messages) tuples describing what travels on each edge
during that communication round.

Message format:  msg[i][j]  =  f"m{i}→{j}"
    means "message originating at node i, destined for node j".
"""

import math
from topologies import node_to_rc, rc_to_node

MSG_SIZE = 1024  # bytes (default)


def _init_messages(p: int) -> dict[int, dict[int, list[str]]]:
    """
    Initialize message buffers.
    Each node i holds p-1 messages: one for every other node j.
    Returns dict:  node -> { dest_node: [msg_labels] }
    """
    buffers = {}
    for i in range(p):
        buffers[i] = {}
        for j in range(p):
            if i != j:
                buffers[i][j] = [f"m{i}→{j}"]
    return buffers


# ═══════════════════════════════════════════════
#  RING  –  (p-1)-step Shift Algorithm
# ═══════════════════════════════════════════════
def ring_all_to_all(p: int):
    """
    Ring shift algorithm for all-to-all personalized communication.

    In step k (k = 1 .. p-1):
        Node i sends the message destined for node (i+k) mod p
        to its clockwise neighbour (i+1) mod p.
        Messages travel hop-by-hop around the ring.

    Returns
    -------
    steps : list[list[tuple(src, dst, list[str])]]
        Each element is one communication round.
    total_steps : int
    """
    # buffers[node] = { final_dest: [msg_labels] }
    buffers = _init_messages(p)
    steps = []

    for k in range(1, p):
        round_transfers = []
        # In step k, every node i sends the message for destination (i+k)%p
        # to neighbour (i+1)%p
        new_buffers = {i: {} for i in range(p)}

        for i in range(p):
            target_dest = (i + k) % p          # final destination of the message
            neighbour   = (i + 1) % p           # next hop (clockwise)

            # Find messages at node i destined for target_dest
            msgs = buffers[i].get(target_dest, [])
            if msgs:
                round_transfers.append((i, neighbour, list(msgs)))

            # Move all messages that are NOT for target_dest into new_buffers
            for dest, m_list in buffers[i].items():
                if dest == target_dest:
                    # This message moves to neighbour
                    new_buffers[neighbour].setdefault(dest, []).extend(m_list)
                else:
                    # stays (or is the node's own received msgs)
                    new_buffers[i].setdefault(dest, []).extend(m_list)

        buffers = new_buffers
        steps.append(round_transfers)

    return steps, p - 1


# ═══════════════════════════════════════════════
#  2D MESH  –  Two-Phase Row/Column Routing
# ═══════════════════════════════════════════════
def mesh_all_to_all(p: int):
    """
    Two-phase all-to-all personalized communication on sqrt(p)×sqrt(p) mesh.

    Phase 1 – Row-wise:
        Within each row, nodes perform all-to-all to gather messages
        destined for their target column.  (sqrt(p)-1 steps)

    Phase 2 – Column-wise:
        Within each column, nodes perform all-to-all to deliver
        messages to the final destination.    (sqrt(p)-1 steps)

    Total steps = 2 * (sqrt(p) - 1)

    Returns
    -------
    steps : list[list[tuple(src, dst, list[str])]]
    total_steps : int
    phase_boundary : int   (index where Phase 2 begins)
    """
    side = int(math.isqrt(p))
    assert side * side == p

    # buffers[node] = { final_dest: [msg_labels] }
    buffers = _init_messages(p)
    steps = []

    # ── Phase 1: Row-wise exchange ──────────────────
    for k in range(1, side):
        round_transfers = []
        new_buffers = {i: {} for i in range(p)}

        for r in range(side):
            for c in range(side):
                node = rc_to_node(r, c, side)
                target_col = (c + k) % side
                neighbour  = rc_to_node(r, (c + 1) % side, side)  # right neighbour in row

                # Collect messages whose final destination is in target_col
                send_msgs = []
                keep = {}
                for dest, m_list in buffers[node].items():
                    dest_r, dest_c = node_to_rc(dest, side)
                    if dest_c == target_col:
                        send_msgs.extend(m_list)
                        # route to the right neighbour
                        new_buffers[neighbour].setdefault(dest, []).extend(m_list)
                    else:
                        new_buffers[node].setdefault(dest, []).extend(m_list)

                if send_msgs:
                    round_transfers.append((node, neighbour, send_msgs))

        buffers = new_buffers
        steps.append(round_transfers)

    phase_boundary = len(steps)

    # ── Phase 2: Column-wise exchange ───────────────
    for k in range(1, side):
        round_transfers = []
        new_buffers = {i: {} for i in range(p)}

        for r in range(side):
            for c in range(side):
                node = rc_to_node(r, c, side)
                target_row = (r + k) % side
                neighbour  = rc_to_node((r + 1) % side, c, side)  # down neighbour

                send_msgs = []
                for dest, m_list in buffers[node].items():
                    dest_r, dest_c = node_to_rc(dest, side)
                    if dest_r == target_row:
                        send_msgs.extend(m_list)
                        new_buffers[neighbour].setdefault(dest, []).extend(m_list)
                    else:
                        new_buffers[node].setdefault(dest, []).extend(m_list)

                if send_msgs:
                    round_transfers.append((node, neighbour, send_msgs))

        buffers = new_buffers
        steps.append(round_transfers)

    total_steps = 2 * (side - 1)
    return steps, total_steps, phase_boundary


# ═══════════════════════════════════════════════
#  HYPERCUBE  –  Dimension-Ordered Routing
# ═══════════════════════════════════════════════
def hypercube_all_to_all(p: int):
    """
    Dimension-ordered all-to-all personalized communication on a d-dim hypercube.

    In step j (j = 0 .. d-1), every node exchanges a bundle of packed
    messages across the j-th dimension.  After each step, bundled
    message sizes double as nodes aggregate data.

    Total steps = d = log2(p)

    Returns
    -------
    steps : list[list[tuple(src, dst, list[str])]]
    total_steps : int
    """
    d = int(math.log2(p))
    assert 2 ** d == p

    # buffers[node] = { final_dest : [msg_labels] }
    buffers = _init_messages(p)
    steps = []

    for j in range(d):
        round_transfers = []
        new_buffers = {i: {} for i in range(p)}

        for i in range(p):
            partner = i ^ (1 << j)  # flip bit j

            # Determine which messages should go to the partner side.
            # After communication along dimension j, node i should hold
            # all messages whose destination matches i in bit j.
            send_msgs = []
            for dest, m_list in buffers[i].items():
                if (dest >> j) & 1 != (i >> j) & 1:
                    # This message needs to cross dimension j
                    send_msgs.extend(m_list)
                    new_buffers[partner].setdefault(dest, []).extend(m_list)
                else:
                    new_buffers[i].setdefault(dest, []).extend(m_list)

            if send_msgs:
                round_transfers.append((i, partner, send_msgs))

        buffers = new_buffers
        steps.append(round_transfers)

    return steps, d
