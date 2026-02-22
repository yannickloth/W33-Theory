#!/usr/bin/env python3
"""Analyze unsat certificate linear combinations and map parity to H vertices."""
import json
from pathlib import Path

ART = Path(__file__).resolve().parents[1] / "artifacts"
cores = json.load(open(ART / "sign_unsat_cores.json", "r", encoding="utf-8"))
heis = json.load(
    open(ART / "e6_cubic_affine_heisenberg_model.json", "r", encoding="utf-8")
)
E6_TRIADS = [
    tuple(sorted(tri)) for item in heis["affine_u_lines"] for tri in item["triads"]
]
sdata = json.load(
    open(ART / "e6_cubic_sign_gauge_solution.json", "r", encoding="utf-8")
)
d_map = {
    tuple(sorted(t["triple"])): 0 if t["sign"] == 1 else 1
    for t in sdata["solution"]["d_triples"]
}
perm = json.load(open(ART / "triad_label_permutation.json", "r", encoding="utf-8"))[
    "mapping"
]
inv = {int(v): int(k) for k, v in perm.items()}

for entry in cores:
    print("\nCertificate from", entry["file"])
    cert = entry["certificate_rows"]
    # compute left-hand parity across 27 nodes
    node_parity = [0] * 27
    rhs_sum = 0
    for tri in cert:
        tri_t = tuple(sorted(tri))
        rhs_sum ^= d_map.get(tri_t, 0)
        for v in tri_t:
            node_parity[v] ^= 1
    odd_nodes = [i for i, p in enumerate(node_parity) if p]
    print("  RHS parity (mod2):", rhs_sum)
    print("  Odd-node count:", len(odd_nodes), "Odd nodes:", odd_nodes)
    # map cert triads to H triangles
    hcert = [tuple(sorted([inv[t] for t in tri])) for tri in cert]
    # check H-vertex parity
    hnode_parity = {}
    for htri in hcert:
        for hv in htri:
            hnode_parity[hv] = (hnode_parity.get(hv, 0) + 1) % 2
    odd_hnodes = sorted([h for h, p in hnode_parity.items() if p])
    print("  Odd H-vertices (mod2):", odd_hnodes)

print("\nDone")
