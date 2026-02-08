#!/usr/bin/env python3
"""Symmetry-pruned CP-SAT search for W33->E8 edge->root bijection.

This script computes per-edge candidate roots as in
`scripts/solve_e8_embedding_cpsat.py`, but prunes candidates for the
edges incident to a chosen base vertex by selecting the top-M roots
with smallest mean distance across that incident-edge orbit. Then it
runs CP-SAT on the pruned candidate set.

Writes `checks/PART_CVII_e8_embedding_cpsat_symmetry_pruned.json`.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections import defaultdict
from typing import Dict, List, Tuple

import numpy as np

# Try importing OR-Tools
try:
    from ortools.sat.python import cp_model
except Exception as e:
    raise SystemExit("ortools required: install 'ortools' (pip install ortools)")


def generate_scaled_e8_roots() -> List[Tuple[int, ...]]:
    roots = set()
    # Type 1: (±2, ±2, 0,0,0,0,0,0)
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
    assert len(roots_list) == 240
    return roots_list


# --- build W33 graph (same as in solve_e8 script)
def build_w33_graph():
    F = 3
    vertices = []
    for a in range(F):
        for b in range(F):
            for c in range(F):
                for d in range(F):
                    if (a, b, c, d) != (0, 0, 0, 0):
                        vertices.append((a, b, c, d))

    def canonical_rep(v):
        for i in range(4):
            if v[i] % F != 0:
                a = v[i] % F
                inv = 1 if a == 1 else 2
                return tuple(((x * inv) % F) for x in v)
        return None

    reps = set(canonical_rep(v) for v in vertices if canonical_rep(v))
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
    return X, edges, adj


def build_edge_vectors(X: np.ndarray, edges: List[Tuple[int, int]]):
    E = []
    for (i, j) in edges:
        v = X[i] - X[j]
        nv = np.linalg.norm(v)
        if nv > 0:
            E.append(v / nv)
        else:
            E.append(v)
    return np.vstack(E)


def enumerate_triangles(n: int, adj: List[List[int]]):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=int, default=0, help="base vertex id (stabilizer) to use for pruning")
    parser.add_argument("--m", type=int, default=12, help="Top-M roots (by mean cost over base orbit) to keep for base-incident edges")
    parser.add_argument("--k", type=int, default=30, help="top-K candidate roots per edge (before pruning)")
    parser.add_argument("--time-limit", type=float, default=600.0, help="solver time limit in seconds")
    parser.add_argument("--seed-json", type=str, default=os.path.join('checks', 'PART_CVII_e8_embedding_attempt_seed.json'), help='seed file with seed_edges')
    parser.add_argument("--seed-reward", type=float, default=10000.0, help="seed reward (soft preference)")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--log", action='store_true')
    args = parser.parse_args()

    t0 = time.time()
    X, edges, adj = compute_embedding_matrix()
    A_mat = build_edge_vectors(X, edges)

    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)

    N_edges = len(A_mat)
    N_roots = len(roots_arr)

    # apply seed rotation if present
    forced_assignments = {}
    seed_obj = None
    if args.seed_json and os.path.exists(args.seed_json):
        try:
            seed_obj = json.load(open(args.seed_json))
            rot = seed_obj.get("rotation")
            if rot:
                rotation = np.array(rot, dtype=float)
                if rotation.shape == (8, 8):
                    A_mat = A_mat @ rotation
                    print("Applied rotation from seed file to edge vectors")
        except Exception:
            seed_obj = None

    # compute full cost matrix
    cost = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)

    # per-edge top-K candidates
    K = int(args.k)
    candidates: List[List[int]] = []
    for e in range(N_edges):
        idxs = np.argsort(cost[e])[:K]
        cand = [int(i) for i in idxs]
        candidates.append(cand)

    # ensure seed edges are included in candidates and record forced_assignments
    if seed_obj:
        for sd in seed_obj.get("seed_edges", []):
            eidx = sd.get("edge_index")
            ridx = sd.get("root_index")
            if eidx is not None and ridx is not None and 0 <= eidx < N_edges and 0 <= ridx < N_roots:
                if ridx not in candidates[eidx]:
                    candidates[eidx].append(ridx)
                forced_assignments[int(eidx)] = int(ridx)

    # identify edges incident to base vertex
    base = int(args.base)
    edges_incident = [i for i, (u, v) in enumerate(edges) if u == base or v == base]
    print(f"Base vertex {base}: incident edges count = {len(edges_incident)}")

    # compute mean cost per root across incident edges
    mean_cost = cost[edges_incident].mean(axis=0) if edges_incident else np.full((N_roots,), np.inf)
    top_m_roots = list(np.argsort(mean_cost)[: int(args.m)])
    print(f"Top-{args.m} roots across base-incident edges: {top_m_roots[:10]} ... (showing up to 10)")

    # prune candidates for incident edges: keep only roots in top_m_roots
    top_m_set = set(top_m_roots)
    pruned_candidates = []
    pruned_counts = []
    for e in range(N_edges):
        if e in edges_incident:
            # enforce that candidates include seed if present
            base_cand = [r for r in candidates[e] if r in top_m_set]
            # if seed assignment is in forced_assignments, ensure it's included
            if e in forced_assignments and forced_assignments[e] not in base_cand:
                base_cand.append(forced_assignments[e])
            # if pruning removed all candidates (unlikely), keep original top-K
            if not base_cand:
                base_cand = candidates[e]
            pruned_candidates.append(base_cand)
            pruned_counts.append(len(base_cand))
        else:
            pruned_candidates.append(candidates[e])
            pruned_counts.append(len(candidates[e]))

    print(f"Candidate counts (min,max,mean) after pruning: {min(pruned_counts)},{max(pruned_counts)},{sum(pruned_counts)/len(pruned_counts):.2f}")

    # Build CP-SAT model using pruned_candidates
    model = cp_model.CpModel()
    bvars: Dict[Tuple[int, int], cp_model.IntVar] = {}
    for e in range(N_edges):
        for r in pruned_candidates[e]:
            bvars[(e, r)] = model.NewBoolVar(f"b_e{e}_r{r}")

    # edge assignment constraints
    for e in range(N_edges):
        model.Add(sum(bvars[(e, r)] for r in pruned_candidates[e]) == 1)

    # root uniqueness
    root_to_pairs = defaultdict(list)
    for (e, r) in bvars.keys():
        root_to_pairs[r].append((e, r))
    for r, pairs in root_to_pairs.items():
        model.Add(sum(bvars[p] for p in pairs) <= 1)

    # triangle constraints
    n, vertices, adj, _ = build_w33_graph()
    triangles = enumerate_triangles(n, adj)
    roots_arr_int = np.array(roots, dtype=int)
    for (a, b, c) in triangles:
        e_ab = None
        e_bc = None
        e_ac = None
        # find edge indices
        if (a, b) in edges:
            e_ab = edges.index((a, b))
        elif (b, a) in edges:
            e_ab = edges.index((b, a))
        if (b, c) in edges:
            e_bc = edges.index((b, c))
        elif (c, b) in edges:
            e_bc = edges.index((c, b))
        if (a, c) in edges:
            e_ac = edges.index((a, c))
        elif (c, a) in edges:
            e_ac = edges.index((c, a))
        if e_ab is None or e_bc is None or e_ac is None:
            continue
        for t in range(8):
            expr_terms = []
            for r in pruned_candidates[e_ab]:
                coeff = int(roots[r][t])
                expr_terms.append((bvars[(e_ab, r)], coeff))
            for r in pruned_candidates[e_bc]:
                coeff = int(roots[r][t])
                expr_terms.append((bvars[(e_bc, r)], coeff))
            for r in pruned_candidates[e_ac]:
                coeff = -int(roots[r][t])
                expr_terms.append((bvars[(e_ac, r)], coeff))
            if not expr_terms:
                continue
            model.Add(sum(coeff * var for (var, coeff) in expr_terms) == 0)

    # objective: minimize scaled cost with seed soft preference
    scale = 10000.0
    seed_reward = float(args.seed_reward)
    objective_terms = []
    for (e, r), var in bvars.items():
        c = cost[e, r]
        ic = int(round(c * scale))
        if e in forced_assignments and forced_assignments[e] is not None and r == forced_assignments[e]:
            ic = max(0, ic - int(round(seed_reward)))
        objective_terms.append(ic * var)
    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(args.time_limit)
    solver.parameters.num_search_workers = 8
    solver.parameters.random_seed = int(args.seed)
    solver.parameters.log_search_progress = args.log

    print(f"Starting CP-SAT (pruned): edges={N_edges} vars={len(bvars)} triangles={len(triangles)} K={K} M={args.m} time_limit={args.time_limit}s")
    status = solver.Solve(model)
    status_name = solver.StatusName(status)
    print("Solver status:", status_name)

    res = {
        "status": status_name,
        "objective": None,
        "time_seconds": time.time() - t0,
        "k": K,
        "m": int(args.m),
        "vars": len(bvars),
        "triangles": len(triangles),
        "assignments": None,
        "found": False,
    }

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        res["objective"] = solver.ObjectiveValue()
        assignment = {}
        for e in range(N_edges):
            for r in pruned_candidates[e]:
                v = bvars.get((e, r))
                if v is not None and solver.Value(v) == 1:
                    assignment[str(e)] = int(r)
                    break
        res["assignments"] = assignment

        # attempt to build vertex positions
        roots_map = {i: tuple(roots[i]) for i in range(len(roots))}
        pos = {0: tuple([0] * 8)}
        changed = True
        while changed:
            changed = False
            for ei, (i, j) in enumerate(edges):
                if str(ei) not in assignment:
                    continue
                r_idx = assignment[str(ei)]
                rvec = roots_map[r_idx]
                if i in pos and j not in pos:
                    pos[j] = tuple(p_i - r for p_i, r in zip(pos[i], rvec))
                    changed = True
                elif j in pos and i not in pos:
                    pos[i] = tuple(p_j + r for p_j, r in zip(pos[j], rvec))
                    changed = True
        if len(pos) == len(vertices):
            ok = True
            for ei, (i, j) in enumerate(edges):
                if i in pos and j in pos:
                    diff = tuple(int(a - b) for a, b in zip(pos[i], pos[j]))
                    if diff not in roots_map.values():
                        ok = False
                        break
            res["valid_embedding"] = ok
            if ok:
                res["found"] = True
                res["positions"] = {str(k): list(v) for k, v in pos.items()}
                res["edge_to_root"] = {str(ei): int(assignment[str(ei)]) for ei in range(N_edges) if str(ei) in assignment}
        else:
            res["found"] = False
            res["positions_partial"] = {str(k): list(v) for k, v in pos.items()}
            res["assigned_vertices"] = len(pos)

    out_path = os.path.join(os.getcwd(), "checks", "PART_CVII_e8_embedding_cpsat_symmetry_pruned.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print("Wrote", out_path)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
