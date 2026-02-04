#!/usr/bin/env python3
"""Find a 27-subset of W33 lines that minimizes total deviation from
Schlaefli SRG constraints (degrees and pairwise common neighbors).

Writes: tools/artifacts/schlafli_near_miss_result.json
"""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import pulp

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

# pair target: 10 if i-j edge else 8
pair_target = {}
for i, j in combinations(range(N), 2):
    pair_target[(i, j)] = 10 if A[i][j] == 1 else 8

# Build LP
prob = pulp.LpProblem("near_miss_schlafli", pulp.LpMinimize)
# selection variables
x = pulp.LpVariable.dicts("x", range(N), lowBound=0, upBound=1, cat="Binary")
# degree variables and deviations
deg = pulp.LpVariable.dicts("deg", range(N), lowBound=0, upBound=N, cat="Continuous")
dev_deg = pulp.LpVariable.dicts(
    "dev_deg", range(N), lowBound=0, upBound=N, cat="Continuous"
)
# pairwise common neighbor counts and deviations
c = {}
dev_pair = {}
for i, j in combinations(range(N), 2):
    c[(i, j)] = pulp.LpVariable(f"c_{i}_{j}", lowBound=0, upBound=N, cat="Continuous")
    dev_pair[(i, j)] = pulp.LpVariable(
        f"dev_{i}_{j}", lowBound=0, upBound=N, cat="Continuous"
    )

# cardinality
prob += pulp.lpSum([x[i] for i in range(N)]) == 27

# deg definition and deviation (only enforced when x[i]==1 using big-M)
Mdeg = 40
for i in range(N):
    prob += deg[i] == pulp.lpSum([A[i][j] * x[j] for j in range(N)])
    prob += dev_deg[i] >= deg[i] - 16 - Mdeg * (1 - x[i])
    prob += dev_deg[i] >= 16 - deg[i] - Mdeg * (1 - x[i])

# pairwise counts definition and deviation (enforced when both x[i] and x[j] ==1)
Mpair = 40
for i, j in combinations(range(N), 2):
    prob += c[(i, j)] == pulp.lpSum([A[i][k] * A[j][k] * x[k] for k in range(N)])
    t = pair_target[(i, j)]
    prob += dev_pair[(i, j)] >= c[(i, j)] - t - Mpair * (2 - x[i] - x[j])
    prob += dev_pair[(i, j)] >= t - c[(i, j)] - Mpair * (2 - x[i] - x[j])

# objective: minimize sum of degree deviations + sum of pairwise deviations
prob += pulp.lpSum([dev_deg[i] for i in range(N)]) + pulp.lpSum(
    [dev_pair[p] for p in dev_pair]
)

# solve with safe interruption handling
solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=600)
status = None
status_str = "Unknown"
interrupted = False
try:
    status = prob.solve(solver)
    status_str = pulp.LpStatus[status]
except KeyboardInterrupt:
    # user cancelled; capture partial solution if any
    interrupted = True
    status_str = "Interrupted"
except Exception as e:
    status_str = f"Error: {e}"

# gather solution (may be partial)
selected = [i for i in range(N) if pulp.value(x[i]) and pulp.value(x[i]) > 0.5]

# compute summary metrics
deg_vals = {i: round(pulp.value(deg[i])) for i in selected}
pair_devs = []
for i, j in combinations(range(N), 2):
    if i in selected and j in selected:
        # guard against None values
        cval = pulp.value(c[(i, j)])
        dval = pulp.value(dev_pair[(i, j)])
        pair_devs.append(
            (
                i,
                j,
                None if cval is None else round(cval),
                None if dval is None else round(dval),
            )
        )

out = {
    "status": status_str,
    "interrupted": interrupted,
    "objective": (
        None if pulp.value(prob.objective) is None else pulp.value(prob.objective)
    ),
    "selected": selected,
    "deg_vals": deg_vals,
    "pair_devs_count": len(pair_devs),
    "worst_pair_deviation": max((d for _, _, _, d in pair_devs), default=0),
    "sum_deg_deviation": sum(
        0 if pulp.value(dev_deg[i]) is None else round(pulp.value(dev_deg[i]))
        for i in selected
    ),
    "sum_pair_deviation": sum(0 if d is None else d for _, _, _, d in pair_devs),
}
(ART / "schlafli_near_miss_result.json").write_text(
    json.dumps(out, indent=2), encoding="utf-8"
)
print("Wrote", ART / "schlafli_near_miss_result.json")
print(json.dumps(out, indent=2))
