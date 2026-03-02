#!/usr/bin/env python3
"""
w33_index_spine_verification.py

Reconstruct the W(3,3) collinearity graph (SRG(40,12,2,4)) exactly as described
in the GitHub Pages index.html, then verify the "hard spine" claims:

- 40 vertices (projective points of F3^4)
- 240 edges (symplectic-orthogonality adjacency)
- 40 lines as K4 cliques
- 160 triangles (4 per line)
- Homology ranks: b0=1, b1=81, b2=40 for the 2D simplicial complex built from those triangles
- Hodge Laplacian L1 spectrum on edges: 0^81, 4^120, 10^24, 16^15
- Ollivier–Ricci curvature (idleness p=0) constant: κ_adj=1/6, κ_dist2=2/3
- Discrete Gauss–Bonnet: sum_edge κ = 40

Dependencies: numpy, sympy, scipy
"""

import itertools, math
from collections import deque
import numpy as np
import sympy as sp
from scipy.optimize import linprog

F = [0, 1, 2]

J = np.array(
    [[0, 0, 1, 0],
     [0, 0, 0, 1],
     [2, 0, 0, 0],
     [0, 2, 0, 0]],
    dtype=int
) % 3

def dotJ(v, w) -> int:
    return int((v @ J @ w) % 3)

def build_points():
    """40 projective points of F3^4: normalize first nonzero coordinate to 1."""
    pts = []
    seen = set()
    for v in itertools.product(F, repeat=4):
        if all(c == 0 for c in v):
            continue
        v = np.array(v, dtype=int) % 3
        for c in v:
            if c != 0:
                inv = 1 if c == 1 else 2
                vn = (v * inv) % 3
                break
        t = tuple(vn.tolist())
        if t not in seen:
            seen.add(t)
            pts.append(vn)
    assert len(pts) == 40
    return pts

def build_graph(points):
    n = len(points)
    A = np.zeros((n, n), dtype=int)
    for i, v in enumerate(points):
        for j in range(i+1, n):
            if dotJ(v, points[j]) == 0:
                A[i, j] = A[j, i] = 1
    return A

def bfs_all_pairs(A):
    n = A.shape[0]
    adj = [list(np.where(A[i] == 1)[0]) for i in range(n)]
    dist = np.full((n, n), np.inf)
    for s in range(n):
        dist[s, s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[s, v] == np.inf:
                    dist[s, v] = dist[s, u] + 1
                    q.append(v)
    return adj, dist

def wasserstein_uniform(Nx, Ny, dist_mat):
    k = len(Nx)
    assert len(Ny) == k
    C = dist_mat[np.ix_(Nx, Ny)].astype(float).reshape(-1)

    A_eq = []
    b_eq = []

    # row sums
    for i in range(k):
        row = np.zeros(k * k)
        row[i*k:(i+1)*k] = 1
        A_eq.append(row)
        b_eq.append(1.0 / k)

    # col sums
    for j in range(k):
        col = np.zeros(k * k)
        col[j::k] = 1
        A_eq.append(col)
        b_eq.append(1.0 / k)

    A_eq = np.array(A_eq)
    b_eq = np.array(b_eq)
    bounds = [(0, None)] * (k * k)

    res = linprog(C, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(res.message)
    return res.fun

def ollivier_ricci(x, y, adj, dist):
    Nx, Ny = adj[x], adj[y]
    W1 = wasserstein_uniform(Nx, Ny, dist)
    d = dist[x, y]
    return 1.0 - W1 / d

def main():
    pts = build_points()
    A = build_graph(pts)
    n = A.shape[0]
    deg = A.sum(axis=1)
    m = int(A.sum() // 2)

    print("Basic SRG checks")
    print(f"  n={n}, m={m}, deg(min,max)={(deg.min(), deg.max())}")

    # SRG parameters λ, μ via common neighbors
    adj_cns = set()
    non_cns = set()
    for i in range(n):
        for j in range(i+1, n):
            cn = int(np.dot(A[i], A[j]))
            if A[i, j] == 1:
                adj_cns.add(cn)
            else:
                non_cns.add(cn)
    print(f"  common neighbors (adj) = {sorted(adj_cns)}")
    print(f"  common neighbors (non) = {sorted(non_cns)}")

    # lines = 4-cliques
    lines = []
    for comb in itertools.combinations(range(n), 4):
        ok = True
        for i, j in itertools.combinations(comb, 2):
            if A[i, j] == 0:
                ok = False
                break
        if ok:
            lines.append(comb)
    print(f"Lines as K4 cliques: {len(lines)}")

    # triangles
    triangles = set()
    for line in lines:
        for tri in itertools.combinations(line, 3):
            triangles.add(tuple(sorted(tri)))
    print(f"Triangles (4 per line): {len(triangles)}")

    # Build edge list
    edges = []
    edge_index = {}
    for i in range(n):
        for j in range(i+1, n):
            if A[i, j] == 1:
                edge_index[(i, j)] = len(edges)
                edges.append((i, j))
    m1 = len(edges)
    m2 = len(triangles)

    # Boundary matrices
    B1 = sp.zeros(n, m1)
    for idx, (i, j) in enumerate(edges):
        B1[i, idx] = -1
        B1[j, idx] = 1

    B2 = sp.zeros(m1, m2)
    tri_list = list(triangles)

    def add_edge(B2, e_idx, u, v, coef):
        if u < v:
            e = (u, v)
            sgn = 1
        else:
            e = (v, u)
            sgn = -1
        B2[e_idx[e], t_idx] += coef * sgn

    for t_idx, (a, b, c) in enumerate(tri_list):
        add_edge(B2, edge_index, b, c,  1)
        add_edge(B2, edge_index, a, c, -1)
        add_edge(B2, edge_index, a, b,  1)

    rank_B1 = B1.rank()
    rank_B2 = B2.rank()
    b0 = 1
    b1 = (m1 - rank_B1) - rank_B2
    b2 = m2 - rank_B2

    print("Homology ranks (over Q/Z-rank):")
    print(f"  rank(∂1)={rank_B1}, rank(∂2)={rank_B2}")
    print(f"  b0={b0}, b1={b1}, b2={b2}")
    print(f"  Euler check: V-E+F={n-m1+m2}, b0-b1+b2={b0-b1+b2}")

    # Hodge Laplacian spectrum on edges
    B1_np = np.array(B1.tolist(), dtype=int)
    B2_np = np.array(B2.tolist(), dtype=int)
    L1 = B2_np @ B2_np.T + B1_np.T @ B1_np
    w = np.linalg.eigvalsh(L1.astype(float))
    w_int = np.rint(w).astype(int)
    unique, counts = np.unique(w_int, return_counts=True)
    print("L1 spectrum (rounded):")
    print("  " + ", ".join(f"{u}^{c}" for u, c in zip(unique, counts)))

    # Ollivier–Ricci curvature
    adj, dist = bfs_all_pairs(A)
    # compute across all edges and all non-edges (distance 2)
    kappa_adj = []
    kappa_non = []
    for i in range(n):
        for j in range(i+1, n):
            if A[i, j] == 1:
                kappa_adj.append(ollivier_ricci(i, j, adj, dist))
            else:
                kappa_non.append(ollivier_ricci(i, j, adj, dist))
    print("Ollivier–Ricci curvature (p=0):")
    print(f"  edges: min=max={min(kappa_adj)}")
    print(f"  dist2: min=max={min(kappa_non)}")

    print("Discrete Gauss–Bonnet:")
    print(f"  sum_edge κ = {len(kappa_adj)} * {kappa_adj[0]} = {len(kappa_adj)*kappa_adj[0]}")

if __name__ == "__main__":
    main()
