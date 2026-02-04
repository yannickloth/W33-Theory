#!/usr/bin/env python3
"""Simulated annealing to minimize deviation from Schlaefli SRG constraints.
Writes: tools/artifacts/schlafli_near_miss_anneal.json
"""
from __future__ import annotations

import json
import math
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

pair_target = {
    (i, j): (10 if A[i][j] == 1 else 8) for i, j in combinations(range(N), 2)
}


# score function
def score_subset(S):
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


# seed with hillclimb best if available
seed_file = ART / "schlafli_near_miss_hillclimb.json"
if seed_file.exists():
    j = json.loads(seed_file.read_text())
    start = j.get("best_selected", None)
else:
    start = None

if start is None:
    # choose 27 nodes with largest degrees
    degrees = [sum(row) for row in A]
    start = sorted(range(N), key=lambda i: -degrees[i])[:27]

# annealing parameters
TIME_BUDGET = 600.0  # seconds
T0 = 200.0
END_T = 1e-3
start_time = time.time()
random.seed(42)

current = list(start)
cur_score = score_subset(current)
best = current.copy()
best_score = cur_score

it = 0
last_save = start_time
history = [(0.0, best_score)]

print(f"Starting anneal: initial score {cur_score}, seed len {len(current)}")

while time.time() - start_time < TIME_BUDGET:
    it += 1
    tfrac = (time.time() - start_time) / TIME_BUDGET
    # geometric schedule
    T = T0 * (1 - tfrac) + END_T

    # propose swap: pick random in-set index and random outside
    in_idx = random.randrange(len(current))
    out_candidates = [i for i in range(N) if i not in current]
    out_idx = random.choice(out_candidates)

    new = current.copy()
    new[in_idx] = out_idx
    new_score = score_subset(new)
    delta = new_score - cur_score
    accept = False
    if delta <= 0:
        accept = True
    else:
        p = math.exp(-delta / T) if T > 0 else 0.0
        if random.random() < p:
            accept = True
    if accept:
        current = new
        cur_score = new_score
        if cur_score < best_score:
            best = current.copy()
            best_score = cur_score
            history.append((time.time() - start_time, best_score))
            print(f"New best {best_score} at {time.time()-start_time:.1f}s (iter {it})")

    # occasional larger move
    if it % 500 == 0:
        # try a double-swap
        a = random.sample(range(len(current)), 2)
        outs = random.sample([i for i in range(N) if i not in current], 2)
        new2 = current.copy()
        new2[a[0]] = outs[0]
        new2[a[1]] = outs[1]
        s2 = score_subset(new2)
        if s2 < cur_score or random.random() < math.exp(
            -(s2 - cur_score) / max(T, 1e-9)
        ):
            current = new2
            cur_score = s2
            if cur_score < best_score:
                best = current.copy()
                best_score = cur_score
                history.append((time.time() - start_time, best_score))
                print(
                    f"New best {best_score} at {time.time()-start_time:.1f}s (iter {it})"
                )

    # periodic save
    if time.time() - last_save > 20:
        out = {
            "status": "running",
            "elapsed": time.time() - start_time,
            "best_score": best_score,
            "best_selected": best,
            "iterations": it,
            "history": history[-20:],
        }
        (ART / "schlafli_near_miss_anneal_partial.json").write_text(
            json.dumps(out, indent=2), encoding="utf-8"
        )
        last_save = time.time()

# final write
out = {
    "status": "done",
    "elapsed": time.time() - start_time,
    "best_score": best_score,
    "best_selected": best,
    "iterations": it,
    "history": history,
}
(ART / "schlafli_near_miss_anneal.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Finished anneal; wrote", ART / "schlafli_near_miss_anneal.json")
print(json.dumps(out, indent=2))
