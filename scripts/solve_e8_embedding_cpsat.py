#!/usr/bin/env python3
"""CP-SAT encoding to search for a W33 -> E8 edge→root bijection.

Approach:
- Model binary variables b[e,r] (edge e assigned to root r) restricted to top-K candidate roots per edge.
- Add per-edge assignment constraints and at-most-one per root across edges.
- Add triangle linear constraints: for each triangle (a<b<c): r_ab + r_bc - r_ac == 0 coordinatewise.
- Minimize sum of assignment distances (from spectral-ICP seed mapping) as objective.

Writes `checks/PART_CVII_e8_embedding_cpsat.json` with solution or best info.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

# Try importing OR-Tools
try:
    from ortools.sat.python import cp_model
except Exception as e:
    raise SystemExit("ortools required: install 'ortools' (pip install ortools)")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

Vector = Tuple[int, ...]


def generate_scaled_e8_roots() -> List[Vector]:
    roots: Set[Vector] = set()
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
    adj: List[List[int]] = [[] for _ in range(n)]
    edges: List[Tuple[int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if symp(vertices[i], vertices[j]) == 0:
                adj[i].append(j)
                adj[j].append(i)
                edges.append((i, j))
    return n, vertices, adj, edges


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


def compute_embedding_matrix():
    # replicate spectral embedding from search script
    n, vertices, adj, edges = build_w33_graph()
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in adj[i]:
            A[i, j] = 1.0
    vals, vecs = np.linalg.eigh(A)
    idx = np.argsort(vals)[::-1]
    vals = vals[idx]
    vecs = vecs[:, idx]
    # find eigenvalue-2 indices
    idxs_2 = [i for i, v in enumerate(vals) if abs(v - 2.0) < 1e-6]
    if len(idxs_2) >= 8:
        chosen = idxs_2[:8]
    else:
        chosen = list(range(1, 9))
    X = vecs[:, chosen]
    X = X - X.mean(axis=0)
    X = X / (X.std(axis=0) + 1e-12)
    return X, edges


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
                    # ensure a<b<c
                    tri = tuple(sorted((a, b, c)))
                    if tri not in tris:
                        tris.append(tri)
    return tris


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-json", type=str, default=None, help="seed file with 'picked_indices' and 'seed_edges'")
    parser.add_argument("--k", type=int, default=30, help="top-K candidate roots per edge")
    parser.add_argument("--time-limit", type=float, default=600.0, help="solver time limit in seconds")
    parser.add_argument("--cost-scale", type=float, default=10000.0, help="scale factor for float costs -> int")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--force-seed", action="store_true", help="Force seed assignments as hard constraints (default: False)")
    parser.add_argument("--seed-reward", type=float, default=10000.0, help="Reward subtracted from the assignment cost when choosing the seed root (larger = prefer seeds)")
    parser.add_argument('--workers', type=int, default=8, help='Number of CP-SAT search workers (num_search_workers)')
    parser.add_argument('--log', action='store_true', help='Enable CP‑SAT search progress logs')
    parser.add_argument('--forbid-json', type=str, default=None, help='Optional JSON file with obstruction sets to forbid (checks/PART_CVII_forbids.json)')
    args = parser.parse_args()
    # if a canonical forbids file exists and none was specified, use it
    if args.forbid_json is None and os.path.exists(os.path.join('checks', 'PART_CVII_forbids.json')):
        args.forbid_json = os.path.join('checks', 'PART_CVII_forbids.json')
        print('Using default forbids file:', args.forbid_json)

    t0 = time.time()
    X, edges = compute_embedding_matrix()
    A_mat = build_edge_vectors(X, edges)
    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)

    # normalize root vectors to unit length (float) for distance matching
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)

    # optional rotation from seed (if present)
    rotation = None
    seed_obj = None
    if args.seed_json and os.path.exists(args.seed_json):
        seed_obj = json.load(open(args.seed_json))
        rot = seed_obj.get("rotation")
        if rot:
            rotation = np.array(rot, dtype=float)
            # apply if shapes match
            if rotation.shape == (8, 8):
                A_map = A_mat @ rotation
                A_mat = A_map
                print("Applied rotation from seed file to edge vectors")

    # compute distances from each edge to each root
    N_edges = len(A_mat)
    N_roots = len(roots_arr)
    cost = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)

    # candidate selection
    K = int(args.k)
    candidates: List[List[int]] = []
    for e in range(N_edges):
        idxs = np.argsort(cost[e])[:K]
        cand = [int(i) for i in idxs]
        candidates.append(cand)

    # ensure seed_edges are included in candidates and also capture forced assignments
    forced_assignments: Dict[int, int] = {}
    if seed_obj:
        for sd in seed_obj.get("seed_edges", []):
            eidx = sd.get("edge_index")
            ridx = sd.get("root_index")
            if eidx is not None and ridx is not None and 0 <= eidx < N_edges and 0 <= ridx < N_roots:
                if ridx not in candidates[eidx]:
                    candidates[eidx].append(ridx)
                forced_assignments[int(eidx)] = int(ridx)

    # Build CP-SAT model
    model = cp_model.CpModel()

    # create variables b_e_r only for candidates
    bvars: Dict[Tuple[int, int], cp_model.IntVar] = {}
    for e in range(N_edges):
        for r in candidates[e]:
            bvars[(e, r)] = model.NewBoolVar(f"b_e{e}_r{r}")

    # edge assignment constraints
    for e in range(N_edges):
        model.Add(sum(bvars[(e, r)] for r in candidates[e]) == 1)

    # root uniqueness (at most one edge per root among candidate links)
    root_to_edges: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for (e, r) in bvars:
        root_to_edges[r].append((e, r))
    for r, pairs in root_to_edges.items():
        model.Add(sum(bvars[p] for p in pairs) <= 1)

    # triangle constraints
    n, vertices, adj, _ = build_w33_graph()
    triangles = enumerate_triangles(n, adj)
    # map vertex pair to edge index
    edge_index = {edges[i]: i for i in range(len(edges))}

    for (a, b, c) in triangles:
        # oriented edges: (a,b), (b,c), (a,c)
        e_ab = edge_index[(a, b)] if (a, b) in edge_index else edge_index.get((b, a))
        e_bc = edge_index[(b, c)] if (b, c) in edge_index else edge_index.get((c, b))
        e_ac = edge_index[(a, c)] if (a, c) in edge_index else edge_index.get((c, a))
        if e_ab is None or e_bc is None or e_ac is None:
            continue
        # r_ab + r_bc - r_ac == 0  (coordinate-wise)
        for t in range(8):
            expr = []
            # sum over candidates for e_ab
            for r in candidates[e_ab]:
                coeff = int(roots[r][t])
                expr.append((bvars[(e_ab, r)], coeff))
            # e_bc
            for r in candidates[e_bc]:
                coeff = int(roots[r][t])
                expr.append((bvars[(e_bc, r)], coeff))
            # e_ac with negative sign
            for r in candidates[e_ac]:
                coeff = -int(roots[r][t])
                expr.append((bvars[(e_ac, r)], coeff))
            if not expr:
                continue
            # Convert to linear expression: sum(coeff * var) == 0
            model.Add(sum(coeff * var for (var, coeff) in expr) == 0)

    # optional forbids: load obstruction sets and add constraints to forbid exact combinations
    if getattr(args, 'forbid_json', None):
        try:
            forb = json.loads(open(args.forbid_json, encoding='utf-8').read())
            for entry in forb.get('obstruction_sets', []):
                edges_forbid = entry.get('set', [])
                roots_forbid = entry.get('roots', [])
                # pair edges->roots mapping: assume same length
                pairs = []
                for e, r in zip(edges_forbid, roots_forbid):
                    if (int(e), int(r)) in bvars:
                        pairs.append(bvars[(int(e), int(r))])
                if len(pairs) >= 1:
                    # forbid the simultaneous assignment of all listed pairs
                    model.Add(sum(pairs) <= max(0, len(pairs)-1))
        except Exception as e:
            print('Failed to load forbid JSON:', e)

    # enforce forced assignments (only if requested)
    if args.force_seed:
        for eidx, ridx in forced_assignments.items():
            if (eidx, ridx) in bvars:
                model.Add(bvars[(eidx, ridx)] == 1)
            else:
                # variable missing? create and force
                v = model.NewBoolVar(f"b_e{eidx}_r{ridx}_forced")
                bvars[(eidx, ridx)] = v
                model.Add(v == 1)
                # adding this var increases domain; original sum(...) == 1 will include it implicitly
    else:
        if forced_assignments:
            print(f"Seed present with {len(forced_assignments)} entries, but not enforcing them (use --force-seed to force). Using seed as soft preference via --seed-reward")

    # objective: minimize scaled assignment distance, optionally reward selecting seed root
    scale = float(args.cost_scale)
    seed_reward = float(getattr(args, 'seed_reward', 0.0))
    objective_terms = []
    for (e, r), var in bvars.items():
        c = cost[e, r]
        ic = int(round(c * scale))
        # reward if this matches the seed's root for this edge (soft preference)
        if e in forced_assignments and forced_assignments:
            seed_r = forced_assignments.get(e)
            if seed_r is not None and r == seed_r:
                ic = max(0, ic - int(round(seed_reward)))
        objective_terms.append(ic * var)
    model.Minimize(sum(objective_terms))

    # solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(args.time_limit)
    solver.parameters.num_search_workers = int(args.workers)
    solver.parameters.random_seed = int(args.seed)
    solver.parameters.log_search_progress = args.log

    print(f"Starting CP-SAT: edges={N_edges} vars={len(bvars)} triangles={len(triangles)} k={K} time_limit={args.time_limit}s")

    status = solver.Solve(model)
    status_name = solver.StatusName(status)
    print("Solver status:", status_name)

    res = {
        "status": status_name,
        "objective": None,
        "time_seconds": time.time() - t0,
        "k": K,
        "vars": len(bvars),
        "triangles": len(triangles),
        "assignments": None,
    }

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        res["objective"] = solver.ObjectiveValue()
        # extract assignment
        assignment = {}
        for e in range(N_edges):
            found = False
            for r in candidates[e]:
                v = bvars.get((e, r))
                if v is None:
                    continue
                if solver.Value(v) == 1:
                    assignment[str(e)] = int(r)
                    found = True
                    break
            if not found:
                # fallback search across all roots
                for r in range(N_roots):
                    v = bvars.get((e, r))
                    if v is not None and solver.Value(v) == 1:
                        assignment[str(e)] = int(r)
                        found = True
                        break
        res["assignments"] = assignment

        # attempt to build vertex positions from assignments
        roots_map = {i: tuple(roots[i]) for i in range(len(roots))}
        pos = {0: tuple([0] * 8)}
        edge_to_root = {}
        # oriented edges are edges list with i<j mapping to pos_i - pos_j = root
        changed = True
        while changed:
            changed = False
            for ei, (i, j) in enumerate(edges):
                if str(ei) not in assignment:
                    continue
                r_idx = assignment[str(ei)]
                rvec = roots_map[r_idx]
                if i in pos and j not in pos:
                    # pos_j = pos_i - rvec
                    pos[j] = tuple(p_i - r for p_i, r in zip(pos[i], rvec))
                    changed = True
                elif j in pos and i not in pos:
                    pos[i] = tuple(p_j + r for p_j, r in zip(pos[j], rvec))
                    changed = True
        # check completeness
        if len(pos) == len(vertices):
            # verify edge differences are roots
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
        else:
            res["found"] = False
            res["positions_partial"] = {str(k): list(v) for k, v in pos.items()}
            res["assigned_vertices"] = len(pos)
    else:
        res["found"] = False

    out_path = os.path.join(os.getcwd(), "checks", "PART_CVII_e8_embedding_cpsat.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print("Wrote", out_path)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
