#!/usr/bin/env python3
"""Extract explicit GL(2,3) module inside E8 mod 3 from the lift subgroup.

Uses the lifted adjacency permutations saved in
artifacts/phi_lift_subgroup.json (section "lift_generators").  For each
lifting permutation we construct the corresponding 8x8 integer matrix which
realises the isometry on the root lattice.  Reducing those matrices mod 3
produces a representation over GF(3); we output all of them so that
further module analysis can be performed externally (e.g. to spot the
4-dimensional natural GL(2,3) submodule).

The method:
 1. load canonical edge->root map and choose an invertible 8x8 basis of roots.
 2. for each permutation of the lift generators compute image of basis.
 3. solve M * B = B' for integer matrix M and reduce mod 3.

Outputs JSON to artifacts/gl23_rep.json with keys:
  - "basis_indices" : indices of the 8 roots used for basis
  - "matrices" : dict mapping generator index -> 8x8 list-of-lists (mod 3)

"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
# ensure tools package on path
import sys
sys.path.insert(0, str(ROOT))

from tools.compute_phi_lift_subgroup import edges, edge_index  # type: ignore

# load root map
root_map = json.loads((ROOT / "artifacts" / "edge_to_e8_root.json").read_text())
edges_sorted = []
root_list: List[List[int]] = []
for k, v in root_map.items():
    if not k.startswith("("):
        continue
    pair = tuple(int(x.strip()) for x in k.strip()[1:-1].split(","))
    if pair[0] < pair[1]:
        edges_sorted.append(pair)
        root_list.append(list(v))
assert len(root_list) == 240

# load lift subgroup certificate
cert = json.loads((ROOT / "artifacts" / "phi_lift_subgroup.json").read_text())
lift_gens = cert.get("lift_generators", [])
if not lift_gens:
    print("no generators recorded in certificate; rerun compute_phi_lift_subgroup.py with default settings")
    lift_gens = []

# choose 8 independent roots for basis
B = None
basis_idx = []
for start in range(0, len(root_list) - 7):
    mat = np.array(root_list[start:start+8], dtype=int).T
    if abs(round(np.linalg.det(mat))) == 1:
        B = mat
        basis_idx = list(range(start, start+8))
        break
if B is None:
    # try random combinations
    import random
    for _ in range(1000):
        idxs = random.sample(range(len(root_list)), 8)
        mat = np.array([root_list[i] for i in idxs], dtype=int).T
        if abs(round(np.linalg.det(mat))) == 1:
            B = mat
            basis_idx = idxs
            break
assert B is not None, "failed to find invertible 8x8 block of roots"

# precompute edge permutations corresponding to lift generators (vertex perms -> edge perms)
import networkx as nx
from scripts.e8_embedding_group_theoretic import build_w33

n, vertices, adj_list, edges40 = build_w33()
G_adj = nx.Graph()
G_adj.add_nodes_from(range(40))
for i, nbrs in enumerate(adj_list):
    for j in nbrs:
        if i < j:
            G_adj.add_edge(i, j)
G_root = nx.Graph()
G_root.add_nodes_from(range(40))
for i, j in edges_sorted:
    if i < j:
        G_root.add_edge(i, j)

gm2 = nx.algorithms.isomorphism.GraphMatcher(G_adj, G_root)
label_map = next(gm2.isomorphisms_iter())
label_map_inv = {v: k for k, v in label_map.items()}

edge_perms = []
for vert_perm in lift_gens:
    g_root = [label_map[vert_perm[label_map_inv[i]]] for i in range(40)]
    perm_edges = []
    for i, j in edges_sorted:
        ni, nj = g_root[i], g_root[j]
        if ni < nj:
            perm_edges.append(edge_index[(ni, nj)])
        else:
            perm_edges.append(edge_index[(nj, ni)])
    edge_perms.append(perm_edges)

# for each edge permutation compute corresponding 8x8 matrix
matrices = {}
for idx, perm in enumerate(edge_perms):
    # compute images of basis vectors
    Bp = np.zeros((8, 8), dtype=int)
    for col, root_idx in enumerate(basis_idx):
        new_root = root_list[perm[root_idx]]
        Bp[:, col] = new_root
    # solve M * B = Bp -> M = Bp * B^{-1}
    M = Bp @ np.linalg.inv(B)
    # round to integer
    M = np.rint(M).astype(int)
    matrices[str(idx)] = (M % 3).tolist()

out = {"basis_indices": basis_idx, "matrices": matrices}
(ROOT / "artifacts" / "gl23_rep.json").write_text(json.dumps(out, indent=2))
print("wrote gl23_rep.json with {} generators".format(len(matrices)))
