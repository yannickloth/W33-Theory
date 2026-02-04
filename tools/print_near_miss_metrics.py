#!/usr/bin/env python3
import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
J = json.loads((ART / "schlafli_near_miss_hillclimb.json").read_text())
selected = J["best_selected"]
# import helpers
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
# degrees
deg = {i: sum(A[i][j] for j in selected if j != i) for i in selected}
print("selected count", len(selected))
print("deg histogram:", sorted(deg.items(), key=lambda x: x[1]))
print("num deg==16", sum(1 for v in deg.values() if v == 16))
# pairwise
pair_devs = []
for i, j in combinations(selected, 2):
    key = (i, j) if i < j else (j, i)
    t = pair_target[key]
    c = sum(1 for k in selected if A[i][k] and A[j][k])
    pair_devs.append((i, j, c, t, abs(c - t)))
pair_devs_sorted = sorted(pair_devs, key=lambda x: x[4], reverse=True)
print("worst pair deviations (top 10):")
for p in pair_devs_sorted[:10]:
    print(p)
print("num pairs exact target", sum(1 for _, _, _, _, d in pair_devs if d == 0))
print("total pair dev sum", sum(d for _, _, _, _, d in pair_devs))
print(
    "total objective-like sum",
    sum(abs(deg[i] - 16) for i in selected) + sum(d for _, _, _, _, d in pair_devs),
)
