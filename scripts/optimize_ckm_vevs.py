#!/usr/bin/env python3
"""Try to lower the CKM error by perturbing the best H27 vertex pair.

Reads the results computed by w33_yukawa_blocks.py (data/w33_yukawa_blocks.json)
and performs a small search around the best up/down vertices.

The algorithm is deliberately simple: for each neighbour of the best
vertex (in the H27 adjacency graph) we form a linear combination
v' = (1-eps)*e_i + eps*e_j with eps in a small grid, and likewise for the
down-type vertex.  We then recompute the CKM error and report any
improvement.

Usage:
    python scripts/optimize_ckm_vevs.py
"""

from __future__ import annotations

import json
import os
import sys
from itertools import product

import numpy as np

# adjust path to import repository modules
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)
sys.path.insert(0, os.path.dirname(__file__))

from w33_ckm_from_vev import (_build_hodge_and_generations,
                             build_generation_profiles,
                             cubic_form_on_h27,
                             compute_ckm_and_jarlskog)
from e8_embedding_group_theoretic import build_w33


def ckme(v_up, v_dn, X_profiles, local_tris):
    Y_u = np.zeros((3, 3), dtype=complex)
    Y_d = np.zeros((3, 3), dtype=complex)
    for a in range(3):
        for b in range(a, 3):
            Y_u[a, b] = Y_u[b, a] = cubic_form_on_h27(None, local_tris, X_profiles[a], X_profiles[b], v_up)
            Y_d[a, b] = Y_d[b, a] = cubic_form_on_h27(None, local_tris, X_profiles[a], X_profiles[b], v_dn)
    V, J = compute_ckm_and_jarlskog(Y_u, Y_d)
    # experimental CKM from w33_yukawa_blocks
    Vexp = np.array([
        [0.97373, 0.2243, 0.00382],
        [0.2210, 0.987, 0.0410],
        [0.0080, 0.0388, 1.013],
    ])
    err = float(np.linalg.norm(np.abs(V) - Vexp))
    return err, V, J


def main():
    # load previous results
    with open("data/w33_yukawa_blocks.json") as f:
        data = json.load(f)
    best = data.get("vertex_scan_best")
    if best is None:
        print("No vertex scan results found; run w33_yukawa_blocks.py first.")
        return
    vi = best["vi_up"]
    vj = best["vj_down"]

    # build H27 adjacency to walk neighbours
    n, vertices, adj, edges = build_w33()
    v0 = 0
    neighbours_v0 = set(adj[v0])
    H27_idx = [i for i in range(n) if i != v0 and i not in neighbours_v0]
    h27_set = set(H27_idx)
    # adjacency within H27
    h27_adj = {i: [] for i in H27_idx}
    for u in H27_idx:
        for w in adj[u]:
            if w in h27_set:
                h27_adj[u].append(w)

    print(f"Best up-index = {vi}, down-index = {vj}")
    print("Neighbours up:", h27_adj[H27_idx[vi]])
    print("Neighbours down:", h27_adj[H27_idx[vj]])

    # prepare Hodge/gen data
    H, triangles, edges, gens = _build_hodge_and_generations()
    H27, local_tris, X_profiles = build_generation_profiles(H, edges, gens, v0=0)

    # initial error
    v_up0 = np.zeros(27); v_up0[vi] = 1.0
    v_dn0 = np.zeros(27); v_dn0[vj] = 1.0
    err0, _, _ = ckme(v_up0, v_dn0, X_profiles, local_tris)
    print(f"baseline CKM error = {err0:.6f}")

    best_err = err0
    best_pair = (vi, vj)
    best_combo = (v_up0.copy(), v_dn0.copy())

    # try simple neighbour mixtures
    eps_values = [0.1, 0.2, 0.3, 0.5]
    for nei_i in h27_adj[H27_idx[vi]]:
        for eps in eps_values:
            v_up = (1 - eps) * v_up0 + eps * np.eye(27)[H27_idx.index(nei_i)]
            for nei_j in h27_adj[H27_idx[vj]]:
                for eps2 in eps_values:
                    v_dn = (1 - eps2) * v_dn0 + eps2 * np.eye(27)[H27_idx.index(nei_j)]
                    err, V, J = ckme(v_up, v_dn, X_profiles, local_tris)
                    if err < best_err:
                        best_err = err
                        best_pair = (nei_i, nei_j)
                        best_combo = (v_up.copy(), v_dn.copy())
                        print(f"improved err {err:.6f} with neighbors {nei_i},{nei_j} eps {eps},{eps2}")
    print("search complete")
    print("best error", best_err, "for up/down", best_pair)
    print("initial error", err0)

if __name__ == "__main__":
    main()
