#!/usr/bin/env python3
"""Local CP-SAT patch: enforce triangle constraints within a small connected subgraph.

This allows attempting exact triangle fixes within a local region while keeping the
global bijection fixed elsewhere (via excluding already-used roots outside the block).

Usage:
  python -X utf8 scripts/solve_e8_embedding_cpsat_local.py --seed-json checks/PART_CVII_e8_bijection_seed_20260207T183157Z.json --start-vertex 5 --edge-limit 24 --k 40 --time-limit 60 --seed 202 --seed-reward 10000
"""
from __future__ import annotations

import argparse
import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# Import core CP-SAT implementation pieces from the global solver
from solve_e8_embedding_cpsat import (
    generate_scaled_e8_roots,
    compute_embedding_matrix,
    build_w33_graph,
    enumerate_triangles,
)
from ortools.sat.python import cp_model


def build_edge_set_from_vertex(start_v: int, adj: List[List[int]], edges: List[Tuple[int, int]], edge_limit: int):
    """BFS outwards from start vertex to collect up to edge_limit edges (by index)."""
    visited_vertices = set([start_v])
    q = deque([start_v])
    edge_idxs = set()
    edge_index = {edges[i]: i for i in range(len(edges))}
    edge_index.update({(v, u): i for (u, v), i in edge_index.items()})

    while q and len(edge_idxs) < edge_limit:
        v = q.popleft()
        for w in adj[v]:
            ei = edge_index.get((v, w))
            if ei is not None:
                edge_idxs.add(ei)
            if w not in visited_vertices:
                visited_vertices.add(w)
                q.append(w)
        # expand further if needed
    return sorted(list(edge_idxs))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-json", type=str, default=None)
    parser.add_argument("--start-vertex", type=int, default=5)
    parser.add_argument("--edge-limit", type=int, default=24)
    parser.add_argument("--k", type=int, default=40)
    parser.add_argument("--time-limit", type=float, default=60.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--seed-reward", type=float, default=10000.0)
    parser.add_argument("--force-seed", action="store_true")
    parser.add_argument("--lock-seed-edges", action="store_true", help='If set, restrict candidate roots for edges inside block to their seed assignment (conservative repair)')
    parser.add_argument("--protect-top-n", type=int, default=0, help='Lock top-N edges in the block by triangle participation to their seed assignment')
    args = parser.parse_args()

    t0 = time.time()
    roots = generate_scaled_e8_roots()
    X, edges = compute_embedding_matrix()
    n, vertices, adj, _edges = build_w33_graph()

    # compute cost distances between edge vectors and roots
    A_mat = X  # edge vectors computed in compute_embedding_matrix
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)
    E = []
    for (i, j) in edges:
        v = X[i] - X[j]
        nv = np.linalg.norm(v)
        if nv > 0:
            E.append(v / nv)
        else:
            E.append(v)
    A_mat = np.vstack(E)

    N_edges = len(A_mat)

    cost = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)

    # Determine the block of edges to optimize
    block_edges = build_edge_set_from_vertex(args.start_vertex, adj, edges, args.edge_limit)
    print(f"Selected {len(block_edges)} edges for local CP-SAT starting at vertex {args.start_vertex}")

    # read seed and block out already-used roots outside the block
    seed_obj = None
    used_roots_outside = set()
    seed_map = {}
    if args.seed_json and os.path.exists(args.seed_json):
        seed_obj = json.load(open(args.seed_json, encoding='utf-8'))
        for sd in seed_obj.get('seed_edges', []):
            eidx = int(sd.get('edge_index'))
            ridx = int(sd.get('root_index'))
            if eidx not in block_edges:
                used_roots_outside.add(ridx)
            else:
                seed_map[eidx] = ridx

    # restrict candidate roots per edge to top-K excluding used_roots_outside
    K = int(args.k)
    candidates: Dict[int, List[int]] = {}
    lock_seed_edges = getattr(args, 'lock_seed_edges', False)
    for e in block_edges:
        # If edge is protected and we have a seed assignment, only allow that root
        if e in protected_edges and (e in seed_map):
            candidates[e] = [seed_map[e]]
            continue
        # If locking seed edges globally is requested, lock those as well
        if lock_seed_edges and (e in seed_map):
            candidates[e] = [seed_map[e]]
            continue
        idxs = np.argsort(cost[e])
        cand = [int(i) for i in idxs if int(i) not in used_roots_outside][:K]
        if not cand:
            # fallback: allow all roots (rare)
            cand = [i for i in range(len(roots)) if i not in used_roots_outside][:K]
        candidates[e] = cand

    # triangles fully in block
    triangles_all = enumerate_triangles(n, adj)
    # simple selection: triangles where all three edge indices are in block_edges
    edge_index = {edges[i]: i for i in range(len(edges))}
    edge_index.update({(v, u): i for (u, v), i in edge_index.items()})
    local_triangles = []
    for (a, b, c) in triangles_all:
        e_ab = edge_index.get((a, b))
        e_bc = edge_index.get((b, c))
        e_ac = edge_index.get((a, c))
        if e_ab in block_edges and e_bc in block_edges and e_ac in block_edges:
            local_triangles.append((a, b, c))
    print(f"Found {len(local_triangles)} triangles fully inside the block")

    # determine protected edges (if requested) by triangle participation counts
    protect_top_n = int(getattr(args, 'protect_top_n', 0))
    protected_edges = set()
    if protect_top_n > 0:
        # count number of triangles each edge participates in (global)
        edge_tri_count = {eidx: 0 for eidx in block_edges}
        for (a, b, c) in triangles_all:
            e_ab = edge_index.get((a, b))
            e_bc = edge_index.get((b, c))
            e_ac = edge_index.get((a, c))
            for e in (e_ab, e_bc, e_ac):
                if e in edge_tri_count:
                    edge_tri_count[e] += 1
        # select top-n edges
        sorted_edges = sorted(edge_tri_count.items(), key=lambda kv: -kv[1])
        for e, cnt in sorted_edges[:protect_top_n]:
            protected_edges.add(e)
        print(f"Protected edges (top {protect_top_n}):", protected_edges)

    # restrict candidate roots per edge to top-K excluding used_roots_outside
    K = int(args.k)
    candidates: Dict[int, List[int]] = {}
    lock_seed_edges = getattr(args, 'lock_seed_edges', False)
    for e in block_edges:
        # If edge is protected and we have a seed assignment, only allow that root
        if e in protected_edges and (e in seed_map):
            candidates[e] = [seed_map[e]]
            continue
        # If locking seed edges globally is requested, lock those as well
        if lock_seed_edges and (e in seed_map):
            candidates[e] = [seed_map[e]]
            continue
        idxs = np.argsort(cost[e])
        cand = [int(i) for i in idxs if int(i) not in used_roots_outside][:K]
        if not cand:
            # fallback: allow all roots (rare)
            cand = [i for i in range(len(roots)) if i not in used_roots_outside][:K]
        candidates[e] = cand

    # Build model
    model = cp_model.CpModel()

    bvars: Dict[Tuple[int, int], cp_model.IntVar] = {}
    for e in block_edges:
        for r in candidates[e]:
            bvars[(e, r)] = model.NewBoolVar(f"b_e{e}_r{r}")

    # per-edge exactly one
    for e in block_edges:
        model.Add(sum(bvars[(e, r)] for r in candidates[e]) == 1)

    # root uniqueness within block (prevent reuse inside block)
    root_to_pairs = defaultdict(list)
    for (e, r) in list(bvars.keys()):
        root_to_pairs[r].append((e, r))
    for r, pairs in root_to_pairs.items():
        model.Add(sum(bvars[p] for p in pairs) <= 1)

    # triangle constraints (exact equality coordinate-wise)
    for (a, b, c) in local_triangles:
        e_ab = edge_index.get((a, b))
        e_bc = edge_index.get((b, c))
        e_ac = edge_index.get((a, c))
        for t in range(8):
            expr_terms = []
            for r in candidates[e_ab]:
                coeff = int(roots[r][t])
                expr_terms.append((bvars[(e_ab, r)], coeff))
            for r in candidates[e_bc]:
                coeff = int(roots[r][t])
                expr_terms.append((bvars[(e_bc, r)], coeff))
            for r in candidates[e_ac]:
                coeff = -int(roots[r][t])
                expr_terms.append((bvars[(e_ac, r)], coeff))
            if expr_terms:
                model.Add(sum(coeff * var for (var, coeff) in expr_terms) == 0)

    # seed-reward objective (soft): minimize cost, reward seed root selections
    scale = 10000.0
    seed_reward = float(args.seed_reward)
    objective_terms = []
    # map seed edges for block
    seed_map = {}
    if seed_obj:
        for sd in seed_obj.get('seed_edges', []):
            eidx = int(sd.get('edge_index'))
            ridx = int(sd.get('root_index'))
            if eidx in block_edges:
                seed_map[eidx] = ridx

    for (e, r), var in bvars.items():
        c = cost[e, r]
        ic = int(round(c * scale))
        if e in seed_map and seed_map[e] == r:
            ic = max(0, ic - int(round(seed_reward)))
        objective_terms.append(ic * var)

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(args.time_limit)
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = int(args.seed)

    print(f"Starting local CP-SAT on block edges={len(block_edges)} vars={len(bvars)} triangles={len(local_triangles)} k={K} time_limit={args.time_limit}s")
    status = solver.Solve(model)
    status_name = solver.StatusName(status)
    print('Solver status:', status_name)

    res = {
        'status': status_name,
        'objective': None,
        'time_seconds': time.time() - t0,
        'k': K,
        'vars': len(bvars),
        'triangles': len(local_triangles),
        'assignments': None,
        'found': False,
        'start_vertex': int(args.start_vertex),
        'block_edges': block_edges,
        'excluded_roots_outside': sorted(list(used_roots_outside)) if used_roots_outside else [],
    }

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        assignment = {}
        for e in block_edges:
            found = False
            for r in candidates[e]:
                v = bvars.get((e, r))
                if v is not None and solver.Value(v) == 1:
                    assignment[str(e)] = int(r)
                    found = True
                    break
        res['assignments'] = assignment
        # check triangle logic
        # compute exact matches in block
        exact = 0
        for (a, b, c) in local_triangles:
            e_ab = edge_index.get((a, b))
            e_bc = edge_index.get((b, c))
            e_ac = edge_index.get((a, c))
            r_ab = tuple(roots[assignment[str(e_ab)]])
            r_bc = tuple(roots[assignment[str(e_bc)]])
            r_ac = tuple(roots[assignment[str(e_ac)]])
            sums = [tuple(np.add(r_ab, r_bc)), tuple(np.subtract(r_ab, r_bc)), tuple(np.add(r_ab, tuple([-x for x in r_bc]))), tuple(np.subtract(tuple([-x for x in r_ab]), r_bc))]
            targets = {r_ac, tuple([-x for x in r_ac])}
            if any(s in targets for s in sums):
                exact += 1
        res['block_exact'] = exact
        res['found'] = True

    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out_path = Path.cwd() / 'checks' / f'PART_CVII_e8_bijection_local_seed_{stamp}.json'
    out_path.write_text(json.dumps(res, indent=2), encoding='utf-8')
    print('Wrote local CP-SAT result to', out_path)
    print(json.dumps(res, indent=2))


if __name__ == '__main__':
    main()
