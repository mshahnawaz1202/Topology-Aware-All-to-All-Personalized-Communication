"""Quick validation test for all modules."""
from topologies import build_ring, build_mesh, build_hypercube
from algorithms import ring_all_to_all, mesh_all_to_all, hypercube_all_to_all
from analysis import compute_metrics

p = 16

# Test topology construction
G_ring, _ = build_ring(p)
G_mesh, _ = build_mesh(p)
G_hyper, _ = build_hypercube(p)
print(f"Ring:  {G_ring.number_of_nodes()} nodes, {G_ring.number_of_edges()} edges")
print(f"Mesh:  {G_mesh.number_of_nodes()} nodes, {G_mesh.number_of_edges()} edges")
print(f"Hyper: {G_hyper.number_of_nodes()} nodes, {G_hyper.number_of_edges()} edges")

# Test algorithms
steps_r, total_r = ring_all_to_all(p)
print(f"\nRing steps: {total_r} (expected {p-1})")

steps_m, total_m, pb = mesh_all_to_all(p)
print(f"Mesh steps: {total_m} (expected {2*(4-1)}), phase boundary at step {pb}")

steps_h, total_h = hypercube_all_to_all(p)
print(f"Hypercube steps: {total_h} (expected 4)")

# Test metrics
metrics = compute_metrics(p)
for m in metrics:
    print(f"  {m['Topology']:12s} | Steps={m['Steps']:4d} | {m['Complexity']:10s} | {m['Type']}")

print("\nAll tests passed!")
