#!/usr/bin/env python3
"""Cycle space of the W(3,3) graph and Sp(4,3) action.

This utility computes a basis for the cycle space of the W33 point graph
(the nullspace of the incidence matrix) and analyses how the automorphism
group Sp(4,3) acts on that space.  The cycle-space dimension is 201, which
corresponds to the familiar formula |E| - |V| + 1, but the simplicial
homology reduces this to 81 by factoring out triangles.

We record the intersection pairing on the basis vectors (just the standard
inner product in Z^{240}) and compute traces of a few automorphisms.  The
hope is that the 201-dimensional permutation representation splits into
copies of the 27-dimensional E6 fundamental plus small extras.

Usage::

    python tools/cycle_space_analysis.py

"""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path

import networkx as nx
import numpy as np
from sympy import Matrix


def build_W33():
    """Return (n, vertices, adj, edges) for the W33 graph."""
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
    """Return basis for the graph cycle space (nullspace of incidence matrix).

    The basis vectors live in Z^{|E|}; there are 201 of them for W33.
    We'll clear denominators to ensure the output is integral.
    """
    m = len(edges)
    # build oriented incidence matrix (n x m)
    B = np.zeros((n, m), dtype=int)
    for k, (i, j) in enumerate(edges):
        B[i, k] = 1
        B[j, k] = -1
    M = Matrix(B.tolist())
    null = M.nullspace()
    basis = []
    for vec in null:
        # vec may have rational entries; clear denominators
        denoms = [fr.q for fr in vec]
        l = 1
        for d in denoms:
            l = l * d // np.gcd(l, d)
        int_vec = np.array([int(fr * l) for fr in vec], dtype=int).flatten()
        basis.append(int_vec)
    return basis


def intersection_matrix(basis: list[np.ndarray]) -> np.ndarray:
    """Compute the symmetric inner product matrix for a list of vectors."""
    r = len(basis)
    I = np.zeros((r, r), dtype=int)
    for i in range(r):
        for j in range(r):
            I[i, j] = int(np.dot(basis[i], basis[j]))
    return I


def compute_automorphisms(n: int, adj: list[list[int]], limit: int | None = None):
    """Return vertex permutations giving Aut(W33) (as dicts).

    If ``limit`` is provided, enumeration stops after that many isomorphisms.
    This allows callers (e.g. tests) to avoid iterating all 51 840 automorphisms
    when only a few examples are needed.  To obtain the full list omit or set
    ``limit=None``.
    """
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
    """Apply a vertex permutation to a cycle-vector (edge-coordinates).

    The edge list uses an orientation (i<j).  When the permutation reverses the
    order of the endpoints the orientation flips sign, so we multiply by -1 in
    that case to keep the cycle space invariant.
    """
    out = np.zeros_like(vec)
    for k, (i, j) in enumerate(edges):
        ni = perm[i]
        nj = perm[j]
        sign = 1
        if ni > nj:
            # orientation reversed relative to our canonical ordering
            ni, nj = nj, ni
            sign = -1
        idx = edges.index((ni, nj))
        out[idx] = sign * vec[k]
    return out


def trace_under_perm(basis: list[np.ndarray], perm: dict[int, int], edges: list[tuple[int, int]]):
    """Compute trace of permutation on cycle space basis."""
    tr = 0
    for v in basis:
        v2 = permute_cycle(v, perm, edges)
        tr += int(np.dot(v, v2))
    return tr


def main():
    n, vertices, adj, edges = build_W33()
    basis = build_cycle_basis(n, adj, edges)
    print(f"cycle space dimension = {len(basis)}")

    I = intersection_matrix(basis)
    print("intersection matrix rank", np.linalg.matrix_rank(I))

    # enumerate automorphisms but keep only a small sample for heavy analysis
    autos = compute_automorphisms(n, adj)
    print(f"found {len(autos)} automorphisms (should be 51840)")

    sample_autos = autos if len(autos) <= 20 else autos[:20]

    # compute traces for a few sample automorphisms
    for idx, perm in enumerate(sample_autos[:5]):
        tr = trace_under_perm(basis, perm, edges)
        print(f"auto {idx} trace = {tr}")

    # orbit sizes of a handful of basis vectors using only the sample
    orbit_sizes = []
    for v in basis[:3]:
        orb = set()
        frontier = [tuple(v)]
        while frontier:
            w = np.array(frontier.pop())
            for perm in sample_autos:
                w2 = permute_cycle(w, perm, edges)
                t = tuple(w2)
                if t not in orb:
                    orb.add(t)
                    frontier.append(t)
        orbit_sizes.append(len(orb))
    print("orbit sizes for first 3 basis vectors (sampled autos):", orbit_sizes)

    out = {
        "dim": len(basis),
        "intersection_rank": int(np.linalg.matrix_rank(I)),
        "traces": [int(trace_under_perm(basis, sample_autos[i], edges)) for i in range(min(5, len(sample_autos)))],
        "orbit_sizes": orbit_sizes,
    }
    Path("data").mkdir(exist_ok=True)
    with open("data/w33_cycle_space.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote data/w33_cycle_space.json")


if __name__ == "__main__":
    main()
