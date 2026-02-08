#!/usr/bin/env python3
"""Check triangle coverage for CP-SAT candidate selection.

Reports how many triangles have no consistent triple among the top-K candidates per edge.
"""
from __future__ import annotations
import json
import numpy as np
from itertools import product

def generate_scaled_e8_roots() -> list:
    roots = set()
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (-2, 2):
                for sj in (-2, 2):
                    v = [0] * 8
                    v[i] = si
                    v[j] = sj
                    roots.add(tuple(v))
    from itertools import product
    for signs in product((-1, 1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            roots.add(tuple(int(s) for s in signs))
    roots_list = sorted(list(roots))
    return roots_list


def build_w33_graph():
    F = 3
    all_vectors = [
        (a, b, c, d)
        for a in range(F)
        for b in range(F)
        for c in range(F)
        for d in range(F)
        if (a, b, c, d) != (0, 0, 0, 0)
    ]

    def canonical_rep(v):
        for i in range(4):
            if v[i] % F != 0:
                a = v[i] % F
                inv = 1 if a == 1 else 2
                return tuple(((x * inv) % F) for x in v)
        return None

    reps = set(canonical_rep(v) for v in all_vectors if canonical_rep(v))
    vertices = sorted(list(reps))

    def symp(x, y):
        return (x[0] * y[1] - x[1] * y[0] + x[2] * y[3] - x[3] * y[2]) % F

    n = len(vertices)
    adj = [[] for _ in range(n)]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if symp(vertices[i], vertices[j]) == 0:
                adj[i].append(j)
                adj[j].append(i)
                edges.append((i, j))
    return n, vertices, adj, edges


def compute_embedding_matrix():
    n, vertices, adj, edges = build_w33_graph()
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in adj[i]:
            A[i, j] = 1.0
    vals, vecs = np.linalg.eigh(A)
    idx = np.argsort(vals)[::-1]
    vals = vals[idx]
    vecs = vecs[:, idx]
    idxs_2 = [i for i, v in enumerate(vals) if abs(v - 2.0) < 1e-6]
    if len(idxs_2) >= 8:
        chosen = idxs_2[:8]
    else:
        chosen = list(range(1, 9))
    X = vecs[:, chosen]
    X = X - X.mean(axis=0)
    X = X / (X.std(axis=0) + 1e-12)
    return X, edges


def load_seed_k(k=30, seed_json=None):
    X, edges = compute_embedding_matrix()
    A_mat = np.vstack([(X[i] - X[j]) / (np.linalg.norm(X[i] - X[j]) + 1e-12) for (i, j) in edges])
    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)

    cost = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)
    N_edges = len(A_mat)
    candidates = [list(np.argsort(cost[e])[:k]) for e in range(N_edges)]

    forced = {}
    if seed_json:
        try:
            s = json.load(open(seed_json))
            for sd in s.get('seed_edges', []):
                eidx = sd.get('edge_index')
                ridx = sd.get('root_index')
                if eidx is not None and ridx is not None:
                    forced[int(eidx)] = int(ridx)
                    if ridx not in candidates[eidx]:
                        candidates[eidx].append(ridx)
        except Exception:
            pass

    return candidates, edges


def enumerate_triangles(n, adj):
    tris = []
    for a in range(n):
        for b in adj[a]:
            if b <= a:
                continue
            for c in adj[b]:
                if c <= b:
                    continue
                if a in adj[c]:
                    tri = tuple(sorted((a, b, c)))
                    if tri not in tris:
                        tris.append(tri)
    return tris


if __name__ == '__main__':
    k = 30
    seed_json = 'checks/PART_CVII_e8_embedding_attempt_seed.json'
    candidates, edges = load_seed_k(k=k, seed_json=seed_json)
    n, vertices, adj, _ = build_w33_graph()
    triangles = enumerate_triangles(n, adj)

    # map edge pair to index
    edge_index = {edges[i]: i for i in range(len(edges))}
    edge_index.update({(j,i): idx for (i,j), idx in edge_index.items()})

    roots = generate_scaled_e8_roots()

    unsat = 0
    checked = 0
    for (a,b,c) in triangles:
        e_ab = edge_index.get((a,b))
        e_bc = edge_index.get((b,c))
        e_ac = edge_index.get((a,c))
        if e_ab is None or e_bc is None or e_ac is None:
            continue
        checked += 1
        ok = False
        for r_ab in candidates[e_ab]:
            for r_bc in candidates[e_bc]:
                # compute r_ac = r_ab + r_bc
                r_ac = tuple(x+y for x,y in zip(roots[r_ab], roots[r_bc]))
                # need r_ac to be one of allowed roots and present in candidates[e_ac]
                # But our true constraint is r_ab + r_bc - r_ac == 0 => r_ac == r_ab + r_bc
                for r_ac_idx in candidates[e_ac]:
                    if tuple(roots[r_ac_idx]) == r_ac:
                        ok = True
                        break
                if ok:
                    break
            if ok:
                break
        if not ok:
            unsat += 1
    print(f"k={k} triangles_checked={checked} unsatisfiable_triangles={unsat} out_of={len(triangles)}")
