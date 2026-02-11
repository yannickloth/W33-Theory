#!/usr/bin/env python3
"""Backtracking search constrained to symmetry-pruned candidate sets.

Heuristics:
- MRV (smallest candidate set) edge ordering
- Cost-sorted candidate ordering per edge
- Propagation: when two edges of a triangle are assigned, deduce the third
- Use seed edges / partials as initial assignments

Writes `checks/PART_CVII_e8_backtrack_pruned.json` with result.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple

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
    assert len(roots_list) == 240
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
    return X, edges, adj


def build_edge_vectors(X: np.ndarray, edges: List[Tuple[int, int]]):
    E = []
    for i, j in edges:
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


class Backtracker:
    def __init__(
        self,
        candidates: List[List[int]],
        roots: List[Tuple[int, ...]],
        edges: List[Tuple[int, int]],
        triangles: List[Tuple[int, int, int]],
        cost: np.ndarray,
        time_limit: float = 1800.0,
        initial_assign: Dict[int, int] = None,
        verbose: bool = False,
    ):
        self.verbose = verbose
        # sort candidates by cost
        self.candidates = [
            list(sorted(c, key=lambda r: cost[e, r])) for e, c in enumerate(candidates)
        ]
        self.roots = roots
        self.edges = edges
        self.triangles = triangles
        self.cost = cost
        self.N_edges = len(edges)
        self.root_used: Set[int] = set()
        self.edge_assign: Dict[int, int] = {}
        self.time_limit = time_limit
        self.t0 = time.time()
        self.nodes = 0
        self.initially_inconsistent = False
        self.conflicts: List[int] = []

        # apply initial_assign if present
        if initial_assign:
            for e, r in initial_assign.items():
                if e < 0 or e >= self.N_edges:
                    print(f"Warning: initial assignment edge {e} out of range")
                    self.initially_inconsistent = True
                    return
                if r < 0 or r >= len(self.roots):
                    print(f"Warning: initial assignment root {r} out of range")
                    self.initially_inconsistent = True
                    return
                if r in self.root_used:
                    print(f"Warning: initial assignments reuse root {r}")
                    self.initially_inconsistent = True
                    return
                if r not in self.candidates[e]:
                    self.candidates[e].append(r)
                self.edge_assign[e] = r
                self.root_used.add(r)
            # remove used roots from other candidates
            for e in range(self.N_edges):
                if e in self.edge_assign:
                    continue
                self.candidates[e] = [
                    r for r in self.candidates[e] if r not in self.root_used
                ]
                if not self.candidates[e]:
                    print(f"Initial assignments eliminated all candidates for edge {e}")
                    self.conflicts.append(e)
                    self.initially_inconsistent = True
                    return

        # map edge->triangles
        self.edge_to_tri = defaultdict(list)
        edge_index = {edges[i]: i for i in range(len(edges))}
        for ti, (a, b, c) in enumerate(triangles):
            # oriented edges as stored (i<j)
            e_ab = edge_index.get((a, b), edge_index.get((b, a)))
            e_bc = edge_index.get((b, c), edge_index.get((c, b)))
            e_ac = edge_index.get((a, c), edge_index.get((c, a)))
            if e_ab is not None:
                self.edge_to_tri[e_ab].append((e_ab, e_bc, e_ac))
            if e_bc is not None:
                self.edge_to_tri[e_bc].append((e_ab, e_bc, e_ac))
            if e_ac is not None:
                self.edge_to_tri[e_ac].append((e_ab, e_bc, e_ac))

    def time_exceeded(self):
        return (time.time() - self.t0) > self.time_limit

    def select_edge(self):
        # MRV: smallest candidate set among unassigned edges
        best_e = None
        best_len = 1_000_000
        for e in range(self.N_edges):
            if e in self.edge_assign:
                continue
            le = len(self.candidates[e])
            if le < best_len:
                best_len = le
                best_e = e
                if best_len <= 2:
                    break
        if self.verbose:
            print(f"select_edge -> e={best_e} candidates={best_len}")
        return best_e

    def check_triangle_consistent(self, tri_tuple):
        # tri_tuple = (e_ab, e_bc, e_ac)
        e_ab, e_bc, e_ac = tri_tuple
        vals = []
        for e in (e_ab, e_bc, e_ac):
            vals.append(self.edge_assign.get(e))
        # If two are assigned, deduce the third and check it's allowed
        assigned_count = sum(1 for v in vals if v is not None)
        if assigned_count < 2:
            return True
        # Using relation r_ab + r_bc - r_ac == 0 => r_ac = r_ab + r_bc
        # Get indices mapping to roots
        if vals[0] is not None and vals[1] is not None and vals[2] is None:
            r_ab = self.roots[vals[0]]
            r_bc = self.roots[vals[1]]
            r_ac_needed = tuple(int(a + b) for a, b in zip(r_ab, r_bc))
            # find index of r_ac_needed in roots
            # precompute mapping? for now linear search: build map outside
            return self.root_tuple_to_index.get(r_ac_needed) in self.candidates[e_ac]
        if vals[1] is not None and vals[2] is not None and vals[0] is None:
            r_bc = self.roots[vals[1]]
            r_ac = self.roots[vals[2]]
            r_ab_needed = tuple(int(a - b) for a, b in zip(r_ac, r_bc))
            return self.root_tuple_to_index.get(r_ab_needed) in self.candidates[e_ab]
        if vals[0] is not None and vals[2] is not None and vals[1] is None:
            r_ab = self.roots[vals[0]]
            r_ac = self.roots[vals[2]]
            r_bc_needed = tuple(int(a - b) for a, b in zip(r_ac, r_ab))
            return self.root_tuple_to_index.get(r_bc_needed) in self.candidates[e_bc]
        # If all three assigned, check equality
        if vals[0] is not None and vals[1] is not None and vals[2] is not None:
            r_ab = self.roots[vals[0]]
            r_bc = self.roots[vals[1]]
            r_ac = self.roots[vals[2]]
            return all(a + b - c == 0 for a, b, c in zip(r_ab, r_bc, r_ac))
        return True

    def initial_setup(self):
        # build mapping from tuple->index for roots
        self.root_tuple_to_index = {tuple(r): i for i, r in enumerate(self.roots)}

    def search(self):
        self.initial_setup()
        # optional: use simple greedy seeding to assign edges with only 1 candidate
        changed = True
        while changed:
            changed = False
            for e in range(self.N_edges):
                if e in self.edge_assign:
                    continue
                # Filter candidate list to remove used roots
                self.candidates[e] = [
                    r for r in self.candidates[e] if r not in self.root_used
                ]
                if not self.candidates[e]:
                    # record conflict edges and abort
                    self.conflicts = [
                        i for i in range(self.N_edges) if not self.candidates[i]
                    ]
                    return False
                if len(self.candidates[e]) == 1:
                    r = self.candidates[e][0]
                    self.edge_assign[e] = r
                    self.root_used.add(r)
                    changed = True
        # start recursive DFS
        return self._dfs()

    def _dfs(self):
        if self.time_exceeded():
            return False
        if len(self.edge_assign) == self.N_edges:
            return True
        self.nodes += 1
        if self.nodes % 1000 == 0 and self.verbose:
            print(
                f"nodes={self.nodes} assigned={len(self.edge_assign)} time={time.time()-self.t0:.1f}s"
            )
        e = self.select_edge()
        if e is None:
            return False
        # sort candidates by cost
        cand_list = sorted(self.candidates[e], key=lambda r: self.cost[e, r])
        for r in cand_list:
            if r in self.root_used:
                continue
            # quick triangle consistency check
            ok = True
            for tri in self.edge_to_tri.get(e, []):
                # if tri includes exactly one assigned and two unassigned, cannot deduce
                if not self.check_triangle_consistent(tri):
                    ok = False
                    break
            if not ok:
                continue
            # assign
            self.edge_assign[e] = r
            self.root_used.add(r)
            # propagate: reduce candidate lists for adjacent edges by removing r
            modified = []
            for ee in range(self.N_edges):
                if ee in self.edge_assign:
                    continue
                before = len(self.candidates[ee])
                newlist = [x for x in self.candidates[ee] if x != r]
                if len(newlist) != before:
                    modified.append((ee, self.candidates[ee]))
                    self.candidates[ee] = newlist
                    if not self.candidates[ee]:
                        ok = False
                        self.conflicts.append(ee)
                        break
            if ok:
                # also check triangles that now have two assigned; if they force third, ensure it's allowed
                forced_assigns = []
                inconsistent = False
                for tri in self.edge_to_tri.get(e, []):
                    e_ab, e_bc, e_ac = tri
                    vals = [self.edge_assign.get(x) for x in (e_ab, e_bc, e_ac)]
                    if sum(1 for v in vals if v is not None) == 2:
                        # deduce third
                        # find index of None
                        none_idx = [i for i, v in enumerate(vals) if v is None][0]
                        if none_idx == 0:
                            # need r_ab = r_ac - r_bc
                            r_ac = self.roots[vals[2]] if vals[2] is not None else None
                            r_bc = self.roots[vals[1]] if vals[1] is not None else None
                            if r_ac is not None and r_bc is not None:
                                needed = tuple(int(a - b) for a, b in zip(r_ac, r_bc))
                                idx_needed = self.root_tuple_to_index.get(needed)
                                if (
                                    idx_needed is None
                                    or idx_needed in self.root_used
                                    or idx_needed not in self.candidates[e_ab]
                                ):
                                    inconsistent = True
                                    break
                                # forced assignment
                                forced_assigns.append((e_ab, idx_needed))
                        elif none_idx == 1:
                            r_ab = self.roots[vals[0]] if vals[0] is not None else None
                            r_ac = self.roots[vals[2]] if vals[2] is not None else None
                            if r_ab is not None and r_ac is not None:
                                needed = tuple(int(a - b) for a, b in zip(r_ac, r_ab))
                                idx_needed = self.root_tuple_to_index.get(needed)
                                if (
                                    idx_needed is None
                                    or idx_needed in self.root_used
                                    or idx_needed not in self.candidates[e_bc]
                                ):
                                    inconsistent = True
                                    break
                                forced_assigns.append((e_bc, idx_needed))
                        else:
                            r_ab = self.roots[vals[0]] if vals[0] is not None else None
                            r_bc = self.roots[vals[1]] if vals[1] is not None else None
                            if r_ab is not None and r_bc is not None:
                                needed = tuple(int(a + b) for a, b in zip(r_ab, r_bc))
                                idx_needed = self.root_tuple_to_index.get(needed)
                                if (
                                    idx_needed is None
                                    or idx_needed in self.root_used
                                    or idx_needed not in self.candidates[e_ac]
                                ):
                                    inconsistent = True
                                    break
                                forced_assigns.append((e_ac, idx_needed))
                if not inconsistent:
                    # apply forced assigns
                    applied_forced = []
                    for ee, rr in forced_assigns:
                        if ee in self.edge_assign:
                            if self.edge_assign[ee] != rr:
                                inconsistent = True
                                break
                            else:
                                continue
                        self.edge_assign[ee] = rr
                        self.root_used.add(rr)
                        applied_forced.append((ee, rr))
                    if not inconsistent:
                        # recurse
                        result = self._dfs()
                        if result:
                            return True
                    # undo forced assigns
                    for ee, rr in applied_forced:
                        del self.edge_assign[ee]
                        self.root_used.remove(rr)
                # else will fall through and undo changes
            # undo assignment and candidate modifications
            for ee, old in reversed(modified):
                self.candidates[ee] = old
            if e in self.edge_assign:
                del self.edge_assign[e]
            if r in self.root_used:
                self.root_used.remove(r)
            if self.time_exceeded():
                return False
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=int, default=0)
    parser.add_argument("--m", type=int, default=24)
    parser.add_argument("--k", type=int, default=30)
    parser.add_argument("--time-limit", type=float, default=600.0)
    parser.add_argument(
        "--seed-json",
        type=str,
        default=os.path.join("checks", "PART_CVII_e8_embedding_attempt_seed.json"),
    )
    parser.add_argument(
        "--use-partial",
        action="store_true",
        help="Use partial mapping from checks/PART_CVII_e8_embedding_backtrack_partial.json if present (soft)",
    )
    parser.add_argument(
        "--force-partial",
        action="store_true",
        help="Force partial mapping as initial assignments (hard)",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Print debug info during search"
    )
    args = parser.parse_args()

    X, edges, adj = compute_embedding_matrix()
    A_mat = build_edge_vectors(X, edges)

    roots = generate_scaled_e8_roots()
    roots_arr = np.array(roots, dtype=int)
    roots_unit = roots_arr.astype(float) / np.linalg.norm(
        roots_arr.astype(float), axis=1, keepdims=True
    )

    N_edges = len(A_mat)
    cost = np.linalg.norm(A_mat[:, None, :] - roots_unit[None, :, :], axis=2)

    # per-edge top-K
    candidates = []
    for e in range(N_edges):
        idxs = np.argsort(cost[e])[: int(args.k)]
        cand = [int(i) for i in idxs]
        candidates.append(cand)

    # include seed roots in candidates
    seed_obj = None
    if args.seed_json and os.path.exists(args.seed_json):
        seed_obj = json.load(open(args.seed_json))
        for sd in seed_obj.get("seed_edges", []):
            eidx = sd.get("edge_index")
            ridx = sd.get("root_index")
            if (
                eidx is not None
                and ridx is not None
                and 0 <= eidx < N_edges
                and 0 <= ridx < len(roots)
            ):
                if ridx not in candidates[eidx]:
                    candidates[eidx].append(ridx)

    # base orbit pruning: take top-M roots by mean cost over edges incident to base vertex
    base = int(args.base)
    edges_incident = [i for i, (u, v) in enumerate(edges) if u == base or v == base]
    mean_cost = (
        cost[edges_incident].mean(axis=0)
        if edges_incident
        else np.full((len(roots),), np.inf)
    )
    top_m_roots = list(np.argsort(mean_cost)[: int(args.m)])
    top_m_set = set(top_m_roots)
    # prune only incident edges
    for e in range(N_edges):
        if e in edges_incident:
            new = [
                r
                for r in candidates[e]
                if r in top_m_set
                or (
                    seed_obj
                    and any(
                        sd.get("edge_index") == e and sd.get("root_index") == r
                        for sd in seed_obj.get("seed_edges", [])
                    )
                )
            ]
            if not new:
                # if pruning removed all, keep original
                continue
            candidates[e] = new

    triangles = enumerate_triangles(len(adj), adj)

    partial_assign = None
    if args.use_partial:
        partial_path = os.path.join(
            "checks", "PART_CVII_e8_embedding_backtrack_partial.json"
        )
        if os.path.exists(partial_path):
            try:
                partial_obj = json.load(open(partial_path))
                e2r = partial_obj.get("edge_to_root", {})
                partial_assign = {int(k): int(v) for k, v in e2r.items()}
                print(
                    f"Loaded partial mapping with {len(partial_assign)} edge->root entries"
                )
            except Exception as exc:
                print("Failed to load partial mapping:", exc)

    # If we have a partial mapping, by default treat it as a soft boost to candidate lists
    # If --force-partial is set, force those assignments as initial assignments
    initial_assign = None
    if partial_assign:
        if not getattr(args, "force_partial", False):
            # ensure assigned roots are included in candidate lists, but don't force their assignment
            assigned_roots = set(partial_assign.values())
            for e, r in partial_assign.items():
                if r not in candidates[e]:
                    candidates[e].append(r)
            # remove assigned roots from other edges' candidates and extend if empty
            for e in range(N_edges):
                if e in partial_assign:
                    continue
                candidates[e] = [r for r in candidates[e] if r not in assigned_roots]
                if not candidates[e]:
                    order = list(np.argsort(cost[e]))
                    extended = [int(r) for r in order if r not in assigned_roots]
                    if not extended:
                        continue
                    candidates[e] = extended[: max(4 * int(args.k), 10)]
        else:
            # force partial mapping
            initial_assign = partial_assign

    bt = Backtracker(
        candidates,
        roots,
        edges,
        triangles,
        cost,
        time_limit=float(args.time_limit),
        initial_assign=initial_assign,
        verbose=bool(args.debug),
    )
    if bt.initially_inconsistent:
        print("Initial assignments inconsistent; aborting")
        out = {
            "found": False,
            "nodes": bt.nodes,
            "time_seconds": time.time() - bt.t0,
            "assigned": len(bt.edge_assign),
            "assignments": {str(k): int(v) for k, v in bt.edge_assign.items()},
            "error": "initial_inconsistent",
        }
        out_path = os.path.join("checks", "PART_CVII_e8_backtrack_pruned.json")
        from utils.json_safe import dump_json

        dump_json(out, out_path, indent=2)
        print("Wrote", out_path)
        print(json.dumps(out, indent=2, default=str))
        return

    print(
        f"Starting backtracking: edges={N_edges} initial_vars={sum(len(c) for c in candidates)} time_limit={args.time_limit}s"
    )
    ok = bt.search()
    out = {
        "found": bool(ok),
        "nodes": bt.nodes,
        "time_seconds": time.time() - bt.t0,
        "assigned": len(bt.edge_assign),
        "assignments": {str(k): int(v) for k, v in bt.edge_assign.items()},
        "conflicts": bt.conflicts,
    }
    out_path = os.path.join("checks", "PART_CVII_e8_backtrack_pruned.json")
    from utils.json_safe import dump_json

    dump_json(out, out_path, indent=2)
    print("Wrote", out_path)
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
