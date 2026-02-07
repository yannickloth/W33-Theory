"""Bootstrap E8 embedding completion from a partial mapping.

Usage: python sage/bootstrap_from_partial.sage --partial-file <path> --time-limit 3600 --seed 42

Writes checks/PART_CVII_e8_embedding_bootstrap.json with result and diagnostics.
"""

import argparse
import json
import os
import time
import random
from typing import Dict, List, Tuple, Set
from collections import deque
import glob

Vector = Tuple[int, ...]

OUT = "checks/PART_CVII_e8_embedding_bootstrap.json"

# --- E8 roots (scaled by 2)

def generate_scaled_e8_roots() -> List[Vector]:
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


# --- W33 builder (same canonical reps as other scripts)

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
    assert len(vertices) == 40

    def symp(x, y):
        return (x[0] * y[1] - x[1] * y[0] + x[2] * y[3] - x[3] * y[2]) % F

    n = len(vertices)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if symp(vertices[i], vertices[j]) == 0:
                adj[i].append(j)
                adj[j].append(i)
    return n, vertices, adj


# --- vector helpers

def add_vec(a: Vector, b: Vector) -> Vector:
    return tuple(x + y for x, y in zip(a, b))


def sub_vec(a: Vector, b: Vector) -> Vector:
    return tuple(x - y for x, y in zip(a, b))


def neg_vec(a: Vector) -> Vector:
    return tuple(-x for x in a)


# --- utilities

def compute_edges_satisfied(pos: Dict[int, Vector], adj: List[List[int]], roots_set: Set[Vector]) -> int:
    edges_satisfied = 0
    for i in pos:
        for j in adj[i]:
            if j in pos and i < j:
                diff = sub_vec(pos[i], pos[j])
                if diff in roots_set or neg_vec(diff) in roots_set:
                    edges_satisfied += 1
    return edges_satisfied


def repair_partial(pos: Dict[int, Vector], adj: List[List[int]], roots_set: Set[Vector], max_remove: int = None):
    """Greedily remove vertices that participate in the most pairwise conflicts until no conflicts remain."""
    def count_conflicts(cur_pos: Dict[int, Vector]):
        counts = {v: 0 for v in cur_pos}
        for i in cur_pos:
            for j in cur_pos:
                if i == j:
                    continue
                diff = sub_vec(cur_pos[i], cur_pos[j])
                is_root = diff in roots_set or neg_vec(diff) in roots_set
                if j in adj[i]:
                    if not is_root:
                        counts[i] += 1
                else:
                    if is_root:
                        counts[i] += 1
        return counts

    cur = dict(pos)
    removed = []
    while True:
        counts = count_conflicts(cur)
        if not counts:
            break
        maxc = max(counts.values())
        if maxc == 0:
            break
        # pick a vertex with max conflicts (tie-breaker by index)
        victim = max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
        del cur[victim]
        removed.append(victim)
        if max_remove and len(removed) >= max_remove:
            break
    return cur, removed


def find_best_partial_in_checks() -> str:
    candidates = glob.glob("checks/**/PART_CVII_e8_embedding_sage.json", recursive=True)
    best_file = None
    best_assigned = -1
    for c in candidates:
        try:
            d = json.load(open(c))
            if d.get("found"):
                continue
            b = d.get("best", {})
            m = b.get("max_assigned", 0)
            if m > best_assigned:
                best_assigned = m
                best_file = c
        except Exception:
            continue
    # fallback
    if not best_file:
        alt = "checks/PART_CVII_e8_embedding_sage.json"
        if os.path.exists(alt):
            best_file = alt
    return best_file


# --- main completion attempt

def complete_from_partial(
    pos: Dict[int, Vector],
    root_list: List[Vector],
    roots_set: Set[Vector],
    n: int,
    adj: List[List[int]],
    time_limit: float,
    rng: random.Random,
):
    start = time.time()
    nodes = 0

    best = {
        "max_assigned": len(pos),
        "edges_satisfied": compute_edges_satisfied(pos, adj, roots_set),
        "pos": {str(k): list(v) for k, v in pos.items()},
        "time_at_best": 0.0,
    }

    order_cache = list(range(n))

    def candidates_for(v: int):
        assigned_neighbors = [w for w in adj[v] if w in pos]
        if not assigned_neighbors:
            base = next(iter(pos.values()))
            cands = [add_vec(base, r) for r in root_list]
            final = [c for c in cands if c not in pos.values()]
        else:
            w0 = assigned_neighbors[0]
            base0 = pos[w0]
            cand_set = {add_vec(base0, r) for r in root_list}
            for w in assigned_neighbors[1:]:
                base = pos[w]
                possible = {add_vec(base, r) for r in root_list}
                cand_set &= possible
                if not cand_set:
                    break
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
        # heuristic: sort by how many assigned-neighbor constraints it satisfies (desc)
        def score(c):
            s = 0
            for u in adj[v]:
                if u in pos:
                    if sub_vec(c, pos[u]) in roots_set or neg_vec(sub_vec(c, pos[u])) in roots_set:
                        s += 1
            return -s

        final.sort(key=score)
        # optionally shuffle among equal scores
        if len(final) > 1:
            rng.shuffle(final)
        return final

    def dfs():
        nonlocal nodes, best
        if time.time() - start > time_limit:
            return None
        nodes += 1
        # update best
        if len(pos) > best["max_assigned"]:
            best["max_assigned"] = len(pos)
            best["edges_satisfied"] = compute_edges_satisfied(pos, adj, roots_set)
            best["pos"] = {str(k): list(v) for k, v in pos.items()}
            best["time_at_best"] = time.time() - start
        if len(pos) == n:
            return dict(pos)
        # pick vertex with most assigned neighbors
        cand_v = None
        best_num = -1
        for v in range(n):
            if v in pos:
                continue
            num = sum(1 for w in adj[v] if w in pos)
            if num > best_num and num > 0:
                best_num = num
                cand_v = v
        if cand_v is None:
            for v in range(n):
                if v not in pos:
                    cand_v = v
                    break
        cands = candidates_for(cand_v)
        for c in cands:
            pos[cand_v] = c
            res = dfs()
            if res is not None:
                return res
            del pos[cand_v]
            if time.time() - start > time_limit:
                return None
        return None

    # sanity check initial partial
    conflicts = []
    for i in pos:
        for j in pos:
            if i < j:
                diff = sub_vec(pos[i], pos[j])
                is_root = diff in roots_set or neg_vec(diff) in roots_set
                if (j in adj[i]) and (not is_root):
                    conflicts.append({"edge_mismatch": [i, j]})
                if (j not in adj[i]) and is_root:
                    conflicts.append({"nonedge_root_diff": [i, j]})
    # if conflicts exist, include them but continue

    sol = dfs()
    elapsed = time.time() - start
    return {
        "found": bool(sol),
        "time_seconds": elapsed,
        "nodes": nodes,
        "assigned": len(pos) if sol is None else len(sol),
        "solution": ({str(k): list(v) for k, v in sol.items()} if sol is not None else None),
        "best": best,
        "conflicts_initial": conflicts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partial-file", type=str, default=None, help="JSON file containing a partial mapping to bootstrap from")
    parser.add_argument("--time-limit", type=float, default=3600.0, help="time limit in seconds")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--repair", action="store_true", help="prune inconsistent vertices from partial before attempting completion")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    if args.partial_file is None:
        pf = find_best_partial_in_checks()
        if not pf:
            raise SystemExit("No partial mapping file found in checks/; provide --partial-file")
    else:
        pf = args.partial_file

    print("Using partial file:", pf)
    data = json.load(open(pf))
    # Try multiple keys for partial
    posdata = None
    if data.get("best") and data["best"].get("pos"):
        posdata = data["best"]["pos"]
    elif data.get("positions"):
        posdata = data["positions"]
    elif data.get("pos"):
        posdata = data["pos"]
    elif data.get("best") and data["best"].get("pos") is None:
        posdata = {}
    if posdata is None:
        raise SystemExit("Partial file does not contain a pos/positions/best.pos mapping")

    pos = {int(k): tuple(v) for k, v in posdata.items()}

    print("Building E8 roots and W33 adjacency...")
    root_list = generate_scaled_e8_roots()
    roots_set = set(root_list)
    n, vertices, adj = build_w33_graph()

    # inspect initial partial for pairwise conflicts
    initial_conflicts = []
    for i in pos:
        for j in pos:
            if i < j:
                diff = sub_vec(pos[i], pos[j])
                is_root = diff in roots_set or neg_vec(diff) in roots_set
                if (j in adj[i]) and (not is_root):
                    initial_conflicts.append({"edge_mismatch": [i, j]})
                if (j not in adj[i]) and is_root:
                    initial_conflicts.append({"nonedge_root_diff": [i, j]})

    repair_removed = []
    if initial_conflicts and args.repair:
        print(f"Initial partial has {len(initial_conflicts)} conflicts; pruning...")
        pos, repair_removed = repair_partial(pos, adj, roots_set)
        print(f"Pruned {len(repair_removed)} vertices from partial: {repair_removed}")
    else:
        if initial_conflicts:
            print(f"Initial partial has {len(initial_conflicts)} conflicts; run with --repair to prune them.")

    # run completion
    res = complete_from_partial(pos, root_list, roots_set, n, adj, args.time_limit, rng)

    # attach provenance and repair metadata
    res["partial_file"] = pf
    res["seed"] = args.seed
    res["time_limit_requested"] = args.time_limit
    res["initial_conflicts_count"] = len(initial_conflicts)
    res["repair_removed"] = repair_removed

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)

    if res["found"]:
        print("Found embedding — wrote:", OUT)
    else:
        print("No embedding found within limits — wrote:", OUT)


if __name__ == "__main__":
    main()
