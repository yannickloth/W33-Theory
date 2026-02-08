#!/usr/bin/env python3
"""Backtracking search to find a W33 -> E8 embedding from candidate lists.

Heuristic: MRV (minimum remaining values) + forward checking with triangle propagation.
Usage: python scripts/backtrack_candidate_search.py --k 30 --time-limit 60 --seed-json checks/PART_CVII_e8_embedding_attempt_seed.json
"""
from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple

import numpy as np


def generate_scaled_e8_roots() -> List[Tuple[int, ...]]:
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


class Backtracker:
    def __init__(self, candidates: List[List[int]], edges: List[Tuple[int, int]], roots: List[Tuple[int, ...]], seed_assign: Dict[int, int] = None, seed_first: bool = True):
        self.candidates = [list(c) for c in candidates]
        self.edges = edges
        self.N_edges = len(edges)
        self.N_roots = len(roots)
        self.roots = roots
        self.seed_assign = seed_assign or {}
        self.seed_first = seed_first

        # triangles in terms of edge indices
        n, vertices, adj, _ = build_w33_graph()
        tris = enumerate_triangles(n, adj)
        # map vertex pair to edge index
        edge_index = {edges[i]: i for i in range(len(edges))}
        edge_index.update({(j, i): idx for (i, j), idx in edge_index.items()})
        self.tri_edges = []
        for (a, b, c) in tris:
            try:
                e_ab = edge_index[(a, b)]
                e_bc = edge_index[(b, c)]
                e_ac = edge_index[(a, c)]
                self.tri_edges.append((e_ab, e_bc, e_ac))
            except Exception:
                continue

        # adjacency of triangles per edge
        self.edge_to_tris = defaultdict(list)
        for tidx, (e1, e2, e3) in enumerate(self.tri_edges):
            self.edge_to_tris[e1].append((tidx, (e1, e2, e3)))
            self.edge_to_tris[e2].append((tidx, (e1, e2, e3)))
            self.edge_to_tris[e3].append((tidx, (e1, e2, e3)))

        # ordering: try to prefer seed root first if available

    def search(self, time_limit: float = 60.0, max_nodes: int = 2_000_000) -> Tuple[bool, Dict[int, int], int]:
        start = time.time()
        self.start_time = start
        self.end_time = start + time_limit
        self.max_nodes = max_nodes
        self.nodes = 0
        self.best_assign = {}

        assignments: Dict[int, int] = {}
        used_roots: Set[int] = set()

        # initial forward-checking domain reduction
        domains = [set(c) for c in self.candidates]

        # function to compute domain considering used roots
        def domain_of(e):
            return [r for r in self.candidates[e] if r not in used_roots]

        # initial MRV heuristic: will be recomputed at each node

        success = self._dfs(assignments, used_roots, domains)
        return success, (self.best_assign if not success else assignments), self.nodes

    def _dfs(self, assignments: Dict[int, int], used_roots: Set[int], domains: List[Set[int]]) -> bool:
        # time / node bounds
        self.nodes += 1
        if self.nodes % 1000 == 0:
            if time.time() > self.end_time or self.nodes > self.max_nodes:
                return False
        if time.time() > self.end_time or self.nodes > self.max_nodes:
            return False

        # update best
        if len(assignments) > len(self.best_assign):
            self.best_assign = dict(assignments)

        if len(assignments) == self.N_edges:
            return True

        # MRV: pick unassigned edge with smallest domain
        min_e = None
        min_dom = None
        for e in range(self.N_edges):
            if e in assignments:
                continue
            dom = [r for r in domains[e] if r not in used_roots]
            # propagate triangle-derived requirements: if any triangle has two assigned edges and this is third, required root must be r_ab + r_bc
            forced_vals = None
            for (tidx, (e1, e2, e3)) in self.edge_to_tris[e]:
                # if two of the edges are assigned
                assigned = []
                for ee in (e1, e2, e3):
                    if ee in assignments:
                        assigned.append((ee, assignments[ee]))
                if len(assigned) == 2:
                    # compute required root for the third
                    # identify orientation: need to compute r_ab + r_bc - r_ac == 0
                    # find mapping such that assigned edges correspond to (ab, bc) or permutations
                    # brute force try to compute required root r_third = r_x + r_y (with appropriate sign)
                    e_set = (e1, e2, e3)
                    # using edges (a,b),(b,c),(a,c) ordering from tri_edges
                    # if e is e_ac and e1,e2 are assigned then r_ac must equal r_ab + r_bc
                    # identify which indices correspond
                    # We'll use tri definition: (e_ab,e_bc,e_ac)
                    if (e1, e2, e3) == (e1, e2, e3):
                        # check cases
                        if e == e3 and e1 in assignments and e2 in assignments:
                            r_ab = assignments[e1]
                            r_bc = assignments[e2]
                            r_req = tuple(x + y for x, y in zip(self.roots[r_ab], self.roots[r_bc]))
                            # find root index matching r_req
                            ridx = None
                            # create mapping once per construction could be heavy; we do linear scan
                            for idx, rv in enumerate(self.roots):
                                if rv == r_req:
                                    ridx = idx
                                    break
                            if ridx is None:
                                return False  # impossible
                            forced_vals = set([ridx]) if forced_vals is None else forced_vals & set([ridx])
                        # other permutations: if e is e1 (ab) and e2 (bc) and e3 (ac) assigned etc.
                        if e == e1 and e2 in assignments and e3 in assignments:
                            # r_ab = r_ac - r_bc
                            r_ac = self.roots[assignments[e3]]
                            r_bc = self.roots[assignments[e2]]
                            r_req = tuple(a - b for a, b in zip(r_ac, r_bc))
                            ridx = None
                            for idx, rv in enumerate(self.roots):
                                if rv == r_req:
                                    ridx = idx
                                    break
                            if ridx is None:
                                return False
                            forced_vals = set([ridx]) if forced_vals is None else forced_vals & set([ridx])
                        if e == e2 and e1 in assignments and e3 in assignments:
                            # r_bc = r_ac - r_ab
                            r_ac = self.roots[assignments[e3]]
                            r_ab = self.roots[assignments[e1]]
                            r_req = tuple(a - b for a, b in zip(r_ac, r_ab))
                            ridx = None
                            for idx, rv in enumerate(self.roots):
                                if rv == r_req:
                                    ridx = idx
                                    break
                            if ridx is None:
                                return False
                            forced_vals = set([ridx]) if forced_vals is None else forced_vals & set([ridx])
            if forced_vals is not None:
                dom = [r for r in dom if r in forced_vals]
            if min_dom is None or len(dom) < len(min_dom):
                min_dom = dom
                min_e = e
            if len(min_dom) == 0:
                # dead end
                return False

        # order values: seed first if present
        order = list(min_dom)
        seed_r = self.seed_assign.get(min_e)
        if self.seed_first and seed_r is not None and seed_r in order:
            order.remove(seed_r)
            order.insert(0, seed_r)

        # try each value
        for r in order:
            if r in used_roots:
                continue
            # assign
            assignments[min_e] = r
            used_roots.add(r)

            # forward-check: record domains we changed to restore later
            changed = []
            consistent = True

            # for any triangle where this assignment with another assigned edge forces the third, check feasibility and pre-assign if possible
            queue = deque()
            queue.append(min_e)
            forced_stack = []
            while queue and consistent:
                ee = queue.popleft()
                for (tidx, (e1, e2, e3)) in self.edge_to_tris[ee]:
                    # if two assigned and third unassigned -> deduce
                    assigned = [(ed, assignments[ed]) for ed in (e1, e2, e3) if ed in assignments]
                    unassigned = [ed for ed in (e1, e2, e3) if ed not in assignments]
                    if len(assigned) == 2 and len(unassigned) == 1:
                        # find required root for the missing edge as above
                        # detect which is missing and compute required
                        missing = unassigned[0]
                        # identify positions
                        # tri tuple is (e_ab,e_bc,e_ac)
                        e_ab, e_bc, e_ac = (e1, e2, e3)
                        try:
                            if missing == e_ac and e_ab in assignments and e_bc in assignments:
                                r_ab = assignments[e_ab]
                                r_bc = assignments[e_bc]
                                r_req = tuple(x + y for x, y in zip(self.roots[r_ab], self.roots[r_bc]))
                            elif missing == e_ab and e_ac in assignments and e_bc in assignments:
                                r_ac = self.roots[assignments[e_ac]]
                                r_bc = self.roots[assignments[e_bc]]
                                r_req = tuple(a - b for a, b in zip(r_ac, r_bc))
                            elif missing == e_bc and e_ac in assignments and e_ab in assignments:
                                r_ac = self.roots[assignments[e_ac]]
                                r_ab = self.roots[assignments[e_ab]]
                                r_req = tuple(a - b for a, b in zip(r_ac, r_ab))
                            else:
                                continue
                        except Exception:
                            consistent = False
                            break
                        ridx = None
                        for idx, rv in enumerate(self.roots):
                            if rv == r_req:
                                ridx = idx
                                break
                        if ridx is None:
                            consistent = False
                            break
                        # check if ridx is in domain for missing and not used
                        if ridx in used_roots:
                            consistent = False
                            break
                        if ridx not in domains[missing]:
                            # cannot satisfy
                            consistent = False
                            break
                        # otherwise, force assign missing= ridx
                        assignments[missing] = ridx
                        used_roots.add(ridx)
                        forced_stack.append(missing)
                        queue.append(missing)

            if consistent:
                # recurse
                if self._dfs(assignments, used_roots, domains):
                    return True

            # rollback forced assignments
            for m in forced_stack:
                used_roots.remove(assignments[m])
                del assignments[m]

            # rollback this assignment
            if r in used_roots:
                used_roots.remove(r)
            if min_e in assignments:
                del assignments[min_e]

        return False


def build_candidates(k: int, seed_json: Optional[str] = None):
    X, edges = compute_embedding_matrix()
    A_mat = np.vstack([(X[i] - X[j]) / (np.linalg.norm(X[i] - X[j]) + 1e-12) for (i, j) in edges])
    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(roots_arr.astype(float), axis=1, keepdims=True)
    cost = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)

    N_edges = len(A_mat)
    candidates: List[List[int]] = []
    for e in range(N_edges):
        idxs = np.argsort(cost[e])[:k]
        candidates.append([int(i) for i in idxs])

    seed_assign = {}
    if seed_json:
        try:
            s = json.load(open(seed_json))
            for sd in s.get("seed_edges", []):
                eidx = sd.get("edge_index")
                ridx = sd.get("root_index")
                if eidx is not None and ridx is not None:
                    seed_assign[int(eidx)] = int(ridx)
                    if ridx not in candidates[eidx]:
                        candidates[eidx].append(ridx)
        except Exception:
            pass
    return candidates, edges, roots, seed_assign


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=30)
    parser.add_argument("--time-limit", type=float, default=60.0)
    parser.add_argument("--max-nodes", type=int, default=2000000)
    parser.add_argument("--seed-json", type=str, default=None)
    parser.add_argument("--seed-first", action="store_true", default=True)
    args = parser.parse_args()

    candidates, edges, roots, seed_assign = build_candidates(args.k, seed_json=args.seed_json)
    print(f"Built candidates: k={args.k} edges={len(edges)} roots={len(roots)} seed_edges={len(seed_assign)}")

    bt = Backtracker(candidates, edges, roots, seed_assign, seed_first=args.seed_first)
    start = time.time()
    success, best, nodes = bt.search(time_limit=args.time_limit, max_nodes=args.max_nodes)
    end = time.time()
    if success:
        print(f"Found full assignment in {end-start:.2f}s nodes={nodes}")
        # write assignment
        out = {"assignments": {str(k): int(v) for k, v in best.items()}, "time_seconds": end-start, "nodes": nodes}
        with open('checks/PART_CVII_e8_embedding_backtrack.json', 'w') as f:
            json.dump(out, f, indent=2)
        print('Wrote checks/PART_CVII_e8_embedding_backtrack.json')
    else:
        print(f"No full assignment (best={len(best)} assigned) after {end-start:.2f}s nodes={nodes}")
        # convert edge->root assignment to vertex positions (partial) for bootstrap
        def assignment_to_positions(edges, assignment, roots):
            pos = {0: tuple([0] * 8)}
            changed = True
            while changed:
                changed = False
                for ei, (i, j) in enumerate(edges):
                    key = ei
                    if key in assignment:
                        r_idx = assignment[key]
                        rvec = roots[r_idx]
                        if i in pos and j not in pos:
                            pos[j] = tuple(p_i - r for p_i, r in zip(pos[i], rvec))
                            changed = True
                        elif j in pos and i not in pos:
                            pos[i] = tuple(p_j + r for p_j, r in zip(pos[j], rvec))
                            changed = True
            return pos

        positions = assignment_to_positions(edges, best, [tuple(r) for r in roots])
        out = {
            "best_assigned": len(best),
            "time_seconds": end-start,
            "nodes": nodes,
            "best": {"pos": {str(k): list(v) for k, v in positions.items()}, "max_assigned": len(best)},
            "edge_to_root": {str(k): int(v) for k, v in best.items()},
        }
        with open('checks/PART_CVII_e8_embedding_backtrack_partial.json', 'w') as f:
            json.dump(out, f, indent=2)
        print('Wrote checks/PART_CVII_e8_embedding_backtrack_partial.json (with positions & edge_to_root)')


if __name__ == '__main__':
    main()
