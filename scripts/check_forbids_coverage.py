#!/usr/bin/env python3
"""Check whether current forbids imply infeasibility via simple coverage tests
and focused CP-SAT on the induced subgraph of forbidden edges.

Writes checks/PART_CVII_forbids_coverage.json with results.
"""
from __future__ import annotations

import json
import argparse
import time
from pathlib import Path
from collections import defaultdict

# Local copies of helper functions from solve_e8_embedding_cpsat.py to avoid importing that module

def generate_scaled_e8_roots() -> list:
    roots = set()
    # Type 1
    for i in range(8):
        for j in range(i + 1, 8):
            for si in (-2, 2):
                for sj in (-2, 2):
                    v = [0] * 8
                    v[i] = si
                    v[j] = sj
                    roots.add(tuple(v))
    # Type 2: (±1)^8 with even number of -1
    from itertools import product
    for signs in product((-1, 1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            roots.add(tuple(int(s) for s in signs))
    roots_list = sorted(list(roots))
    assert len(roots_list) == 240, f"expected 240 roots, got {len(roots_list)}"
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


def enumerate_triangles(n: int, adj: list):
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

from ortools.sat.python import cp_model
import numpy as np

CHECKS = Path('checks')
FORB = CHECKS / 'PART_CVII_forbids.json'
OUT = CHECKS / 'PART_CVII_forbids_coverage.json'


def compute_candidates(k: int = 40):
    X, edges = compute_embedding_matrix()
    A_mat = X
    # build edge vectors from solve script logic
    # reuse the function's behavior: build_edge_vectors is not exported; recompute here
    def build_edge_vectors(X, edges):
        E = []
        for (i, j) in edges:
            v = X[i] - X[j]
            nv = np.linalg.norm(v)
            if nv > 0:
                E.append(v / nv)
            else:
                E.append(v)
        return np.vstack(E)
    E_mat = build_edge_vectors(X, edges)
    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)
    N_edges = len(E_mat)
    cost = np.linalg.norm(E_mat[:, None, :] - roots_unit[None, :, :], axis=2)
    candidates = {}
    for e in range(N_edges):
        idxs = np.argsort(cost[e])[:k]
        candidates[e] = [int(i) for i in idxs]
    return candidates, edges, roots


def single_edge_coverage_test(forbids, candidates):
    # forbids: list of entries with 'set' and 'roots'
    forbidden_by_edge = defaultdict(set)
    for ent in forbids:
        s = ent.get('set', [])
        roots = ent.get('roots', [])
        if len(s) == 1:
            e = int(s[0])
            r = int(roots[0]) if roots else None
            if r is not None:
                forbidden_by_edge[e].add(r)
    blocked_edges = []
    for e, cand in candidates.items():
        forbidden = forbidden_by_edge.get(e, set())
        allowed = [r for r in cand if r not in forbidden]
        if not allowed:
            blocked_edges.append({'edge': e, 'forbidden_roots': list(forbidden), 'candidates': cand})
    return blocked_edges


def build_subgraph_model(edges, candidates, forbids, radius=0):
    # edges: list of (i,j) pairs
    # pick edges that appear in forbids
    involved_edges = set()
    vertices = set()
    for ent in forbids:
        s = ent.get('set', [])
        for e in s:
            involved_edges.add(int(e))
    # expand to include edges within radius by vertex adjacency
    for eidx in list(involved_edges):
        i, j = edges[eidx]
        vertices.add(i); vertices.add(j)
    if radius > 0:
        # include edges incident to these vertices
        for ei, (a, b) in enumerate(edges):
            if a in vertices or b in vertices:
                involved_edges.add(ei)
    # Build CP-SAT model restricted to involved_edges
    model = cp_model.CpModel()
    bvars = {}
    for e in sorted(involved_edges):
        for r in candidates[e]:
            bvars[(e, r)] = model.NewBoolVar(f'b_e{e}_r{r}')
    # per-edge assignment
    for e in sorted(involved_edges):
        model.Add(sum(bvars[(e, r)] for r in candidates[e]) == 1)
    # root uniqueness (only among variables present)
    root_map = defaultdict(list)
    for (e, r), v in bvars.items():
        root_map[r].append(v)
    for r, vs in root_map.items():
        model.Add(sum(vs) <= 1)
    # triangle constraints: include triangles fully contained in vertex set defined by edges
    n, vertices_all, adj, edges_all = build_w33_graph()
    triangles = enumerate_triangles(n, adj)
    edge_index = {edges_all[i]: i for i in range(len(edges_all))}
    for (a, b, c) in triangles:
        # include only if corresponding edges in our involved_edges
        e_ab = edge_index.get((a, b)) if (a, b) in edge_index else edge_index.get((b, a))
        e_bc = edge_index.get((b, c)) if (b, c) in edge_index else edge_index.get((c, b))
        e_ac = edge_index.get((a, c)) if (a, c) in edge_index else edge_index.get((c, a))
        if e_ab in involved_edges and e_bc in involved_edges and e_ac in involved_edges:
            # add triangle constraints as in solver
            for t in range(8):
                expr = []
                for r in candidates[e_ab]:
                    if (e_ab, r) in bvars:
                        expr.append((bvars[(e_ab, r)], int(generate_scaled_e8_roots()[r][t])))
                for r in candidates[e_bc]:
                    if (e_bc, r) in bvars:
                        expr.append((bvars[(e_bc, r)], int(generate_scaled_e8_roots()[r][t])))
                for r in candidates[e_ac]:
                    if (e_ac, r) in bvars:
                        expr.append((bvars[(e_ac, r)], -int(generate_scaled_e8_roots()[r][t])))
                if expr:
                    model.Add(sum(c * v for v, c in [(pair[0], pair[1]) for pair in expr]) == 0)
    # apply forbids only those that fit into bvars
    for ent in forbids:
        edges_f = ent.get('set', [])
        roots_f = ent.get('roots', [])
        pairs = []
        for e, r in zip(edges_f, roots_f):
            t = (int(e), int(r))
            if t in bvars:
                pairs.append(bvars[t])
        if len(pairs) >= 1:
            model.Add(sum(pairs) <= max(0, len(pairs)-1))
    return model


def run_focused_solver(model, time_limit=30):
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(time_limit)
    solver.parameters.num_search_workers = 8
    st = solver.Solve(model)
    return solver.StatusName(st)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--k', type=int, default=40)
    parser.add_argument('--time-limit', type=int, default=30)
    args = parser.parse_args()

    if not FORB.exists():
        print('No forbids file found')
        raise SystemExit(0)
    forb = json.loads(open(FORB, encoding='utf-8').read())

    candidates, edges, roots = compute_candidates(args.k)
    blocked = single_edge_coverage_test(forb.get('obstruction_sets', []), candidates)

    out = {'timestamp': time.time(), 'single_edge_blocked': blocked, 'focused': None}

    if blocked:
        print('Single-edge coverage found blocked edges:', blocked)
    else:
        # build focused model and run solver
        model = build_subgraph_model(edges, candidates, forb.get('obstruction_sets', []), radius=1)
        # if model uses no vars -> nothing to test
        if len([v for v in dir(model) if v]) == 0:
            print('No focused model constructed')
        else:
            st = run_focused_solver(model, time_limit=args.time_limit)
            out['focused'] = {'status': st}
            print('Focused solver status:', st)

    OUT.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print('Wrote summary to', OUT)


if __name__ == '__main__':
    main()
