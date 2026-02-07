"""Backtracking search to embed W33 vertices into 8D so that each edge vector
is an E8 root. Runs a configurable number of attempts and respects a time limit.
Writes checks/PART_CVII_e8_embedding_sage.json with the result (found / not found)
for reproducible provenance.

Usage (examples):
  sage -python sage/find_e8_embedding_backtrack.sage --time-limit 300 --initial-attempts 2000

This is intentionally heuristic: it tries randomized initial neighbor root picks,
then propagates vertex positions by backtracking with strong pruning.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import deque
from itertools import product
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

# Use only standard Python integer arithmetic to keep determinism inside Sage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "checks" / "PART_CVII_e8_embedding_sage.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

Vector = Tuple[int, ...]  # scaled-by-2 integer vector representation


def generate_scaled_e8_roots() -> List[Vector]:
    """Return E8 roots scaled by 2 so coordinates are integers.

    Type1: permutations of (±2, ±2, 0, 0, 0, 0, 0, 0)
    Type2: (±1)^8 with an even number of negative signs (corresponds to ±1/2 original)
    After scaling, all root vectors satisfy sum(coord^2) == 8.
    """
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
    # Type 2
    for signs in product((-1, 1), repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            roots.add(tuple(int(s) for s in signs))
    roots_list = sorted(list(roots))
    assert len(roots_list) == 240, f"expected 240 roots, got {len(roots_list)}"
    return roots_list


def build_w33_graph() -> Tuple[int, List[Vector], List[List[int]]]:
    """Return n=40, list of projective representatives (tuples in F3^4), and adjacency list."""
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
    assert len(vertices) == 40

    def symp(x, y):
        return (x[0] * y[1] - x[1] * y[0] + x[2] * y[3] - x[3] * y[2]) % F

    n = len(vertices)
    adj: List[List[int]] = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if symp(vertices[i], vertices[j]) == 0:
                adj[i].append(j)
                adj[j].append(i)
    # sanity
    degrees = [len(adj[i]) for i in range(n)]
    assert set(degrees) == {12}
    return n, vertices, adj


def add_vec(a: Vector, b: Vector) -> Vector:
    return tuple(x + y for x, y in zip(a, b))


def sub_vec(a: Vector, b: Vector) -> Vector:
    return tuple(x - y for x, y in zip(a, b))


def neg_vec(a: Vector) -> Vector:
    return tuple(-x for x in a)


def canonical_root(root_list: List[Vector]) -> Vector:
    return root_list[0]


# -----------------------------------------------------------------------------
# Backtracking engine
# -----------------------------------------------------------------------------


def try_embedding(
    root_list: List[Vector],
    roots_set: Set[Vector],
    n: int,
    adj: List[List[int]],
    time_limit: float,
    max_initial_attempts: int,
    rng: random.Random,
):
    start = time.time()

    # BFS order by distance from 0 (we fix vertex 0 to origin)
    dist = [-1] * n
    q = deque([0])
    dist[0] = 0
    order = []
    while q:
        v = q.popleft()
        order.append(v)
        for w in adj[v]:
            if dist[w] == -1:
                dist[w] = dist[v] + 1
                q.append(w)
    # neighbors of 0
    neigh0 = adj[0]
    assert len(neigh0) == 12

    # neighbor adjacency matrix for the 12 neighbors
    neigh_index = {v: i for i, v in enumerate(neigh0)}
    neigh_adj = [[False] * 12 for _ in range(12)]
    for i, vi in enumerate(neigh0):
        for j, vj in enumerate(neigh0):
            if vi != vj and (vj in adj[vi]):
                neigh_adj[i][j] = True

    # candidate enumeration for initial neighbor roots: random sampling with pruning
    attempts = 0

    # Precompute small subset heuristic: often 2-sparse roots are useful
    two_sparse = [r for r in root_list if sum(1 for x in r if x != 0) == 2]
    candidate_pool = root_list

    # fix first root to canonical to break symmetries
    fixed_root = canonical_root(root_list)

    # diagnostics: track best partial assignment found across all attempts
    best: Dict[str, object] = {
        "max_assigned": 0,
        "edges_satisfied": 0,
        "attempt": None,
        "picked_indices": None,
        "pos": None,
        "time_at_best": None,
    }

    while attempts < max_initial_attempts and (time.time() - start) < time_limit:
        attempts += 1
        # sample a set of 12 distinct roots (first fixed)
        picked = [fixed_root]
        picked_set = {fixed_root}
        # mix: mostly take from two_sparse for speed, allow some chance of global pool
        while len(picked) < 12:
            if rng.random() < 0.6 and two_sparse:
                r = rng.choice(two_sparse)
            else:
                r = rng.choice(candidate_pool)
            if r in picked_set:
                continue
            picked.append(r)
            picked_set.add(r)

        # Map neighbor index -> root
        mapping = {neigh0[i]: picked[i] for i in range(12)}

        # check neighbor internal adjacency difference constraints quickly
        ok = True
        for i in range(12):
            for j in range(i + 1, 12):
                vi = neigh0[i]
                vj = neigh0[j]
                if neigh_adj[i][j]:
                    diff = sub_vec(mapping[vj], mapping[vi])
                    if diff not in roots_set and neg_vec(diff) not in roots_set:
                        ok = False
                        break
            if not ok:
                break
        if not ok:
            continue

        # We have a promising seed; try to propagate
        pos: Dict[int, Vector] = {}
        pos[0] = (0,) * 8
        for v, r in mapping.items():
            pos[v] = neg_vec(r)  # set v = -r so v0 - v = r

        assigned = set(pos.keys())

        # per-attempt local best tracker
        local_best_assigned = len(assigned)

        # helper: get candidate positions for vertex v consistent with assigned neighbors
        def candidates_for(v: int) -> List[Vector]:
            assigned_neighbors = [w for w in adj[v] if w in pos]
            if not assigned_neighbors:
                # arbitrary new vertex: can be pos of any assigned + root
                # but avoid collision with existing positions
                base = next(iter(pos.values()))
                cands = [add_vec(base, r) for r in root_list]
                return [c for c in cands if c not in pos.values()]
            # start with first neighbor's possibilities
            w0 = assigned_neighbors[0]
            base0 = pos[w0]
            cand_set = {add_vec(base0, r) for r in root_list}
            # intersect with other neighbors
            for w in assigned_neighbors[1:]:
                base = pos[w]
                possible = {add_vec(base, r) for r in root_list}
                cand_set &= possible
                if not cand_set:
                    break
            # filter collisions and global adjacency consistency with already assigned
            final = []
            for c in cand_set:
                if c in pos.values():
                    continue
                conflict = False
                for z, pz in pos.items():
                    if z == v:
                        continue
                    diff = sub_vec(c, pz)
                    is_root = diff in roots_set or neg_vec(diff) in roots_set
                    if z in adj[v]:
                        if not is_root:
                            conflict = True
                            break
                    else:
                        if is_root:
                            conflict = True
                            break
                if not conflict:
                    final.append(c)
            # sort candidates with heuristic: favor those with small L1 to origin
            final.sort(key=lambda x: sum(abs(t) for t in x))
            return final

        # DFS backtracking with time limit
        def dfs_assign():
            nonlocal local_best_assigned
            if (time.time() - start) >= time_limit:
                return None
            if len(assigned) > local_best_assigned:
                local_best_assigned = len(assigned)
            if len(assigned) == n:
                return dict(pos)
            # pick next unassigned vertex with max assigned neighbors
            cand_v = None
            best_num = -1
            for v in range(n):
                if v in assigned:
                    continue
                num = sum(1 for w in adj[v] if w in assigned)
                if num > best_num and num > 0:
                    best_num = num
                    cand_v = v
            if cand_v is None:
                # no vertices adjacent to assigned ones? pick any
                for v in range(n):
                    if v not in assigned:
                        cand_v = v
                        break
            cands = candidates_for(cand_v)
            rng.shuffle(cands)
            for c in cands:
                # assign
                pos[cand_v] = c
                assigned.add(cand_v)
                res = dfs_assign()
                if res is not None:
                    return res
                # backtrack
                assigned.remove(cand_v)
                del pos[cand_v]
                if (time.time() - start) >= time_limit:
                    return None
            return None

        sol = dfs_assign()

        # compute edges satisfied in partial pos
        edges_satisfied = 0
        for i in pos:
            for j in adj[i]:
                if j in pos and i < j:
                    diff = sub_vec(pos[i], pos[j])
                    if diff in roots_set or neg_vec(diff) in roots_set:
                        edges_satisfied += 1

        if sol is not None:
            # verify solution
            ok_all = True
            for i in range(n):
                for j in adj[i]:
                    if i < j:
                        diff = sub_vec(sol[i], sol[j])
                        if not (diff in roots_set or neg_vec(diff) in roots_set):
                            ok_all = False
                            break
                if not ok_all:
                    break
            if ok_all:
                # format result and return
                return {
                    "found": True,
                    "time_seconds": time.time() - start,
                    "attempts": attempts,
                    "positions": {str(k): list(v) for k, v in sol.items()},
                }

        # Update global best partial attempt if improved.
        if (
            local_best_assigned > best["max_assigned"]
            or (
                local_best_assigned == best["max_assigned"]
                and edges_satisfied > best["edges_satisfied"]
            )
        ):
            try:
                picked_indices = [root_list.index(r) for r in picked]
            except Exception:
                picked_indices = None
            best["max_assigned"] = local_best_assigned
            best["edges_satisfied"] = edges_satisfied
            best["attempt"] = attempts
            best["picked_indices"] = picked_indices
            best["pos"] = {str(k): list(v) for k, v in pos.items()}
            best["time_at_best"] = time.time() - start

    # no solution found
    return {
        "found": False,
        "time_seconds": time.time() - start,
        "attempts": attempts,
        "best": best,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--time-limit", type=float, default=300.0, help="total time limit in seconds")
    parser.add_argument("--initial-attempts", type=int, default=2000, help="random initial neighbor sampling attempts")
    parser.add_argument("--seed", type=int, default=123456, help="random seed")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    print("Generating E8 scaled roots...")
    root_list = generate_scaled_e8_roots()
    roots_set = set(root_list)
    print("Built E8 root list (scaled) of length", len(root_list))

    print("Building W33 adjacency...")
    n, vertices, adj = build_w33_graph()
    print("W33 n=", n, "edges=", sum(len(adj[i]) for i in range(n)) // 2)

    print("Starting heuristic backtracking attempt")
    res = try_embedding(root_list, roots_set, n, adj, args.time_limit, args.initial_attempts, rng)

    # write out artifact with summary
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    if res.get("found"):
        print("Found embedding — wrote:", str(OUT))
    else:
        print("No embedding found within limits — wrote:", str(OUT))


if __name__ == "__main__":
    main()
