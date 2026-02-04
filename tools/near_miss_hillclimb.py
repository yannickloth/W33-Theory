#!/usr/bin/env python3
"""Greedy hill-climb search to find a 27-subset minimizing total deviation
from Schlaefli SRG constraints (fast heuristic). Writes results to
tools/artifacts/schlafli_near_miss_hillclimb.json
"""
from __future__ import annotations

import json
import random
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# import helpers by path
import importlib.util

modp = Path(__file__).parent / "find_schlafli_embedding_in_w33.py"
spec = importlib.util.spec_from_file_location(
    "find_schlafli_embedding_in_w33", str(modp)
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
construct_w33_points = mod.construct_w33_points
compute_w33_lines = mod.compute_w33_lines

pts = construct_w33_points()
lines = compute_w33_lines(pts)
N = len(lines)
A = [[0] * N for _ in range(N)]
for i in range(N):
    for j in range(N):
        if i != j and set(lines[i]).isdisjoint(set(lines[j])):
            A[i][j] = 1

# precompute common neighbors count for any pair
common = [[0] * N for _ in range(N)]
for i in range(N):
    for j in range(N):
        if i == j:
            continue
        cnt = 0
        for k in range(N):
            if A[i][k] and A[j][k]:
                cnt += 1
        common[i][j] = cnt

pair_target = {
    (i, j): (10 if A[i][j] == 1 else 8) for i, j in combinations(range(N), 2)
}


# objective for subset S (list of indices)
def score_subset(S):
    Sset = set(S)
    # degree deviations
    deg_dev = 0
    for i in S:
        deg = sum(A[i][j] for j in S if j != i)
        deg_dev += abs(deg - 16)
    # pairwise deviations
    pair_dev = 0
    for i, j in combinations(S, 2):
        key = (i, j) if i < j else (j, i)
        t = pair_target[key]
        c = sum(1 for k in S if A[i][k] and A[j][k])
        pair_dev += abs(c - t)
    return deg_dev + pair_dev


# hill-climb with random restarts and best-first swaps
random.seed(0)
start_time = time.time()
best_sol = None
best_score = 10**9

TIME_BUDGET = 60.0  # seconds
RESTARTS = 500
for r in range(RESTARTS):
    if time.time() - start_time > TIME_BUDGET:
        break
    # initialize: choose 27 nodes with highest degree in A (heuristic), then randomize a bit
    degrees = [sum(row) for row in A]
    cand = sorted(range(N), key=lambda i: -degrees[i])[:27]
    # random perturbation: swap a few in-set nodes with outsiders
    outsiders = [i for i in range(N) if i not in cand]
    for _ in range(3):
        a_idx = random.randrange(len(cand))
        b_idx = random.randrange(len(outsiders))
        cand[a_idx] = outsiders[b_idx]
        outsiders = [i for i in range(N) if i not in cand]
    improved = True
    cur_score = score_subset(cand)
    while improved and time.time() - start_time <= TIME_BUDGET:
        improved = False
        # attempt all swaps (in_set, out_set) and take first improving swap
        in_set = set(cand)
        outsiders = [i for i in range(N) if i not in in_set]
        best_local_delta = 0
        best_swap = None
        for u in list(cand):
            for v in outsiders:
                new = cand.copy()
                new[new.index(u)] = v
                new_score = score_subset(new)
                delta = cur_score - new_score
                if delta > best_local_delta:
                    best_local_delta = delta
                    best_swap = (u, v, new_score, new)
        if best_swap:
            _, _, new_score, new = best_swap
            cand = new
            cur_score = new_score
            improved = True
    if cur_score < best_score:
        best_score = cur_score
        best_sol = cand.copy()
        print(
            f"New best: {best_score} at restart {r} (time {time.time()-start_time:.1f}s)"
        )

out = {
    "best_score": best_score,
    "best_selected": best_sol,
    "time": time.time() - start_time,
}
(ART / "schlafli_near_miss_hillclimb.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Wrote", ART / "schlafli_near_miss_hillclimb.json")
print(json.dumps(out, indent=2))
