#!/usr/bin/env python3
"""Exhaustive local exchange search around the hill-climb solution:
try all 1-swap and 2-swap replacements to see if any strictly improve the objective.
Writes: tools/artifacts/schlafli_local_exchange_result.json
"""
from __future__ import annotations

import json
import time
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

# helpers
import importlib.util

modp = Path(__file__).parent / "find_schlafli_embedding_in_w33.py"
spec = importlib.util.spec_from_file_location(
    "find_schlafli_embedding_in_w33", str(modp)
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
construct_w33_points = mod.construct_w33_points
compute_w33_lines = mod.compute_w33_lines

# load hill-climb selection
hill_file = ART / "schlafli_near_miss_hillclimb.json"
hill = json.loads(hill_file.read_text()) if hill_file.exists() else None
hill_sel = hill.get("best_selected") if hill else None
hill_best = hill.get("best_score") if hill else None
if hill_sel is None:
    print("No hill-climb solution found; aborting.")
    raise SystemExit(1)

pts = construct_w33_points()
lines = compute_w33_lines(pts)
N = len(lines)
A = [[0] * N for _ in range(N)]
for i in range(N):
    for j in range(N):
        if i != j and set(lines[i]).isdisjoint(set(lines[j])):
            A[i][j] = 1

# pair target
pair_target = {
    (i, j): (10 if A[i][j] == 1 else 8) for i, j in combinations(range(N), 2)
}

# objective function
from functools import lru_cache


@lru_cache(None)
def pair_common(i, j, S_tuple):
    S = set(S_tuple)
    return sum(1 for k in S if A[i][k] and A[j][k])


def objective(S):
    Sset = set(S)
    deg_dev = 0
    for i in S:
        deg = sum(A[i][j] for j in S if j != i)
        deg_dev += abs(deg - 16)
    pair_dev = 0
    for i, j in combinations(S, 2):
        key = (i, j) if i < j else (j, i)
        t = pair_target[key]
        c = sum(1 for k in S if A[i][k] and A[j][k])
        pair_dev += abs(c - t)
    return deg_dev + pair_dev


start = tuple(hill_sel)
start_obj = hill_best
print("Start objective", start_obj)

best_obj = start_obj
best_set = list(start)

outsiders = [i for i in range(N) if i not in start]
insiders = list(start)

start_time = time.time()
# 1-swap
for u in insiders:
    for v in outsiders:
        new = list(start)
        new[new.index(u)] = v
        val = objective(new)
        if val < best_obj:
            best_obj = val
            best_set = new.copy()
            print("Found improvement with 1-swap", u, "->", v, "obj", val)

# 2-swap
for u1, u2 in combinations(insiders, 2):
    for v1, v2 in combinations(outsiders, 2):
        new = list(start)
        i1 = new.index(u1)
        i2 = new.index(u2)
        new[i1] = v1
        new[i2] = v2
        val = objective(new)
        if val < best_obj:
            best_obj = val
            best_set = new.copy()
            print("Found improvement with 2-swap", (u1, u2), "->", (v1, v2), "obj", val)

out = {
    "start_obj": start_obj,
    "best_obj": best_obj,
    "best_selected": best_set,
    "time": time.time() - start_time,
}
(ART / "schlafli_local_exchange_result.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Wrote", ART / "schlafli_local_exchange_result.json")
print(json.dumps(out, indent=2))
