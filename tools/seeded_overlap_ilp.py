#!/usr/bin/env python3
"""Overlap-seeded ILP: force overlap with hill-climb solution and minimize deviation.
Writes: tools/artifacts/schlafli_seeded_overlap_result.json
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import pulp

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
if hill_sel is None:
    print("No hill-climb solution found; aborting.")
    raise SystemExit(1)

print(f"Hill-climb selection length {len(hill_sel)}")

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

# Build MILP
prob = pulp.LpProblem("seeded_overlap", pulp.LpMinimize)
# variables
x = pulp.LpVariable.dicts("x", range(N), lowBound=0, upBound=1, cat="Binary")
# degree deviations
deg = pulp.LpVariable.dicts("deg", range(N), lowBound=0, upBound=N, cat="Continuous")
dev_deg = pulp.LpVariable.dicts(
    "dev_deg", range(N), lowBound=0, upBound=N, cat="Continuous"
)
# pair deviations
c = {}
dev_pair = {}
for i, j in combinations(range(N), 2):
    key = (i, j) if i < j else (j, i)
    c[key] = pulp.LpVariable(
        f"c_{key[0]}_{key[1]}", lowBound=0, upBound=N, cat="Continuous"
    )
    dev_pair[key] = pulp.LpVariable(
        f"dev_{key[0]}_{key[1]}", lowBound=0, upBound=N, cat="Continuous"
    )

# cardinality
prob += pulp.lpSum([x[i] for i in range(N)]) == 27

# overlap constraint: enforce at least K of hill_sel
K = 24
prob += pulp.lpSum([x[i] for i in hill_sel]) >= K
print(f"Enforced overlap >= {K}")

# degree definitions and deviations
Mdeg = 40
for i in range(N):
    prob += deg[i] == pulp.lpSum([A[i][j] * x[j] for j in range(N)])
    prob += dev_deg[i] >= deg[i] - 16 - Mdeg * (1 - x[i])
    prob += dev_deg[i] >= 16 - deg[i] - Mdeg * (1 - x[i])

# pairwise counts
Mpair = 40
for i, j in combinations(range(N), 2):
    key = (i, j) if i < j else (j, i)
    prob += c[key] == pulp.lpSum([A[i][k] * A[j][k] * x[k] for k in range(N)])
    t = pair_target[key]
    prob += dev_pair[key] >= c[key] - t - Mpair * (2 - x[i] - x[j])
    prob += dev_pair[key] >= t - c[key] - Mpair * (2 - x[i] - x[j])

# objective
total_dev = pulp.lpSum([dev_deg[i] for i in range(N)]) + pulp.lpSum(
    [dev_pair[p] for p in dev_pair]
)
prob += total_dev

# solve
solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=600)
status = None
status_str = "Unknown"
selected = []
obj_val = None
try:
    status = prob.solve(solver)
    status_str = pulp.LpStatus[status]
    selected = [i for i in range(N) if pulp.value(x[i]) and pulp.value(x[i]) > 0.5]
    obj_val = None if pulp.value(total_dev) is None else pulp.value(total_dev)
    print("Status", status_str)
except Exception as e:
    status_str = f"Error: {e}"
    print("Solver error:", e)

out = {
    "status": status_str,
    "objective": obj_val,
    "selected": selected,
}
(ART / "schlafli_seeded_overlap_result.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Wrote", ART / "schlafli_seeded_overlap_result.json")
print(json.dumps(out, indent=2))
