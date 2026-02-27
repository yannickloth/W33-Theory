#!/usr/bin/env python3
"""Solve sign-gauge linear system to enlarge phi lift subgroup.

The standard edge->root bijection maps 240 edges to E8 root vectors.  By
flipping the sign of some roots (gauge transformation) we may be able to
convert additional automorphisms of W33 into Weyl isometries, thus
increasing the size of the lift subgroup.

This script builds a linear system over GF(2) encoding the requirement that
for each selected group element $g$ the signed Gram matrix be invariant.  If
solutions exist they correspond to a vector of $\pm1$ signs for the 240
edges.  We try a variety of subsets of Aut(W33) and report the best result.

Outputs:
  - artifacts/sign_gauge.json  : the chosen sign vector (0/1 representation)
  - artifacts/edge_to_e8_root_with_sign_gauge.json : same map with roots
    negated according to the gauge.
  - printed summary giving the size of the lift subgroup before/after gauge

The default behaviour attempts to find a gauge valid for *all* group
elements; if that fails it falls back to a greedy search over those
individual elements which are gauge-liftable on their own.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# allow importing our tools package
import sys
sys.path.insert(0, str(ROOT))

from tools.compute_phi_lift_subgroup import (
    edges,
    edge_index,
    dot,
    compute_lift_for_roots,
    Gperms,
)  # type: ignore

# load canonical root list
orig_map = json.loads((ROOT / "artifacts" / "edge_to_e8_root.json").read_text())
edges_sorted = []
root_list = []
for k,v in orig_map.items():
    if not k.startswith("("):
        continue
    pair = tuple(int(x.strip()) for x in k.strip()[1:-1].split(","))
    if pair[0] < pair[1]:
        edges_sorted.append(pair)
        root_list.append(tuple(int(x) for x in v))

m = len(root_list)
assert m == 240

# precompute Gram
Gram = np.zeros((m, m), dtype=int)
for a in range(m):
    for b in range(m):
        Gram[a, b] = dot(root_list[a], root_list[b])

# we will need to convert vertex permutations (length 40) to edge
# permutations of size 240 using the same label_map logic from
# compute_phi_lift_subgroup.py
import networkx as nx
from scripts.e8_embedding_group_theoretic import build_w33

n, vertices, adj_list, edges40 = build_w33()
# adjacency graph on 40 vertices
G_adj = nx.Graph()
G_adj.add_nodes_from(range(40))
for i, nbrs in enumerate(adj_list):
    for j in nbrs:
        if i < j:
            G_adj.add_edge(i, j)
# graph on edges (same naming as global 'edges_sorted')
G_root = nx.Graph()
G_root.add_nodes_from(range(40))
for i, j in edges_sorted:
    if i < j:
        G_root.add_edge(i, j)

gm2 = nx.algorithms.isomorphism.GraphMatcher(G_adj, G_root)
label_map = next(gm2.isomorphisms_iter())
label_map_inv = {v: k for k, v in label_map.items()}

# helpers for linear system over GF(2)

def add_equation(basis: dict[int, tuple[int, int]], mask: int, rhs: int) -> bool:
    """Add equation mask*x = rhs to basis; returns False if inconsistent."""
    while mask:
        lead = mask.bit_length() - 1
        if lead in basis:
            prev_mask, prev_rhs = basis[lead]
            mask ^= prev_mask
            rhs ^= prev_rhs
        else:
            basis[lead] = (mask, rhs)
            return True
    # mask reduced to zero
    return rhs == 0


def solve_basis(basis: dict[int, tuple[int, int]]) -> List[int]:
    """Back-substitute to obtain one solution vector (free vars zero)."""
    sol = [0] * m
    for lead, (mask, rhs) in sorted(basis.items(), reverse=True):
        s = rhs
        other = mask & ~(1 << lead)
        while other:
            lb = (other & -other).bit_length() - 1
            s ^= sol[lb]
            other &= other - 1
        sol[lead] = s
    return sol


def solve_gauge_for_permutation(vert_perm: List[int]) -> Optional[List[int]]:
    """Return sign vector (0/1) making *this single* vertex permutation
    liftable after gauge, or None if impossible."""
    # convert to edge permutation
    edge_perm = []
    g_root = [label_map[vert_perm[label_map_inv[i]]] for i in range(40)]
    for i, j in edges_sorted:
        ni, nj = g_root[i], g_root[j]
        if ni < nj:
            edge_perm.append(edge_index[(ni, nj)])
        else:
            edge_perm.append(edge_index[(nj, ni)])
    # now solve constraints using edge_perm
    basis: dict[int, tuple[int, int]] = {}
    for a in range(m):
        for b in range(a + 1, m):
            A = Gram[a, b]
            B = Gram[edge_perm[a], edge_perm[b]]
            if A == B:
                continue
            if A == -B:
                mask = (1 << a) ^ (1 << b) ^ (1 << edge_perm[a]) ^ (1 << edge_perm[b])
                if not add_equation(basis, mask, 1):
                    return None
            else:
                return None
    return solve_basis(basis)


def solve_gauge_for_subset(indices: List[int]) -> Optional[List[int]]:
    """Solve together for a subset of group elements (by index in Gperms)."""
    basis: dict[int, tuple[int, int]] = {}
    for idx in indices:
        vert_perm = Gperms[idx]
        # convert to edge perm as above
        edge_perm = []
        g_root = [label_map[vert_perm[label_map_inv[i]]] for i in range(40)]
        for i, j in edges_sorted:
            ni, nj = g_root[i], g_root[j]
            if ni < nj:
                edge_perm.append(edge_index[(ni, nj)])
            else:
                edge_perm.append(edge_index[(nj, ni)])
        for a in range(m):
            for b in range(a + 1, m):
                A = Gram[a, b]
                B = Gram[edge_perm[a], edge_perm[b]]
                if A == B:
                    continue
                if A == -B:
                    mask = (1 << a) ^ (1 << b) ^ (1 << edge_perm[a]) ^ (1 << edge_perm[b])
                    if not add_equation(basis, mask, 1):
                        return None
                else:
                    return None
    return solve_basis(basis)


# main logic
if __name__ == "__main__":
    initial_lift = compute_lift_for_roots(root_list)
    print("initial lift size", initial_lift)

    # attempt full gauge
    all_idxs = list(range(len(Gperms)))
    sol_all = solve_gauge_for_subset(all_idxs)
    if sol_all is not None:
        print("found common gauge for all {} elements".format(len(Gperms)))
        best_sol = sol_all
        best_set = all_idxs
    else:
        print("no gauge works for entire group, scanning individual elements")
        good_idxs = []
        for idx,perm in enumerate(Gperms):
            s = solve_gauge_for_permutation(perm)
            if s is not None:
                good_idxs.append(idx)
        print("{} elements gauge-liftable individually".format(len(good_idxs)))
        # greedy combine
        best_set, best_sol = [], []
        for idx in good_idxs:
            candidate = best_set + [idx]
            sol = solve_gauge_for_subset(candidate)
            if sol is not None:
                best_set = candidate
                best_sol = sol
        print("greedy combined subset size", len(best_set))
    if best_sol:
        # apply sign gauge to roots
        signed_roots = [tuple(-x if best_sol[i] else x for x in root_list[i]) for i in range(m)]
        new_map = {str(edges_sorted[i]): list(signed_roots[i]) for i in range(m)}
        (ROOT / "artifacts" / "edge_to_e8_root_with_sign_gauge.json").write_text(json.dumps(new_map, indent=2))
        (ROOT / "artifacts" / "sign_gauge.json").write_text(json.dumps(best_sol, indent=2))
        new_lift = compute_lift_for_roots(signed_roots)
        print("lift size after gauge", new_lift)
    else:
        print("no nontrivial gauge found")
