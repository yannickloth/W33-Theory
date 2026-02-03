#!/usr/bin/env python3
"""Analyze the hill-climb near-miss solution and report per-node and pair summaries."""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)

res = json.loads((ART / "schlafli_near_miss_hillclimb.json").read_text())
selected = res["best_selected"]

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

# per-node degree under selected
deg = {i: sum(A[i][j] for j in selected if j != i) for i in selected}
# per-pair deviations
pair_devs = []
for i, j in combinations(selected, 2):
    key = (i, j) if i < j else (j, i)
    t = pair_target[key]
    c = sum(1 for k in selected if A[i][k] and A[j][k])
    pair_devs.append(((i, j), c, t, abs(c - t)))

out = {
    "best_score": res["best_score"],
    "selected": selected,
    "deg": deg,
    "num_deg_exact_16": sum(1 for v in deg.values() if v == 16),
    "pair_devs_summary": {
        "num_pairs_exact": sum(1 for _, _, _, d in pair_devs if d == 0),
        "worst_pair_dev": max((d for _, _, _, d in pair_devs), default=0),
    },
}
(ART / "schlafli_near_miss_hillclimb_analysis.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print(json.dumps(out, indent=2))
