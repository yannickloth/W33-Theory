"""Part CLXIX: Graph cycle space and its Sp(4,3) decomposition

The usual simplicial homology calculation in ``scripts/w33_homology.py``
shows that the clique complex has $b_1=81$.  That is the number that appears
in the previous pillars and is perfectly suited to the matter sector of the
$E_8$ decomposition.  However the graph underlying W33 has a much larger
first homology when one ignores the 2-simplices:

    \[H_1^{\mathrm{graph}}(W33;\mathbb Z) \cong \mathbb Z^{201},\]\

since every edge not in a spanning tree produces an independent cycle and
there are $240-39=201$ such edges.  In the language of combinatorics this
is simply the cycle space of the 4-regular SRG(40,12,2,4), a $201$-dimensional
$\\mathbb Z$-module.

The goal of this part is to *compute* an explicit basis for that cycle
space, endow it with the obvious intersection pairing, and study how the
automorphism group Sp(4,3) acts on the resulting $201$-dimensional
permutation representation.  If the representation breaks cleanly into
copies of the $27$-dimensional E6 fundamental plus a small remainder, then
it will provide the long-sought geometric origin of the Yukawa matrices.

Results recorded by executing this script are also stored in
``data/w33_cycle_space.json``.

"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import networkx as nx
import numpy as np
from sympy import Matrix


def build_W33():
    def omega(v, w):
        return (v[0] * w[1] - v[1] * w[0] + v[2] * w[3] - v[3] * w[2]) % 3

    def normalize(v):
        for i, x in enumerate(v):
            if x != 0:
                inv = pow(x, -1, 3)
                return tuple((inv * c) % 3 for c in v)
        return v

    points = [p for p in product(range(3), repeat=4) if p != (0, 0, 0, 0)]
    vertices = list({normalize(p) for p in points})
    n = len(vertices)
    edges = []
    adj = [[] for _ in range(n)]
    for i, v in enumerate(vertices):
        for j, w in enumerate(vertices):
            if i < j and omega(v, w) == 0:
                edges.append((i, j))
                adj[i].append(j)
                adj[j].append(i)
    return n, vertices, adj, edges


def build_cycle_basis(n: int, adj: list[list[int]], edges: list[tuple[int, int]]):
    # incidence matrix (n x m)
    m = len(edges)
    B = np.zeros((n, m), dtype=int)
    for k, (i, j) in enumerate(edges):
        B[i, k] = 1
        B[j, k] = -1
    M = Matrix(B.tolist())
    null = M.nullspace()
    basis = [np.array([int(v) for v in vec], dtype=int).flatten() for vec in null]
    return basis


def intersection_matrix(basis: list[np.ndarray]) -> np.ndarray:
    r = len(basis)
    I = np.zeros((r, r), dtype=int)
    for i in range(r):
        for j in range(r):
            I[i, j] = int(np.dot(basis[i], basis[j]))
    return I


def compute_automorphisms(n: int, adj: list[list[int]], limit: int | None = None):
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in adj[i]:
            if j > i:
                G.add_edge(i, j)
    matcher = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos: list[dict[int, int]] = []
    for iso in matcher.isomorphisms_iter():
        autos.append(iso)
        if limit is not None and len(autos) >= limit:
            break
    return autos


def permute_cycle(vec: np.ndarray, perm: dict[int, int], edges: list[tuple[int, int]]):
    out = np.zeros_like(vec)
    for k, (i, j) in enumerate(edges):
        ni = perm[i]
        nj = perm[j]
        if ni > nj:
            ni, nj = nj, ni
        idx = edges.index((ni, nj))
        out[idx] = vec[k]
    return out


def trace_under_perm(basis: list[np.ndarray], perm: dict[int, int], edges: list[tuple[int, int]]):
    tr = 0
    for v in basis:
        v2 = permute_cycle(v, perm, edges)
        tr += int(np.dot(v, v2))
    return tr


def main():
    n, verts, adj, edges = build_W33()
    basis = build_cycle_basis(n, adj, edges)

    print(f"cycle space dimension = {len(basis)}")
    I = intersection_matrix(basis)
    print("intersection matrix rank", np.linalg.matrix_rank(I))

    autos = compute_automorphisms(n, adj)
    print(f"found {len(autos)} automorphisms (should be 51840)")

    sample = autos if len(autos) <= 20 else autos[:20]
    for idx, perm in enumerate(sample[:5]):
        print(f"auto {idx} trace = {trace_under_perm(basis, perm, edges)}")

    orbit_sizes = []
    for v in basis[:3]:
        orb = set()
        frontier = [tuple(v)]
        while frontier:
            w = np.array(frontier.pop())
            for perm in sample:
                w2 = permute_cycle(w, perm, edges)
                t = tuple(w2)
                if t not in orb:
                    orb.add(t)
                    frontier.append(t)
        orbit_sizes.append(len(orb))
    print("orbit sizes (sampled automorphisms):", orbit_sizes)

    out = {
        "dim": len(basis),
        "intersection_rank": int(np.linalg.matrix_rank(I)),
        "traces": [int(trace_under_perm(basis, sample[i], edges)) for i in range(min(5, len(sample)))],
        "orbit_sizes": orbit_sizes,
    }
    Path("data").mkdir(exist_ok=True)
    with open("data/w33_cycle_space.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote data/w33_cycle_space.json")


if __name__ == "__main__":
    main()
